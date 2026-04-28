"""
langchain_pipeline.py
──────────────────────
The core RAG pipeline for the AI Gift Finder.

Architecture:
  Step 1 — Query Parser Chain
    User query (string)
    → LLM (OpenRouter / Mixtral)
    → QueryContext (validated Pydantic model)

  Step 2 — Vector Search
    QueryContext
    → FAISS similarity search (HuggingFace embeddings, local)
    → List[(product_dict, similarity_score)]

  Step 3 — LLM Recommendation Chain
    Retrieved products + QueryContext
    → LLM (OpenRouter / Mixtral)
    → Raw JSON string

  Step 4 — Output Validation
    Raw JSON string
    → GiftResponse (Pydantic model, strict schema)
    → Always valid JSON response

Usage:
  pipeline = GiftFinderPipeline()
  response = await pipeline.run("thoughtful gift for 6-month-old under 200 AED")
"""

from __future__ import annotations

import json
import logging
import re
from typing import Any, Dict

from langchain_openai import ChatOpenAI
from tenacity import retry, stop_after_attempt, wait_exponential

from .config import get_settings
from .embeddings.vector_store import VectorStoreManager, get_vector_store
from .prompts.templates import QUERY_PARSER_PROMPT, RECOMMENDATION_PROMPT
from .validators.schemas import (
    GiftResponse,
    Intent,
    Language,
    ProductResult,
    QueryContext,
)

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# Utilities
# ─────────────────────────────────────────────────────────────────────────────

def _extract_json(text: str) -> str:
    """
    Robustly extract JSON from LLM output that may contain markdown fences
    or surrounding prose.

    Tries in order:
      1. Strip markdown fences (```json ... ```)
      2. Find first '{' to last '}'
      3. Return the raw text as-is and let the caller handle the error
    """
    # Remove ```json ... ``` fences
    text = re.sub(r"```json\s*", "", text)
    text = re.sub(r"```\s*", "", text)
    text = text.strip()

    # Find JSON object boundaries
    start = text.find("{")
    end = text.rfind("}") + 1
    if start != -1 and end > start:
        return text[start:end]

    return text


def _build_llm(settings=None) -> ChatOpenAI:
    """
    Instantiate a ChatOpenAI client pointed at OpenRouter.

    OpenRouter uses an OpenAI-compatible API so langchain_openai works out-of-the-box.
    We just override base_url and api_key.
    """
    if settings is None:
        settings = get_settings()

    return ChatOpenAI(
        model=settings.openrouter_model,
        openai_api_key=settings.openrouter_api_key,
        openai_api_base=settings.openrouter_base_url,
        temperature=0.2,          # Low temp → consistent, factual output
        max_tokens=2048,
        model_kwargs={
            # OpenRouter-specific: identifies your app in their dashboard
            "extra_headers": {
                "HTTP-Referer": "https://giftfinder.local",
                "X-Title": "AI Gift Finder",
            }
        },
    )


# ─────────────────────────────────────────────────────────────────────────────
# Main Pipeline
# ─────────────────────────────────────────────────────────────────────────────

