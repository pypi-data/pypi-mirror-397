"""Tests for the payment processing system.

These tests require proper implementation of:
1. PaymentMethod abstract base class
2. Concrete payment method classes
3. PaymentProcessor with strategy pattern
4. Proper validation for all payment types
"""

from abc import ABC

import pytest
from payment_processor import (
    BankTransferPayment,
    CreditCardPayment,
    # After refactoring, these should be importable:
    PaymentMethod,
    PaymentProcessor,
    PayPalPayment,
)


class TestPaymentMethodAbstraction:
    """Test the abstract PaymentMethod class."""

    def test_payment_method_is_abstract(self):
        """PaymentMethod should be an abstract class."""
        assert issubclass(PaymentMethod, ABC)

    def test_payment_method_has_validate(self):
        """PaymentMethod should have abstract validate method."""
        assert hasattr(PaymentMethod, "validate")

    def test_payment_method_has_process(self):
        """PaymentMethod should have abstract process method."""
        assert hasattr(PaymentMethod, "process")


class TestCreditCardPayment:
    """Test credit card payment method."""

    @pytest.fixture
    def cc_payment(self):
        return CreditCardPayment()

    def test_valid_credit_card(self, cc_payment):
        """Valid credit card should process successfully."""
        result = cc_payment.process(
            amount=100.00,
            currency="USD",
            card_number="4111111111111111",
            expiry="12/25",
            cvv="123",
        )
        assert result.success is True
        assert result.transaction_id is not None
        assert result.transaction_id.startswith("CC-")

    def test_invalid_card_number(self, cc_payment):
        """Short card number should fail validation."""
        result = cc_payment.process(
            amount=100.00,
            currency="USD",
            card_number="411",  # Too short
            expiry="12/25",
            cvv="123",
        )
        assert result.success is False
        assert "card number" in result.error_message.lower()

    def test_invalid_expiry_format(self, cc_payment):
        """Invalid expiry format should fail."""
        result = cc_payment.process(
            amount=100.00,
            currency="USD",
            card_number="4111111111111111",
            expiry="invalid",  # Bad format
            cvv="123",
        )
        assert result.success is False
        assert "expiry" in result.error_message.lower()

    def test_invalid_cvv(self, cc_payment):
        """CVV must be 3-4 digits."""
        result = cc_payment.process(
            amount=100.00,
            currency="USD",
            card_number="4111111111111111",
            expiry="12/25",
            cvv="12",  # Too short
        )
        assert result.success is False
        assert "cvv" in result.error_message.lower()


class TestPayPalPayment:
    """Test PayPal payment method."""

    @pytest.fixture
    def pp_payment(self):
        return PayPalPayment()

    def test_valid_paypal(self, pp_payment):
        """Valid PayPal email should process successfully."""
        result = pp_payment.process(
            amount=50.00,
            currency="USD",
            email="user@example.com",
        )
        assert result.success is True
        assert result.transaction_id is not None
        assert result.transaction_id.startswith("PP-")

    def test_invalid_email_format(self, pp_payment):
        """Invalid email format should fail."""
        result = pp_payment.process(
            amount=50.00,
            currency="USD",
            email="not-an-email",
        )
        assert result.success is False
        assert "email" in result.error_message.lower()


class TestBankTransferPayment:
    """Test bank transfer payment method."""

    @pytest.fixture
    def bt_payment(self):
        return BankTransferPayment()

    def test_valid_bank_transfer(self, bt_payment):
        """Valid bank details should process successfully."""
        result = bt_payment.process(
            amount=1000.00,
            currency="USD",
            account_number="123456789",
            routing_number="021000021",
        )
        assert result.success is True
        assert result.transaction_id is not None
        assert result.transaction_id.startswith("BT-")

    def test_missing_routing_number(self, bt_payment):
        """Missing routing number should fail."""
        result = bt_payment.process(
            amount=1000.00,
            currency="USD",
            account_number="123456789",
            # Missing routing_number
        )
        assert result.success is False
        assert "routing" in result.error_message.lower()


class TestPaymentProcessor:
    """Test the PaymentProcessor class."""

    @pytest.fixture
    def processor(self):
        """Create processor with all payment methods registered."""
        proc = PaymentProcessor()
        proc.register_method("credit_card", CreditCardPayment())
        proc.register_method("paypal", PayPalPayment())
        proc.register_method("bank_transfer", BankTransferPayment())
        return proc

    def test_process_credit_card(self, processor):
        """Processor should route credit card payments."""
        result = processor.process(
            payment_type="credit_card",
            amount=100.00,
            currency="USD",
            card_number="4111111111111111",
            expiry="12/25",
            cvv="123",
        )
        assert result.success is True

    def test_unknown_payment_type(self, processor):
        """Unknown payment type should fail gracefully."""
        result = processor.process(
            payment_type="bitcoin",
            amount=100.00,
            currency="BTC",
        )
        assert result.success is False
        assert "unknown" in result.error_message.lower()

    def test_negative_amount_validation(self, processor):
        """Negative amount should fail for all payment types."""
        result = processor.process(
            payment_type="credit_card",
            amount=-100.00,  # Invalid!
            currency="USD",
            card_number="4111111111111111",
            expiry="12/25",
            cvv="123",
        )
        assert result.success is False
        assert "amount" in result.error_message.lower()
