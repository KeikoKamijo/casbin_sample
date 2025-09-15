from sqlalchemy.orm import Session
import models
from schemas.corporations import CorporationCreate, CorporationUpdate


def get_corporation(db: Session, corporation_id: int):
    return db.query(models.Corporation).filter(models.Corporation.id == corporation_id).first()


def get_corporation_by_name(db: Session, name: str):
    return db.query(models.Corporation).filter(models.Corporation.name == name).first()


def get_corporation_by_code(db: Session, code: str):
    return db.query(models.Corporation).filter(models.Corporation.code == code).first()


def get_corporations(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Corporation).offset(skip).limit(limit).all()


def create_corporation(db: Session, corporation: CorporationCreate):
    db_corporation = models.Corporation(
        name=corporation.name,
        code=corporation.code,
        description=corporation.description
    )
    db.add(db_corporation)
    db.commit()
    db.refresh(db_corporation)
    return db_corporation


def update_corporation(db: Session, corporation_id: int, corporation: CorporationUpdate):
    db_corporation = get_corporation(db, corporation_id)
    if not db_corporation:
        return None

    update_data = corporation.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_corporation, key, value)

    db.commit()
    db.refresh(db_corporation)
    return db_corporation


def delete_corporation(db: Session, corporation_id: int):
    db_corporation = get_corporation(db, corporation_id)
    if db_corporation:
        db.delete(db_corporation)
        db.commit()
        return True
    return False