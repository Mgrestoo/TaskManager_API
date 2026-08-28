import asyncio
import sys

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import URL
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app import app
from auth import get_current_user
from database import Base, get_db
from models import User

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


TEST_DATABASE_URL = URL.create(
    "postgresql+asyncpg",
    username="task_manager_app",
    password="Restoo@066",
    port=5432,
    host="localhost",
    database="task_manager_test",
)

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    poolclass=NullPool,
)

TestSessionLocal = async_sessionmaker(
    bind=test_engine,
    expire_on_commit=False,
)


@pytest.fixture(scope="session", autouse=True)
async def setup_database():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await test_engine.dispose()


@pytest.fixture
async def db():
    connection = await test_engine.connect()
    transaction = await connection.begin()

    db = TestSessionLocal(
        bind=connection,
        join_transaction_mode="create_savepoint",
    )

    try:
        yield db
    finally:
        await db.close()
        await transaction.rollback()
        await connection.close()


@pytest.fixture
async def client(db):
    async def override_db():
        yield db

    app.dependency_overrides[get_db] = override_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()


@pytest.fixture
async def test_user(db):
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password="test-hash",
    )

    db.add(user)
    await db.commit()
    await db.refresh(user)

    return user


@pytest.fixture
async def authenticated_client(client, test_user):
    def override_current_user():
        return test_user

    app.dependency_overrides[get_current_user] = override_current_user

    try:
        yield client
    finally:
        app.dependency_overrides.pop(get_current_user, None)
