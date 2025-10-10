from database import SessionLocal
from crud.users import verify_password
from models import User

def check_users():
    db = SessionLocal()
    try:
        # Check existing users and their passwords
        users = db.query(User).all()

        print("Existing users in database:")
        for user in users:
            print(f"- {user.username} (email: {user.email}, corp_id: {user.corporation_id})")

        # Test password verification
        print("\nTesting password verification:")
        alice = db.query(User).filter_by(username="Alice").first()
        bob = db.query(User).filter_by(username="Bob").first()
        dave = db.query(User).filter_by(username="Dave").first()

        if alice:
            print(f"Alice - alice123: {verify_password('alice123', alice.hashed_password)}")
            print(f"Alice - alicepass: {verify_password('alicepass', alice.hashed_password)}")

        if bob:
            print(f"Bob - bob123: {verify_password('bob123', bob.hashed_password)}")

        if dave:
            print(f"Dave - dave123: {verify_password('dave123', dave.hashed_password)}")
            print(f"Dave - davepass: {verify_password('davepass', dave.hashed_password)}")

    finally:
        db.close()

if __name__ == "__main__":
    check_users()