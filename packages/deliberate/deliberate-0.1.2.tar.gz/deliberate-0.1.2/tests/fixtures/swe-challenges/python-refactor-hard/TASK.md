# Task: Refactor Payment Processing System

## Objective
Refactor the monolithic `payment_processor.py` into a proper OOP design with strategy pattern for different payment methods.

## Current Problems
1. All payment logic is in a single function with many conditionals
2. No separation of concerns - validation, processing, and logging are mixed
3. Adding new payment types requires modifying the main function
4. Poor testability - functions are tightly coupled

## Requirements
1. Create an abstract `PaymentMethod` base class
2. Implement concrete classes: `CreditCardPayment`, `PayPalPayment`, `BankTransferPayment`
3. Each payment method should:
   - Validate its specific input requirements
   - Process the payment with proper error handling
   - Return a standardized `PaymentResult`
4. Create a `PaymentProcessor` class that uses strategy pattern
5. All 12 tests must pass

## Success Criteria
- All tests pass: `pytest test_payments.py -v`
- Code follows SOLID principles
- New payment types can be added without modifying existing code

## Constraints
- Maintain backwards compatibility with existing function signatures where noted
- Use Python 3.10+ features (type hints, match statements allowed)
