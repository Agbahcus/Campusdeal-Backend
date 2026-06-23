# CampusDeal API Documentation

This document is the complete reference for mobile app developers and any client consuming the CampusDeal backend API.

**Backend repository:** https://github.com/Agbahcus/Campusdeal-Backend  
**Live API:** https://campusdeal-backend.onrender.com  
**Health check:** https://campusdeal-backend.onrender.com/health/

---

## Base URLs

| Service | URL |
|---|---|
| Auth & Users | `https://campusdeal-backend.onrender.com/api` |
| Marketplace | `https://campusdeal-backend.onrender.com/api/marketplace` |
| Chats | `https://campusdeal-backend.onrender.com/api/chats` |

---

## Authentication

Most endpoints require a JWT Bearer token in the request header:

```http
Authorization: Bearer <access_token>
Content-Type: application/json
```

### Token lifecycle

1. Register → receive `user_id`
2. Verify phone OTP → receive `access_token` + `refresh_token`
3. Store both tokens securely on device
4. Attach `access_token` to every authenticated request
5. On `401` response → call refresh endpoint to get a new `access_token`
6. If refresh fails → clear tokens and redirect to login

### Token expiry

- `access_token` expires after **60 minutes**
- `refresh_token` expires after **7 days**
- Refresh tokens are rotated on every use — always save the new one

---

## Standard Rules

### Phone numbers
Always submit in Nigerian international format: `+2348012345678`  
Local format `08012345678` is auto-converted by the backend.

### Locations (allowed values)
```
ilorin | malete | offa | lagos | abuja | ibadan | kano | port-harcourt
```

### Delivery methods
```
pickup | seller | campusdeal
```
- `pickup` — buyer collects from seller directly (free)
- `seller` — seller delivers themselves (free)
- `campusdeal` — CampusDeal courier (+₦500 delivery fee)

### Payment methods
```
wallet | paystack
```

### Item conditions
```
new | fairly_used | used
```

### User types
```
student | landlord
```

### Order statuses (complete list)
```
payment_pending → paid → seller_preparing → with_courier → delivered → completed
                                                                      ↘ cancelled
                                                                      ↘ refund_requested → refunded
```

| Status | Meaning |
|---|---|
| `payment_pending` | Order created, waiting for buyer to pay |
| `paid` | Payment received and held in escrow |
| `seller_preparing` | Seller is packing/preparing the item |
| `with_courier` | Item handed to courier |
| `delivered` | Item delivered to buyer |
| `completed` | Buyer confirmed receipt — funds released to seller |
| `cancelled` | Order cancelled by buyer or seller |
| `refund_requested` | Buyer has raised a refund request |
| `refunded` | Refund processed back to buyer |

---

## Error Format

```json
{ "error": "Human readable message" }
```

Validation errors return field-specific messages:

```json
{ "phone_number": ["This phone number is already registered."] }
```

---

## HTTP Status Codes

| Code | Meaning |
|---|---|
| `200` | OK |
| `201` | Created |
| `400` | Bad Request / Validation Error |
| `401` | Unauthorized — token missing or expired |
| `403` | Forbidden — not allowed to perform this action |
| `404` | Not Found |
| `429` | Rate Limited — too many requests |
| `500` | Server Error |

---

## Pagination

All list endpoints that are paginated return:

```json
{
  "count": 123,
  "next": "https://campusdeal-backend.onrender.com/api/marketplace/listings/?page=2",
  "previous": null,
  "results": []
}
```

Use `?page=2&page_size=20` to navigate pages.

---

## Health

### `GET /health/`
Returns app and database health. Used by Render for uptime monitoring.

### `GET /ready/`
Readiness check for load balancers.

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
Register a new account. Sends an OTP to the phone number via SMS.

> Rate limited: 5 requests per hour per IP.

**Password requirements:** minimum 8 characters, must include uppercase, lowercase, and a number.

Request:
```json
{
  "full_name": "Ada Lovelace",
  "email": "ada@example.com",
  "phone_number": "+2348012345678",
  "password": "StrongPass1",
  "primary_location": "ilorin",
  "user_type": "student"
}
```

Response `201`:
```json
{
  "user_id": 1,
  "message": "Verification code sent to your phone",
  "phone_masked": "***5678",
  "verification_code": null
}
```

> Note: `verification_code` is only returned in DEBUG mode for testing. It is `null` in production.

---

### `POST /api/auth/verify-phone/`
Verify the OTP and receive JWT tokens. OTP expires after 10 minutes.

> This endpoint is rate-limited to reduce brute-force attempts on OTP codes.

Request:
```json
{ "user_id": 1, "code": "123456" }
```

Response `200`:
```json
{
  "message": "Phone verified successfully",
  "access_token": "<token>",
  "refresh_token": "<token>",
  "user": {
    "id": 1,
    "username": "+2348012345678",
    "email": "ada@example.com",
    "first_name": "Ada",
    "last_name": "Lovelace"
  },
  "profile": {
    "id": 1,
    "user": { ... },
    "user_type": "student",
    "phone_number": "+2348012345678",
    "phone_verified": true,
    "primary_location": "ilorin",
    "profile_picture": null,
    "university": "",
    "bio": "",
    "wallet_balance": "0.00",
    "rating": "5.00",
    "total_ratings": 0,
    "chat_strikes": 0,
    "is_suspended": false,
    "created_at": "2026-05-07 10:00:00",
    "updated_at": "2026-05-07 10:00:00"
  }
}
```

