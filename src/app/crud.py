from sqlalchemy.orm import Session

from app.models import orm, pydantic

def get_task(db: Session, task_id: int):
    return db.query(orm.Task).filter(orm.Task.id == task_id).first()


def get_tasks(db: Session, skip: int = 0, limit: int = 100):
    return db.query(orm.Task).offset(skip).limit(limit).all()


def create_task(db: Session, task: pydantic.TaskCreate):
    db_task = orm.Task(keywords=task.keywords)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


def get_resources(db: Session, skip: int = 0, limit: int = 100):
    return db.query(orm.Resource).offset(skip).limit(limit).all()


def create_resource(db: Session, resource: pydantic.ResourceCreate, task_id: int):
    db_resource = orm.Resource(**resource.dict(), task_id=task_id)
    db.add(db_resource)
    db.commit()
    db.refresh(db_resource)
    return db_resource
