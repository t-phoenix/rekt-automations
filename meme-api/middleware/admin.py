"""Admin authentication helpers for bypassing x402 payment."""
import hmac
import logging
from typing import Optional

from fastapi import Request

from config import settings

logger = logging.getLogger(__name__)

ADMIN_KEY_HEADER = "x-admin-key"
AUTHORIZATION_HEADER = "authorization"


def _extract_bearer_token(authorization: Optional[str]) -> Optional[str]:
    if not authorization:
        return None
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        return None
    return token.strip()


def is_admin_request(request: Request) -> bool:
    """Return True when the request presents a valid admin credential."""
    if not settings.admin_api_key:
        return False

    candidates = [
        request.headers.get(ADMIN_KEY_HEADER),
        _extract_bearer_token(request.headers.get(AUTHORIZATION_HEADER)),
    ]

    for candidate in candidates:
        if candidate and hmac.compare_digest(candidate, settings.admin_api_key):
            return True

    return False


def log_admin_access(request: Request) -> None:
    """Log admin bypass usage without leaking secrets."""
    client = request.client.host if request.client else "unknown"
    logger.info(
        "Admin bypass used for %s %s from %s",
        request.method,
        request.url.path,
        client,
    )