---

### `POST /api/auth/resend-code/`
Request a new OTP.

> This endpoint is rate-limited to reduce SMS abuse.

Request:
```json
{ "user_id": 1 }
```

Response `200`:
```json
{
  "message": "Verification code resent",
  "verification_code": null
}
```

> `verification_code` is only non-null in DEBUG mode.

---

### `POST /api/auth/login/`
Login with phone and password.

> Rate limited: 10 requests per minute per IP.

Request:
```json
{
  "phone_number": "+2348012345678",
  "password": "StrongPass1"
}
```

Response `200`:
```json
{
  "message": "Login successful",
  "access_token": "<token>",
  "refresh_token": "<token>",
  "user": {
    "id": 1,
    "username": "+2348012345678",
    "email": "ada@example.com",
    "first_name": "Ada",
    "last_name": "Lovelace"
  },
  "profile": {
    "id": 1,
    "user_type": "student",
    "phone_number": "+2348012345678",
    "phone_verified": true,
    "primary_location": "ilorin",
    "profile_picture": "https://res.cloudinary.com/.../profile.jpg",
    "university": "UNILORIN",
    "bio": "Engineering student",
    "wallet_balance": "15000.00",
    "rating": "4.80",
    "total_ratings": 5,
    "chat_strikes": 0,
    "is_suspended": false,
    "created_at": "2026-01-01 08:00:00",
    "updated_at": "2026-05-07 10:00:00"
  }
}
```

> After login, immediately call `POST /api/accounts/device-token/` to register the device for push notifications.

**Special login error responses:**

Phone not verified `403`:
```json
{
  "error": "Phone not verified",
  "user_id": 1,
  "message": "Please verify your phone number first"
}
```

Account suspended `403`:
```json
{
  "error": "Account suspended",
  "reason": "Violation of community guidelines"
}
```

---

### `POST /api/auth/logout/`
Blacklist the refresh token.

Request:
```json
{ "refresh_token": "<refresh_token>" }
```

Response `200`:
```json
{ "message": "Logout successful" }
```

---

### `POST /api/auth/request-password-reset/`
Send OTP for password reset.

> This endpoint is rate-limited to reduce SMS abuse.

Request:
```json
{ "phone_number": "+2348012345678" }
```

Response `200`:
```json
{
  "message": "Reset code sent to your phone",
  "phone_masked": "***5678",
  "reset_code": null
}
```

> The reset code expires after 10 minutes. It is only returned in DEBUG mode for testing; production receives `null`.

---

### `POST /api/auth/confirm-password-reset/`
Reset password with OTP.

> This endpoint is rate-limited to reduce brute-force attempts on reset codes.

Request:
```json
{
  "phone_number": "+2348012345678",
  "code": "123456",
  "new_password": "NewStrongPass1"
}
```

Response `200`:
```json
{ "message": "Password reset successful. You can now login with your new password." }
```

---

### `POST /api/auth/refresh-token/`
Get a new access token using the refresh token.

Request:
```json
{ "refresh": "<refresh_token>" }
```

Response `200`:
```json
{ "access": "<new_access_token>", "refresh": "<new_refresh_token>" }
```

> This endpoint uses the standard SimpleJWT response shape. Save both values because refresh tokens are rotated on every use.

---

### `GET /api/users/me/`
Get the authenticated user's full profile.

Response `200`:
```json
{
  "id": 1,
  "user": {
    "id": 1,
    "username": "+2348012345678",
    "email": "ada@example.com",
    "first_name": "Ada",
    "last_name": "Lovelace"
  },
  "user_type": "student",
  "phone_number": "+2348012345678",
  "phone_verified": true,
  "primary_location": "ilorin",
  "profile_picture": "https://res.cloudinary.com/.../profile.jpg",
  "university": "UNILORIN",
  "bio": "Engineering student",
  "wallet_balance": "15000.00",
  "rating": "4.80",
  "total_ratings": 5,
  "chat_strikes": 0,
  "is_suspended": false,
  "created_at": "2026-01-01 08:00:00",
  "updated_at": "2026-05-07 10:00:00"
}
```

---

### `PATCH /api/users/me/`
Update allowed profile fields.

Allowed fields: `university`, `bio`, `profile_picture`

Use `multipart/form-data` when uploading a profile picture.

Request (multipart/form-data):
```
university=UNILORIN
bio=Engineering student
profile_picture=<file>
```

Response `200`: returns the full updated profile object (same shape as `GET /api/users/me/`).

---

### `GET /api/users/{user_id}/profile/`
Get public profile for any user.

Response `200`:
```json
{
  "id": 1,
  "full_name": "Ada Lovelace",
  "profile_picture": "https://res.cloudinary.com/.../profile.jpg",
  "university": "UNILORIN",
  "bio": "Engineering student",
  "rating": "4.80",
  "total_ratings": 5,
  "primary_location": "ilorin",
  "member_since": "January 2026"
}
```

---

## Push Notifications

Push notifications are delivered via **Firebase Cloud Messaging (FCM)**. To receive them the mobile app must register its device token after every login.

### `POST /api/accounts/device-token/`
Register or update the FCM device token. Call this immediately after every successful login.

