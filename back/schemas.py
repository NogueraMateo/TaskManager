from pydantic import BaseModel
from typing import Optional
from datetime import datetime 

# Before creating the task we don't know the id
class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None

# Schema expected when creating a Task
class TaskCreate(TaskBase):
    pass 

# Schema expected when updating a Task
class TaskUpdate(BaseModel):
    title : Optional[str] = None
    description: Optional[str]  = None
    completed: Optional[bool] = None

# When reading (returning) we alredy know the id assigned
class Task(TaskBase):
    id : int
    user_id : int 
    date_of_creation : datetime
    completed : bool = False

    class ConfigDict:
        from_attributes = True


# Before creating the user we don't know the id
# When returning this object throughout the API we don't return the password
class UserBase(BaseModel):
    email: str
    username: str

# Schema expected when creating an user
class UserCreate(UserBase):
    password: str

# Schema expected when updating an user
class UserUpdate(BaseModel):
    email: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None

# Reading operations
class User(UserBase):
    id : int 
    username: str
    tasks : list[Task] = []

    class ConfigDict:
        from_attributes = True


class TokenData(BaseModel):
    username: str | None = None