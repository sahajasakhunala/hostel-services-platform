# HostelFlow Application Layer Architecture Guide

## 1. Application Layer Design Pattern

HostelFlow implements a strict **layered architecture** to separate client communication, business control flow, data manipulation, and database driver management.

```text
    Flask Route (Controller)
              │
              ▼
    Business Service (Layer)
              │
              ▼
    Data Repository (Layer)
              │
              ▼
    PyMySQL Driver (Connection)
```

### Layer Descriptions

1. **Flask Route (Controller)**: Handles HTTP requests, parses query parameters or JSON payloads, validates formats (using validation helpers), invokes the appropriate service method, and returns structured JSON responses.
2. **Business Service (Layer)**: Contains core business logic rules. Coordinates transactions and prevents database operations if validation policies fail.
3. **Data Repository (Layer)**: Contains raw parameterized SQL execution logic. Interfaces with PyMySQL, ensuring database queries are fully isolated from higher business service layers.
4. **PyMySQL Driver**: Executes SQL statements within a transaction boundary, returning dictionary cursor rows to the repository layer.

---

## 2. Flask Application Factory & Session Lifecycle

### Application Factory Pattern (`create_app()`)
HostelFlow utilizes Flask's App Factory pattern. The application is initialized dynamically using specific configuration configurations (`DevelopmentConfig`, `TestingConfig`, `ProductionConfig`). During startup, `validate_config()` checks the loaded configurations and raises an exception if security or environment invariants are violated.

### Session Lifecycle & Request Context Management
- **Database Connection Cleanup**: Connections are bound to the Flask application context (`g.db_conn`). They are opened on demand and automatically closed at the end of the request lifecycle using the `@app.teardown_appcontext` callback.
- **Request Correlation**: Correlation IDs (`request_id`) are generated in `@app.before_request`, stored in `g.request_id`, and attached to the outgoing HTTP headers via `X-Request-ID` in `@app.after_request`.
