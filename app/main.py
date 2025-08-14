from fastapi import FastAPI
from app.routes import user as user_routes
from app.routes import auth as auth_routes

tags_metadata = [
    {
        "name": "Auth",
        "description": "Login, refresh, and logout. Issues access/refresh tokens and cookies.",
    },
    {
        "name": "Users",
        "description": "User management with pagination, filtering, and RBAC.",
    },
]

app = FastAPI(
    title="Role base user management",
    description="""
A secure User & Role Management API built with FastAPI.

**Key Features**
- JWT auth with access/refresh tokens
- Auto-refresh via HttpOnly cookies
- Role-based access control (admin/user)
- CRUD users with pagination, filtering, sorting
- Fully tested with pytest + coverage
""",
    version="0.3.0",
    openapi_tags=tags_metadata,
    contact={
        "name": "API Support",
        "email": "support@example.com",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
    docs_url="/docs",     # Swagger
    redoc_url="/redoc",   # ReDoc
)

app.include_router(auth_routes.router, prefix="/auth", tags=["Auth"])
app.include_router(user_routes.router, prefix="/users", tags=["Users"])
