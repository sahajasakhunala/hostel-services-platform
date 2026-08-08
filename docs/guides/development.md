# HostelFlow Developer & Contribution Guide

## 1. Directory Structure Layout

```text
hostel-services-platform/
├── app/
│   ├── routes/          # Flask HTTP controllers & Blueprints
│   ├── services/        # Business logic controllers
│   ├── repositories/    # Raw parameterized SQL repositories
│   ├── db/              # Connection pooling & teardown context
│   ├── utils/           # Validation, logging, config validation
│   └── templates/       # HTML view templates
│
├── database/            # Authoritative SQL schema files
│   ├── schema/          # DDL tables & constraints
│   ├── views/           # SQL views
│   ├── procedures/      # Transactional stored procedures
│   ├── triggers/        # Relational integrity triggers
│   └── seed/            # Setup seed scripts
│
├── tests/               # Pytest suite files
└── docs/                # Architecture, runbooks, and phase reports
```

---

## 2. Layer Integration Recipe

To add a new vertical business feature (e.g. Visitors, Billing):

1. **Database Layer**: Write DDL schema updates and database objects (views, stored procedures, triggers) in their respective `database/` folders.
2. **Repository Layer**: Create a PyMySQL-based repository under `app/repositories/` executing parameterized queries.
3. **Service Layer**: Write a business logic service under `app/services/` to coordinate actions and validate operations.
4. **Route Controller**: Add HTTP endpoint logic under `app/routes/`, applying relevant security, authentication, and validation decorators.
5. **UI Layer**: Update views and templates under `app/templates/` and `app/static/`.

---

## 3. Log Observability & Formatting Conventions

Use standard log helper functions when writing new endpoints:
- `log_app_event('EVENT_NAME', {'metadata': 'value'})`: Application lifecycle changes.
- `log_security_event('EVENT_NAME', {'reason': 'value'})`: Authentication/privilege events.
- `log_exception('ERROR_EVENT', exc_info=True)`: Stack traces logged to `error.log`.
*Correlation IDs are automatically attached under the hood.*
