"""x402 payment middleware with optional admin bypass."""
import logging
from typing import Awaitable, Callable

from fastapi import FastAPI, Request, Response

from config import settings
from middleware.admin import is_admin_request, log_admin_access

logger = logging.getLogger(__name__)

PROTECTED_ROUTE = "POST /api/meme/generate"


def _build_x402_middleware():
    from x402.http import FacilitatorConfig, HTTPFacilitatorClient, PaymentOption
    from x402.http.middleware.fastapi import payment_middleware
    from x402.http.types import RouteConfig
    from x402.mechanisms.evm.exact import ExactEvmServerScheme
    from x402.server import x402ResourceServer

    facilitator = HTTPFacilitatorClient(
        FacilitatorConfig(url=settings.x402_facilitator_url)
    )
    server = x402ResourceServer(facilitator)
    server.register(settings.x402_evm_network, ExactEvmServerScheme())

    payment_options = [
        PaymentOption(
            scheme="exact",
            pay_to=settings.x402_evm_pay_to,
            price=settings.x402_price,
            network=settings.x402_evm_network,
        )
    ]

    if settings.x402_svm_pay_to:
        from x402.mechanisms.svm.exact import ExactSvmServerScheme

        server.register(settings.x402_svm_network, ExactSvmServerScheme())
        payment_options.append(
            PaymentOption(
                scheme="exact",
                pay_to=settings.x402_svm_pay_to,
                price=settings.x402_price,
                network=settings.x402_svm_network,
            )
        )

    routes = {
        PROTECTED_ROUTE: RouteConfig(
            accepts=payment_options,
            mime_type="multipart/form-data",
            description=(
                "Generate top 3 AI meme text options from a topic and template image."
            ),
        )
    }

    return payment_middleware(routes, server)


def setup_x402_middleware(app: FastAPI) -> None:
    """Register x402 payment middleware when enabled in settings."""
    if not settings.x402_enabled:
        logger.info("x402 payments disabled (X402_ENABLED=false)")
        return

    if not settings.x402_evm_pay_to:
        raise ValueError(
            "X402_ENABLED is true but X402_EVM_PAY_TO is not configured"
        )

    x402_middleware = _build_x402_middleware()
    logger.info(
        "x402 enabled: %s at %s on %s (facilitator: %s)",
        settings.x402_price,
        PROTECTED_ROUTE,
        settings.x402_evm_network,
        settings.x402_facilitator_url,
    )

    @app.middleware("http")
    async def x402_with_admin_bypass(
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        if (
            request.method == "POST"
            and request.url.path == "/api/meme/generate"
            and is_admin_request(request)
        ):
            log_admin_access(request)
            request.state.payment_bypass = "admin"
            return await call_next(request)

        return await x402_middleware(request, call_next)