Request:
```json
{
  "token": "<fcm_device_token>",
  "platform": "android"
}
```

Allowed `platform` values: `android` | `ios`

Response `200`:
```json
{ "message": "Device token registered" }
```

> If the user logs in on a new device, the old token is automatically deactivated.

### Setting up FCM (for the mobile developer)
1. Create a Firebase project at https://console.firebase.google.com
2. Add your Android/iOS app to the project
3. Download `google-services.json` (Android) or `GoogleService-Info.plist` (iOS)
4. Integrate the Firebase SDK in your app
5. On every app launch / login, retrieve the FCM token and call `POST /api/accounts/device-token/`

---

## Notification Center

### `GET /api/accounts/notifications/`
List the authenticated user's notifications, newest first.

Query params:
- `?unread_only=true` — only return unread notifications
- `?page=1&page_size=20`

Response:
```json
{
  "count": 5,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "New Offer Received",
      "body": "John offered ₦5,000 for your Engineering Textbook",
      "type": "new_offer",
      "related_id": "42",
      "is_read": false,
      "created_at": "2026-05-07 10:00:00"
    }
  ]
}
```

Notification types:
```
new_message | new_offer | offer_accepted | offer_rejected |
order_created | payment_received | order_status | delivery_confirmed | general
```

Use `related_id` to navigate to the relevant screen (e.g. open chat, order, or offer).

---

### `PATCH /api/accounts/notifications/{id}/read/`
Mark a single notification as read.

Response `200`:
```json
{ "message": "Marked as read" }
```

---

### `PATCH /api/accounts/notifications/read-all/`
Mark all notifications as read. Call this when the user opens the notification center.

Response `200`:
```json
{ "message": "5 notifications marked as read" }
```

---

## Home Feed

### `GET /api/marketplace/feed/`
**Single call for the mobile app home screen.** Returns everything needed on launch.

No authentication required, but if a valid token is provided, user-specific stats are included.

Response:
```json
{
  "featured_listings": [ ... ],
  "categories": [ ... ],
  "user_stats": {
    "pending_orders": 2,
    "wallet_balance": "15000.00",
    "unread_messages": 3
  },
  "unread_notifications": 1
}
```

> Use this instead of making separate calls to `/listings/`, `/categories/`, and `/wallet/balance/` on app launch.

---

## Marketplace API

### `GET /api/marketplace/categories/`
List all active item categories.

Response:
```json
[
  { "id": 1, "name": "Electronics", "icon": "phone", "is_active": true },
  { "id": 2, "name": "Books", "icon": "book", "is_active": true }
]
```

---

### `GET /api/marketplace/listings/`
Browse active listings with filters.

Query params:
- `?search=textbook`
- `?category=1`
- `?location=ilorin`
- `?condition=fairly_used`
- `?min_price=1000`
- `?max_price=50000`
- `?page=1&page_size=20`

---

### `POST /api/marketplace/listings/create/`
Create a new listing. Requires verified phone.

Use `multipart/form-data`. Fields:

| Field | Required | Notes |
|---|---|---|
| `title` | ✅ | |
| `description` | ✅ | |
| `category` | ✅ | category ID |
| `condition` | ✅ | `new` / `fairly_used` / `used` |
| `price` | ✅ | decimal |
| `is_negotiable` | ✅ | `true` / `false` |
| `location` | ✅ | see allowed locations |
| `allow_pickup` | ✅ | boolean |
| `allow_seller_delivery` | | boolean |
| `allow_campusdeal_delivery` | | boolean |
| `image_1` | | file |
| `image_2` | | file |
| `image_3` | | file |

At least one delivery option must be `true`.

---

### `GET /api/marketplace/listings/{listing_id}/`
Get listing details including seller info.

---

### `PATCH /api/marketplace/listings/{listing_id}/update/`
Update own listing. Seller only.

---

### `DELETE /api/marketplace/listings/{listing_id}/delete/`
Soft-delete (marks as `removed`). Seller only.

---

### `GET /api/marketplace/my-listings/`
Get authenticated user's listings.

Query params: `?status=active|pending|sold|removed`

---

### `GET /api/marketplace/users/{user_id}/listings/`
Get active listings for any public user.

---

## Offers (Negotiation Flow)

This is the recommended flow for **negotiable items** (`is_negotiable = true`).

### Full offer flow:
1. Buyer opens chat → negotiates price
2. Buyer sends offer via API
3. Seller receives push notification
4. Seller accepts or rejects
5. On accept → order is automatically created at agreed price
6. Buyer receives push notification to pay
7. Buyer calls checkout

---

### `POST /api/marketplace/listings/{listing_id}/offer/`
Buyer sends an offer on a negotiable listing.

> Only works on listings where `is_negotiable = true`. For non-negotiable items use `POST /api/marketplace/orders/buy/` instead.

Request:
```json
{
  "proposed_price": 5000,
  "message": "Will you take 5k? It's slightly used.",
  "delivery_method": "pickup"
}
```

Response `201`:
```json
{
  "offer_id": 1,
  "status": "pending",
  "proposed_price": "5000.00",
  "message": "Offer sent. Waiting for seller response."
}
```

> Sending a new offer on the same listing automatically expires any previous pending offer from the same buyer.

---

