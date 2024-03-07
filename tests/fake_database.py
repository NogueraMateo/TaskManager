from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from back.main import app
from back.database import Base, get_db
import pytest


SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args= {"check_same_thread" : False}
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

@pytest.fixture(scope="function")
def db_session():
    '''Establishes a connection to the test database and starts a transaction so all the changes made
    can be reverted, then creates a session to interactuate with the database. It returs the session and 
    once the tests are finished and the session is no loger needed, the function undoes the changes'''

    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    yield session
    transaction.rollback()
    session.close()
    connection.close()


@pytest.fixture(scope="function")
def client_with_db_override(db_session):
    '''
    This function is used in order to overwrite the get_db dependency so the get_db function
    doesn't use the actual database, but a test database managed by db_session funcion. Once 
    the session is closed we need to make sure to clear all the overridden dependecies
    '''
    def _override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()

    app.dependency_overrides[get_db] = _override_get_db
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()