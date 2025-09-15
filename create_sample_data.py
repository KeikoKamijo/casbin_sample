#!/usr/bin/env python3

from sqlalchemy.orm import Session
from database import SessionLocal, engine
import models
import crud
import schemas

def create_sample_data():
    models.Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        # Create corporations
        abc_corp = crud.create_corporation(db, schemas.CorporationCreate(
            name="ABC Corporation",
            code="ABC001",
            description="Sample corporation ABC"
        ))

        def_corp = crud.create_corporation(db, schemas.CorporationCreate(
            name="DEF Corporation",
            code="DEF001",
            description="Sample corporation DEF"
        ))

        # Create users
        alice = crud.create_user(db, schemas.UserCreate(
            username="alice",
            email="alice@abc.com",
            password="alicepass",
            corporation_id=abc_corp.id
        ))

        dave = crud.create_user(db, schemas.UserCreate(
            username="dave",
            email="dave@def.com",
            password="davepass",
            corporation_id=def_corp.id
        ))

        print(f"Created sample data:")
        print(f"- ABC Corporation (ID: {abc_corp.id})")
        print(f"- DEF Corporation (ID: {def_corp.id})")
        print(f"- Alice (ID: {alice.id}, Corporation: {alice.corporation_id})")
        print(f"- Dave (ID: {dave.id}, Corporation: {dave.corporation_id})")

    finally:
        db.close()

if __name__ == "__main__":
    create_sample_data()