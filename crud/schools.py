from sqlalchemy.orm import Session
import models
from schemas.schools import SchoolCreate, SchoolUpdate
from .corporations import get_corporation


def get_school(db: Session, school_id: int):
    return db.query(models.School).filter(models.School.id == school_id).first()


def get_school_by_code(db: Session, code: str):
    return db.query(models.School).filter(models.School.code == code).first()


def get_schools(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.School).offset(skip).limit(limit).all()


def create_school(db: Session, school: SchoolCreate):
    db_school = models.School(
        name=school.name,
        code=school.code,
        address=school.address,
        phone=school.phone,
        email=school.email
    )

    # Add corporations if provided
    if school.corporation_ids:
        corporations = db.query(models.Corporation).filter(
            models.Corporation.id.in_(school.corporation_ids)
        ).all()
        db_school.corporations = corporations

    db.add(db_school)
    db.commit()
    db.refresh(db_school)
    return db_school


def update_school(db: Session, school_id: int, school: SchoolUpdate):
    db_school = get_school(db, school_id)
    if not db_school:
        return None

    update_data = school.dict(exclude_unset=True)

    # Handle corporation_ids separately
    if "corporation_ids" in update_data:
        corporation_ids = update_data.pop("corporation_ids")
        if corporation_ids is not None:
            corporations = db.query(models.Corporation).filter(
                models.Corporation.id.in_(corporation_ids)
            ).all()
            db_school.corporations = corporations

    for key, value in update_data.items():
        setattr(db_school, key, value)

    db.commit()
    db.refresh(db_school)
    return db_school


def delete_school(db: Session, school_id: int):
    db_school = get_school(db, school_id)
    if db_school:
        db.delete(db_school)
        db.commit()
        return True
    return False


def get_schools_by_corporation(db: Session, corporation_id: int, skip: int = 0, limit: int = 100):
    corporation = get_corporation(db, corporation_id)
    if not corporation:
        return []
    return corporation.schools[skip:skip + limit]


def add_school_to_corporation(db: Session, school_id: int, corporation_id: int):
    school = get_school(db, school_id)
    corporation = get_corporation(db, corporation_id)

    if not school or not corporation:
        return None

    if corporation not in school.corporations:
        school.corporations.append(corporation)
        db.commit()
        db.refresh(school)

    return school


def remove_school_from_corporation(db: Session, school_id: int, corporation_id: int):
    school = get_school(db, school_id)
    corporation = get_corporation(db, corporation_id)

    if not school or not corporation:
        return None

    if corporation in school.corporations:
        school.corporations.remove(corporation)
        db.commit()
        db.refresh(school)

    return school