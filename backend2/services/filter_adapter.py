from models.schemas import (
    Budget,
    Persona,
    Preferences,
    RawInput,
    RecommendationRequest,
    UserNeed,
)
from services.filter_service import build_search_keyword
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


def _safe_filters(filters):
    filters = filters or {}

    return {
        "device_type": filters.get("device_type") or "",
        "usage": filters.get("usage") or "",
        "style": filters.get("style") or "",
        "battery": filters.get("battery") or "",
        "features": _as_list(
            filters.get("features")
        ),
        "os": filters.get("os") or "",
        "core_factors": _as_list(
            filters.get("core_factors")
        ),
        "min_price": filters.get("min_price") or 0,
        "max_price": filters.get("max_price") or 999999
    }


def adapt_filter_request(filters):
    original_filters = filters or {}
    safe_filters = _safe_filters(
        original_filters
    )

    need = UserNeed(
        # 新增：把前端「我的」頁面 + Filter Q9 送來的個人資訊接進 Persona
        # 這四個都是選填，使用者沒填就是空字串，_none_if_empty 會轉成 None
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
        budget=Budget(
            min=_none_if_empty(
                original_filters.get("min_price")
            ),
            max=_none_if_empty(
                original_filters.get("max_price")
            )
        ),
        device_type=normalize_device_type(
            original_filters.get("device_type")
        ),
        usage=normalize_list(
            original_filters.get("usage"),
            normalize_usage
        ),
        features=normalize_list(
            original_filters.get("features"),
            normalize_feature
        ),
        preferences=Preferences(
            os=normalize_os(
                original_filters.get("os")
            ),
            style=normalize_style(
                original_filters.get("style")
            ),
            battery=normalize_battery(
                original_filters.get("battery")
            )
        ),
        priorities=normalize_list(
            original_filters.get("core_factors"),
            normalize_priority
        ),
        search_query=_none_if_empty(
            build_search_keyword(safe_filters)
        ),
        raw=RawInput(
            filters=original_filters
        )
    )

    return RecommendationRequest(
        source="filter",
        need=need
    )
