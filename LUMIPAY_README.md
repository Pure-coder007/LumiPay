# Lumipay — A Modern Digital Banking System

**Tagline:** *Banking reimagined. Fast, simple, auditable.*

**Project type:** Developer + Product README (Pitch-style)  
**Stack:** Django + Django REST Framework (DRF), PostgreSQL, Redis, Celery, React/Next.js for frontend.

---

## Overview — What is Lumipay?
Lumipay is a full-featured fintech backend designed as a realistic, extendable prototype for a digital bank / wallet product. It supports:
- User registration & authentication (email/phone + JWT)
- Auto-generated bank-style accounts and multi-currency wallets (NGN, USD, EUR, GBP)
- **₦100,000 welcome bonus** on successful registration (configurable)
- Peer-to-peer transfers between users (internal rails)
- Bill payments: **Airtime, Data, Electricity** with provider adapters and webhook handling
- External bank rails (Moniepoint, UBA) for top-ups and payouts via adapter pattern
- Virtual card provisioning (single-use & multi-use) via card provider adapters
- Background tasks: Celery workers + Celery Beat for reconciliation, FX updates, webhook processing, and async provisioning
- Admin endpoints for reconciliation, provider reports, and manual settlements
- Swagger / OpenAPI docs via DRF schema generation

Lumipay is intentionally product-shaped: it reads like a startup README you’d show to investors, but contains the technical bones engineers need to scaffold a real system.

---

## Project Vision (one-liner)
Create a safe, auditable, and developer-friendly platform to move money, pay bills, and issue virtual cards — fast enough for users and strict enough for audits.

---

## Quick demo flow (what a user experiences)
1. Register → receive account number + NGN wallet credited with **₦100,000**.
2. Log in → obtain JWT token.
3. Transfer to another user by account number (instant internal settlement).
4. Buy airtime/data/electricity from the Bills page (funds debited instantly; providers reconciled asynchronously).
5. Top up wallet — get redirect/payment instructions, and webhook finalizes top-up.
6. Create virtual card for online payments — provisioned by partner and tied to a wallet's balance.

---

## Brand & Naming
Project name and artifacts use **Lumipay**. Example API base path: `/api/lumipay/`

---

## Tech Stack (details)
- **Backend:** Django 4.x, Django REST Framework (DRF)
- **Database:** PostgreSQL (store money as integer minor units — kobo/cents)
- **Cache / Broker:** Redis (Celery broker + cache)
- **Tasks:** Celery + Celery Beat
- **Auth:** JWT (djangorestframework-simplejwt)
- **Storage:** MinIO or AWS S3 for receipts & KYC docs
- **Frontend:** React (CRA) or Next.js (for SSR/SSG where needed)
- **Docs:** drf-yasg or DRF built-in OpenAPI for API docs
- **Testing:** pytest-django, FactoryBoy
- **Monitoring:** Prometheus + Grafana (optional), Sentry for errors

---

