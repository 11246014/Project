from datetime import datetime
from typing import List, Optional,Dict,Any
from pydantic import BaseModel


class UserCreate(BaseModel):
    username: str
    email: str
    password: str


class ProductCreate(BaseModel):
    name: str
    price: int
    description: str


class ProductResponse(BaseModel):
    id: int
    name: str
    price: int
    description: str

    class Config:
        from_attributes = True
# =========================
# Sponsor Schema
# =========================

class SponsorResponse(BaseModel):

    brand_name: str
    platform: str
    sponsor_level: str
    boost_rate: float
    is_active: bool


class SponsorListResponse(BaseModel):

    sponsors: List[SponsorResponse]


class RecommendationEventCreate(BaseModel):
    source: str
    age_range: Optional[str] = None
    occupation: Optional[str] = None
    usage_scope: Optional[str] = None
    device_type: Optional[str] = None
    usage: Optional[str] = None
    features: Optional[str] = None
    os: Optional[str] = None
    brand_preference: Optional[str] = None
    budget_min: Optional[int] = None
    budget_max: Optional[int] = None
    top_brands: Optional[str] = None
    top_platforms: Optional[str] = None
    product_count: int = 0

# =========================
# Analytics Summary Schema
# =========================

class AnalyticsSummaryResponse(BaseModel):

    total_recommendations: int

    popular_brands: List[Dict[str, Any]]

    popular_products: List[Dict[str, Any]]

    average_match_score: float

    sponsored_exposure_rate: float