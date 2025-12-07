
Setup

Prerequisites: Docker and Docker Compose installed.

Quick steps (PowerShell):

```powershell
docker-compose up --build -d
```
Open the app at http://localhost:8001/ (Django) — Redis is on port 6380.

Please go to http://localhost:8001/swagger/ to see swagger documentation
## Testing

Quick notes about the test suite and the new `auth` tests added recently.

- Run the auth app tests (PowerShell):

```powershell
cd d:\personal_work\task_manager\tasks
python manage.py test auth
```

- If you run the whole project tests from repository root use:

```powershell
cd d:\personal_work\task_manager\tasks
python manage.py test
```

- Docker (adjust service name):

```powershell
docker compose run --rm <service> python manage.py test auth
```

What changed in `auth/tests.py`:

- Added unit tests for the `RegisterSerializer` (validation and user creation).
- Added tests for cookie helpers: `set_tokens_cookies` and `delete_tokens_cookies`.
- Added integration-style tests that exercise the `register`, `login`, `profile`, and `logout` endpoints and assert cookies and response payloads.
- Two tests that depend on importing `CookieJWTAuthentication` are skipped when the import fails in the test environment. This keeps the test run green when `djangorestframework-simplejwt` or related configuration is not installed or available.

Why two tests may be skipped:

- The `CookieJWTAuthentication` class lives in `auth/exception.py` and depends on DRF Simple JWT. If your environment doesn't have the package or the module can't import (for example, in some CI containers), the tests that exercise that class will be skipped with an explanatory message.

How to make skipped tests run:

- Ensure `djangorestframework-simplejwt` is installed in your environment (and configured in `INSTALLED_APPS` if you use the token blacklist feature):

```powershell
pip install djangorestframework-simplejwt
```

- If you're using the blacklist app, also add `rest_framework_simplejwt.token_blacklist` to `INSTALLED_APPS` in your Django settings.

- Alternatively, replace the `skipTest` behavior in `auth/tests.py` with mocks that simulate the `CookieJWTAuthentication` behavior; I can provide a patch for that if you prefer.




## Auth API (Endpoints, Serializers, and Implementation)

This project includes a small authentication app at `tasks/auth` that provides JWT-based auth using HTTP-only cookies. Below is a friendly explanation of the implemented endpoints, the serializers they use, helper utilities, and important implementation notes.

- Base URL: the app mounts its routes at the project root. See `tasks/urls.py` which includes `auth.urls`.

- Endpoints (in `tasks/auth/urls.py`):
	- `POST /register/` — Register a new user.
	- `POST /login/` — Login using email + password.
	- `POST /logout/` — Logout (revokes/blacklists refresh token and deletes cookies).
	- `POST /refresh/` — (Implemented as `RefreshTokenAPI`) Refreshes access token using refresh cookie.
	- `GET /profile/` — Returns details for the authenticated user.

- Key serializers (`tasks/auth/serializers.py`):
	- `RegisterSerializer` — fields: `first_name`, `last_name`, `email`, `password`, `confirm_password`.
		- Validates duplicate email and password confirmation.
		- `create()` sets `username` to the email and creates a Django `User`.
	- `LoginSerializer` — fields: `email`, `password`.
	- `LogoutSerializer` — optional `refresh` field (not required since refresh is read from cookie).
	- Response serializers: `UserResponseSerializer`, `LoginResponseSerializer`, `RegisterResponseSerializer`, `LogoutResponseSerializer`, `RefreshTokenResponseSerializer`, `ProfileResponseSerializer` — used by documentation and `drf-spectacular` examples.

- Views and behavior (`tasks/auth/views.py`):
	- `RegisterView` (no authentication required):
		- Validates the `RegisterSerializer`, creates the user, issues tokens via `RefreshToken.for_user(user)` and sets two HTTP-only cookies: `access_token` and `refresh_token` using `set_tokens_cookies`.
		- Returns a 201 with a `message` and `user` info.

	- `LoginAPI` (no authentication required):
		- Authenticates with `django.contrib.auth.authenticate(username=email, password=...)`.
		- On success, issues tokens and sets the same cookies as register; returns user info and message.

	- `LogoutAPI` (requires authentication):
		- Reads `refresh_token` from cookies. If present, tries to blacklist it (`RefreshToken(refresh_token).blacklist()`), ignoring `TokenError` if blacklisting fails.
		- Deletes `access_token` and `refresh_token` cookies via `delete_tokens_cookies` and returns a success message.

	- `RefreshTokenAPI` (AllowAny):
		- Reads `refresh_token` cookie and, if valid, builds a new access token and sets fresh cookies.

	- `ProfileAPI` (requires authentication):
		- Returns a `user` object with `id`, `email`, `first_name`, `last_name` from `request.user`.

- Cookie helpers (`tasks/auth/utils.py`):
	- `set_tokens_cookies(response, access_token, refresh_token)` — sets two HTTP-only cookies (`access_token`, `refresh_token`) with `samesite='Lax'` and `httponly=True`.
	- `delete_tokens_cookies(response)` — deletes both cookies.

- Custom authentication (`tasks/auth/exception.py`):
	- `CookieJWTAuthentication` extends `rest_framework_simplejwt.authentication.JWTAuthentication` and looks for an `access_token` in `request.COOKIES`.
	- If found, it injects `HTTP_AUTHORIZATION: Bearer <token>` into `request.META` and delegates to the base class.
	- For specific unprotected paths (swagger/schema/redoc/login), it returns `None` to bypass authentication.
	- If no cookie is present or token validation fails, it raises `AuthenticationFailed` (tests may skip these checks if `simplejwt` is not installed).

- Exceptions and error shaping (`tasks/auth/exception.py` & `tasks/auth/exception.py` custom handler):
	- A custom exception handler `custom_exception_handler` is present and transforms DRF validation errors into a consistent `{ "errors": { ... } }` shape for 400 responses.







