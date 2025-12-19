feature/
├── main.py                # Feature initialization
├── api/                   # Versioning and routing aggregation
│   └── api_v1/
│       └── api.py         # Includes all domain routers
├── core/                  # Global config, security/JWT
├── domains/               # Domain-specific logic
│   ├── items/
│   │   ├── router.py      # Endpoints
│   │   ├── service.py     # "CRUD" and logic
│   │   ├── models.py      # SQLAlchemy/Tortoise models
│   │   └── schemas.py     # Pydantic models
│   └── users/
│       └── ...
└── db/                    # Session management and migrations