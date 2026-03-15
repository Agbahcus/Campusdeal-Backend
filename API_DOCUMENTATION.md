# CampusDeal Backend API (Production-ready)

This document summarizes the public HTTP surface that the mobile app (or any frontend) can consume from the CampusDeal backend. Most endpoints sit under `/api/...` and require authentication using JWT access tokens issued by the `accounts` app.

## Authentication

- **Register** `POST /api/accounts/auth/register/`  
  Body: `{ "username": "+234801...", "email": "...", "password": "...", "phone_number": "+234801..." }`  
  Response: 201 with `{ "detail": "Verification code sent" }`.
- **Verify phone** `POST /api/accounts/auth/verify-phone/`  
  Body: `{ "username": "...", "code": "123456" }`  
  Response: 200 with tokens.
- **Login** `POST /api/accounts/auth/login/`  
  Body: `{ "username": "...", "password": "..." }`  
  Response: `{ "access": "...", "refresh": "...", "user": { ... } }`.
- **Refresh token** `POST /api/accounts/auth/refresh-token/` (DRF SimpleJWT)  
- **Logout**, password reset, profile lookup/update: see `accounts.urls`.

> Every subsequent authenticated request must send `Authorization: Bearer <access_token>` header.

## Marketplace Core APIs (`/api/marketplace/`)

### Catalogs & Listings

- `GET /categories/`  
  Lists active categories.
- `GET /listings/`  
  Paginated browse of items (supports filtering via query params).
- `POST /listings/create/`  
  Create a new listing (requires authenticated seller). Body must include `title`, `description`, `category`, `price`, `location`, etc.
- `GET /listings/<id>/`, `/listings/<id>/update/`, `/listings/<id>/delete/`  
  Read/update/delete an individual listing.
- `GET /my-listings/`, `GET /users/<user_id>/listings/`

### Orders & Payments

- `POST /orders/initiate/`  
  Create a new order (escrow-style) with `item_id`, `delivery_method`, `payment_method`, `amount`.
- `GET /orders/`, `GET /orders/<order_id>/`, `/orders/<order_id>/checkout/`, `/orders/<order_id>/update-status/`, `/orders/<order_id>/confirm-delivery/`, `/orders/<order_id>/cancel/`  
- `GET /payments/verify/`  
  Hit this endpoint after Paystack redirects back; body includes `reference`.
- `POST /payments/webhook/`  
  Internal endpoint for Paystack webhook events. Validate `X-Paystack-Signature`.

### Reviews

- `POST /reviews/` – leave a review tied to an order.
- `GET /users/<user_id>/reviews/` – fetch reviews for a seller.

### Refunds

- `POST /orders/<order_id>/request-refund/`  
- `/refunds/<refund_id>/approve/` /reject, `/refunds/pending/`.

## Wallet & Withdrawal APIs (`/api/marketplace/wallet/`)

### Wallet balance and transactions

- `GET /wallet/balance/` – current `wallet_balance`.
- `GET /wallet/transactions/` – paginated transactions.
- `POST /wallet/add-funds/` – initialize top-up (handled via Paystack).
- `POST /wallet/verify-deposit/` – confirm deposit reference.
- `GET /wallet/banks/` – list Paystack-supported banks.

### Bank accounts

- `POST /wallet/add-bank-account/` – verify and persist a recipient account. Body: `account_number`, `bank_code`, `bank_name`.
- `POST /wallet/verify-account/` – purely verifies an account number + bank code via Paystack.
- `GET /wallet/bank-accounts/`, `/bank-accounts/<id>/set-primary/`, `/bank-accounts/<id>/` (DELETE).

### Withdrawals

- `POST /wallet/withdraw/` – the main endpoint hardened by our recent changes. Request body:
  ```json
  {
    "amount": "1500.00",
    "bank_account_id": 5                // optional; defaults to primary verified account
  }
  ```
  Responses:
  * 201 on success with payload: withdrawal metadata, balances before/after, reference.
  * 400 for: invalid amounts (non-numeric/zero/negative), below minimum, above daily limit, insufficient balance, missing bank account, or Paystack transfer failure.
  * 500 only when the atomic transfer logic raises.

- `GET /wallet/withdrawals/` – list of recent withdrawal requests.
- `GET /wallet/withdrawal-fees/` – returns `withdrawal_fee`, `minimum_withdrawal`, `maximum_per_day`.

## Admin & Platform Monitoring

- `GET /admin/financials/` – platform revenue/liability snapshot.
- `POST /admin/withdraw-profit/` – admin-only endpoint to siphon platform balance.
- All admin endpoints expect elevated permissions; use staff user tokens.

## Hostels & Supplementary Features

- Hostels: `/hostels/`, `/hostels/<id>/`, `/hostels/create/`, `/hostels/my-listings/`, `/hostels/<id>/verify/`, etc.
- `/setup/` – one-time setup hook (delete after initialization).

## Testing & Readiness Notes

- The withdrawal stress tests live in `test_withdrawal_stress.py`; run `python manage.py test test_withdrawal_stress.WithdrawalStressTest`.
- The full Django test suite is `python manage.py test`.
- Keep `.env` out of version control; use `.env.example` as a template.

## Cleanup Suggestions (files to revisit before finalizing)

- Delete temporary/debug scripts such as `debug_withdraw.py`, `debug_withdraw_test.py` once you no longer need them.  
- Remove `__pycache__` folders and compiled `.pyc` files before packaging or commit (these are regeneration artifacts).  
- Verify whether `db.sqlite3` is still needed locally or should be replaced with migrations for production databases.  
- Any other bespoke scripts (deployment guides, test harnesses) can be archived elsewhere once their instructions are captured in documentation.

With this documentation in hand, a mobile engineer can authenticate, load listings, manage wallets, initiate withdrawals, and respond to Paystack callbacks. Let me know if you want this file tailored to swagger/openapi or exported elsewhere.
