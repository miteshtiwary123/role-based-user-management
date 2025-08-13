from fastapi import FastAPI
from app.routes import user as user_routes
from app.routes import auth as auth_routes

app = FastAPI(title="Role base user management")

app.include_router(auth_routes.router, prefix="/auth", tags=["Auth"])
app.include_router(user_routes.router, prefix="/users", tags=["Users"])
