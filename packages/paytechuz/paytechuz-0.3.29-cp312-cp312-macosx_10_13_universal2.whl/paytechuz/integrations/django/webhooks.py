"""
Django webhook handlers for PayTechUZ.

Public webhook classes that provide type hints and IDE support.
These classes inherit from internal webhooks which contain the compiled business logic.
"""
import logging

from .internal_webhooks import (
    PaymeWebhook as PaymeWebhookInternal,
    ClickWebhook as ClickWebhookInternal,
    AtmosWebhook as AtmosWebhookInternal
)

logger = logging.getLogger(__name__)


class PaymeWebhook(PaymeWebhookInternal):
    """
    Base Payme webhook handler for Django.

    This class handles webhook requests from the Payme payment system.
    You can extend this class and override the event methods to customize
    the behavior.

    Example:
    ```python
    from paytechuz.integrations.django.webhooks import PaymeWebhook

    class CustomPaymeWebhook(PaymeWebhook):
        def successfully_payment(self, params, transaction):
            # Your custom logic here
            print(f"Payment successful: {transaction.transaction_id}")

            # Update your order status
            order = Order.objects.get(id=transaction.account_id)
            order.status = 'paid'
            order.save()
    ```
    """

    # Event methods that can be overridden by subclasses

    def before_check_perform_transaction(self, params, account):
        """
        Called before checking if a transaction can be performed.

        Args:
            params: Request parameters
            account: Account object
        """
        pass

    def transaction_already_exists(self, params, transaction):
        """
        Called when a transaction already exists.

        Args:
            params: Request parameters
            transaction: Transaction object
        """
        pass

    def transaction_created(self, params, transaction, account):
        """
        Called when a transaction is created.

        Args:
            params: Request parameters
            transaction: Transaction object
            account: Account object
        """
        pass

    def successfully_payment(self, params, transaction):
        """
        Called when a payment is successful.

        Args:
            params: Request parameters
            transaction: Transaction object
        """
        pass

    def check_transaction(self, params, transaction):
        """
        Called when checking a transaction.

        Args:
            params: Request parameters
            transaction: Transaction object
        """
        pass

    def cancelled_payment(self, params, transaction):
        """
        Called when a payment is cancelled.

        Args:
            params: Request parameters
            transaction: Transaction object
        """
        pass

    def get_statement(self, params, transactions):
        """
        Called when getting a statement.

        Args:
            params: Request parameters
            transactions: List of transactions
        """
        pass


class ClickWebhook(ClickWebhookInternal):
    """
    Base Click webhook handler for Django.

    This class handles webhook requests from the Click payment system.
    You can extend this class and override the event methods to customize
    the behavior.

    Example:
    ```python
    from paytechuz.integrations.django.webhooks import ClickWebhook

    class CustomClickWebhook(ClickWebhook):
        def successfully_payment(self, params, transaction):
            # Your custom logic here
            print(f"Payment successful: {transaction.transaction_id}")

            # Update your order status
            order = Order.objects.get(id=transaction.account_id)
            order.status = 'paid'
            order.save()
    ```
    """

    # Event methods that can be overridden by subclasses

    def before_check_perform_transaction(self, params, account):
        """
        Called before checking if a transaction can be performed.

        Args:
            params: Request parameters
            account: Account object
        """
        pass

    def transaction_already_exists(self, params, transaction):
        """
        Called when a transaction already exists.

        Args:
            params: Request parameters
            transaction: Transaction object
        """
        pass

    def transaction_created(self, params, transaction, account):
        """
        Called when a transaction is created.

        Args:
            params: Request parameters
            transaction: Transaction object
            account: Account object
        """
        pass

    def successfully_payment(self, params, transaction):
        """
        Called when a payment is successful.

        Args:
            params: Request parameters
            transaction: Transaction object
        """
        pass

    def cancelled_payment(self, params, transaction):
        """
        Called when a payment is cancelled.

        Args:
            params: Request parameters
            transaction: Transaction object
        """
        pass


class AtmosWebhook(AtmosWebhookInternal):
    """
    Base Atmos webhook handler for Django.

    This class handles webhook requests from the Atmos payment system.
    You can extend this class and override the event methods to customize
    the behavior.

    Example:
    ```python
    from paytechuz.integrations.django.webhooks import AtmosWebhook

    class CustomAtmosWebhook(AtmosWebhook):
        def successfully_payment(self, params, transaction):
            # Your custom logic here
            print(f"Payment successful: {transaction.transaction_id}")

            # Update your order status
            order = Order.objects.get(id=transaction.account_id)
            order.status = 'paid'
            order.save()
    ```
    """

    # Event methods that can be overridden by subclasses

    def transaction_created(self, params, transaction, account):
        """
        Called when a transaction is created.

        Args:
            params: Request parameters
            transaction: Transaction object
            account: Account object
        """
        pass

    def successfully_payment(self, params, transaction):
        """
        Called when a payment is successful.

        Args:
            params: Request parameters
            transaction: Transaction object
        """
        pass

    def cancelled_payment(self, params, transaction):
        """
        Called when a payment is cancelled.

        Args:
            params: Request parameters
            transaction: Transaction object
        """
        pass
