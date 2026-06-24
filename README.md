# Venue Pulse Backend

Venue Pulse is a Django backend for a hospitality operations dashboard. It receives POS transactions, stores them in MySQL, provides dashboard metrics through REST APIs, and sends real-time transaction notifications over WebSocket.

This repository contains the backend only. It does not include a frontend.

## Main features

- JWT login and token refresh
- Transaction ingest for sales, refunds, and voids
- Dashboard metrics for venue sales, top items, hourly sales, and alerts
- Venue-level dashboard details
- WebSocket notifications when a transaction is stored
- MySQL storage and Redis-backed Django Channels
- Consistent JSON responses, logging, and translated API messages

## Tech stack

- Python 3.12
- Django 5.1
- Django REST Framework
- Simple JWT
- Django Channels and Daphne
- MySQL 8
- Redis
- Docker Compose

## Project structure

```text
api/
├── models.py                 # Database models
├── constants.py              # Transaction types, limits, and alert thresholds
├── custom_authentication.py  # JWT authentication for WebSocket connections
├── auth/                     # Login and token refresh
├── transactions/             # Transaction validation and ingest
├── dashboard/                # Dashboard queries and alert detection
├── realtime/                 # WebSocket consumer and broadcasts
└── utilities/                # Response, pagination, and shared helpers

config/                       # Django settings, URLs, ASGI, and WSGI
docker/                       # Container entrypoint
locale/                       # Translation files
logs/                         # Application and error logs
```

## How it works

When a transaction reaches the API, the request is validated and the transaction and line items are saved in one database transaction. After the database commit succeeds, the backend sends a small WebSocket event to connected dashboard clients.

The event tells the client that data has changed. The client can then request the dashboard endpoint it needs. This keeps the WebSocket message small and keeps the REST endpoints as the source of truth.

`transaction_number` is unique. If a POS system sends the same transaction again, the duplicate is rejected instead of being stored twice.

## Environment setup

Create a `.env` file in the project root before choosing either setup method.

The `SECRET_KEY` is used by Django for security-related signing. In this project, it also signs the JWT access and refresh tokens. If the key is exposed, someone could create tokens that the backend accepts as valid.

If Python and the project dependencies are available, generate a secret key
with:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Add the settings to `.env`:

```dotenv
SECRET_KEY=<paste-the-generated-key-here>
DEBUG=true
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:5173
TIME_ZONE=Asia/Kolkata

DB_NAME=venue_pulse
DB_USER=root
DB_PASSWORD=root
DB_HOST=127.0.0.1
DB_PORT=3306

# Use redis://127.0.0.1:6379/0 to enable Redis locally.
REDIS_URL=
```

Keep the secret key private and use a different value for each environment.

The current Docker Compose configuration provides its own database connection values for the containers. The database values above are used when running the backend without Docker.

## Running with Docker

This is the easiest way to run the project locally. You only need Docker and
Docker Compose. MySQL, Redis, and Python do not need to be installed separately.

From the project root, build and start all services:

```bash
docker compose up --build -d
```

Docker automatically creates the `venue_pulse` database, waits for MySQL to be
ready, runs the migrations, and starts the backend with Daphne.

Check that the containers are running:

```bash
docker compose ps
```

Create an admin user:

```bash
docker compose exec backend python manage.py createsuperuser
```

The API is then available at:

```text
http://localhost:8000
```

To view the backend logs:

```bash
docker compose logs -f backend
```

To stop the services:

```bash
docker compose down
```

The MySQL data is kept in a Docker volume when the services stop. To remove the containers and delete the local database data, run:

```bash
docker compose down -v
```

The MySQL container is available from the host on port `3307`. Application logs are written to the local `logs/` directory. The Docker configuration includes a development-only secret key, which must be replaced before deployment.

## Running without Docker

You need Python 3.12, MySQL 8, and optionally Redis. Redis is recommended when more than one backend process is running. A single local process can use the in-memory channel layer.

Create and activate a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Create the MySQL database. Its name must match the `DB_NAME` value in `.env`
(`venue_pulse` in the example above):

```sql
CREATE DATABASE venue_pulse
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;
```

Then run:

```bash
python manage.py migrate
python manage.py createsuperuser
daphne -b 0.0.0.0 -p 8000 config.asgi:application
```

## Authentication

All transaction, dashboard, and WebSocket requests require a valid access token. The login and refresh endpoints are public.

### Login

```http
POST /api/auth/login/
Content-Type: application/json
```

```json
{
  "email": "user@example.com",
  "password": "your-password"
}
```

