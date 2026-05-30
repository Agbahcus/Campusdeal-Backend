# CampusDeal API Documentation

This document is for mobile app developers and any client consuming the CampusDeal backend.

## Base URLs

- Production: `https://campusdeal-backend.onrender.com/api`
- Marketplace: `https://campusdeal-backend.onrender.com/api/marketplace`
- Chats: `https://campusdeal-backend.onrender.com/api/chats`

## Authentication

Most endpoints require a JWT access token:

```http
Authorization: Bearer <access_token>
Content-Type: application/json
```

### Token flow

1. Register a user.
2. Verify the phone number with the OTP code.
3. Save the returned `access_token` and `refresh_token`.
4. Use `access_token` for authenticated requests.
5. Refresh the access token when it expires.

## Standard data rules

- Phone numbers should be submitted in Nigerian international format, for example `+2348012345678`.
- The backend stores phone numbers using the normalized phone format.
- Common allowed locations:
  - `ilorin`
  - `malete`
  - `offa`
  - `lagos`
  - `abuja`
  - `ibadan`
  - `kano`
  - `port-harcourt`
- Common order payment methods:
  - `wallet`
  - `paystack`
- Common delivery methods:
  - `campusdeal`
  - `seller`
  - `pickup`

## Error format

Most failures return JSON like:

```json
{
  "error": "Human readable message"
}
```

Validation failures may also return field-specific errors:

```json
{
  "phone_number": ["This phone number is already registered."]
}
```

## Status codes

- `200` OK
- `201` Created
- `400` Bad Request
- `401` Unauthorized
- `403` Forbidden
- `404` Not Found
- `429` Too Many Requests
- `500` Server Error

## Pagination

Paginated endpoints use Django REST Framework pagination:

```json
{
  "count": 123,
  "next": "https://...",
  "previous": null,
  "results": []
}
```

Some list endpoints also accept `page` and `page_size`.

---

## Health

### `GET /health/`

Returns application and database health.

### `GET /ready/`

Readiness check for deployment platforms and load balancers.

Example response:

```json
{
  "status": "healthy",
  "checks": {
    "database": "connected",
    "configuration": "ok"
  }
}
```

---

## Auth API

### `POST /api/auth/register/`

Register a new account and send an OTP.

Request body:

```json
{
  "full_name": "Ada Lovelace",
  "email": "ada@example.com",
  "phone_number": "+2348012345678",
  "password": "StrongPass123",
  "primary_location": "ilorin",
  "user_type": "student"
}
```

Response:

```json
{
  "user_id": 1,
  "message": "Verification code sent to your phone",
  "phone_masked": "***5678",
  "verification_code": null
}
```

### `POST /api/auth/verify-phone/`

Verify the OTP and receive JWT tokens.

Request body:

```json
{
  "user_id": 1,
  "code": "123456"
}
```

### `POST /api/auth/resend-code/`

Request a new OTP.

Request body:

```json
{
  "user_id": 1
}
```

### `POST /api/auth/login/`

Login with phone number and password.

Request body:

```json
{
  "phone_number": "+2348012345678",
  "password": "StrongPass123"
}
```

### `POST /api/auth/logout/`

Blacklist the refresh token.

Request body:

```json
{
  "refresh_token": "<refresh_token>"
}
```

### `POST /api/auth/request-password-reset/`

Request an OTP for password reset.

Request body:

```json
{
  "phone_number": "+2348012345678"
}
```

### `POST /api/auth/confirm-password-reset/`

Reset password with OTP.

Request body:

```json
{
  "phone_number": "+2348012345678",
  "code": "123456",
  "new_password": "NewStrongPass123"
}
```

### `POST /api/auth/refresh-token/`

Refresh the JWT access token using SimpleJWT.

Request body:

```json
{
  "refresh": "<refresh_token>"
}
```

### `GET /api/users/me/`

Get the authenticated user profile.

### `PATCH /api/users/me/`

Update allowed profile fields such as `university`, `bio`, and `profile_picture`.

### `GET /api/users/{user_id}/profile/`

Get a public profile for another user.

---

## Marketplace API

### Categories

