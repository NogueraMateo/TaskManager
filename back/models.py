from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship
from passlib.context import CryptContext
from .database import Base
from datetime import datetime

crypt = CryptContext(schemes=["bcrypt"])

class User(Base):
    __tablename__ = 'usuarios'

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    email = Column(String, unique=True)
    password_hash = Column(String)

    tasks = relationship('Task', back_populates='owner')

    def verify_password(self, plain_password:str):
        return crypt.verify(plain_password, self.password_hash)


class Task(Base):
    __tablename__ = 'tareas'

    id = Column(Integer, primary_key=True)
    title = Column(String)
    description = Column(String)
    completed = Column(Boolean, default= False)
    date_of_creation = Column(DateTime, default=datetime.utcnow)
    user_id = Column(Integer, ForeignKey('usuarios.id'))

    owner = relationship('User', back_populates='tasks')