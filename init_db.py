from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from models import Base, User, Corporation, Role
from database import engine, SessionLocal
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def init_database():
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully")

    db = SessionLocal()
    try:
        # Create Roles
        admin_role = db.query(Role).filter_by(name="admin").first()
        if not admin_role:
            admin_role = Role(
                name="admin",
                description="Administrator with full access",
                is_active=True
            )
            db.add(admin_role)
            db.commit()
            print("Admin role created successfully")

        accountant_role = db.query(Role).filter_by(name="accountant").first()
        if not accountant_role:
            accountant_role = Role(
                name="accountant",
                description="Accountant with financial access",
                is_active=True
            )
            db.add(accountant_role)
            db.commit()
            print("Accountant role created successfully")

        # Create Corporations
        abc_corp = db.query(Corporation).filter_by(code="ABC").first()
        if not abc_corp:
            abc_corp = Corporation(
                name="ABC Corporation",
                code="ABC",
                description="ABC Corporation - Main Company",
                is_active=True
            )
            db.add(abc_corp)
            db.commit()
            print("ABC Corporation created successfully")

        def_corp = db.query(Corporation).filter_by(code="DEF").first()
        if not def_corp:
            def_corp = Corporation(
                name="DEF Corporation",
                code="DEF",
                description="DEF Corporation - Secondary Company",
                is_active=True
            )
            db.add(def_corp)
            db.commit()
            print("DEF Corporation created successfully")

        # Create or update users
        alice = db.query(User).filter_by(username="Alice").first()
        if not alice:
            alice = User(
                username="Alice",
                email="alice@example.com",
                full_name="Alice Smith",
                hashed_password=pwd_context.hash("alice123"),
                is_active=True,
                corporation_id=abc_corp.id
            )
            db.add(alice)
            print("User Alice created and linked to ABC Corporation")
        else:
            alice.corporation_id = abc_corp.id
            print("User Alice updated to link to ABC Corporation")

        bob = db.query(User).filter_by(username="Bob").first()
        if not bob:
            bob = User(
                username="Bob",
                email="bob@example.com",
                full_name="Bob Johnson",
                hashed_password=pwd_context.hash("bob123"),
                is_active=True,
                corporation_id=abc_corp.id
            )
            db.add(bob)
            print("User Bob created and linked to ABC Corporation")
        else:
            bob.corporation_id = abc_corp.id
            print("User Bob updated to link to ABC Corporation")

        dave = db.query(User).filter_by(username="Dave").first()
        if not dave:
            dave = User(
                username="Dave",
                email="dave@example.com",
                full_name="Dave Williams",
                hashed_password=pwd_context.hash("dave123"),
                is_active=True,
                corporation_id=def_corp.id
            )
            db.add(dave)
            print("User Dave created and linked to DEF Corporation")
        else:
            dave.corporation_id = def_corp.id
            print("User Dave updated to link to DEF Corporation")

        db.commit()

    finally:
        db.close()

if __name__ == "__main__":
    init_database()