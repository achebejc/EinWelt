# Deployment Guide

This document covers deploying the OneWorld API to production on Railway, as well as running it locally with Docker Compose.

---

## Local Development

### Prerequisites

- Docker Desktop (or Docker Engine + Compose plugin)
- Node.js 18+ (for the React Native frontend)

### Start the full stack

```bash
# Clone and enter the repo
git clone <repo-url> && cd <repo>

# Copy the environment template
cp .env.example .env
# Edit .env with your real values (SMTP, Stripe, OpenAI, etc.)

# Build and start all services
docker compose up --build
```

Services started:
| Service  | URL                        |
|----------|----------------------------|
| API      | http://localhost:8000      |
| Swagger  | http://localhost:8000/docs |
| ReDoc    | http://localhost:8000/redoc|
| Postgres | localhost:5432             |
| Redis    | localhost:6379             |

### Run migrations manually

```bash
docker compose exec backend alembic -c alembic/alembic.ini upgrade head
```

### Run tests locally

```bash
# Install dependencies
pip install -r requirements.txt

# Set test environment variables
export DATABASE_URL=sqlite:///./test.db
export REDIS_URL=redis://localhost:6379/1
export SECRET_KEY=test-secret

# Run the full test suite
pytest

# Run only unit tests (no DB required)
pytest -m unit

# Run with coverage report
pytest --cov=app --cov-report=html
open htmlcov/index.html
```

---

## Railway Deployment

### One-time setup

1. Create a Railway project at https://railway.app
2. Add a **PostgreSQL** plugin and a **Redis** plugin to the project
3. Add a **Service** pointing at this repository
4. Set the following environment variables in the Railway dashboard:

| Variable | Description |
|---|---|
| `SECRET_KEY` | 64-char random hex (`python -c "import secrets; print(secrets.token_hex(64))"`) |
| `DATABASE_URL` | Provided automatically by the Railway Postgres plugin |
| `REDIS_URL` | Provided automatically by the Railway Redis plugin |
| `ENVIRONMENT` | `production` |
| `FRONTEND_URL` | Your Expo / React Native app URL |
| `APP_BASE_URL` | Your Railway service URL (e.g. `https://api.oneworld.up.railway.app`) |
| `OWNER_EMAIL` | Initial owner account e-mail |
| `OWNER_PASSWORD` | Strong initial owner password |
| `OWNER_FULL_NAME` | Owner display name |
| `SMTP_HOST` | SMTP server hostname |
| `SMTP_USERNAME` | SMTP username |
| `SMTP_PASSWORD` | SMTP password |
| `STRIPE_SECRET_KEY` | Stripe secret key (`sk_live_...`) |
| `STRIPE_PRICE_ID` | Stripe price ID for the subscription |
| `STRIPE_WEBHOOK_SECRET` | Stripe webhook signing secret |
| `SENTRY_DSN` | Sentry DSN for error tracking |
| `OPENAI_API_KEY` | OpenAI API key |
| `LOG_JSON` | `true` (structured JSON logs for Railway's log viewer) |

5. Set the **Start Command** to `./entrypoint.sh` (or leave blank — the Dockerfile ENTRYPOINT handles it)

### Automated deployments (GitHub Actions)

Add the following secret to your GitHub repository:

| Secret | Value |
|---|---|
| `RAILWAY_TOKEN` | Your Railway API token (from Railway dashboard → Account → Tokens) |

Every push to `main` will trigger `.github/workflows/deploy.yml`, which runs the Railway CLI to deploy the latest image.

### Database migrations

Migrations run automatically on every deploy via `entrypoint.sh`:

```bash
alembic -c alembic/alembic.ini upgrade head
```

To create a new migration after changing a model:

```bash
alembic -c alembic/alembic.ini revision --autogenerate -m "describe your change"
```

Always review the generated migration file before committing.

---

## Production Checklist

- [ ] `SECRET_KEY` is a strong random value (not the default)
- [ ] `OWNER_PASSWORD` is changed from the default
- [ ] `ENVIRONMENT=production` is set
- [ ] `LOG_JSON=true` for structured log ingestion
- [ ] HTTPS is enforced (Railway provides this automatically)
- [ ] `FRONTEND_URL` is set to the exact origin of your frontend (no trailing slash)
- [ ] Stripe webhook endpoint is registered at `POST /billing/webhook` in the Stripe dashboard
- [ ] Sentry DSN is configured for error tracking
- [ ] Database backups are enabled in Railway
- [ ] Rate limits are reviewed for your expected traffic

---

## Health Check

The `/health` endpoint returns the application status and database connectivity:

```json
{
  "status": "ok",
  "environment": "production",
  "version": "1.0.0",
  "checks": {
    "database": "ok"
  }
}
```

Railway uses this endpoint for automatic health monitoring. If `status` is `degraded`, check the database connection.
