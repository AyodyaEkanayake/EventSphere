
import pytest

from datetime import datetime, timedelta, timezone

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from fastapi.testclient import TestClient

from app.main import app
from app.database.connection import Base, get_db
from app.database.models import (
    User,
    Venue,
    Event,
    TicketCategory,
    WaitlistEntry
)
from app.services.security import hash_password, create_access_token


# Separate temporary test database
TEST_DATABASE_URL = "sqlite://"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_engine
)


# Create test database for each test
@pytest.fixture
def db_session():

    Base.metadata.create_all(bind=test_engine)

    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=test_engine)


# Override FastAPI database dependency
@pytest.fixture
def client(db_session):

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    test_client = TestClient(app)

    yield test_client

    app.dependency_overrides.clear()


# Create test users, event and ticket category
@pytest.fixture
def test_data(db_session):

    attendee = User(
        full_name="Test Attendee",
        email="attendee@test.com",
        password_hash=hash_password("Test12345"),
        role="attendee",
        is_active=True
    )

    admin = User(
        full_name="Test Admin",
        email="admin@test.com",
        password_hash=hash_password("Test12345"),
        role="admin",
        is_active=True
    )

    staff = User(
        full_name="Test Gate Staff",
        email="staff@test.com",
        password_hash=hash_password("Test12345"),
        role="gate_staff",
        is_active=True
    )

    db_session.add_all([attendee, admin, staff])
    db_session.commit()

    db_session.refresh(attendee)
    db_session.refresh(admin)
    db_session.refresh(staff)

    venue = Venue(
        name="Test Venue",
        location="Vavuniya",
        capacity=500,
        description="Test venue",
        hourly_hire_rate=1000,
        private_hire_available=True
    )

    db_session.add(venue)
    db_session.commit()
    db_session.refresh(venue)

    event = Event(
        title="Test Event",
        category="University",
        venue_id=venue.id,
        start_time=datetime.now(timezone.utc) + timedelta(days=10),
        end_time=datetime.now(timezone.utc) + timedelta(days=10, hours=4),
        description="Test event",
        status="published"
    )

    db_session.add(event)
    db_session.commit()
    db_session.refresh(event)

    category = TicketCategory(
        event_id=event.id,
        name="Standard",
        price=1000,
        total_quantity=100,
        sold_quantity=0
    )

    db_session.add(category)
    db_session.commit()
    db_session.refresh(category)

    waitlist = WaitlistEntry(
        user_id=attendee.id,
        event_id=event.id,
        ticket_category_id=category.id,
        quantity=1,
        status="waiting"
    )

    db_session.add(waitlist)
    db_session.commit()

    return {
        "attendee": attendee,
        "admin": admin,
        "staff": staff,
        "venue": venue,
        "event": event,
        "category": category,
        "waitlist": waitlist
    }


# Generate access token for each role
@pytest.fixture
def auth_headers(test_data):

    def create_headers(user):

        token = create_access_token({
            "sub": str(user.id)
        })

        return {
            "Authorization": f"Bearer {token}"
        }

    return create_headers
