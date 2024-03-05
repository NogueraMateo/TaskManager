from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from . import authenticate_users as oauth2
from .. import crud, schemas, models
from ..database import SessionLocal, get_db

router = APIRouter(prefix="/tasks",
                   tags=["Tasks"])


@router.get("/", response_model=list[schemas.Task])
def read_user_tasks(skip:int = 0, limit:int = 100, db :Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    tasks = crud.get_user_tasks(user_id=current_user.id,skip=skip, limit=limit, db=db)
    return tasks


@router.put("/{task_id}", response_model=schemas.Task)
def update_task(task_id: int,to_update: schemas.TaskUpdate, db: Session = Depends(get_db), current_user : models.User = Depends(oauth2.get_current_user)):
    task = crud.get_task(db=db, task_id= task_id)
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No task found to update")
    
    if task.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Not authorized to update this task")
    updated_task = crud.update_task(db=db, task_id=task_id, task_update=to_update)

    return updated_task


@router.delete("/{task_id}", response_model= schemas.Task)
def delete_task(task_id: int, db: Session= Depends(get_db), current_user : models.User = Depends(oauth2.get_current_user)):
    task = crud.get_task(db=db, task_id=task_id)
    if task.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this task")
    deleted_task = crud.delete_task(db=db, task_id=task_id)
    return deleted_task