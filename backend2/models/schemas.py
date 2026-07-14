from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field


class UserRequest(BaseModel):
    message: str


class Budget(BaseModel):
    min: Optional[int] = None
    max: Optional[int] = None


class Persona(BaseModel):
    age_range: Optional[str] = None       # 改名：原本叫 age_group，統一對齊前端的 age_range
    occupation: Optional[str] = None
    usage_scope: Optional[str] = None     # 新增：個人用／家庭用／送禮（來自 Filter 問卷 Q9）
    current_device: Optional[str] = None  # 新增：目前使用中的穿戴裝置


class Preferences(BaseModel):
    os: Optional[str] = None
    brand: Optional[str] = None
    style: Optional[str] = None
    battery: Optional[str] = None


class RawInput(BaseModel):
    text: Optional[str] = None
    filters: Optional[Dict[str, Any]] = None


class UserNeed(BaseModel):
    persona: Persona = Field(default_factory=Persona)
    budget: Budget = Field(default_factory=Budget)
    device_type: Optional[str] = None
    usage: List[str] = Field(default_factory=list)
    features: List[str] = Field(default_factory=list)
    preferences: Preferences = Field(default_factory=Preferences)
    priorities: List[str] = Field(default_factory=list)
    search_query: Optional[str] = None
    raw: RawInput = Field(default_factory=RawInput)

    def to_dict(self):
        if hasattr(self, "model_dump"):
            return self.model_dump()

        return self.dict()


class RecommendationRequest(BaseModel):
    source: Literal["chat", "filter"]
    need: UserNeed
