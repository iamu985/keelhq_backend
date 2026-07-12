# Reusable Exception Handling System

Implement a reusable exception handling layer that maps KeelHQ domain exceptions to consistent JSON error responses, starting with registration uniqueness errors, while leaving the hierarchy open for future exceptions without per-exception handler edits.

## Decisions confirmed

- Error response body: `{ "error": { "code": "...", "message": "..." } }`.
- HTTP status is **not** duplicated inside the body; it lives on the response line.
- Registration exceptions:
  - `UsernameAlreadyExistsError` → `409 Conflict`
  - `EmailAlreadyExistsError` → `409 Conflict`
- Unmapped `DomainError` / `IdentityError` → `400 Bad Request`.
- Unexpected non-domain exceptions → `500 Internal Server Error`.
- Service layer remains HTTP-agnostic; HTTP metadata is attached to exception classes and consumed by a single global handler.

## Files to create or modify

| File | Action |
|---|---|
| `app/exceptions/__init__.py` | Add `status_code`, `error_code`, `default_message` class attributes to `KeelException` and set defaults on `DomainError`, `InfrastructureError`, `ApplicationError` |
| `app/exceptions/identity/base.py` | Set `IdentityError` defaults (`400`) so identity errors have a sensible fallback |
| `app/exceptions/identity/registration_exceptions.py` | Add `RegistrationError` base; make `UsernameAlreadyExistsError` and `EmailAlreadyExistsError` set `status_code=409` and explicit `error_code` |
| `app/api/errors.py` (new) | Build the JSON response, implement `KeelException` and catch-all `Exception` handlers, export `register_exception_handlers` |
| `server.py` | Call `register_exception_handlers(app)` after router inclusion |
| `tests/core/test_exception_handlers.py` (new) | Test 409 mapping for registration errors, 400 fallback for unmapped `DomainError`, and 500 catch-all |
| `app/api/v1/identity/registration_routes.py` | No route-level try/except needed; handler converts domain errors automatically |

## Implementation steps

### 1. Attach HTTP metadata to the exception hierarchy

In `app/exceptions/__init__.py`, make `KeelException` carry declarative HTTP metadata:

```python
class KeelException(Exception):
    status_code: int = 500
    error_code: str = "INTERNAL_SERVER_ERROR"
    default_message: str = "An unexpected error occurred."

    def __init__(self, message: str | None = None) -> None:
        super().__init__(message or self.default_message)


class DomainError(KeelException):
    status_code: int = 400
    error_code: str = "DOMAIN_ERROR"
    default_message: str = "Business rule violation."


class InfrastructureError(KeelException):
    status_code: int = 500
    error_code: str = "INFRASTRUCTURE_ERROR"
    default_message: str = "Infrastructure error."


class ApplicationError(KeelException):
    status_code: int = 400
    error_code: str = "APPLICATION_ERROR"
    default_message: str = "Application error."
```

### 2. Update identity and registration exceptions

In `app/exceptions/identity/base.py`:

```python
class IdentityError(DomainError):
    status_code: int = 400
    error_code: str = "IDENTITY_ERROR"
    default_message: str = "Identity operation failed."
```

In `app/exceptions/identity/registration_exceptions.py`:

```python
class RegistrationError(IdentityError):
    status_code: int = 400
    error_code: str = "REGISTRATION_ERROR"
    default_message: str = "Registration failed."


class UsernameAlreadyExistsError(RegistrationError):
    status_code: int = 409
    error_code: str = "USERNAME_ALREADY_EXISTS"
    default_message: str = "Username already exists."


class EmailAlreadyExistsError(RegistrationError):
    status_code: int = 409
    error_code: str = "EMAIL_ALREADY_EXISTS"
    default_message: str = "Email already exists."
```

### 3. Build the response and handlers

In `app/api/errors.py`:

```python
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.core.logger import logger
from app.exceptions import KeelException


async def keel_exception_handler(request: Request, exc: KeelException) -> JSONResponse:
    status_code = exc.status_code
    body = {"error": {"code": exc.error_code, "message": str(exc)}}
    logger.warning(f"Domain error {exc.error_code} -> {status_code}: {exc}")
    return JSONResponse(status_code=status_code, content=body)


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled exception")
    body = {"error": {"code": "INTERNAL_SERVER_ERROR", "message": "An unexpected error occurred."}}
    return JSONResponse(status_code=500, content=body)


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(KeelException, keel_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)
```

### 4. Register handlers

In `server.py`, after including routers, call `register_exception_handlers(app)`.

### 5. Tests

Create `tests/core/test_exception_handlers.py`:

- Build a minimal FastAPI app and call `register_exception_handlers(app)`.
- Add a route that raises `UsernameAlreadyExistsError`.
  - Assert response status is `409` and JSON equals `{ "error": { "code": "USERNAME_ALREADY_EXISTS", "message": "Username already exists." } }`.
- Add a route that raises an unmapped `DomainError`.
  - Assert response status is `400` and code is `DOMAIN_ERROR`.
- Add a route that raises a generic `Exception`.
  - Assert response status is `500` and code is `INTERNAL_SERVER_ERROR`.

## Notes / risks

- Class attributes on `KeelException` couple exceptions to HTTP metadata, but only as declarative mapping data; services never import HTTP or response logic.
- Because `DomainError` defaults to `400`, future business-rule exceptions only need to define `status_code`/`error_code` if they need a different code.
- The generic `Exception` handler only catches exceptions without a more specific registered handler; FastAPI's `RequestValidationError` handler remains more specific and continues returning `422`.
- Routes stay free of try/except blocks; the global handler converts domain errors automatically.
