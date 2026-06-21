"""Seed demo users for each role."""

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config import get_settings
from app.db.mongodb import init_db
from app.models.user import User, Role
from app.core.security import hash_password


DEMO_USERS = [
    {"email": "admin@company.com", "password": "admin123", "full_name": "Admin User", "role": Role.ADMIN, "departments": []},
    {"email": "alice@company.com", "password": "employee123", "full_name": "Alice Johnson", "role": Role.EMPLOYEE, "departments": []},
    {"email": "hr@company.com", "password": "hr123", "full_name": "Bob Smith", "role": Role.HR, "departments": ["hr"]},
    {"email": "finance@company.com", "password": "finance123", "full_name": "Carol Davis", "role": Role.FINANCE, "departments": ["finance"]},
    {"email": "marketing@company.com", "password": "marketing123", "full_name": "David Wilson", "role": Role.MARKETING, "departments": ["marketing"]},
    {"email": "engineer@company.com", "password": "engineer123", "full_name": "Eve Martinez", "role": Role.ENGINEERING, "departments": ["engineering"]},
    {"email": "exec@company.com", "password": "exec123", "full_name": "Frank Brown", "role": Role.EXECUTIVE, "departments": []},
]


async def seed_users():
    """Create demo users in the database."""
    settings = get_settings()
    client = await init_db(settings)

    print("Seeding demo users...")
    for user_data in DEMO_USERS:
        existing = await User.find_one(User.email == user_data["email"])
        if existing:
            print(f"  User {user_data['email']} already exists, skipping.")
            continue

        user = User(
            email=user_data["email"],
            hashed_password=hash_password(user_data["password"]),
            full_name=user_data["full_name"],
            role=user_data["role"],
            departments=user_data["departments"],
        )
        await user.insert()
        print(f"  Created user: {user_data['email']} ({user_data['role'].value})")

    print(f"\nDemo users seeded successfully!")
    print("\nLogin credentials:")
    for u in DEMO_USERS:
        print(f"  {u['email']} / {u['password']} ({u['role'].value})")

    client.close()


if __name__ == "__main__":
    asyncio.run(seed_users())