### `POST /api/marketplace/offers/{offer_id}/respond/`
Seller accepts or rejects an offer.

Request:
```json
{ "action": "accept" }
```
or
```json
{ "action": "reject" }
```

Response on accept `201`:
```json
{
  "message": "Offer accepted. Order created.",
  "offer_id": 1,
  "order_id": "CD1A2B3C4D5E",
  "total_amount": "5175.00",
  "breakdown": {
    "item_price": "5000.00",
    "service_fee": "175.00",
    "delivery_fee": "0.00"
  }
}
```

> On accept, all other pending offers on the item are automatically expired. Buyer is notified via push notification to proceed to payment.

---

### `GET /api/marketplace/offers/`
List offers.

Query params:
- `?role=buyer` — offers the authenticated user sent (default)
- `?role=seller` — offers received on the authenticated user's listings
- `?status=pending|accepted|rejected|expired`

---

### `GET /api/marketplace/listings/{listing_id}/offers/`
Seller views all offers on a specific listing. Seller only.

---

## Order Flow

### Recommended flows:

**Non-negotiable item (fixed price):**
1. Buyer taps "Buy Now" → `POST /api/marketplace/orders/buy/`
2. Buyer calls `POST /api/marketplace/orders/{order_id}/checkout/`
3. If Paystack → save the `reference` locally, then open `authorization_url` in an in-app WebView/browser
4. When the user finishes payment (or closes the WebView) → call `POST /api/marketplace/payments/verify/` with the saved `reference`
5. Buyer receives item → `POST /api/marketplace/orders/{order_id}/confirm-delivery/`

**Negotiable item (offer flow):**
1. Chat → negotiate → `POST /api/marketplace/listings/{id}/offer/`
2. Seller accepts → `POST /api/marketplace/offers/{id}/respond/`
3. Order auto-created → buyer pays via `POST /api/marketplace/orders/{order_id}/checkout/`
4. Buyer confirms delivery → funds released to seller

**Seller-initiated (from chat):**
1. Seller manually creates order after agreeing price in chat
2. `POST /api/marketplace/orders/initiate/` with `item_id`, `buyer_id`, `delivery_method`
3. Buyer notified to pay → proceeds same as above

---

### `POST /api/marketplace/orders/buy/`
Buyer directly creates an order on a **non-negotiable** item.

Request:
```json
{
  "item_id": 12,
  "delivery_method": "pickup"
}
```

Response `201`:
```json
{
  "order_id": "CD1A2B3C4D5E",
  "total_amount": "5175.00",
  "breakdown": {
    "item_price": "5000.00",
    "service_fee": "175.00",
    "delivery_fee": "0.00"
  },
  "waybill_number": null,
  "message": "Order created. Please proceed to payment."
}
```

---

### `POST /api/marketplace/orders/initiate/`
Seller creates an order for a buyer (after negotiating in chat).

Request:
```json
{
  "item_id": 12,
  "buyer_id": 44,
  "delivery_method": "pickup"
}
```

Response `201`:
```json
{
  "order_id": "CD1A2B3C4D5E",
  "total_amount": "5175.00",
  "breakdown": {
    "item_price": "5000.00",
    "service_fee": "175.00",
    "delivery_fee": "0.00"
  },
  "waybill_number": null,
  "payment_required": true,
  "message": "Order created. Waiting for buyer payment."
}
```

---

### `GET /api/marketplace/orders/`
List orders for the current user.

Query params:
- `?role=buyer|seller`
- `?status=payment_pending|paid|seller_preparing|with_courier|delivered|completed|cancelled|refund_requested|refunded`

Response `200`:
```json
{
  "count": 2,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "order_id": "CD1A2B3C4D5E",
      "item_title": "Engineering Textbook",
      "item_image": "https://res.cloudinary.com/.../book.jpg",
      "buyer_name": "Ada Lovelace",
      "seller_name": "John Doe",
      "total_amount": "5175.00",
      "status": "paid",
      "delivery_method": "pickup",
      "created_at": "2026-05-07 10:00:00"
    }
  ]
}
```

---

### `GET /api/marketplace/orders/{order_id}/`
Get a single order. Only buyer or seller of that order can access.

Response `200`:
```json
{
  "id": 1,
  "order_id": "CD1A2B3C4D5E",
  "item": {
    "id": 12,
    "title": "Engineering Textbook",
    "price": "5000.00",
    "image_1": "https://res.cloudinary.com/.../book.jpg",
    "location": "ilorin",
    "condition": "fairly_used"
  },
  "buyer": {
    "id": 1,
    "first_name": "Ada",
    "last_name": "Lovelace",
    "email": "ada@example.com"
  },
  "seller": {
    "id": 2,
    "first_name": "John",
    "last_name": "Doe",
    "email": "john@example.com"
  },
  "delivery_method": "pickup",
  "delivery_address": "",
  "delivery_phone": "",
  "waybill_number": null,
  "item_price": "5000.00",
  "service_fee": "175.00",
  "delivery_fee": "0.00",
  "total_amount": "5175.00",
  "paystack_reference": "PAY_CD1A2B3C4D5E_...",
  "payment_method": "paystack",
  "status": "paid",
  "funds_held": true,
  "funds_released_to_seller": false,
  "created_at": "2026-05-07 10:00:00",
  "paid_at": "2026-05-07 10:05:00",
  "delivered_at": null,
  "completed_at": null
}
```

