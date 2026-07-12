<div align="center">

# ⚓ KeelHQ

### The source of truth for websites built by AI.

[![Version](https://img.shields.io/badge/version-v0.1.0-beta-blue)]()
[![Python](https://img.shields.io/badge/python-3.12-blue)]()

</div>

---

## Why KeelHQ?

Building websites with AI has never been easier.

Maintaining them has never been harder.

AI can generate beautiful frontends in minutes, but it doesn't solve problems like:

- Content management
- Media storage
- Forms
- API integrations
- Authentication
- Structured data
- Versioning
- Long-term maintenance

Every regeneration risks breaking the backend or losing data.

KeelHQ separates **presentation** from **application state**, giving AI complete freedom to redesign the frontend while keeping the underlying data and infrastructure stable.

---

## What is KeelHQ?

KeelHQ is a backend platform designed for AI-generated websites.

It provides a stable API and data layer that AI-generated frontends can connect to, making regeneration safe and repeatable.

Instead of treating a website as static code, KeelHQ treats it as a collection of structured resources:

- Sites
- Content
- Media
- Forms
- Integrations
- APIs
- AI-editable components

---

## Core Principles

- ⚓ Stable backend for rapidly changing frontends
- 🤖 AI-first architecture
- 🔌 API & MCP driven
- 🧩 Headless by default
- 🔒 Secure authentication
- 📦 Structured content management
- 🚀 Built for continuous regeneration

---

## Current Features

- ✅ Local user registration
- ✅ Authentication architecture
- ✅ Repository Pattern
- ✅ Unit of Work
- ✅ Service Layer
- ✅ SQLModel + PostgreSQL
- ✅ FastAPI REST API
- 🚧 Login
- 🚧 Site Management
- 🚧 Content Management
- 🚧 Media Library
- 🚧 Forms
- 🚧 MCP Integration

---

## Technology Stack

| Layer | Technology |
|--------|------------|
| Language | Python 3.12 |
| API | FastAPI |
| Database | PostgreSQL |
| ORM | SQLModel |
| Validation | Pydantic v2 |
| Authentication | JWT |
| Migrations | Alembic |
| Package Manager | uv |

---

## Architecture

```text
Browser / AI Website
            │
            ▼
       REST API / MCP
            │
            ▼
      Application Services
            │
            ▼
       Unit of Work
            │
            ▼
      Repository Layer
            │
            ▼
 PostgreSQL Database
```

---

## Project Structure

```text
keelhq/

├── api/
├── core/
├── db/
├── exceptions/
├── models/
├── repositories/
├── schemas/
├── services/
└── utils/
```

---

## Running locally

Clone the repository

```bash
git clone https://github.com/iamu985/keelhq.git
cd keelhq
```

Install dependencies

```bash
uv sync
```

Run migrations

```bash
uv run alembic upgrade head
```

Start the development server

```bash
uv run uvicorn server:app --reload
```

Open

```
http://localhost:8000/docs
```

---

## Roadmap

### v0.1-beta

- [x] Backend architecture
- [x] Registration
- [ ] Login
- [ ] JWT Authentication
- [ ] Dashboard
- [ ] Site Management
- [ ] Content API
- [ ] Media Library
- [ ] Forms
- [ ] MCP Support

---

## Contributing

Contributions, ideas, discussions, and bug reports are always welcome.

Please open an issue before working on larger features so we can discuss the implementation.

