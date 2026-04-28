"""
validators/schemas.py — Strict Pydantic v2 schemas.
QueryContext → ProductResult → GiftResponse
"""
from __future__ import annotations
from enum import Enum
from typing import Annotated, List, Optional
from pydantic import BaseModel, Field, field_validator, model_validator


class Language(str, Enum):
    EN = "EN"
    AR = "AR"


class Intent(str, Enum):
    PRACTICAL = "practical"
    EMOTIONAL = "emotional"
    MIXED = "mixed"
    UNKNOWN = "unknown"


class QueryContext(BaseModel):
    raw_query: str
    language: Language
    budget_aed: Optional[float] = Field(None, ge=0)
    baby_age_months: Optional[int] = Field(None, ge=0, le=120)
    intent: Intent = Intent.MIXED
    keywords: List[str] = Field(default_factory=list)
    recipient_description: Optional[str] = None

    @field_validator("budget_aed", mode="before")
    @classmethod
    def coerce_budget(cls, v):
        if v is None or v == "":
            return None
        try:
            return float(v)
        except (ValueError, TypeError):
            return None

    @field_validator("baby_age_months", mode="before")
    @classmethod
    def coerce_age(cls, v):
        if v is None or v == "":
            return None
        try:
            return int(v)
        except (ValueError, TypeError):
            return None


class ProductResult(BaseModel):
    name: str
    price: str
    reason: str
    age_fit: str
    confidence: Annotated[float, Field(ge=0.0, le=1.0)]
    category: Optional[str] = None
    brand: Optional[str] = None
    in_stock: Optional[bool] = None
    rating: Optional[float] = Field(None, ge=0, le=5)
    image_url: Optional[str] = None
    purchase_link: Optional[str] = None

    @field_validator("confidence")
    @classmethod
    def round_confidence(cls, v: float) -> float:
        return round(v, 2)

    @field_validator("price", mode="before")
    @classmethod
    def format_price(cls, v) -> str:
        if isinstance(v, (int, float)):
            return f"{v:.0f} AED"
        return str(v)


class GiftResponse(BaseModel):
    products: List[ProductResult] = Field(default_factory=list)
    language: Language = Language.EN
    message: Optional[str] = None
    query_context: Optional[QueryContext] = None
    retrieval_count: int = 0

    @model_validator(mode="after")
    def ensure_message_on_empty(self) -> "GiftResponse":
        if not self.products and not self.message:
            if self.language == Language.AR:
                self.message = "عذراً، لم أجد منتجات مناسبة لطلبك. حاول تعديل الميزانية أو العمر."
            else:
                self.message = (
                    "I don't know — no products in our catalog match your criteria. "
                    "Try adjusting the budget or age range."
                )
        return self

    @classmethod
    def empty(cls, language: Language = Language.EN, message: str | None = None) -> "GiftResponse":
        return cls(products=[], language=language, message=message)