#### `GET /api/marketplace/categories/`

List categories.

#### `POST /api/marketplace/categories/create/`

Create a category. Admin only.

### Listings

#### `GET /api/marketplace/listings/`

Browse listings.

Common query params:

- `search`
- `category`
- `location`
- `min_price`
- `max_price`
- `page`

#### `POST /api/marketplace/listings/create/`

Create a listing.

Typical fields:

- `title`
- `description`
- `category`
- `condition`
- `price`
- `location`
- `allow_campusdeal_delivery`
- `allow_seller_delivery`
- `allow_pickup`
- optional images

#### `GET /api/marketplace/listings/{listing_id}/`

Get listing details.

#### `PUT/PATCH /api/marketplace/listings/{listing_id}/update/`

Update a listing.

#### `DELETE /api/marketplace/listings/{listing_id}/delete/`

Delete or remove a listing.

#### `GET /api/marketplace/my-listings/`

Get the authenticated user’s listings.

#### `GET /api/marketplace/users/{user_id}/listings/`

Get listings for a public user profile.

---

## Order Flow

### Recommended mobile flow

1. Seller initiates the order.
2. Buyer checks out with wallet or Paystack.
3. Payment is verified.
4. Seller updates fulfillment status.
5. Buyer confirms delivery.
6. Both parties may leave a review.

### `POST /api/marketplace/orders/initiate/`

Seller creates an order.

Request body:

```json
{
  "item_id": 12,
  "buyer_id": 44,
  "delivery_method": "pickup"
}
```

### `GET /api/marketplace/orders/`

List orders for the current user.

Query params:

- `role=buyer|seller`
- `status=payment_pending|paid|delivered|completed|cancelled`

### `GET /api/marketplace/orders/{order_id}/`

Get a single order.

### `POST /api/marketplace/orders/{order_id}/checkout/`

Buyer chooses payment method.

Request body:

```json
{
  "payment_method": "paystack",
  "delivery_address": "123 Main Street",
  "delivery_phone": "+2348012345678"
}
```

### `POST /api/marketplace/payments/verify/`

Verify a Paystack payment reference.

Request body:

```json
{
  "reference": "CD123_1234567890"
}
```

### `POST /api/marketplace/payments/webhook/`

Paystack webhook endpoint. This is server-to-server and should not be called by the mobile app.

### `PATCH /api/marketplace/orders/{order_id}/update-status/`

Seller updates the order status.

Request body:

```json
{
  "status": "seller_preparing",
  "notes": "Packing item"
}
```

Allowed status values:

- `seller_preparing`
- `with_courier`
- `delivered`
- `cancelled`

### `POST /api/marketplace/orders/{order_id}/confirm-delivery/`

Buyer confirms delivery and releases funds.

### `POST /api/marketplace/orders/{order_id}/cancel/`

Cancel an order.

### `GET /api/marketplace/orders/{order_id}/status-history/`

Get order status history.

### `GET /api/marketplace/orders/{order_id}/review/`

Get review attached to an order.

---

## Wallet API

### `GET /api/marketplace/wallet/balance/`

Get current wallet balance.

### `GET /api/marketplace/wallet/transactions/`

Get wallet transaction history.

Query params:

- `transaction_type=credit|debit`
- `source=sale|refund|deposit|purchase|withdrawal`
- `page`
- `page_size`

### `POST /api/marketplace/wallet/add-funds/`

Initialize a wallet deposit with Paystack.

Request body:

```json
{
  "amount": "5000.00"
}
```

### `POST /api/marketplace/wallet/verify-deposit/`

Verify wallet deposit after Paystack payment.

Request body:

```json
{
  "reference": "WALLET_1_1717000000"
}
```

### `GET /api/marketplace/wallet/banks/`

Get bank list for withdrawal.

---

## Withdrawals

### `POST /api/marketplace/wallet/verify-account/`

Verify bank account name before saving.

### `POST /api/marketplace/wallet/add-bank-account/`

Add a bank account for withdrawals.

### `GET /api/marketplace/wallet/bank-accounts/`

List saved bank accounts.