class GiftFinderPipeline:
    """
    Orchestrates the full 4-step RAG pipeline.

    Thread-safe for concurrent use — all state is either immutable or
    created per-call. The LLM client and vector store are shared.
    """

    def __init__(self):
        self._settings = get_settings()
        self._llm = _build_llm(self._settings)
        self._vector_store: VectorStoreManager | None = None  # lazy-loaded

    # ── Internal: lazy vector store access ───────────────────────────────────

    @property
    def vector_store(self) -> VectorStoreManager:
        if self._vector_store is None:
            self._vector_store = get_vector_store()
        return self._vector_store

    # ─────────────────────────────────────────────────────────────────────────
    # Step 1: Query Parser
    # ─────────────────────────────────────────────────────────────────────────

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
    )
    async def _parse_query(self, query: str) -> QueryContext:
        """
        Call the LLM to extract structured intent from the raw user query.

        Returns a validated QueryContext. Falls back to a minimal default
        if the LLM returns unparseable output.
        """
        logger.info("Step 1 — Parsing query: %r", query)

        chain = QUERY_PARSER_PROMPT | self._llm
        response = await chain.ainvoke({"query": query})

        raw_text = response.content if hasattr(response, "content") else str(response)
        logger.debug("Query parser raw output: %s", raw_text)

        try:
            json_str = _extract_json(raw_text)
            data = json.loads(json_str)
            context = QueryContext(raw_query=query, **data)
            logger.info(
                "Parsed context — lang=%s budget=%s age=%s intent=%s",
                context.language,
                context.budget_aed,
                context.baby_age_months,
                context.intent,
            )
            return context

        except (json.JSONDecodeError, ValueError, TypeError) as exc:
            logger.warning("Query parser JSON parse failed (%s). Using fallback context.", exc)
            # Graceful degradation: create a minimal context
            return QueryContext(
                raw_query=query,
                language=Language.EN,
                intent=Intent.UNKNOWN,
                keywords=query.lower().split()[:5],
            )

    # ─────────────────────────────────────────────────────────────────────────
    # Step 2: Vector Search / Retrieval
    # ─────────────────────────────────────────────────────────────────────────

    def _retrieve_products(self, context: QueryContext) -> list:
        """
        Run semantic search over the FAISS index.

        The search query combines the raw query with extracted keywords for
        richer semantic coverage.
        """
        logger.info("Step 2 — Retrieving products from vector store...")

        # Build a rich search query from context
        search_query = context.raw_query
        if context.keywords:
            search_query += " " + " ".join(context.keywords)

        retrieved = self.vector_store.retrieve(
            query=search_query,
            budget_aed=context.budget_aed,
            baby_age_months=context.baby_age_months,
        )

        logger.info("Retrieved %d products after filtering.", len(retrieved))
        for product, score in retrieved:
            logger.debug("  • %s (%.2f AED) similarity=%.3f", product["name"], product["price_aed"], score)

        return retrieved

    # ─────────────────────────────────────────────────────────────────────────
    # Step 3: LLM Recommendation
    # ─────────────────────────────────────────────────────────────────────────

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
    )
    async def _generate_recommendations(
        self,
        context: QueryContext,
        retrieved: list,
    ) -> Dict[str, Any]:
        """
        Pass the retrieved product catalog to the LLM and generate recommendations.

        The catalog is injected directly into the prompt — the LLM can only
        recommend products it explicitly sees, eliminating hallucination.
        """
        logger.info("Step 3 — Generating recommendations with LLM...")

        catalog_str = self.vector_store.format_catalog_for_prompt(retrieved)

        chain = RECOMMENDATION_PROMPT | self._llm
        response = await chain.ainvoke({
            "raw_query": context.raw_query,
            "query_language": context.language.value,
            "budget_aed": context.budget_aed or "No limit",
            "baby_age_months": context.baby_age_months or "Not specified",
            "intent": context.intent.value,
            "keywords": ", ".join(context.keywords) if context.keywords else "N/A",
            "product_catalog": catalog_str,
        })

        raw_text = response.content if hasattr(response, "content") else str(response)
        logger.debug("Recommendation raw output: %s", raw_text)

        json_str = _extract_json(raw_text)
        return json.loads(json_str)

    # ─────────────────────────────────────────────────────────────────────────
    # Step 4: Output Validation
    # ─────────────────────────────────────────────────────────────────────────

    def _validate_output(
        self,
        raw_data: Dict[str, Any],
        context: QueryContext,
        retrieval_count: int,
    ) -> GiftResponse:
        """
        Validate and coerce the LLM's JSON output into a strict GiftResponse.

        Applies post-validation business rules:
          • Enforce minimum confidence threshold
          • Enforce category diversity (max 1 per category)
          • Always includes query_context for transparency
        """
        logger.info("Step 4 — Validating output schema...")

        language = Language(raw_data.get("language", context.language.value))
        raw_products = raw_data.get("products", [])

        validated_products = []
        seen_categories: set[str] = set()

        for item in raw_products:
            try:
                product = ProductResult(**item)
            except Exception as exc:
                logger.warning("Skipping malformed product entry: %s — %s", item, exc)
                continue

            # Confidence gate
            if product.confidence < self._settings.min_confidence:
                logger.debug("Filtered low-confidence product: %s (%.2f)", product.name, product.confidence)
                continue

            # Category diversity constraint
            cat = (product.category or "").lower()
            if cat and cat in seen_categories:
                logger.debug("Skipping duplicate category: %s", cat)
                continue
            if cat:
                seen_categories.add(cat)

            validated_products.append(product)

        response = GiftResponse(
            products=validated_products,
            language=language,
            query_context=context,
            retrieval_count=retrieval_count,
        )

        logger.info(
            "Final response: %d products returned (lang=%s)",
            len(response.products),
            response.language.value,
        )
        return response

    # ─────────────────────────────────────────────────────────────────────────
    # Public Entry Point
    # ─────────────────────────────────────────────────────────────────────────

    async def run(self, query: str) -> GiftResponse:
        """
        Execute the full pipeline for a user query.

        Args:
            query: Natural language gift query in English or Arabic.

        Returns:
            GiftResponse — always valid JSON-serializable, never raises.
        """
        logger.info("═══ Gift Finder Pipeline START ═══")
        logger.info("Query: %r", query)

        # ── Step 1: Parse query ───────────────────────────────────────────────
        try:
            context = await self._parse_query(query)
        except Exception as exc:
            logger.error("Query parsing failed permanently: %s", exc)
            return GiftResponse.empty(
                message=f"Failed to understand your query. Please rephrase and try again."
            )

        # ── Step 2: Retrieve products ─────────────────────────────────────────
        retrieved = self._retrieve_products(context)

        # Early exit: no products match hard constraints at all
        if not retrieved:
            logger.warning("No products retrieved after filtering. Returning empty response.")
            return GiftResponse.empty(
                language=context.language,
                message=(
                    "عذراً، لم أجد منتجات ضمن معاييرك."
                    if context.language == Language.AR
                    else "I don't know — no products match your filters (budget / age)."
                ),
            )

        # ── Step 3: Generate recommendations ─────────────────────────────────
        try:
            raw_data = await self._generate_recommendations(context, retrieved)
        except (json.JSONDecodeError, Exception) as exc:
            logger.error("Recommendation generation failed: %s", exc)
            return GiftResponse.empty(
                language=context.language,
                message="Recommendation engine encountered an error. Please try again.",
            )

        # ── Step 4: Validate and return ───────────────────────────────────────
        try:
            response = self._validate_output(raw_data, context, len(retrieved))
        except Exception as exc:
            logger.error("Output validation failed: %s", exc)
            return GiftResponse.empty(
                language=context.language,
                message="Output validation failed. Please try again.",
            )

        logger.info("═══ Gift Finder Pipeline END ═══\n")
        return response


# ─────────────────────────────────────────────────────────────────────────────
# Module-level singleton
# ─────────────────────────────────────────────────────────────────────────────

_pipeline_singleton: GiftFinderPipeline | None = None


def get_pipeline() -> GiftFinderPipeline:
    """Return the shared GiftFinderPipeline singleton."""
    global _pipeline_singleton
    if _pipeline_singleton is None:
        _pipeline_singleton = GiftFinderPipeline()
    return _pipeline_singleton


def run_pipeline(query: str) -> GiftResponse:
    """
    Synchronous wrapper for the async pipeline.
    Used by run.py entry point.
    """
    import asyncio
    pipeline = get_pipeline()
    return asyncio.run(pipeline.run(query))