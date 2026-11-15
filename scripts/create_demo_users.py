
from getpass import getpass

from sqlalchemy import select

from app.database.connection import SessionLocal
from app.database.models import User
from app.services.security import hash_password


def create_demo_user(db, full_name, email, role):

    email = email.lower().strip()

    existing_user = db.scalar(
        select(User).where(User.email == email)
    )

    if existing_user:
        print(f"\n{email} already exists.")
        print(f"Existing role: {existing_user.role}")
        print("No changes were made.")
        return

    password = getpass(f"Enter password for {role}: ")
    confirm_password = getpass("Confirm password: ")

    if password != confirm_password:
        print("Passwords do not match. User was not created.")
        return

    if len(password) < 8:
        print("Password must contain at least 8 characters.")
        return

    new_user = User(
        full_name=full_name,
        email=email,
        password_hash=hash_password(password),
        role=role,
        is_active=True
    )

    db.add(new_user)
    db.commit()

    print(f"\n{role} account created successfully!")
    print(f"Email: {email}")


def main():

    db = SessionLocal()

    try:
        print("=== EventSphere Demo Account Setup ===")

        create_demo_user(
            db,
            "EventSphere Admin",
            "admin@eventsphere.com",
            "admin"
        )

        create_demo_user(
            db,
            "EventSphere Gate Staff",
            "staff@eventsphere.com",
            "gate_staff"
        )

    finally:
        db.close()


if __name__ == "__main__":
    main()