---

### `POST /api/marketplace/orders/{order_id}/checkout/`
Buyer proceeds to payment.

> For retries, send a stable `X-Idempotency-Key` header or `request_id` field in the JSON body. Reusing the same key safely reuses the existing payment session instead of creating a duplicate one.

Request:
```json
{
  "payment_method": "paystack",
  "delivery_address": "123 Main Street, Ilorin",
  "delivery_phone": "+2348012345678"
}
```

`delivery_address` and `delivery_phone` are required only when `delivery_method` is `campusdeal` or `seller`.

Response for Paystack `200`:
```json
{
  "authorization_url": "https://checkout.paystack.com/abc123",
  "access_code": "abc123",
  "reference": "PAY_CD1A2B3C4D5E_..."
}
```

Response for wallet payment `200`:
```json
{
  "success": true,
  "order_id": "CD1A2B3C4D5E",
  "status": "paid",
  "message": "Payment successful. Seller will prepare your item.",
  "waybill_number": null
}
```

---

### Paystack payment flow for mobile apps

> **Critical:** The Paystack callback/redirect URL is not reliable in a mobile context. Your app must **always** verify payment manually using the `reference` — do not depend on any redirect.

**Step-by-step:**

1. Call `POST /api/marketplace/orders/{order_id}/checkout/` with `"payment_method": "paystack"`
2. **Save the `reference` value** from the response into local state before opening the browser
3. Open `authorization_url` in an in-app WebView or browser
4. **When the WebView closes** (whether the user completed payment, cancelled, or the page redirected) — call `POST /api/marketplace/payments/verify/` with the saved `reference`
5. Check the verify response:
   - `"success": true` → payment confirmed, update UI to show order as paid
   - `"success": false` → payment not completed, show a retry option

```
// Pseudocode
reference = checkout_response.reference
openWebView(checkout_response.authorization_url)

onWebViewClosed():
    result = POST /api/marketplace/payments/verify/ { reference }
    if result.success:
        navigateToOrderDetail(order_id)
    else:
        showRetryPaymentScreen()
```

> The backend webhook (`POST /api/marketplace/payments/webhook/`) also processes payments server-side as a backup, but the app should never rely on this — always call verify yourself.

---

### `POST /api/marketplace/payments/verify/`
Verify a Paystack payment after the user returns from the payment page.

Request:
```json
{ "reference": "PAY_CD1A2B3C4D5E_..." }
```

Response on success `200`:
```json
{
  "success": true,
  "order_id": "CD1A2B3C4D5E",
  "status": "paid",
  "message": "Payment verified successfully"
}
```

Response on failure `400`:
```json
{
  "success": false,
  "message": "Payment verification failed"
}
```

> If you call verify and get `"success": true` but `status` is still `payment_pending`, wait 2 seconds and retry once — the webhook may have already processed it.

---

### `POST /api/marketplace/payments/webhook/`
Paystack webhook. **Server-to-server only. Do not call from the mobile app.**

---

### `PATCH /api/marketplace/orders/{order_id}/update-status/`
Seller updates the order fulfillment status.

Request:
```json
{
  "status": "seller_preparing",
  "notes": "Packing item now"
}
```

Allowed status transitions for sellers:
```
seller_preparing → with_courier → delivered
```

Both buyer and seller can set: `cancelled`

Response `200`:
```json
{
  "success": true,
  "order_id": "CD1A2B3C4D5E",
  "status": "seller_preparing",
  "message": "Order status updated to seller_preparing"
}
```

---

### `POST /api/marketplace/orders/{order_id}/confirm-delivery/`
Buyer confirms they received the item. This **releases funds to the seller's wallet**.

> Only call this when the buyer has physically received the item. This action is irreversible.

Response `200`:
```json
{
  "success": true,
  "message": "Delivery confirmed. Funds released to seller.",
  "order_id": "CD1A2B3C4D5E"
}
```

---

### `POST /api/marketplace/orders/{order_id}/cancel/`
Cancel an order. If the order was already paid, the buyer is refunded to their wallet.

> If the seller has already withdrawn the released funds, cancellation/reversal can fail with an insufficient seller balance error. Show the user a support path in that case.

Response `200`:
```json
{
  "message": "Order cancelled successfully",
  "refund_amount": "5175.00"
}
```

> `refund_amount` is `"0.00"` if the order was not yet paid.

---

### `GET /api/marketplace/orders/{order_id}/status-history/`
Get the full status change history for an order.

Response `200`:
```json
[
  {
    "id": 2,
    "from_status": "payment_pending",
    "to_status": "paid",
    "notes": "",
    "changed_by_name": "Ada Lovelace",
    "created_at": "2026-05-07 10:05:00"
  },
  {
    "id": 1,
    "from_status": "",
    "to_status": "payment_pending",
    "notes": "",
    "changed_by_name": "John Doe",
    "created_at": "2026-05-07 10:00:00"
  }
]
```

---

## Wallet API

### `GET /api/marketplace/wallet/balance/`
Get current wallet balance.

Response `200`:
```json
{ "balance": "15000.00", "currency": "NGN" }
```

---

### `GET /api/marketplace/wallet/transactions/`
Wallet transaction history.

