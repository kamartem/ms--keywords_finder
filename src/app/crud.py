from sqlalchemy.orm import Session

from app import models, schemas


def get_task(db: Session, task_id: int):
    return db.query(models.Task).filter(models.Task.id == task_id).first()


def get_tasks(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Task).offset(skip).limit(limit).all()


def create_task(db: Session, task: schemas.TaskCreate):
    db_task = models.Task(keywords=task.keywords)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


def get_resources(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Resource).offset(skip).limit(limit).all()


def create_resource(db: Session, resource: schemas.ResourceCreate, task_id: int):
    db_resource = models.Resource(**resource.dict(), task_id=task_id)
    db.add(db_resource)
    db.commit()
    db.refresh(db_resource)
    return db_resource
