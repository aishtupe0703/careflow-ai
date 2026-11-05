
import pytest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session

from app.database import Base, get_db, DATABASE_URL
from app.main import app

from app.classifier import classify_ticket
from app.main import get_ticket_classifier

# Construct a URL pointing ONLY to the test database.
test_url = make_url(DATABASE_URL).set(
    database="careflow_test_db"
)

if (
    test_url.database != "careflow_test_db"
    or test_url.host not in ("localhost", "127.0.0.1")
    or test_url.port != 5432
):
    raise RuntimeError(
        "Tests must use the local careflow_test_db database"
    )

test_engine = create_engine(
    test_url,
    pool_pre_ping=True,
)


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    # Create missing tables in the test database.
    # Import models so SQLAlchemy knows about them.
    from app.models import Ticket

    Base.metadata.create_all(bind=test_engine)

    yield

    test_engine.dispose()


@pytest.fixture
def client(setup_test_database):
    # Start a transaction before the test.
    connection = test_engine.connect()
    transaction = connection.begin()

    # API commits use savepoints within this transaction.
    db = Session(
        bind=connection,
        join_transaction_mode="create_savepoint",
        expire_on_commit=False,
    )

    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_ticket_classifier] = (
        lambda: classify_ticket
    )

    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()
        db.close()

        # Undo every database change made by the test.
        transaction.rollback()
        connection.close()
