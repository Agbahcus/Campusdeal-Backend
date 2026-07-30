# campusdeal-backend

REST API + WebSocket backend for CampusDeal — a peer-to-peer student marketplace serving Nigerian university campuses, with built-in escrow, wallet, and hostel listing features.

---

**Live API:** `https://campusdeal-backend.onrender.com`
**Client integration guide:** [`API_DOCUMENTATION.md`](API_DOCUMENTATION.md)

---

## The Problem

Nigerian students buying and selling between themselves have no safe rails. Money changes hands over WhatsApp, items don't arrive, sellers ghost buyers, and there's no recourse. Campus areas also have a fragmented hostel rental market where students rely on word-of-mouth and unverified agents. CampusDeal keeps the money held in escrow until delivery is confirmed — neither party can be cheated.

---

## Architecture Overview

**Escrow via wallet ledger, not a payment gateway hold.**
Funds paid via Paystack flow into a platform-controlled Paystack balance. A `PlatformFinancials` singleton model tracks three running totals in real time: `user_funds_liability` (what we owe users), `platform_revenue` (fees earned), and `paystack_balance` (actual Paystack balance). Every money movement — deposit, order payment, refund, withdrawal — writes an immutable `FinancialTransaction` audit row and updates these counters inside a `select_for_update` transaction. This makes reconciliation a subtraction (`paystack_balance - user_funds_liability`) rather than a full ledger scan, and makes drift immediately visible.

**Dual payment path with consistent ledger semantics.**
Orders can be paid via Paystack (card/bank) or from a wallet balance. The ledger service handles both through the same `record_order_payment` method but with different delta logic: Paystack payments increase `paystack_balance`, wallet payments do not (funds are already on platform). This distinction is explicit in the code rather than inferred, which is where most fintech bugs hide.

**Background tasks via ThreadPoolExecutor, not Celery.**
Notifications (SMS via Sendchamp/SmartSMS, FCM push) and reconciliation jobs are dispatched to a `ThreadPoolExecutor` with `transaction.on_commit` guards. This was a deliberate tradeoff: no broker infrastructure to manage at early scale, at the cost of no retries and no distributed execution. The design is explicit about this — task failures log and alert, but don't block the request.

**WebSockets via Django Channels + Redis channel layer.**
Real-time chat uses `AsyncJsonWebsocketConsumer` backed by a Redis channel layer in production. JWT auth is enforced at the WS handshake layer before the socket is accepted. The consumer delegates message persistence to a synchronous service layer via `sync_to_async`, keeping the async consumer thin.

**Chat moderation at write time.**
A regex-based `ContentModerator` scans every outbound message for phone numbers, emails, and off-platform meetup keywords before the message is persisted. Violations apply a 3-strike system stored on the user profile. This runs synchronously in the WebSocket consumer because a blocked message must not be written — async would introduce a race.

**SMS provider abstraction.**
The codebase runs two SMS providers (Sendchamp, SmartSMS) behind a factory interface. The active provider is selected at runtime via `SMS_PROVIDER` env var. This was built after the first provider had repeated delivery failures — the interface made swapping providers a one-line config change rather than a refactor.

---

## Tech Stack

| Technology | Why this, not the alternative |
|---|---|
| **Django 4.2 LTS** | The ORM's `select_for_update` and `F()` expressions handle concurrent wallet updates correctly without raw SQL; LTS gives a stable base through April 2026 |
| **Django REST Framework** | Serializer validation catches bad financial input at the boundary before it reaches the ledger; the alternative (manual validation) is error-prone with money |
| **PostgreSQL** | Row-level locking (`select_for_update`) is reliable; SQLite's table-level locks would serialize all wallet operations under concurrency |
| **Django Channels + Daphne** | Enables WebSockets on the same Django codebase without a separate Node.js process; Daphne is the ASGI server maintained by the Channels team |
| **channels-redis** | Required for Channels to broadcast across multiple Daphne workers; InMemoryChannelLayer only works with a single process |
| **Simple JWT** | Stateless auth with refresh token rotation and blacklisting; session auth doesn't fit a mobile-first API |
| **Paystack** | Only payment gateway with reliable Nigerian bank transfers and a well-documented webhook signature scheme; Flutterwave's webhook reliability was worse at the time of evaluation |
| **Cloudinary** | Handles image variants and CDN delivery for listing photos without managing S3 lifecycle policies |
| **Sentry** | Error tracking with Django integration and `send_default_pii=False` to avoid accidentally logging user data |
| **Whitenoise** | Serves compressed static files without Nginx in front; removes an infrastructure dependency during early deployment |

---

## Local Setup

```bash
git clone https://github.com/<your-username>/campusdeal-backend.git
cd campusdeal-backend

python -m venv venv && source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# Fill in: SECRET_KEY, PAYSTACK_SECRET_KEY, PAYSTACK_PUBLIC_KEY, SMS credentials

python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

WebSocket support locally uses `InMemoryChannelLayer` (no Redis needed). For Redis-backed channels, set `REDIS_URL` in `.env`.

---

## Key Engineering Challenges

**Preventing double wallet credits on Paystack webhook retries.**
Paystack retries webhook delivery if it doesn't receive a `200` response within a short window. A slow DB write could cause a second webhook to arrive before the first transaction commits, crediting a wallet twice. The fix: `record_wallet_deposit` performs a `select_for_update` lookup for an existing `WalletTransaction` with the same `(user, reference, source='deposit')` tuple inside the same atomic block. If found, it returns early with `duplicate: True` without touching the balance. The uniqueness check and the balance update are a single serializable unit.

**Keeping the financial ledger consistent across two payment paths.**
When a wallet-funded order is cancelled, reversing the ledger is different from reversing a Paystack-funded order — the Paystack balance doesn't move, but the liability accounting must still correct itself. Getting this wrong means `reconciliation_status()` shows a false surplus or deficit. The solution was to make `reverse_order_payment` purely delta-based (it adds back the service fee liability without touching `paystack_balance`) and to test the accounting identity `paystack_balance == user_funds_liability + platform_revenue` explicitly in the reconciliation snapshot job.

**WebSocket authentication without Django session middleware.**
DRF's JWT auth doesn't work out of the box on the WebSocket handshake because `scope` isn't a standard HTTP request. A custom `ws_middleware.py` intercepts the ASGI scope, extracts the JWT from query params or headers, validates it using Simple JWT's internals, and attaches the resolved `User` to the scope before the consumer sees it. The consumer then closes with `4401` on an anonymous user rather than silently accepting and failing later.

---

## What's Next

- **Retry queue for background tasks.** The current `ThreadPoolExecutor` approach has no retry on failure. A lightweight persistent queue (even Django's DB-backed one) would handle SMS delivery failures more reliably than the current fire-and-forget.
- **Paystack transfer webhook handling.** Withdrawals are initiated via Paystack transfers but the `transfer.success` / `transfer.failed` webhook path isn't fully implemented. Currently, withdrawal status is polled manually via admin. Completing this would close the last manual step in the money-out flow.
- **Rate limiting on financial endpoints.** `django-ratelimit` is installed and configured but not yet applied to wallet deposit and withdrawal endpoints, which are the highest-value targets for abuse.

---

**Author:** Divine Agbah — [LinkedIn](https://www.linkedin.com/in/divine-agbah?utm_source=share_via&utm_content=profile&utm_medium=member_ios)
