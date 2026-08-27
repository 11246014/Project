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


# =========================
# Analytics Event Schema
# =========================

class RecommendationEventCreate(BaseModel):

    timestamp: Optional[datetime] = None

    user_need: Dict[str, Any]

    recommend_results: List[Dict[str, Any]]


# =========================
# Analytics Summary Schema
# =========================

class AnalyticsSummaryResponse(BaseModel):

    total_recommendations: int

    popular_brands: List[Dict[str, Any]]

    popular_products: List[Dict[str, Any]]

    average_match_score: float

    sponsored_exposure_rate: float