## Folder Structure (suggested)
```
lumipay/
├── backend/
│   ├── lumipay/                 # Django project
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi/asgi.py
│   ├── apps/
│   │   ├── users/
│   │   ├── accounts/            # Account, Wallet models
│   │   ├── transactions/
│   │   ├── bills/
│   │   ├── cards/
│   │   ├── providers/           # Moniepoint, UBA, VTU adapters
│   │   └── payments/
│   ├── tasks/                   # celery tasks
│   └── requirements.txt
├── frontend/                    # react or next app
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## Core Data Models (conceptual)

> Money stored in minor units (integer): NGN → kobo, USD → cents

### User (apps.users.models.User)
- id (UUID), email, phone, password_hash, full_name, is_active, kyc_status, created_at, updated_at

### Account (apps.accounts.models.Account)
- id (UUID), user (FK), account_number (string, unique), account_type (wallet/current), currency (default NGN)

### Wallet (apps.accounts.models.Wallet)
- id (UUID), user (FK), currency (char3), balance (BIGINT), available_balance (BIGINT), reserved (BIGINT)

### Transaction / LedgerEntry (apps.transactions.models)
- Transaction: id, tx_ref, type, status, amount, currency, description, initiated_by
- LedgerEntry: id, transaction (FK), wallet (FK), entry_type (debit/credit), amount, balance_after

### BillPayment (apps.bills.models.BillPayment)
- id, user, wallet, provider, bill_type (airtime/data/electricity), recipient, amount, fee, provider_ref, status, metadata, created_at

### ExternalBankTransfer (apps.providers.models.ExternalBankTransfer)
- provider, provider_ref, from_wallet, to_bank_account (json), amount, fee, status

### VirtualCard (apps.cards.models.VirtualCard)
- id, user, wallet, provider_card_id, last4, exp_month, exp_year, status, limit

### AuditLog
- user, action, meta (json), ip, user_agent, created_at

---

## API Design — Key Endpoints (developer-friendly, pitch-style)

Base path: `/api/lumipay/v1/`

### Auth & Users
- `POST /api/lumipay/v1/auth/register`  
  Body: `{ "email","phone","password","full_name" }`  
  Response: `201 { user_id, account_number, tokens }`  
  Notes: Creates default NGN wallet and credits **₦100,000** (configurable `INITIAL_BONUS`).

- `POST /api/lumipay/v1/auth/login`  
  Body: `{ "email","password" }` → Returns JWT access/refresh.

- `GET /api/lumipay/v1/users/me`  
  Auth required: returns user profile and wallets summary.

### Accounts & Wallets
- `GET /api/lumipay/v1/accounts/` → lists bank-style accounts & wallets.  
- `POST /api/lumipay/v1/wallets/` → create additional currency wallet (USD, EUR, GBP).  
- `GET /api/lumipay/v1/wallets/{wallet_id}/balance`

### Transfers (internal)
- `POST /api/lumipay/v1/transfers/`  
  Headers: `Idempotency-Key` required.  
  Body: `{ "from_wallet_id", "to_account_number"|"to_wallet_id", "amount", "currency", "narration" }`  
  Response: `201 { transfer_id, transaction_ref, status }`

- `GET /api/lumipay/v1/transfers/{tx_ref}`

### Bill Payments (Airtime / Data / Electricity)
- `POST /api/lumipay/v1/bills/pay`  
  Body: `{ "wallet_id","bill_type","recipient","provider","amount" }`  
  Response: `202 { bill_id, status: "processing", provider_ref }`

- `GET /api/lumipay/v1/bills/{bill_id}`  
- `POST /api/lumipay/v1/webhooks/bills`  — provider POSTs status updates

### Bank Top-ups & Payouts (Providers: Moniepoint, UBA)
- `POST /api/lumipay/v1/bank/topup`  
  Body: `{ "wallet_id","amount","provider","return_url" }` → returns provider payment URL or bank transfer details.  
- `POST /api/lumipay/v1/webhooks/bank`  — handle provider confirmation
- `POST /api/lumipay/v1/bank/payout`  — payout to external bank (requires KYC/admin)

### Virtual Cards
- `POST /api/lumipay/v1/cards/`  — create virtual card `{ wallet_id, currency, limit, type }`  
- `GET /api/lumipay/v1/cards/`  
- `PATCH /api/lumipay/v1/cards/{card_id}/block`

### FX & Conversions
- `GET /api/lumipay/v1/fx/rates`  — cached FX rates  
- `POST /api/lumipay/v1/fx/convert`  — `{ from_wallet_id, to_wallet_id, amount }`

### Admin & Reconciliation
- `POST /api/lumipay/v1/admin/reconcile`  — trigger reconcile job for date range  
- `GET /api/lumipay/v1/admin/provider-report`  — get provider settlement status

### Health & Docs
- `GET /healthz`  
- `GET /api/docs`  — Swagger / Redoc

---

## Example Flows (practical)

### Registration (simplified)
1. `POST /auth/register` → validate payload.  
2. Create `User`.  
3. Create default NGN `Wallet`.  
4. Create `Transaction` credit referencing `INITIAL_BONUS`.  
5. Create `LedgerEntry` to credit wallet and a balancing platform subsidy entry.  
6. Return tokens + account.  
_Important: use DB transaction or Saga pattern to avoid partial commits._

### P2P Transfer (atomic)
- Use `SELECT ... FOR UPDATE` (or Django `select_for_update()`) on wallet rows in consistent order.  
- Check `available_balance`.  
- Create `Transaction` with `pending` status; create ledger entries (debit & credit); commit.  
- Emit event / Celery task to notify parties and update caches.
- Use `Idempotency-Key` to dedupe duplicate submits.

### Bill Payment (airtime/data/electricity)
- `POST /bills/pay` → debit user's wallet (hold/available balance), create `BillPayment` record, call provider via adapter.  
- Provider responds sync or async (webhook). On success, finalize ledger entries and mark bill `success`. On failure, release hold and mark `failed`.  
- Celery tasks handle retries, reconciliation, and receipts.

### Virtual Card Issuance
- `POST /cards` → create pending request, call card provider adapter via Celery.  
- Adapter returns token/pan/last4 (store token & last4 only).  
- On charge webhook, treat as external charge: debit wallet, create ledger entries, and reconcile with provider report.

---

## Background Jobs (Celery)
- `celery worker` processes: webhook handlers, notification sender, async provider calls, card provisioning, reconcile jobs.  
- `celery beat`: scheduled jobs — `fx_update`, `reconcile_providers`, `cleanup_expired_authorizations`.

Sample task design:
```python
@shared_task(bind=True, max_retries=5)
def process_bill_webhook(self, payload):
    # normalize payload, find BillPayment, mark success/failure, create ledger entries
    pass
