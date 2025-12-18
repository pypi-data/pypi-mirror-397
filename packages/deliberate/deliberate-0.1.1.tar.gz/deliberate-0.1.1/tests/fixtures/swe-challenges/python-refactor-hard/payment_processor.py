"""Payment processing module - NEEDS REFACTORING.

This module processes payments but has several design issues:
1. Single function with too many responsibilities
2. Hard to extend with new payment types
3. Poor separation of concerns
4. Difficult to test individual components

TODO: Refactor using Strategy pattern with proper OOP design.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass
class PaymentResult:
    """Result of a payment operation."""

    success: bool
    transaction_id: str | None
    error_message: str | None
    processed_at: datetime


def process_payment(
    payment_type: str,
    amount: float,
    currency: str,
    **details: Any,
) -> PaymentResult:
    """Process a payment - THIS IS A MESS!

    This function handles ALL payment types with conditionals.
    It mixes validation, processing, and error handling.

    Args:
        payment_type: One of 'credit_card', 'paypal', 'bank_transfer'
        amount: Payment amount
        currency: Three-letter currency code
        **details: Payment-specific details

    Returns:
        PaymentResult with success/failure status
    """
    # BUG: No amount validation!
    # BUG: Currency validation is incomplete

    if payment_type == "credit_card":
        # Credit card processing
        card_number = details.get("card_number", "")
        expiry = details.get("expiry", "")
        cvv = details.get("cvv", "")

        # Validation mixed with processing
        if not card_number or len(card_number) < 13:
            return PaymentResult(
                success=False,
                transaction_id=None,
                error_message="Invalid card number",
                processed_at=datetime.now(),
            )

        # BUG: Expiry validation is broken - doesn't check format
        if not expiry:
            return PaymentResult(
                success=False,
                transaction_id=None,
                error_message="Expiry date required",
                processed_at=datetime.now(),
            )

        # BUG: CVV should be 3-4 digits
        if not cvv:
            return PaymentResult(
                success=False,
                transaction_id=None,
                error_message="CVV required",
                processed_at=datetime.now(),
            )

        # Simulate processing
        txn_id = f"CC-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        return PaymentResult(
            success=True,
            transaction_id=txn_id,
            error_message=None,
            processed_at=datetime.now(),
        )

    elif payment_type == "paypal":
        # PayPal processing
        email = details.get("email", "")

        # BUG: No email format validation
        if not email:
            return PaymentResult(
                success=False,
                transaction_id=None,
                error_message="PayPal email required",
                processed_at=datetime.now(),
            )

        txn_id = f"PP-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        return PaymentResult(
            success=True,
            transaction_id=txn_id,
            error_message=None,
            processed_at=datetime.now(),
        )

    elif payment_type == "bank_transfer":
        # Bank transfer processing
        account_number = details.get("account_number", "")
        details.get("routing_number", "")

        # BUG: Incomplete validation
        if not account_number:
            return PaymentResult(
                success=False,
                transaction_id=None,
                error_message="Account number required",
                processed_at=datetime.now(),
            )

        # BUG: Missing routing number validation

        txn_id = f"BT-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        return PaymentResult(
            success=True,
            transaction_id=txn_id,
            error_message=None,
            processed_at=datetime.now(),
        )

    else:
        # Unknown payment type
        return PaymentResult(
            success=False,
            transaction_id=None,
            error_message=f"Unknown payment type: {payment_type}",
            processed_at=datetime.now(),
        )


# TODO: Add these classes as part of refactoring:
#
# class PaymentMethod(ABC):
#     """Abstract base class for payment methods."""
#     @abstractmethod
#     def validate(self, amount: float, currency: str, **details) -> None: ...
#     @abstractmethod
#     def process(self, amount: float, currency: str, **details) -> PaymentResult: ...
#
# class CreditCardPayment(PaymentMethod): ...
# class PayPalPayment(PaymentMethod): ...
# class BankTransferPayment(PaymentMethod): ...
#
# class PaymentProcessor:
#     """Processes payments using registered payment methods."""
#     def register_method(self, name: str, method: PaymentMethod) -> None: ...
#     def process(self, payment_type: str, ...) -> PaymentResult: ...
