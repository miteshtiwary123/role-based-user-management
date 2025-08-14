import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.db.session import SessionLocal
from app.models.user import Base, User, RoleEnum
from app.core.security import hash_password
from app.core.deps import get_db

# use an in-memory sqlite db for tests
TEST_DB_URL = "sqlite+pysqlite:///:memory:"
engine = create_engine(TEST_DB_URL,  connect_args={"check_same_thread": False})
TestinSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session", autouse=True)
def create_test_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

def override_get_db():
    db = TestinSessionLocal()
    try:
        yield db
    finally:
        db.close()

# Override app dependency
app.dependency_overrides[get_db] = lambda: TestinSessionLocal()

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def db():
    session = TestinSessionLocal()
    try:
        yield session
    finally:
        session.close()

@pytest.fixture
def seed_users(db):
    db.query(User).delete()
    db.commit()
    
    admin = User(
        name="Admin",
        email="admin@example.com",
        hashed_password=hash_password("adminpass"),
        role=RoleEnum.admin
    )
    user = User(
        name="Bob",
        email="bob@example.com",
        hashed_password=hash_password("bobpass"),
        role=RoleEnum.user
    )
    db.add_all([admin, user])
    db.commit()
    db.refresh(admin)
    db.refresh(user)
    return {"admin": admin, "user": user}

@pytest.fixture
def admin_tokens(client, seed_users):
    # login to obtain tokens
    res = client.post("/auth/login", data={"username": "admin@example.com", "password": "adminpass"})
    assert res.status_code == 200
    data = res.json()
    return data

@pytest.fixture
def user_tokens(client, seed_users):
    res = client.post("/auth/login", data={"username": "bob@example.com", "password": "bobpass"})
    assert res.status_code == 200
    return res.json()