from fastapi import FastAPI
from app.routes import user as user_routes
from app.models.user import Base
from app.db.session import engine

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Role base user management")
app.include_router(user_routes.router, prefix="/users", tags=["users"])