from sqlalchemy.orm import Session
import models
from schemas.inquiries import InquiryCreate, InquiryUpdate, InquiryStatusUpdate


def get_inquiry(db: Session, inquiry_id: int):
    return db.query(models.Inquiry).filter(models.Inquiry.id == inquiry_id).first()


def get_inquiries(db: Session, skip: int = 0, limit: int = 100, status: str = None, priority: str = None):
    query = db.query(models.Inquiry)
    if status:
        query = query.filter(models.Inquiry.status == status)
    if priority:
        query = query.filter(models.Inquiry.priority == priority)
    return query.offset(skip).limit(limit).all()


def get_inquiries_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Inquiry).filter(models.Inquiry.user_id == user_id).offset(skip).limit(limit).all()


def get_inquiries_assigned_to_user(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Inquiry).filter(models.Inquiry.assigned_to_id == user_id).offset(skip).limit(limit).all()


def get_inquiries_by_school(db: Session, school_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Inquiry).filter(models.Inquiry.school_id == school_id).offset(skip).limit(limit).all()


def get_inquiries_by_corporation(db: Session, corporation_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Inquiry).filter(models.Inquiry.corporation_id == corporation_id).offset(skip).limit(limit).all()


def create_inquiry(db: Session, inquiry: InquiryCreate):
    db_inquiry = models.Inquiry(
        title=inquiry.title,
        content=inquiry.content,
        status=inquiry.status,
        priority=inquiry.priority,
        user_id=inquiry.user_id,
        school_id=inquiry.school_id,
        corporation_id=inquiry.corporation_id
    )
    db.add(db_inquiry)
    db.commit()
    db.refresh(db_inquiry)
    return db_inquiry


def update_inquiry(db: Session, inquiry_id: int, inquiry: InquiryUpdate):
    db_inquiry = get_inquiry(db, inquiry_id)
    if not db_inquiry:
        return None

    update_data = inquiry.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_inquiry, key, value)

    db.commit()
    db.refresh(db_inquiry)
    return db_inquiry


def assign_inquiry(db: Session, inquiry_id: int, assigned_to_id: int):
    db_inquiry = get_inquiry(db, inquiry_id)
    if not db_inquiry:
        return None

    db_inquiry.assigned_to_id = assigned_to_id
    db_inquiry.status = "in_progress" if db_inquiry.status == "pending" else db_inquiry.status
    db.commit()
    db.refresh(db_inquiry)
    return db_inquiry


def update_inquiry_status(db: Session, inquiry_id: int, status_update: InquiryStatusUpdate):
    db_inquiry = get_inquiry(db, inquiry_id)
    if not db_inquiry:
        return None

    db_inquiry.status = status_update.status
    if status_update.status == "resolved" and status_update.resolved_at:
        db_inquiry.resolved_at = status_update.resolved_at
    elif status_update.status == "resolved":
        from datetime import datetime
        db_inquiry.resolved_at = datetime.utcnow()

    db.commit()
    db.refresh(db_inquiry)
    return db_inquiry


def delete_inquiry(db: Session, inquiry_id: int):
    db_inquiry = get_inquiry(db, inquiry_id)
    if db_inquiry:
        db.delete(db_inquiry)
        db.commit()
        return True
    return False