Query params:
- `?page=1&page_size=20`
- `?transaction_type=credit|debit`
- `?source=sale|refund|deposit|purchase|withdrawal`

Response `200`:
```json
{
  "count": 3,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "transaction_type": "credit",
      "amount": "5000.00",
      "source": "deposit",
      "reference": "WALLET_1_abc123",
      "balance_before": "10000.00",
      "balance_after": "15000.00",
      "created_at": "2026-05-07 10:00:00"
    }
  ]
}
```

---

### `POST /api/marketplace/wallet/add-funds/`
Initialize a wallet top-up via Paystack. Minimum deposit is ₦100.

> For retries, send a stable `X-Idempotency-Key` header or `request_id` field in the JSON body.

Request:
```json
{ "amount": "5000.00" }
```

Response `200`:
```json
{
  "authorization_url": "https://checkout.paystack.com/abc123",
  "access_code": "abc123",
  "reference": "WALLET_1_abc123",
  "amount": "5000.00"
}
```

### Wallet deposit flow for mobile apps

> Same principle as order payments — always verify manually. Do not rely on redirects.

**Step-by-step:**

1. Call `POST /api/marketplace/wallet/add-funds/` with the desired amount
2. **Save the `reference`** from the response into local state
3. Open `authorization_url` in an in-app WebView or browser
4. **When the WebView closes** — call `POST /api/marketplace/wallet/verify-deposit/` with the saved `reference`
5. Check the verify response and refresh the wallet balance display

```
// Pseudocode
reference = add_funds_response.reference
openWebView(add_funds_response.authorization_url)

onWebViewClosed():
    result = POST /api/marketplace/wallet/verify-deposit/ { reference }
    if result.success:
        refreshWalletBalance()
        showToast("Wallet credited: ₦" + result.amount)
    else:
        showToast("Payment not completed. Try again.")
```

---

### `POST /api/marketplace/wallet/verify-deposit/`
Verify the deposit after Paystack payment completes.

Request:
```json
{ "reference": "WALLET_1_abc123" }
```

Response on success `200`:
```json
{
  "success": true,
  "message": "Wallet credited successfully",
  "amount": "5000.00",
  "new_balance": "20000.00"
}
```

Response if already processed `200`:
```json
{
  "success": true,
  "message": "Wallet deposit already processed",
  "amount": "5000.00",
  "new_balance": "20000.00"
}
```

Response on failure `400`:
```json
{
  "success": false,
  "message": "Payment verification failed"
}
```

---

### `GET /api/marketplace/wallet/banks/`
Get the list of supported Nigerian banks for withdrawals.

Response `200`:
```json
[
  { "name": "Guaranty Trust Bank", "code": "058" },
  { "name": "Access Bank", "code": "044" }
]
```

---

### `POST /api/marketplace/wallet/verify-account/`
Verify a bank account name before saving.

Request:
```json
{ "account_number": "0123456789", "bank_code": "058" }
```

Response `200`:
```json
{
  "success": true,
  "account_number": "0123456789",
  "account_name": "ADA LOVELACE"
}
```

---

### `POST /api/marketplace/wallet/add-bank-account/`
Save a bank account for withdrawals.

Request:
```json
{
  "account_number": "0123456789",
  "bank_code": "058",
  "bank_name": "Guaranty Trust Bank",
  "set_as_primary": true
}
```

---

### `GET /api/marketplace/wallet/bank-accounts/`
List saved bank accounts.

Response `200`:
```json
[
  {
    "id": 1,
    "account_number": "0123456789",
    "account_name": "ADA LOVELACE",
    "bank_name": "Guaranty Trust Bank",
    "bank_code": "058",
    "is_verified": true,
    "is_primary": true
  }
]
```

---

### `POST /api/marketplace/wallet/bank-accounts/{account_id}/set-primary/`
Set a bank account as the default withdrawal account.

---

### `DELETE /api/marketplace/wallet/bank-accounts/{account_id}/`
Remove a bank account.

---

### `POST /api/marketplace/wallet/withdraw/`
Withdraw from wallet to bank account.

> Withdrawal fee is currently NGN 25 flat. Minimum withdrawal amount is NGN 1,000. Maximum per day is NGN 500,000. If `bank_account_id` is omitted, the API uses your primary verified bank account.

> For retries, send a stable `X-Idempotency-Key` header or `request_id` field in the JSON body.

Request:
```json
{
  "amount": "10000.00",
  "bank_account_id": 1
}
```

Response `200`:
```json
{
  "message": "Withdrawal initiated successfully",
  "reference": "WD_abc123",
  "amount": "10000.00",
  "fee": "25.00",
  "net_amount": "9975.00",
  "new_balance": "5000.00",
  "status": "processing"
}
```

---

### `GET /api/marketplace/wallet/withdrawals/`
Withdrawal history.

Response `200`:
```json
[
  {
    "id": 1,
    "amount": "10000.00",
    "withdrawal_fee": "25.00",
    "net_amount": "9975.00",
    "reference": "WD_abc123",
    "status": "success",
    "created_at": "2026-05-07 10:00:00",
    "completed_at": "2026-05-07 10:02:00"
  }
]
```

Withdrawal statuses: `pending` | `processing` | `success` | `failed` | `reversed`

---

### `GET /api/marketplace/wallet/withdrawal-fees/`
Get current withdrawal fee rules.

