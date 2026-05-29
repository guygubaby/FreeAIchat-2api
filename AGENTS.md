# Repository Guidelines

## Project Structure & Module Organization

This repository is a small FastAPI proxy that exposes OpenAI-compatible endpoints for `chatgptfree.ai`.

- `main.py` defines the FastAPI app, authentication dependency, and `/v1/*` routes.
- `app/core/config.py` owns environment-backed settings and model mappings.
- `app/providers/` contains provider abstractions and the FreeAIchat implementation.
- `Dockerfile`, `docker-compose.yml`, and `nginx.conf` define the containerized runtime.
- `.env.example` documents required local configuration. Keep real `.env` files untracked.

There is no committed `tests/` directory yet. Add new tests under `tests/` when changing request handling, provider parsing, authentication, or configuration behavior.

## Build, Test, and Development Commands

Install Python dependencies locally:

```bash
python -m pip install -r requirements.txt
```

Run the documented Docker deployment:

```bash
docker-compose up -d --build
docker-compose logs -f app
```

The service is exposed through Nginx on `${NGINX_PORT:-8080}`. For API checks, use the configured `API_MASTER_KEY`:

```bash
curl -H "Authorization: Bearer your-secret-key" http://localhost:8080/v1/models
```

For agent work in this legacy project, do not run lint, typecheck, build, or dev-server commands unless the maintainer explicitly asks.

## Coding Style & Naming Conventions

Use Python 3.10-compatible code. Follow the existing style: 4-space indentation, typed function signatures where useful, clear FastAPI exceptions, and module-level loggers via `logging.getLogger(__name__)`. Keep provider-specific network logic in `app/providers/`; keep environment and model-map changes in `app/core/config.py`.

Prefer explicit names such as `conversation_id`, `request_data`, and `previous_response_id`. Keep public API response shapes OpenAI-compatible unless the change is intentional and documented.

## Testing Guidelines

When adding tests, use `pytest` with `httpx`/FastAPI test clients. Name files `tests/test_*.py` and test functions `test_*`. Cover authentication failures, invalid models, conversation lifecycle, streaming parsing, and `.env` configuration edge cases. Mock upstream `chatgptfree.ai` calls; tests must not require real cookies, nonces, or network access.

## Commit & Pull Request Guidelines

Recent commits use short imperative messages, for example `Create .env.example` and `Update README.md`. Keep commits focused and describe the user-visible change.

Pull requests should include a concise summary, affected endpoints or config keys, manual verification steps, and screenshots or logs only when they clarify runtime behavior. Link related issues when available. Never include real cookies, `AJAX_NONCE`, `SESSION_ID`, `POST_ID`, or `API_MASTER_KEY` values.

## Security & Configuration Tips

Treat `.env` values as secrets. If a cookie contains `$`, follow the README guidance and escape it as `$$` for Docker Compose. Avoid logging full credentials; redact tokens in warnings and errors.
