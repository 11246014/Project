#chat_parser.py
from models.schemas import (
    Budget,
    Persona,
    Preferences,
    RawInput,
    RecommendationRequest,
    UserNeed,
)
from services.keyword_service import extract_keyword
from services.vocabulary_normalizer import (
    normalize_age_group,
    normalize_battery,
    normalize_device_type,
    normalize_feature,
    normalize_list,
    normalize_occupation,
    normalize_os,
    normalize_style,
    normalize_usage,
)


def _none_if_empty(value):
    if value in ("", [], {}, 0):
        return None

    return value


def parse_chat_message(message):

    keyword_result = extract_keyword(message)

    budget = Budget(
        min=_none_if_empty(
            keyword_result.get("budget_min")
        ),
        max=_none_if_empty(
            keyword_result.get("budget_max")
        )
    )

    need = UserNeed(

        persona=Persona(
            age_range=normalize_age_group(
                keyword_result.get("age_group")
            ),
            occupation=normalize_occupation(
                keyword_result.get("occupation")
            )
        ),

        budget=budget,

        device_type=normalize_device_type(
            keyword_result.get("product_type")
            or keyword_result.get("device_type")
        ),

        usage=normalize_list(
            keyword_result.get("usage"),
            normalize_usage
        ),

        features=normalize_list(
            keyword_result.get("features"),
            normalize_feature
        ),

        preferences=Preferences(

            os=normalize_os(
                keyword_result.get("os")
            ),

            brand=_none_if_empty(
                keyword_result.get("brand")
            ),

            style=normalize_style(
                keyword_result.get("style")
            ),

            battery=normalize_battery(
                keyword_result.get("battery")
            )
        ),

        search_query=_none_if_empty(
            keyword_result.get("keyword")
        ),

        raw=RawInput(
            text=message
        )
    )

    return RecommendationRequest(
        source="chat",
        need=need
    )