Response `200`:
```json
{
  "withdrawal_fee": "25.00",
  "minimum_withdrawal": "1000.00",
  "maximum_per_day": "500000.00"
}
```

---

## Reviews

### `POST /api/marketplace/reviews/`
Leave a review after a completed order. One review per order.

> Only allowed when order status is `completed`. Both buyer and seller can leave a review.

Request:
```json
{
  "order_id": "CD1A2B3C4D5E",
  "rating": 5,
  "comment": "Great seller, item exactly as described!"
}
```

Response `201`:
```json
{
  "id": 1,
  "order": 1,
  "reviewer": 1,
  "reviewer_name": "Ada Lovelace",
  "reviewee": 2,
  "reviewee_name": "John Doe",
  "rating": 5,
  "comment": "Great seller, item exactly as described!",
  "created_at": "2026-05-07 11:00:00"
}
```

---

### `GET /api/marketplace/users/{user_id}/reviews/`
Get reviews for any user.

Response `200`:
```json
{
  "user_id": 2,
  "average_rating": "4.80",
  "total_reviews": 5,
  "reviews": [
    {
      "id": 1,
      "order": 1,
      "reviewer": 1,
      "reviewer_name": "Ada Lovelace",
      "reviewee": 2,
      "reviewee_name": "John Doe",
      "rating": 5,
      "comment": "Great seller!",
      "created_at": "2026-05-07 11:00:00"
    }
  ]
}
```

---

### `GET /api/marketplace/orders/{order_id}/review/`
Get the review for a specific order.

Response `200`:
```json
{
  "id": 1,
  "order": 1,
  "reviewer": 1,
  "reviewer_name": "Ada Lovelace",
  "reviewee": 2,
  "reviewee_name": "John Doe",
  "rating": 5,
  "comment": "Great seller, item exactly as described!",
  "created_at": "2026-05-07 11:00:00"
}
```

Response when no review exists `404`:
```json
{ "message": "No review yet for this order" }
```

---

## Refunds

### `POST /api/marketplace/orders/{order_id}/request-refund/`
Buyer requests a refund. Use `multipart/form-data` to attach evidence images.

> Refund requests are only allowed for `completed` or `delivered` orders, and only within 7 days of completion when `completed_at` is set.

Request fields:
- `reason` — one of: `not_as_described` | `damaged` | `wrong_item` | `seller_unresponsive` | `other`
- `detailed_explanation` — text description
- `evidence_image_1`, `evidence_image_2`, `evidence_image_3` — optional images

---

### `GET /api/marketplace/orders/{order_id}/refund-request/`
Get the refund request status for an order.

Response `200`:
```json
{
  "id": 1,
  "status": "pending",
  "reason": "not_as_described",
  "detailed_explanation": "The item colour was different from the photos.",
  "admin_notes": ""
}
```

Refund statuses: `pending` | `approved` | `rejected` | `processed`

---

### `POST /api/marketplace/refunds/{refund_id}/approve/`
Admin approves a refund.

> Approval can fail if the seller wallet no longer has enough balance to reverse the payout.

---

### `POST /api/marketplace/refunds/{refund_id}/reject/`
Admin rejects a refund.

---

### `GET /api/marketplace/refunds/pending/`
Admin — list all pending refunds.

---

## Hostels

### `GET /api/marketplace/hostels/`
Browse hostel listings.

Query params: `?location=ilorin&min_rent=10000&max_rent=50000&search=kwasu`

---

### `GET /api/marketplace/hostels/{hostel_id}/`
Get hostel details.

---

### `POST /api/marketplace/hostels/create/`
Landlord creates a hostel listing. Use `multipart/form-data`.

Key fields: `name`, `address`, `description`, `location`, `rent_per_month`, `contact_phone`, `amenities` (JSON array string e.g. `["wifi","water","security"]`), `image_1`, `image_2`, `image_3`

---

### `GET /api/marketplace/hostels/my-listings/`
Landlord's own hostel listings.

---

### `PATCH /api/marketplace/hostels/{hostel_id}/update/`
Update a hostel listing. Landlord only.

---

### `DELETE /api/marketplace/hostels/{hostel_id}/delete/`
Delete a hostel listing. Landlord only.

---

### Admin hostel endpoints

- `GET /api/marketplace/hostels/admin/pending/` — pending verification queue
- `GET /api/marketplace/hostels/admin/all/` — all hostels
- `POST /api/marketplace/hostels/{hostel_id}/verify/` — verify a hostel
- `GET /api/marketplace/hostels/admin/stats/` — stats

---

## Chat API

### `GET /api/chats/`
List all chats for the authenticated user, ordered by most recent message.

---

### `POST /api/chats/create/`
Create or open a chat. Returns existing chat if one already exists between the two users.

Request:
```json
{
  "other_user_id": 45,
  "item_id": 12,
  "initial_message": "Is this still available?"
}
```

`item_id` and `initial_message` are optional. The other user is notified via push notification when a new chat is created.

---

### `GET /api/chats/{chat_id}/`
Get chat details.

---

### `GET /api/chats/{chat_id}/messages/`
Get paginated messages for a chat.

Query params: `?page=1&page_size=50`

Messages are returned newest first.

---

### `POST /api/chats/{chat_id}/messages/send/`
Send a message. Messages are automatically moderated — phone numbers and off-platform contact attempts are flagged.

