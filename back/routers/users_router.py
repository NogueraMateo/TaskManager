from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .. import crud, schemas, models
from ..database import SessionLocal, get_db
from . import authenticate_users as oauth2

router = APIRouter(prefix="/users",
                   tags=["Users"],)



@router.post("/", response_model=schemas.User, status_code= 201)
def create_user(user: schemas.UserCreate, db: Session= Depends(get_db)):
    '''Email, username and password required to create a new user. If the user 
    alredy exists an HTTP exception will be raised'''
    db_user_email = crud.get_user_by_email(db, user_email=user.email)
    db_user_usname = crud.get_user_by_username(db, username=user.username)
    if db_user_email:
        raise HTTPException(status_code=400, detail="Email alredy registered")
    elif db_user_usname:
        raise HTTPException(status_code=400, detail="Username alredy registered")
    
    if len(user.password) < 7 :
        raise HTTPException(status_code=400, detail="Password should be at least 7 characters")
    
    if len(user.username) < 5:
        raise HTTPException(status_code=400, detail="Username should be at least 5 characters")
    
    return crud.create_user(db=db, user=user)


@router.get("/", response_model=list[schemas.User])
def read_users(skip:int = 0, limit:int= 100, db: Session= Depends(get_db)):
    users = crud.get_users(db=db, skip=skip, limit=limit)
    return users


@router.get("/{username}", response_model=schemas.User)
def read_user(username: str, db: Session = Depends(get_db), current_user : models.User = Depends(oauth2.get_current_user)):
    if current_user.username != username:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized to read this user")
    db_user = crud.get_user_by_username(db=db, username=username)
    if db_user is None:
        raise HTTPException(status_code=404, detail='User not found')
    return db_user


@router.post("/{user_id}/tasks/", response_model=schemas.Task, status_code=201)
def create_task_for_user(
    user_id : int, task: schemas.TaskCreate, 
    db : Session= Depends(get_db), 
    current_user : models.User = Depends(oauth2.get_current_user)
):
    '''Users can only create tasks in their corresponding accounts'''
    if current_user.id != user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Unauthorized")
    return crud.create_user_task(db= db, task=task, usr_id=user_id)


@router.delete("/{user_id}", response_model= schemas.User)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user)):
    '''Only the creator of the user is authorized to delete his account'''
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized to delete this user")
    
    deleted_user = crud.delete_user(db=db, user_id=user_id)

    if deleted_user is None:
        raise HTTPException(status_code=400, detail='The user has not been found')
    return deleted_user


@router.put("/{user_id}", response_model= schemas.User)
def update_user(
    user_id: int, user_update: schemas.UserUpdate,
    db: Session = Depends(get_db), 
    current_user:models.User= Depends(oauth2.get_current_user)
    ):
    '''Only the creator of the account is authorized to update his data''' 
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized")
    
    updated_user = crud.update_user(user_id=user_id, user_update=user_update, db=db)

    if updated_user is None:
        raise HTTPException(status_code=400, detail='Email alredy registered')
    return updated_user