### `POST /api/marketplace/wallet/bank-accounts/{account_id}/set-primary/`

Set a primary withdrawal account.

### `DELETE /api/marketplace/wallet/bank-accounts/{account_id}/`

Delete a saved bank account.

### `POST /api/marketplace/wallet/withdraw/`

Withdraw wallet funds.

### `GET /api/marketplace/wallet/withdrawals/`

Get withdrawal history.

### `GET /api/marketplace/wallet/withdrawal-fees/`

Get withdrawal fee rules.

---

## Reviews

### `POST /api/marketplace/reviews/`

Leave a review after a completed order.

Request body:

```json
{
  "order_id": "CD1A2B3C4D5E6F7G",
  "rating": 5,
  "comment": "Great seller!"
}
```

### `GET /api/marketplace/users/{user_id}/reviews/`

Get reviews for a user.

---

## Refunds

### `POST /api/marketplace/orders/{order_id}/request-refund/`

Buyer requests a refund.

Request body:

```json
{
  "reason": "not_as_described",
  "detailed_explanation": "The item condition was different from the listing."
}
```

Accepted refund reasons:

- `not_as_described`
- `damaged`
- `wrong_item`
- `seller_unresponsive`
- `other`

### `GET /api/marketplace/orders/{order_id}/refund-request/`

Get the refund request for an order.

### `POST /api/marketplace/refunds/{refund_id}/approve/`

Admin approves a refund.

### `POST /api/marketplace/refunds/{refund_id}/reject/`

Admin rejects a refund.

### `GET /api/marketplace/refunds/pending/`

List pending refunds for admins.

---

## Hostels

### Public

#### `GET /api/marketplace/hostels/`

Browse hostels.

#### `GET /api/marketplace/hostels/{hostel_id}/`

Get hostel details.

### Landlord

#### `POST /api/marketplace/hostels/create/`

Create a hostel listing.

#### `GET /api/marketplace/hostels/my-listings/`

List current landlord’s hostel listings.

#### `PUT/PATCH /api/marketplace/hostels/{hostel_id}/update/`

Update a hostel listing.

#### `DELETE /api/marketplace/hostels/{hostel_id}/delete/`

Delete a hostel listing.

### Admin

#### `GET /api/marketplace/hostels/admin/pending/`

List pending hostel listings.

#### `GET /api/marketplace/hostels/admin/all/`

List all hostel listings.

#### `POST /api/marketplace/hostels/{hostel_id}/verify/`

Verify a hostel listing.

#### `GET /api/marketplace/hostels/admin/stats/`

Get hostel stats.

---

## Chat API

### `GET /api/chats/`

List the authenticated user’s chats.

### `POST /api/chats/create/`

Create or open a chat.

Request body:

```json
{
  "other_user_id": 45,
  "item_id": 12,
  "initial_message": "Is this still available?"
}
```

### `GET /api/chats/{chat_id}/`

Get chat details.

### `GET /api/chats/{chat_id}/messages/`

Get chat messages.

### `POST /api/chats/{chat_id}/messages/send/`

Send a message.

Request body:

```json
{
  "text": "Hello, is this available?"
}
```

### `PATCH /api/chats/{chat_id}/mark-read/`

Mark unread messages as read.

### `GET /api/chats/unread-count/`

Get unread message count.

### Moderation

#### `GET /api/chats/moderation-logs/`

Admin-only moderation logs.

#### `POST /api/chats/test-moderator/`

Debug-only content moderation test endpoint.

---

## Notes for mobile app developers

- Store the access token securely and refresh it when needed.
- Treat `401` responses as a signal to refresh or re-authenticate.
- Handle validation errors by showing field-specific messages.
- Use `multipart/form-data` for profile or listing image uploads.
- Do not call webhook endpoints from the mobile app.
- Build retries around network failures for payment and OTP actions.

## Production warning

This API is functional and usable, but consumers should still expect:

- OTP delivery failures when SMS provider settings are incorrect
- Payment verification delays from external providers
- Permission errors for admin-only endpoints
- `400` validation responses when frontend values do not match backend choices

If you want, I can also generate an **OpenAPI/Swagger spec** from this same backend next.