Request:
```json
{ "text": "Hello, is this available?" }
```

If a message is blocked by moderation:
```json
{
  "error": "Message blocked",
  "warning": "Sharing contact details is not allowed",
  "strike_number": 1,
  "strikes_remaining": 2,
  "account_suspended": false
}
```

> 3 strikes = account suspended automatically.

---

### `PATCH /api/chats/{chat_id}/mark-read/`
Mark all messages in the chat as read. Call when user opens a chat.

---

### `GET /api/chats/unread-count/`
Get total unread message count across all chats.

Response:
```json
{ "unread_count": 3 }
```

---

## Real-Time Chat

The mobile app can use WebSockets for live chat updates.

### `wss://campusdeal-backend.onrender.com/ws/chats/{chat_id}/?token=<access_token>`
Connect to a chat room using the user's JWT access token as a query parameter.

> Always use `wss://` (not `ws://`) when connecting to the production server.

> WebSocket auth uses the `token` query parameter, not the `Authorization` header.

Events you may receive:

| Event | Payload | Description |
|---|---|---|
| `chat.connected` | `{ "messages": [...] }` | Initial payload with recent messages on connect |
| `chat.message` | `{ "message": {...} }` | A new message delivered in real time |
| `chat.warning` | `{ "message": {...}, "warning": "..." }` | A moderated message was blocked |
| `chat.read` | — | Unread count changed — refresh your badge |
| `chat.typing` | — | The other user is typing |

Client actions (send as JSON over the socket):

| Action | Payload | Description |
|---|---|---|
| `send_message` | `{ "action": "send_message", "text": "Hello" }` | Send a message |
| `mark_read` | `{ "action": "mark_read" }` | Mark messages as read |
| `typing` | `{ "action": "typing" }` | Notify the other user you are typing |

**Fallback:** If WebSocket is unavailable, poll `GET /api/chats/{chat_id}/messages/` every few seconds instead.

---

## Admin API

### `GET /api/marketplace/admin/financials/`
Platform financial summary. Staff only.

### `POST /api/marketplace/admin/withdraw-profit/`
Withdraw platform profit. Staff only.

---

## Environment Variables Required on Render

| Variable | Description |
|---|---|
| `SECRET_KEY` | Django secret key |
| `DATABASE_URL` | PostgreSQL connection string |
| `PAYSTACK_SECRET_KEY` | Paystack live secret key |
| `PAYSTACK_PUBLIC_KEY` | Paystack live public key |
| `SENDCHAMP_SECRET_KEY` | Sendchamp API key |
| `SENDCHAMP_SENDER_ID` | Approved Sendchamp sender ID |
| `CLOUDINARY_CLOUD_NAME` | Cloudinary cloud name |
| `CLOUDINARY_API_KEY` | Cloudinary API key |
| `CLOUDINARY_API_SECRET` | Cloudinary API secret |
| `FCM_SERVER_KEY` | Firebase Cloud Messaging server key |
| `CORS_ALLOWED_ORIGINS` | Comma-separated list of allowed frontend origins |
| `FRONTEND_URL` | Frontend base URL for Paystack callbacks (ignored for mobile — verify manually) |
| `FINANCE_ALERT_EMAILS` | Comma-separated emails for financial alerts |
| `REDIS_URL` | Redis URL (optional — enables WebSocket channels) |

---

## Notes for Mobile Developers

- **Always register the FCM device token after login** via `POST /api/accounts/device-token/`
- **Use `/api/marketplace/feed/`** on app launch instead of separate calls
- **Handle `401` automatically** — refresh the token and retry the request once before redirecting to login
- **Use `multipart/form-data`** for any endpoint that accepts image uploads
- **Do not call webhook endpoints** from the mobile app — they are server-to-server only
- **Build retries** around network failures for payment and OTP actions
- **Save the Paystack `reference` before opening any WebView** — always call the verify endpoint when the WebView closes, regardless of how it was closed (payment completed, cancelled, redirected, or errored)
- **The `is_negotiable` flag on listings** determines which purchase flow to use:
  - `false` → show Buy Now → `POST /api/marketplace/orders/buy/`
  - `true` → show Make Offer → `POST /api/marketplace/listings/{id}/offer/`
- **Offer `related_id`** in notifications tells you which screen to navigate to
- **Notification types** and their target screens:

| Type | Navigate to |
|---|---|
| `new_message` | Chat screen (use `related_id` as `chat_id`) |
| `new_offer` | Offers screen |
| `offer_accepted` | Order detail (use `related_id` as `order_id`) |
| `offer_rejected` | Listing detail |
| `order_created` | Order detail |
| `payment_received` | Order detail |
| `order_status` | Order detail |
| `delivery_confirmed` | Wallet screen |

---

## Production Considerations

- OTP delivery depends on Sendchamp sender ID being approved
- Paystack payments require live keys to be set in Render environment variables
- Images are stored on Cloudinary in production — ensure credentials are set
- Redis is optional but required for WebSocket real-time chat
- Background jobs (notifications, reconciliation) run in threads — not a durable queue. For high scale, migrate to Celery + Redis
- Financial reconciliation alerts are sent to `FINANCE_ALERT_EMAILS` — set at least one email

---

*Last updated: July 2026*
