#!/usr/bin/env python3
"""
User Account Creation Utility for RICOH POC

Usage:
    python create_user.py

The script will prompt you for username, email, and password.
"""

import getpass
import sys

from app import app, db
from auth_utils import validate_email, validate_password, validate_username
from models import User


def create_user_account(username, email, password):
    """Create a new user account"""
    with app.app_context():
        # Validate inputs
        username_valid, username_msg = validate_username(username)
        if not username_valid:
            print(f"❌ Username validation failed: {username_msg}")
            return False

        email_valid, email_msg = validate_email(email)
        if not email_valid:
            print(f"❌ Email validation failed: {email_msg}")
            return False

        password_valid, password_msg = validate_password(password)
        if not password_valid:
            print(f"❌ Password validation failed: {password_msg}")
            return False

        # Check if user already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            print(f"❌ Username '{username}' already exists")
            return False

        existing_email = User.query.filter_by(email=email).first()
        if existing_email:
            print(f"❌ Email '{email}' already exists")
            return False

        try:
            # Create new user
            user = User(username=username, email=email)
            user.set_password(password)

            db.session.add(user)
            db.session.commit()

            print("✅ User account created successfully!")
            print(f"   Username: {username}")
            print(f"   Email: {email}")
            print(f"   User ID: {user.id}")
            return True

        except Exception as e:
            db.session.rollback()
            print(f"❌ Error creating user: {str(e)}")
            return False


def prompt_for_user_details():
    """Prompt user for account details"""
    print("🤖 RICOH POC - Create User Account")
    print("=" * 40)

    # Get username
    while True:
        username = input("Enter username: ").strip()
        if not username:
            print("❌ Username cannot be empty")
            continue

        username_valid, username_msg = validate_username(username)
        if not username_valid:
            print(f"❌ {username_msg}")
            continue

        # Check if username exists
        with app.app_context():
            if User.query.filter_by(username=username).first():
                print(f"❌ Username '{username}' already exists")
                continue

        break

    # Get email
    while True:
        email = input("Enter email: ").strip()
        if not email:
            print("❌ Email cannot be empty")
            continue

        email_valid, email_msg = validate_email(email)
        if not email_valid:
            print(f"❌ {email_msg}")
            continue

        # Check if email exists
        with app.app_context():
            if User.query.filter_by(email=email).first():
                print(f"❌ Email '{email}' already exists")
                continue

        break

    # Get password
    while True:
        password = getpass.getpass("Enter password: ")
        if not password:
            print("❌ Password cannot be empty")
            continue

        password_valid, password_msg = validate_password(password)
        if not password_valid:
            print(f"❌ {password_msg}")
            continue

        confirm_password = getpass.getpass("Confirm password: ")
        if password != confirm_password:
            print("❌ Passwords do not match")
            continue

        break

    return username, email, password


def main():
    """Main function - always prompts for user input"""
    try:
        # Get user details through prompts
        username, email, password = prompt_for_user_details()

        print("\n" + "-" * 40)
        print("Creating user account...")

        # Create the user
        success = create_user_account(username, email, password)

        if success:
            print("\n🎉 Account created successfully!")
            print("You can now log in to the RICOH POC system.")
        else:
            print("\n💥 Failed to create account.")

        sys.exit(0 if success else 1)

    except KeyboardInterrupt:
        print("\n\n⚠️ Account creation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
