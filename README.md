# Travel Itinerary Backend

**A modern React application that centralizes travel planning in one organized platform - solving the problem of scattered trip information across multiple apps and emails.**

## Table of Contents

- [📖 Project Overview](#-project-overview)
- [✨ Features](#-features)
- [🚀 Live Demo](#-live-demo)
- [📡 API Endpoints Reference](#-api-endpoints-reference)
- [🛠️ Tech Stack](#tech-stack)
- [▶️ How to Run the Application](#-how-to-run-the-application)
- [🏗️ Project Structure Overview](#-project-structure-overview)
- [🧪 How to Run Tests](#-how-to-run-tests)
- [💡 Key Technical Decisions](#-key-technical-decisions)
- [🏢 Enterprise Ops and Governance](#-enterprise-ops-and-governance)
- [🔒 Security](#-security)
- [✅ Code Quality](#-code-quality)
- [🔄 CI Pipeline and Git Practices](#-ci-pipeline-and-git-practices)

## 📖 Project Overview

### What is this application?

The **Travel Itinerary Planner** is a full-stack web application designed to help travelers organize and manage their trips in one centralized platform. Built with React and powered by a Django REST API backend, this application provides an intuitive interface for creating detailed travel plans, tracking activities, and sharing experiences with others.

### Real-World Problem

**The Problem:** Travelers struggle with trip information scattered across emails, booking sites, and notes apps - leading to lost reservations, no centralized view, and difficulty sharing experiences.

**My Solution:** A single platform that centralizes trip management with:
- **Status Lifecycle** - Track trips from Planning → Ongoing → Completed
- **Activity Management** - Day-by-day itinerary with descriptions
- **Cloud Storage** - Images via Cloudinary
- **Privacy Controls** - Public sharing with private status
- **Smart Features** - Auto-suggested status based on dates, JWT authentication, SendGrid password reset

**Built for:** Individual travelers, group coordinators, travel enthusiasts, and digital nomads.

## ✨ Features

### 🔐 Authentication & User Management
- **Secure Registration** - Email-based account creation with validation
- **JWT Authentication** - Token-based login with automatic refresh
- **Password Reset** - Email-powered password recovery via SendGrid
- **Profile Management** - Update personal details and profile image
- **Protected Routes** - Automatic authentication guards

### 🗺️ Itinerary Management
- **Create Trips** - Title, destination, start/end dates with validation
- **Status Lifecycle** - Track trips through Planning → Ongoing → Completed
- **Auto-Suggest Status** - Intelligent status suggestions based on dates
- **Image Uploads** - Multiple photos per trip via Cloudinary integration
- **Edit & Delete** - Full CRUD operations on your itineraries
- **Privacy Controls** - Toggle between public and private visibility

### 📅 Activity Planning
- **Day-by-Day Organization** - Structure activities by trip day
- **Rich Descriptions** - Detailed activity information
- **Real-time Updates** - Instant add, edit, and delete operations
- **Flexible Structure** - Optional day numbers for unscheduled activities

### 🌍 Public Sharing & Discovery
- **Explore Page** - Browse public trips from other travelers
- **Detailed Views** - See complete itineraries with photos and activities
- **Guest Access** - View public trips without authentication
- **Call-to-Action** - Encourage users to create their own itineraries

### 🎨 User Experience
- **Responsive Design** - Mobile-first approach, works on all devices
- **Loading States** - Smooth loading indicators for better UX
- **Error Handling** - User-friendly error messages with retry options
- **Status Badges** - Visual indicators for trip status with color coding
- **Consistent UI** - Unified design system across all pages

### 🔒 Security Features
- **JWT Tokens** - Secure access and refresh token system
- **Token Auto-Refresh** - Seamless session management
- **User-Scoped Data** - Users only see their own private data
- **Public/Private Separation** - Clear boundaries for data access
- **CORS Protection** - Proper cross-origin resource sharing configuration

---

## 🚀 Live Demo

The application is fully deployed and accessible online:

**Frontend:** https://travel-itinerary-frontend-5oyl.onrender.com

**Backend API:** https://travel-itinerary-backend-yvk7.onrender.com/api

### ⚠️ Important Note

The free tier on Render spins down after inactivity. The first request may take up to **1 minute** to start up. Please be patient!

### Testing the Live API

The easiest way to test the API is using the interactive Swagger documentation:

👉 **Visit:** https://travel-itinerary-backend-yvk7.onrender.com/api/docs/

Swagger provides a user-friendly interface to test all endpoints directly in your browser. You can also use tools like Postman or cURL if you prefer.

### Frontend Repository

The backend Django application is available at:
https://github.com/warishaak/travel-itinerary-backend.git

### OpenAPI and API Docs

OpenAPI schema and interactive docs are available at:

- `http://localhost:8000/api/schema/` (machine-readable schema)
- `http://localhost:8000/api/docs/` (Swagger UI)
- `http://localhost:8000/api/redoc/` (ReDoc)

---

## 📡 API Endpoints Reference

This section documents all available REST API endpoints, organized by domain.

### 🔐 Authentication Endpoints

All authentication endpoints use **JSON request/response format** and support **CORS** for cross-origin requests.

| Method | Endpoint | Auth Required | Description | Response |
|--------|----------|---------------|-------------|----------|
| `POST` | `/api/auth/register/` | ❌ No | Register new user account | `201 Created` with user data |
| `POST` | `/api/auth/token/` | ❌ No | Login - obtain JWT tokens | `200 OK` with `{ "access": "token", "refresh": "token" }` |
| `POST` | `/api/auth/token/refresh/` | ❌ No | Refresh access token | `200 OK` with new `{ "access": "token" }` |
| `GET` | `/api/auth/me/` | ✅ Yes | Get current user profile | `200 OK` with user data |
| `PUT` | `/api/auth/me/` | ✅ Yes | Update current user profile | `200 OK` with updated user data |
| `PATCH` | `/api/auth/me/` | ✅ Yes | Partial update user profile | `200 OK` with updated user data |
| `POST` | `/api/auth/password-reset/request/` | ❌ No | Request password reset email | `200 OK` (always, anti-enumeration) |
| `POST` | `/api/auth/password-reset/confirm/` | ❌ No | Confirm password reset with token | `200 OK` on success |

**Authentication Headers:**
```http
Authorization: Bearer <access_token>
```

**Rate Limits:**
- Login/Token endpoints: **5 requests per minute** (scoped throttle)
- Password reset: **5 requests per minute** (scoped throttle)
- Other authenticated endpoints: **1000 requests per day** (user throttle)
- Anonymous endpoints: **100 requests per day** (anon throttle)

---

### 🗺️ Itinerary Endpoints (Authenticated Users)

All itinerary management endpoints require authentication via JWT token. Users can only access/modify their own itineraries.

| Method | Endpoint | Description | Response |
|--------|----------|-------------|----------|
| `GET` | `/api/itineraries/my/` | List all user's itineraries | `200 OK` with paginated list |
| `POST` | `/api/itineraries/my/` | Create new itinerary | `201 Created` with itinerary data |
| `GET` | `/api/itineraries/my/{id}/` | Retrieve specific itinerary details | `200 OK` with full itinerary + activities |
| `PUT` | `/api/itineraries/my/{id}/` | Full update of itinerary | `200 OK` with updated data |
| `PATCH` | `/api/itineraries/my/{id}/` | Partial update of itinerary | `200 OK` with updated data |
| `DELETE` | `/api/itineraries/my/{id}/` | Delete itinerary | `204 No Content` |
| `POST` | `/api/itineraries/my/{id}/update_status/` | Update itinerary status | `200 OK` with updated itinerary |

---

### 🌍 Public Itinerary Endpoints (No Auth Required)

These endpoints allow **anyone** (including non-authenticated users) to browse public itineraries shared by travelers.

| Method | Endpoint | Auth Required | Description | Response |
|--------|----------|---------------|-------------|----------|
| `GET` | `/api/itineraries/public/` | ❌ No | List all public itineraries (is_public=true) | `200 OK` with paginated list |
| `GET` | `/api/itineraries/public/{id}/` | ❌ No | View specific public itinerary details | `200 OK` with full itinerary + activities |

**Notes:**
- Only itineraries marked as `is_public: true` are visible
- User's `status` field is **hidden** from public view (privacy control)
- Full CRUD operations require authentication (read-only for public)

---

### 🛠️ Admin & Documentation Endpoints

| Method | Endpoint | Auth Required | Description |
|--------|----------|---------------|-------------|
| `GET` | `/api/` | ❌ No | API root - shows available endpoints |
| `GET` | `/api/schema/` | ❌ No | OpenAPI 3.0 schema (machine-readable JSON) |
| `GET` | `/api/docs/` | ❌ No | Swagger UI - interactive API documentation |
| `GET` | `/api/redoc/` | ❌ No | ReDoc UI - alternative API documentation |
| `GET` | `/admin/` | ✅ Superuser | Django admin panel |


---

## How to Run the Application

### Prerequisites

- Python 3.11+
- PostgreSQL (recommended) or SQLite for local development
- `pip`

### 1. Clone and enter the project

```bash
git clone <https://github.com/warishaak/travel-itinerary-frontend.git>
cd travel-itinerary-backend
```

### 2. Create and activate virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create `.env` in repo root:

```env
SECRET_KEY=replace-with-a-long-random-secret
DEBUG=True
DATABASE_URL=sqlite:///db.sqlite3
FRONTEND_URL=http://localhost:5173

SENDGRID_API_KEY=optional-for-local
FROM_EMAIL=noreply@example.com

ADMIN_EMAIL=admin@example.com
ADMIN_USERNAME=admin
ADMIN_PASSWORD=replace-with-strong-password
```

Notes:
- For production, use PostgreSQL via `DATABASE_URL`.
- Use a strong `SECRET_KEY` (32+ bytes recommended).

### 5. Run migrations

```bash
python manage.py migrate
```

### 6. Create/update admin user

```bash
python manage.py create_admin
```

### 7. Start API server

```bash
python manage.py runserver 8000
```

API entry points:
- `http://localhost:8000/api/`
- `http://localhost:8000/api/auth/register/`
- `http://localhost:8000/api/auth/token/`
- `http://localhost:8000/api/itineraries/my/`
- `http://localhost:8000/api/itineraries/public/`

## 🏗️ Project Structure Overview

The backend is organized by domain app and explicit layers.

```text
travel-itinerary-backend/
├── config/                      # Project settings, URLs, middleware, logging
│   ├── settings.py              # Django/DRF/Security/OpenAPI configuration
│   ├── urls.py                  # Root route registration + docs endpoints
│   ├── middleware.py            # Correlation ID middleware
│   ├── logging_filters.py       # request_id log injection filter
│   └── tests/                   # Config/system-level tests
├── users/                       # User and auth domain
│   ├── api/                     # API views + DTO serializers
│   ├── services/                # Registration/password-reset use-cases
│   ├── selectors/               # Read/query helpers
│   ├── domain/                  # Domain constants/rules
│   ├── permissions.py           # Auth/permission policy classes
│   ├── models.py                # User + PasswordReset models
│   └── tests/                   # User/auth tests
├── itineraries/                 # Itinerary domain
│   ├── api/                     # API views + DTO serializers
│   ├── services/                # Status transition service
│   ├── selectors/               # Read/query helpers
│   ├── domain/                  # Business rules/validations
│   ├── permissions.py           # Ownership/public access permissions
│   ├── models.py                # Itinerary model
│   ├── migrations/              # Django migrations
│   └── tests/                   # Itinerary tests
├── docs/
│   └── ARCHITECTURE.md          # Module boundaries, auth model, extension points
├── scripts/
│   └── send_email_smoke.py      # Manual email smoke script
├── .github/workflows/main.yml   # CI pipeline (format, lint, security, tests)
├── .pre-commit-config.yaml      # Local pre-push quality gates
├── requirements.txt             # Python dependencies
├── render.yaml                  # Render deployment config
└── manage.py                    # Django command entrypoint
```

This structure enforces explicit boundaries between API transport, business logic, queries, and policy/security concerns.

### Layer responsibilities

API layer: request/response handling, serializer validation, endpoint orchestration
Service layer: business use-cases and state transitions
Selector layer: query logic separated from mutation/use-case logic
Domain layer: pure business rules and validations
Permission layer: authorization rules isolated from views
This separation supports maintainability, easier testing, and safer extension.

## Tech Stack

### Core Framework

- Django 5.2
- Django REST Framework 3.16

### Authentication and Security

- `djangorestframework-simplejwt` (JWT auth)
- DRF throttling (anon/user/scoped rate limits)
- Django password validators

### API Documentation

- `drf-spectacular` for OpenAPI schema generation
- Swagger UI (`/api/docs/`)
- ReDoc (`/api/redoc/`)

### Database and Persistence

- PostgreSQL (primary production database)
- SQLite (local development option)
- Django ORM + migrations
- `dj-database-url` for environment-driven DB configuration

### Deployment and Runtime

- Gunicorn (WSGI server)
- WhiteNoise (static file serving)
- Render deployment configuration (`render.yaml`)

### Email and External Services

- SendGrid SDK (`sendgrid`) for transactional email

### Quality and Testing Tooling

- Black (formatting)
- isort (import ordering)
- Ruff (linting)
- Bandit (security linting in CI)
- Django test framework + Coverage.py


## How to Run Tests

### Run full test suite

```bash
python manage.py test --verbosity=1
```

### Run a specific test module

```bash
python manage.py test users.tests.test_api
```

### Run with coverage

```bash
coverage run --source='.' manage.py test --verbosity=2
coverage report --show-missing
coverage html
```

### Pre-push validation (same checks run in local hooks/CI)

```bash
black --check .
isort --check-only --profile black .
ruff check . --exclude=venv,migrations
python manage.py check
python manage.py makemigrations --check --dry-run --no-input
python manage.py test --verbosity=1
```

## Key Technical Decisions

1. DRF global secure defaults
- `DEFAULT_PERMISSION_CLASSES` set to authenticated by default
- Public endpoints explicitly opt-in via dedicated permission classes

2. JWT with secure token lifecycle
- Access and refresh token strategy with refresh rotation
- Blacklist support enabled for rotated refresh tokens

3. Scoped throttling for sensitive endpoints
- Authentication and password reset endpoints use scoped throttles
- Additional anti-enumeration response strategy for password reset request

4. DTO-style serializers
- Read and write serializers separated where appropriate
- Status update endpoint uses dedicated input serializer

5. Service-based status transitions
- Itinerary status transitions enforced in a dedicated service and domain rules
- Prevents rule duplication across serializers/views

6. Compatibility-first refactor strategy
- Legacy import paths retained through compatibility exports during layering migration

## Enterprise Ops and Governance

### OpenAPI governance

- Schema generation powered by DRF Spectacular.
- Public docs are exposed through Swagger UI and ReDoc.
- Endpoint changes should be reviewed with schema updates in PRs.

### Structured logging and correlation IDs

- Correlation IDs are handled via middleware (`X-Request-ID`).
- Every response includes `X-Request-ID`.
- Logs include `request_id` for traceability across API and background operations.

### Architecture governance docs

- Detailed architecture governance is documented in:
  - `docs/ARCHITECTURE.md`
- It covers:
  - module boundaries
  - auth model
  - extension points for adding new domains and cross-cutting concerns

## Security

Implemented security controls include:

- JWT authentication for API access
- Authenticated-by-default API permissions
- Dedicated public permissions for allowed anonymous endpoints
- Scoped rate limiting for login, token refresh, register, and password reset flows
- Password validation via Django validators
- Password reset token model with expiration/used checks
- Anti-enumeration responses for password reset requests
- CORS/CSRF environment-aware configuration

Production recommendations:

- Use a strong `SECRET_KEY` and rotate secrets securely
- Keep `DEBUG=False` in production
- Restrict `ALLOWED_HOSTS` and trusted origins to known domains
- Use managed PostgreSQL and TLS everywhere

## Code Quality

Tools in use:

- Black for formatting
- isort for import ordering
- Ruff for linting
- Django system checks and migration drift checks
- Extensive unit/integration tests (`users`, `itineraries`, `config`)

Pre-commit configuration (`.pre-commit-config.yaml`) enforces these checks, including pre-push gate hooks.

## CI Pipeline and Git Practices

### GitHub Actions pipeline

Workflow file: `.github/workflows/main.yml`

CI jobs include:
- Formatting check (Black)
- Import sorting check (isort)
- Linting (Ruff)
- Security linting (Bandit)
- Django checks and migration consistency
- Full test run with coverage threshold enforcement (PostgreSQL service in CI)
- Coverage artifact upload

### Git practices

Recommended workflow:

1. Create feature branch from `develop` or `main`
2. Commit small, focused changes
3. Run local pre-push checks before pushing
4. Open PR with clear summary and test evidence
5. Ensure CI passes before merge

Example local push-safe workflow:

```bash
git checkout -b feat/some-change
# implement change
python manage.py test --verbosity=1
git add .
git commit -m "feat: implement ..."
git push origin feat/some-change
```

This repository is configured to encourage secure, maintainable, and enterprise-ready delivery.