The response contains `access_token` and `refresh_token`.

### Refresh a token

```http
POST /api/auth/refresh/
Content-Type: application/json
```

```json
{
  "refresh_token": "<refresh_token>"
}
```

Authenticated HTTP requests must include:

```http
Authorization: Bearer <access_token>
```

Access tokens last 8 hours. Refresh tokens last 1 day.

## API endpoints

### Create a transaction

```http
POST /api/transactions/
Authorization: Bearer <access_token>
Content-Type: application/json
```

```json
{
  "venue_id": 1,
  "transaction_id": "TXN1001",
  "transaction_type": "SALE",
  "total_amount": 250.00,
  "staff_id": 1,
  "items": [
    {
      "item_id": 1,
      "quantity": 2,
      "price": 50.00
    },
    {
      "item_id": 2,
      "quantity": 1,
      "price": 150.00
    }
  ]
}
```

`transaction_type` must be `SALE`, `REFUND`, or `VOID`.

`venue_id`, `staff_id`, and every `item_id` must already exist. The API records the transaction time when the request is received. It does not accept a transaction timestamp in the payload.

### Dashboard

```http
GET /api/dashboard/venue-sales/
GET /api/dashboard/top-items/
GET /api/dashboard/alerts/
GET /api/dashboard/hourly-sales/
GET /api/dashboard/venue/?venue_id=1
```

- `venue-sales` returns today's sales ranked by venue.
- `top-items` returns today's best-selling products across all venues.
- `alerts` returns sales-drop, refund-spike, and void-spike alerts.
- `hourly-sales` returns sales totals for the last 12 hours.
- `venue` returns today's sales, hourly sales, and top items for one venue.

`venue-sales`, `top-items`, and `venue` use page-number pagination. Use `page` and `pageSize` query parameters to change the page. `pageSize` has a maximum of 100.

## WebSocket updates

Connect with an access token in the query string:

```text
ws://localhost:8000/ws/dashboard/?token=<access_token>
```

Browsers cannot set a normal authorization header when creating a WebSocket, so the backend reads the token from the `token` query parameter. Invalid or missing tokens close the connection with code `4401`.

Each stored transaction sends an event like this:

```json
{
  "event": "transaction_created",
  "venue_id": 1,
  "transaction_id": "TXN1001",
  "total_amount": 250.0
}
```

The broadcast runs after the database commit. A failed WebSocket broadcast does not roll back a stored transaction.

Redis is used for the channel layer when `REDIS_URL` is set. Without it, the backend uses an in-memory channel layer, which only works across a single process.

## Response format

Successful responses use this shape:

```json
{
  "success": true,
  "message": "",
  "data": {}
}
```

Paginated responses also include:

```json
{
  "meta": {
    "pagination": {
      "page": 1,
      "pageSize": 10,
      "pageCount": 1,
      "total": 1
    }
  }
}
```

Errors use:

```json
{
  "success": false,
  "message": "Request could not be completed.",
  "errors": {}
}
```

Unexpected errors are logged, while the API returns a general error message without exposing a traceback.

## Data model

| Model | Purpose |
| --- | --- |
| `Venue` | A pub, restaurant, or function venue |
| `Staff` | A staff member linked to a venue |
| `Product` | A product that can appear on a transaction |
| `Transaction` | A sale, refund, or void |
| `TransactionItem` | A product line within a transaction |

Transactions protect their linked venue, staff member, and products from deletion while financial history still refers to them. Transaction items are deleted with their parent transaction.

Dashboard queries use the timezone set by `TIME_ZONE`. The default is Asia/Kolkata, and all venues currently share that timezone.

For revenue calculations, sales include `SALE` transactions. Net sales subtract refunds. Voids are counted for alert detection but do not add to revenue.

## Alerts

Alert thresholds are defined in `api/constants.py`.

- A sales-drop alert compares the latest 60 minutes with the previous 60 minutes.
- Refund and void alerts compare their transaction counts with the number of recent sales.
- Minimum activity rules help prevent alerts for venues with too little data.

## Logging

Logs are configured in `config/settings.py`:

- `logs/application.log` contains messages at `INFO` level and above.
- `logs/error.log` contains errors and tracebacks.

## Translations

API message text is stored in `locale/en/LC_MESSAGES/django.po`. After changing the translation file, rebuild the compiled catalog:

```bash
python manage.py compilemessages --ignore=venv
```

To scan the code for new translation messages first, run:

```bash
python manage.py makemessages -l en --ignore=venv
```
