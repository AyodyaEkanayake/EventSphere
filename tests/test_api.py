
def test_home_page(client):
    response = client.get("/", follow_redirects=False)

    assert response.status_code == 307
    assert response.headers["location"] == "/login"


def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_user_registration(client):
    response = client.post(
        "/auth/register",
        json={
            "full_name": "New Attendee",
            "email": "newattendee@test.com",
            "password": "Test12345"
        }
    )

    assert response.status_code == 200
    assert response.json()["email"] == "newattendee@test.com"


def test_duplicate_registration(client):
    user_data = {
        "full_name": "New Attendee",
        "email": "duplicate@test.com",
        "password": "Test12345"
    }

    first = client.post("/auth/register", json=user_data)
    second = client.post("/auth/register", json=user_data)

    assert first.status_code == 200
    assert second.status_code == 409


def test_successful_login(client, test_data):
    response = client.post(
        "/auth/login",
        data={
            "username": "attendee@test.com",
            "password": "Test12345"
        }
    )

    assert response.status_code == 200
    assert "access_token" in response.json()


def test_invalid_login(client):
    response = client.post(
        "/auth/login",
        data={
            "username": "wrong@test.com",
            "password": "WrongPassword"
        }
    )

    assert response.status_code == 401


def test_get_current_user(client, test_data, auth_headers):
    headers = auth_headers(test_data["attendee"])

    response = client.get("/auth/me", headers=headers)

    assert response.status_code == 200
    assert response.json()["email"] == "attendee@test.com"


def test_admin_dashboard_access(client, test_data, auth_headers):
    headers = auth_headers(test_data["admin"])

    response = client.get("/dashboard/", headers=headers)

    assert response.status_code == 200
    assert "summary" in response.json()


def test_attendee_cannot_access_admin_dashboard(
    client, test_data, auth_headers
):
    headers = auth_headers(test_data["attendee"])

    response = client.get("/dashboard/", headers=headers)

    assert response.status_code == 403


def test_attendee_can_view_own_waitlist(
    client, test_data, auth_headers
):
    headers = auth_headers(test_data["attendee"])

    response = client.get(
        "/waitlist/my-entries",
        headers=headers
    )

    assert response.status_code == 200


def test_gate_staff_cannot_view_all_waitlist(
    client, test_data, auth_headers
):
    headers = auth_headers(test_data["staff"])

    response = client.get(
        "/waitlist/",
        headers=headers
    )

    assert response.status_code == 403


from app.database.models import Booking, Ticket


def test_overbooking_is_prevented(client, db_session, test_data, auth_headers):
    attendee = test_data["attendee"]
    event = test_data["event"]
    category = test_data["category"]

    # Only 2 tickets are available
    category.total_quantity = 2
    category.sold_quantity = 0
    db_session.commit()

    response = client.post(
        "/bookings/",
        json={
            "event_id": event.id,
            "ticket_category_id": category.id,
            "quantity": 3
        },
        headers=auth_headers(attendee)
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Not enough tickets available"

    db_session.refresh(category)
    assert category.sold_quantity == 0


def test_double_check_in_is_prevented(
    client, db_session, test_data, auth_headers
):
    attendee = test_data["attendee"]
    staff = test_data["staff"]
    event = test_data["event"]

    booking = Booking(
        user_id=attendee.id,
        event_id=event.id,
        ticket_category_id=test_data["category"].id,
        quantity=1,
        total_amount=1000,
        status="confirmed",
        payment_reference="TEST-PAYMENT-001"
    )

    db_session.add(booking)
    db_session.commit()
    db_session.refresh(booking)

    ticket = Ticket(
        booking_id=booking.id,
        event_id=event.id,
        ticket_code="TEST-QR-DOUBLE-CHECKIN",
        status="valid"
    )

    db_session.add(ticket)
    db_session.commit()

    headers = auth_headers(staff)

    # First scan - should succeed
    first_response = client.post(
        f"/tickets/scan/{event.id}/TEST-QR-DOUBLE-CHECKIN",
        headers=headers
    )

    assert first_response.status_code == 200
    assert first_response.json()["status"] == "checked_in"

    # Second scan - should be rejected
    second_response = client.post(
        f"/tickets/scan/{event.id}/TEST-QR-DOUBLE-CHECKIN",
        headers=headers
    )

    assert second_response.status_code == 400
    assert second_response.json()["detail"] == "Ticket already checked in"