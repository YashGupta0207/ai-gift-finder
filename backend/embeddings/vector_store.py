"""
embeddings/vector_store.py
───────────────────────────
Builds and manages the FAISS vector store over the products catalog.

Flow:
  1. Load products.json
  2. Build rich text documents from each product (EN + AR fields merged)
  3. Embed with HuggingFace sentence-transformers (local, no API needed)
  4. Store/load FAISS index to/from disk for fast startup
  5. Expose retrieve() for similarity-based product lookup
"""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Dict, List, Tuple

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings

from ..config import get_settings

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _load_products(path: str) -> List[Dict]:
    """Load and validate the products JSON file."""
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Products file not found: {path}")
    with open(p, encoding="utf-8") as f:
        products = json.load(f)
    logger.info("Loaded %d products from %s", len(products), path)
    return products


def _product_to_document(product: Dict) -> Document:
    """
    Convert a product dict into a LangChain Document.

    The page_content is a rich, natural-language description combining all
    searchable fields so that semantic search works well across EN and AR queries.
    The full product dict is stored in metadata for downstream use.
    """
    tags = ", ".join(product.get("tags", []))
    intent = ", ".join(product.get("intent", []))
    age_range = f"{product.get('min_age_months', 0)}–{product.get('max_age_months', 120)} months"

    content = (
        f"Product: {product['name']}. "
        f"Arabic name: {product.get('name_ar', '')}. "
        f"Brand: {product.get('brand', '')}. "
        f"Category: {product.get('category', '')}. "
        f"Price: {product['price_aed']} AED. "
        f"Age range: {age_range}. "
        f"Tags: {tags}. "
        f"Intent: {intent}. "
        f"Description: {product.get('description', '')} "
        f"Arabic description: {product.get('description_ar', '')}. "
        f"In stock: {product.get('in_stock', True)}. "
        f"Rating: {product.get('rating', 0)}/5."
    )
    return Document(page_content=content, metadata=product)


# ─────────────────────────────────────────────────────────────────────────────
# Public: VectorStoreManager
# ─────────────────────────────────────────────────────────────────────────────

class VectorStoreManager:
    """
    Manages the FAISS vector store lifecycle:
      - Build from products.json on first run
      - Persist to disk and reload on subsequent runs
      - Expose retrieve() for RAG pipeline consumption
    """

    def __init__(self):
        settings = get_settings()
        self._index_path = settings.faiss_index_path
        self._products_path = settings.products_path
        self._embedding_model_name = settings.embedding_model
        self._top_k = settings.top_k_retrieval

        self._embeddings: HuggingFaceEmbeddings | None = None
        self._store: FAISS | None = None
        self._products: List[Dict] = []

    # ── Initialization ────────────────────────────────────────────────────────

    def initialize(self) -> None:
        """
        Load or build the FAISS index.
        Call once at application startup.
        """
        logger.info("Initializing embedding model: %s", self._embedding_model_name)
        self._embeddings = HuggingFaceEmbeddings(
            model_name=self._embedding_model_name,
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True},
        )

        self._products = _load_products(self._products_path)

        index_dir = Path(self._index_path)
        if index_dir.exists() and any(index_dir.iterdir()):
            logger.info("Loading existing FAISS index from %s", self._index_path)
            self._store = FAISS.load_local(
                self._index_path,
                self._embeddings,
                allow_dangerous_deserialization=True,
            )
        else:
            logger.info("Building new FAISS index from products...")
            self._build_and_persist()

        logger.info("Vector store ready — %d products indexed.", len(self._products))

    def _build_and_persist(self) -> None:
        """Embed all products and save FAISS index to disk."""
        documents = [_product_to_document(p) for p in self._products]
        self._store = FAISS.from_documents(documents, self._embeddings)

        os.makedirs(self._index_path, exist_ok=True)
        self._store.save_local(self._index_path)
        logger.info("FAISS index saved to %s", self._index_path)

    # ── Retrieval ─────────────────────────────────────────────────────────────

    def retrieve(
        self,
        query: str,
        budget_aed: float | None = None,
        baby_age_months: int | None = None,
        top_k: int | None = None,
    ) -> List[Tuple[Dict, float]]:
        """
        Retrieve the most relevant products for a query.

        Returns a list of (product_dict, similarity_score) tuples,
        pre-filtered by budget and age constraints.

        Args:
            query:             Natural language query for semantic search.
            budget_aed:        If set, exclude products above this price.
            baby_age_months:   If set, exclude products outside age range.
            top_k:             Number of results (defaults to config value).

        Returns:
            List of (product_dict, score) sorted by score descending.
        """
        if self._store is None:
            raise RuntimeError("VectorStoreManager not initialized. Call initialize() first.")

        k = top_k or self._top_k
        # Fetch extra candidates to allow for post-filtering
        fetch_k = min(k * 3, len(self._products))

        results = self._store.similarity_search_with_score(query, k=fetch_k)

        filtered: List[Tuple[Dict, float]] = []
        for doc, score in results:
            product = doc.metadata

            # ── Hard filters ───────────────────────────────────────────────
            # Skip out-of-stock items
            if not product.get("in_stock", True):
                continue

            # Skip over-budget items
            if budget_aed is not None and product.get("price_aed", 0) > budget_aed:
                continue

            # Skip age-inappropriate items
            if baby_age_months is not None:
                min_age = product.get("min_age_months", 0)
                max_age = product.get("max_age_months", 120)
                if not (min_age <= baby_age_months <= max_age):
                    continue

            # FAISS returns L2 distances; lower = more similar.
            # Normalize to a 0–1 similarity score.
            similarity = float(max(0.0, 1.0 - score / 2.0))
            filtered.append((product, round(similarity, 3)))

        # Sort by similarity descending and cap at k
        filtered.sort(key=lambda x: x[1], reverse=True)
        return filtered[:k]

    def format_catalog_for_prompt(
        self, retrieved: List[Tuple[Dict, float]]
    ) -> str:
        """
        Format retrieved products into a numbered catalog string for LLM injection.

        Example output:
          [1] Fisher-Price Baby's First Blocks | 89 AED | 6-36 months
              Tags: learning, motor skills | Similarity: 0.92
              Description: Classic shape-sorting toy...
        """
        if not retrieved:
            return "No products available."

        lines: List[str] = []
        for i, (product, score) in enumerate(retrieved, start=1):
            age_range = f"{product.get('min_age_months', 0)}-{product.get('max_age_months', 120)} months"
            tags = ", ".join(product.get("tags", []))
            lines.append(
                f"[{i}] {product['name']} | {product['price_aed']} AED | {age_range}\n"
                f"    Brand: {product.get('brand', 'N/A')} | "
                f"Category: {product.get('category', 'N/A')} | "
                f"In Stock: {product.get('in_stock', True)} | "
                f"Similarity: {score}\n"
                f"    Tags: {tags}\n"
                f"    Description: {product.get('description', '')}\n"
                f"    Arabic Name: {product.get('name_ar', '')}"
            )

        return "\n\n".join(lines)

    @property
    def products(self) -> List[Dict]:
        return self._products


# ─────────────────────────────────────────────────────────────────────────────
# Module-level singleton
# ─────────────────────────────────────────────────────────────────────────────

_vector_store_singleton: VectorStoreManager | None = None


def get_vector_store() -> VectorStoreManager:
    """Return the initialized singleton VectorStoreManager."""
    global _vector_store_singleton
    if _vector_store_singleton is None:
        _vector_store_singleton = VectorStoreManager()
        _vector_store_singleton.initialize()
    return _vector_store_singleton