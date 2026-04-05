from sqlalchemy.orm import Session
from . import models, schemas

def create_doctor(db: Session, doctor: schemas.DoctorCreate):
    db_doc = models.Doctor(**doctor.dict())
    db.add(db_doc)
    db.commit()
    db.refresh(db_doc)
    return db_doc

def get_doctors(db: Session):
    return db.query(models.Doctor).all()

def get_doctor_count(db: Session):
    return db.query(models.Doctor).count()

def update_doctor(db: Session, doctor_id: int, doctor: schemas.DoctorCreate):
    db_doc = db.query(models.Doctor).filter(models.Doctor.id == doctor_id).first()
    if db_doc:
        db_doc.name = doctor.name
        db_doc.specialization = doctor.specialization
        db.commit()
        return db_doc
    return None

def delete_doctor(db: Session, doctor_id: int):
    db_doc = db.query(models.Doctor).filter(models.Doctor.id == doctor_id).first()
    if db_doc:
        db.delete(db_doc)
        db.commit()
        return True
    return False