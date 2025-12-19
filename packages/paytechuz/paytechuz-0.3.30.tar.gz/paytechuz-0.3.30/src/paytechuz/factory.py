from paytechuz.core.base import BasePaymentGateway
from paytechuz.gateways.payme.client import PaymeGateway
from paytechuz.gateways.click.client import ClickGateway
from paytechuz.gateways.atmos.client import AtmosGateway
from paytechuz.core.constants import PaymentGateway

def create_gateway(gateway_type: str, **kwargs) -> BasePaymentGateway:
    """
    Create a payment gateway instance.

    Args:
        gateway_type: Type of gateway ('payme', 'click', or 'atmos')
        **kwargs: Gateway-specific configuration

    Returns:
        Payment gateway instance

    Raises:
        ValueError: If the gateway type is not supported
        ImportError: If the required gateway module is not available
        UnknownPartnerError: If the license check fails
    """
    # license_api_key is passed in kwargs and validated internally by the gateway

    if gateway_type.lower() == PaymentGateway.PAYME.value:
        return PaymeGateway(**kwargs)
    if gateway_type.lower() == PaymentGateway.CLICK.value:
        return ClickGateway(**kwargs)
    if gateway_type.lower() == PaymentGateway.ATMOS.value:
        return AtmosGateway(**kwargs)

    raise ValueError(f"Unsupported gateway type: {gateway_type}")
