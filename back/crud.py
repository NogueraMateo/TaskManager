from sqlalchemy.orm import Session
from passlib.context import CryptContext

from . import models, schemas

crypt = CryptContext(schemes=["bcrypt"])

# Finds the user using the id 
def get_user(db : Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


# Finds the user by the email
def get_user_by_email(db: Session, user_email: str):
    return db.query(models.User).filter(models.User.email == user_email).first()


# Finds the user by its username
def get_user_by_username(db:Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()


# Returns all users in the database
def get_users(db: Session, skip:int = 0, limit:int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


# Creates a new user in the database
def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = crypt.hash(user.password)
    db_user = models.User(email=user.email, username= user.username, password_hash = hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user



def get_task(db:Session, task_id : int):
    return db.query(models.Task).filter(models.Task.id == task_id).first()


# Returns all tasks in the database
def get_user_tasks(db: Session, user_id:int, skip: int = 0, limit:int = 100):
    tasks = db.query(models.Task).filter(models.Task.user_id == user_id).all()
    return tasks


# Creates a new task in the database according to the user_id
def create_user_task(db: Session, task: schemas.TaskCreate, usr_id: int):
    db_task = models.Task(**task.model_dump(), user_id= usr_id)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task    


def update_task(db: Session, task_id: int, task_update: schemas.TaskUpdate):
    db_task = get_task(db=db, task_id=task_id)
    if db_task is None:
        return None
    
    # Updates the fields with the given values
    update_data = task_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_task, key, value)

    db.commit()
    db.refresh(db_task)
    return db_task


def delete_task(db: Session, task_id: int):
    db_task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if db_task is None:
        return None

    db.delete(db_task)
    db.commit()
    return db_task


def delete_tasks_by_user_id(db: Session, user_id: int):
    tasks_to_delete = db.query(models.Task).filter(models.Task.user_id == user_id).all()
    for task in tasks_to_delete:
        db.delete(task)
    db.commit()


def delete_user(db: Session, user_id:int):
    delete_tasks_by_user_id(db=db, user_id=user_id)

    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user is None:
        return None
    
    db.delete(db_user)
    db.commit()
    return db_user


def update_user(db: Session, user_id: int, user_update:schemas.UserUpdate):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user is None:
        return None
    
    existsemail = get_user_by_email(db=db, user_email=user_update.email)

    if existsemail:
        return "email"
    
    existsusername = get_user_by_username(db=db, username=user_update.username)
    
    if existsusername:
        return "username"
    
    update_data = user_update.model_dump(exclude_unset=True)

    if "password" in update_data:
        password_hash = crypt.hash(update_data['password'])
        update_data["password_hash"] = password_hash
        del update_data['password']

    for key, value in update_data.items():
        setattr(db_user, key, value)

    db.commit()
    db.refresh(db_user)
    return db_user
    