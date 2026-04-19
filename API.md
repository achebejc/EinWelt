# OneWorld API Reference

Interactive documentation is available at `/docs` (Swagger UI) and `/redoc` (ReDoc) when the server is running.

Base URL: `https://api.oneworld.up.railway.app` (production) or `http://localhost:8000` (local)

---

## Authentication

All endpoints except `/health`, `/auth/register`, `/auth/login`, `/auth/forgot-password`, `/auth/reset-password`, and `/auth/verify-email` require a Bearer JWT in the `Authorization` header:

```
Authorization: Bearer <access_token>
```

Tokens are obtained from `POST /auth/login` or `POST /auth/register`. They expire after 7 days by default.

---

## Endpoints

### Auth (`/auth`)

#### `POST /auth/register`
Register the owner account. Public registration is disabled — only the configured `OWNER_EMAIL` is accepted.

**Request body:**
```json
{
  "email": "ceo@oneworld.app",
  "password": "Str0ng!Pass1",
  "full_name": "Jessica Achebe"
}
```

**Response `201`:**
```json
{
  "access_token": "eyJ...",
  "token_type": "bearer"
}
```

Password requirements: 8–128 characters, at least one uppercase, one lowercase, one digit, one special character.

---

#### `POST /auth/login`
Authenticate and receive a JWT.

**Request body:**
```json
{
  "email": "ceo@oneworld.app",
  "password": "Str0ng!Pass1"
}
```

**Response `200`:**
```json
{
  "access_token": "eyJ...",
  "token_type": "bearer"
}
```

Rate limit: 20 requests/minute per IP.

---

#### `POST /auth/forgot-password`
Trigger a password-reset e-mail. Always returns `202` to avoid leaking whether the e-mail exists.

**Request body:**
```json
{ "email": "ceo@oneworld.app" }
```

**Response `202`:**
```json
{ "detail": "If that e-mail is registered you will receive a reset link shortly." }
```

---

#### `POST /auth/reset-password`
Complete a password reset using the one-time token from the e-mail link.

**Request body:**
```json
{
  "token": "<one-time-token>",
  "new_password": "N3wStr0ng!Pass"
}
```

**Response `200`:**
```json
{ "detail": "Password updated successfully." }
```

---

#### `POST /auth/verify-email`
Verify an e-mail address using the one-time token from the verification e-mail.

**Request body:**
```json
{ "token": "<one-time-token>" }
```

**Response `200`:**
```json
{ "detail": "E-mail verified successfully." }
```

---

### Users (`/users`)

#### `GET /users/me` 🔒
Return the authenticated user's profile.

**Response `200`:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "ceo@oneworld.app",
  "full_name": "Jessica Achebe",
  "is_owner": true,
  "is_verified": true,
  "created_at": "2024-01-01T00:00:00Z"
}
```

---

#### `PATCH /users/me` 🔒
Update the authenticated user's display name.

**Request body:**
```json
{ "full_name": "Jessica Chekwube Achebe" }
```

**Response `200`:** Updated `UserOut` object.

---

### Analytics (`/analytics`)

#### `POST /analytics/events` 🔒
Record a client-side analytics event.

**Request body:**
```json
{
  "event_name": "screen.view",
  "payload": { "screen": "home", "duration_ms": 1200 }
}
```

**Response `201`:**
```json
{ "detail": "Event recorded." }
```

`event_name` must be 1–255 characters. `payload` is optional arbitrary JSON.

---

### Billing (`/billing`)

#### `POST /billing/checkout` 🔒
Create a Stripe Checkout Session and return the redirect URL.

**Response `200`:**
```json
{ "checkout_url": "https://checkout.stripe.com/pay/..." }
```

Returns `503` if Stripe is not configured, `502` if the Stripe API call fails.

---

### Utility — AI Features (`/utility`)

All utility endpoints require authentication and an `OPENAI_API_KEY` to be configured. Returns `503` if the key is absent.

#### `POST /utility/chat` 🔒
Send a message to the AI financial assistant.

**Request body:**
```json
{
  "message": "How do I open a bank account in Germany?",
  "language": "en"
}
```

**Response `200`:**
```json
{
  "response": "To open a bank account in Germany...",
  "language": "en"
}
```

---

#### `POST /utility/scan` 🔒
Analyse text extracted from a scanned financial document.

**Request body:**
```json
{
  "extracted_text": "Kontoauszug\nDatum: 01.01.2024\nBetrag: -150,00 EUR",
  "language": "en"
}
```

**Response `200`:** `ChatResponse` with AI analysis.

---

#### `POST /utility/translate` 🔒
Translate text to a target language.

**Request body:**
```json
{
  "text": "Hello, how are you?",
  "targetLanguage": "de"
}
```

**Response `200`:** `ChatResponse` with translated text.

---

#### `POST /utility/budget` 🔒
Get AI-powered budgeting advice based on income and expenses.

**Request body:**
```json
{
  "income": 3500.00,
  "expenses": 2800.00
}
```

**Response `200`:** `ChatResponse` with budgeting recommendations.

---

### System

#### `GET /health`
Returns application status and dependency health. No authentication required.

**Response `200`:**
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

`status` is `"degraded"` when the database is unreachable.

---

## Error Responses

All errors follow the standard FastAPI format:

```json
{ "detail": "Human-readable error message." }
```

| Status | Meaning |
|--------|---------|
| `400` | Bad request (invalid token, malformed input) |
| `401` | Unauthenticated (missing or invalid JWT) |
| `403` | Forbidden (insufficient permissions) |
| `404` | Resource not found |
| `409` | Conflict (e.g. duplicate e-mail) |
| `413` | Request body too large (> 1 MB) |
| `422` | Validation error (field constraints not met) |
| `429` | Rate limit exceeded |
| `500` | Internal server error |
| `502` | Upstream API error (Stripe, OpenAI) |
| `503` | Service not configured |

---

## React Native Integration

### Install an HTTP client

```bash
npm install axios
```

### Example auth flow

```typescript
import axios from 'axios';

const API = axios.create({
  baseURL: process.env.EXPO_PUBLIC_API_URL ?? 'http://localhost:8000',
  headers: { 'Content-Type': 'application/json' },
});

// Attach JWT to every request
API.interceptors.request.use((config) => {
  const token = getStoredToken(); // your AsyncStorage helper
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// Login
const { data } = await API.post('/auth/login', { email, password });
await storeToken(data.access_token);

// Get profile
const { data: user } = await API.get('/users/me');

// Chat
const { data: reply } = await API.post('/utility/chat', {
  message: 'How do I save money?',
  language: 'en',
});
```

### Request ID tracking

Every response includes an `X-Request-ID` header. Log this value alongside errors to correlate client-side issues with server-side logs.
