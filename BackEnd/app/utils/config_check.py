from .errors import APIError


PLACEHOLDER_MARKERS = (
    "your-project-id",
    "your-anon-public-key",
    "your-service-role-key",
)


def is_placeholder(value):
    return any(marker in (value or "") for marker in PLACEHOLDER_MARKERS)


def require_supabase_config(supabase_url, anon_key):
    if not supabase_url or not anon_key or is_placeholder(supabase_url) or is_placeholder(anon_key):
        raise APIError(
            "SERVER_NOT_CONFIGURED",
            "Supabase is not configured. Please set real SUPABASE_URL and SUPABASE_ANON_KEY in BackEnd/.env, then restart Flask.",
            500,
        )