```

---

## Providers & Adapter Pattern (recommended)
Implement adapters in `apps.providers.adapters` with a simple interface:

```python
class ProviderAdapter(ABC):
    def charge(self, **kwargs): pass
    def status(self, provider_ref): pass
    def webhook(self, payload): pass
```

Adapters to create:
- `MoniepointAdapter` — top-ups & payouts  
- `UBAAdapter` — account verification & payouts  
- `BillProviderAdapter` — airtime/data/electricity  
- `CardProviderAdapter` — virtual card provisioning

Adapters should be testable (mock provider responses) and pluggable via settings (swap provider per country or per bill type).

---

## Environment & Config (example `.env` keys)
```
DJANGO_SECRET_KEY=...
DATABASE_URL=postgres://user:pass@postgres:5432/lumipay
REDIS_URL=redis://redis:6379/0
INITIAL_BONUS=10000000   # in kobo => ₦100,000
MONIEPOINT_API_KEY=...
MONIEPOINT_SECRET=...
UBA_CLIENT_ID=...
UBa_CLIENT_SECRET=...
BILL_PROVIDER_KEY=...
CARD_PROVIDER_KEY=...
FX_API_KEY=...
AWS_S3_BUCKET=...
```

---

## Setup & Quickstart (Django + Celery)

### Prereqs
- Python 3.10+  
- PostgreSQL  
- Redis

### Local Dev (simplified)
```bash
git clone https://github.com/yourorg/lumipay.git
cd lumipay/backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # fill values
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
# Start Redis separately
celery -A lumipay worker --loglevel=info
celery -A lumipay beat --loglevel=info
```

### Running Tests
```bash
pytest
```

---

## Security & Money Rules (short & clear)
- Store money as integers (minor units).  
- Use database transactions and `select_for_update()` for balance ops.  
- Idempotency required for mutating endpoints (`Idempotency-Key`).  
- Webhook verification with HMAC + timestamp + nonce.  
- Payouts and high-value actions require KYC & admin approval.  
- Secure secrets in environment or secret manager (no .env in VCS).

---

## Example Requests (curl)

**Register (gives initial bonus)**
```bash
curl -X POST http://localhost:8000/api/lumipay/v1/auth/register  -H "Content-Type: application/json"  -d '{
   "email":"alex@example.com",
   "phone":"+2348012345678",
   "password":"StrongP@ssw0rd",
   "full_name":"Alex Johnson"
 }'
```

**Transfer (idempotent)**
```bash
curl -X POST http://localhost:8000/api/lumipay/v1/transfers/  -H "Authorization: Bearer <token>"  -H "Content-Type: application/json"  -H "Idempotency-Key: f81d4fae-7dec-11d0-a765-00a0c91e6bf6"  -d '{
   "from_wallet_id":"11111111-2222-3333-4444",
   "to_account_number":"0392098765",
   "amount":5000000,
   "currency":"NGN",
   "narration":"Payment for design work"
 }'
```

**Pay Airtime**
```bash
curl -X POST http://localhost:8000/api/lumipay/v1/bills/pay  -H "Authorization: Bearer <token>"  -H "Content-Type: application/json"  -H "Idempotency-Key: bill-123"  -d '{
   "wallet_id":"11111111-2222-3333-4444",
   "bill_type":"airtime",
   "provider":"VTUProviderA",
   "recipient":"+2348012345678",
   "amount":500000
 }'
```

---

## Roadmap (product & engineering)
**Phase 1 (MVP)**  
- Core user flows: register, wallet, transfers, transactions, basic bill payments.  
- Admin UI & basic reconciliation.  
- Celery tasks for async provider handling.

**Phase 2 (Scale)**  
- Bank integrations (Moniepoint, UBA) fully tested and reconciled.  
- Virtual card issuance and card-webhook reconciliation.  
- Multi-currency support and FX engine.

**Phase 3 (Production)**  
- High-availability infra (K8s), hardened security, PCI scope reduction (partners), monitoring + SLOs, formal audit & compliance.

---

## Want me to scaffold this?
I can now generate code stubs for Lumipay immediately:  
- Django models & serializers for `Wallet`, `BillPayment`, `VirtualCard`.  
- Provider adapter skeletons (Moniepoint & UBA).  
- DRF viewsets & routes for all endpoints listed.  
- Celery tasks and a sample `docker-compose.yml` for local development.

Tell me which scaffold(s) to generate first and I’ll create them right away.

---

## Downloadable README
I saved this polished pitch-style README as **LUMIPAY_README.md**.

[Download LUMIPAY_README.md](sandbox:/mnt/data/LUMIPAY_README.md)

---

**Lumipay** — Build money rails people trust.  
If you want code stubs next, say **"scaffold models"**, **"scaffold adapters"**, or **"scaffold API"** and I'll generate them.