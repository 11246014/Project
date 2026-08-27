#filter_adapter.py
from models.schemas import (
    Budget,
    Persona,
    Preferences,
    RawInput,
    RecommendationRequest,
    UserNeed,
)

from services.vocabulary_normalizer import (
    normalize_battery,
    normalize_device_type,
    normalize_feature,
    normalize_list,
    normalize_os,
    normalize_priority,
    normalize_style,
    normalize_usage,
)


def _as_list(value):

    if value is None or value == "":
        return []

    if isinstance(value, list):
        return value

    return [value]


def _none_if_empty(value):

    if value in ("", [], {}, 0):
        return None

    return value


def adapt_filter_request(filters):

    original_filters = filters or {}

    need = UserNeed(

        # =========================
        # Persona
        # =========================

        persona=Persona(

            age_range=_none_if_empty(
                original_filters.get("age_range")
            ),

            occupation=_none_if_empty(
                original_filters.get("occupation")
            ),

            usage_scope=_none_if_empty(
                original_filters.get("usage_scope")
            ),

            current_device=_none_if_empty(
                original_filters.get("current_device")
            ),
        ),

        # =========================
        # Budget
        # =========================

        budget=Budget(

            min=_none_if_empty(
                original_filters.get("min_price")
            ),

            max=_none_if_empty(
                original_filters.get("max_price")
            ),
        ),

        # =========================
        # Device
        # =========================

        device_type=normalize_device_type(
            original_filters.get("device_type")
        ),

        # =========================
        # Usage
        # =========================

        usage=normalize_list(
            original_filters.get("usage"),
            normalize_usage
        ),

        # =========================
        # Features
        # =========================

        features=normalize_list(
            original_filters.get("features"),
            normalize_feature
        ),

        # =========================
        # Preferences
        # =========================

        preferences=Preferences(

            os=normalize_os(
                original_filters.get("os")
            ),

            style=normalize_style(
                original_filters.get("style")
            ),

            battery=normalize_battery(
                original_filters.get("battery")
            ),
        ),

        # =========================
        # Priorities
        # =========================

        priorities=normalize_list(
            original_filters.get("core_factors"),
            normalize_priority
        ),

        # =========================
        # Search Query
        # 由 Recommendation Pipeline 建立
        # =========================

        search_query=None,

        # =========================
        # Raw Input
        # =========================

        raw=RawInput(
            filters=original_filters
        ),
    )

    return RecommendationRequest(

        source="filter",

        need=need,
    )