from fastapi.testclient import TestClient
from httpx import WSGITransport
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


def test_user_creation_and_login(client_with_db_override):
    client = client_with_db_override

    # Creating an user
    user_data = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "testpassword"
    }
    response = client.post("/users/", json=user_data)
    assert response.status_code == 201, response.text

    # Logging in 
    login_data = {
        "username": user_data["username"],
        "password": user_data["password"],
    }
    response = client.post("/login/", data=login_data)
    assert response.status_code == 200, response.text
    assert "access_token" in response.json()
    assert response.json().get('username') == login_data.get("username")

    login_data["password"] = "incorrectpassword"
    response = client.post("/login/", data=login_data)
    assert response.status_code == 401, response.text

    login_data["username"] = "incorrectusername"
    login_data["password"] = user_data["password"]
    response = client.post("/login/", data=login_data)
    assert response.status_code == 401, response.text


def test_verify_token(client_with_db_override):
    client = client_with_db_override

    # Creating an user
    user_data = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "testpassword"
    }
    response = client.post("/users/", json=user_data)
    assert response.status_code == 201, response.text
    
    login_data = {
        "username": user_data["username"],
        "password": user_data["password"],
    }
    response = client.post("/login/", data=login_data)
    assert response.status_code == 200, response.text
    access_token = response.json().get("access_token")
    assert access_token is not None

    # Testing with valid access_token
    headers = {'Authorization' : 'Bearer ' + access_token}
    response = client.get("/login/verify-token", headers=headers)
    assert response.status_code == 200

    # Testing with invalid access_token
    headers = {'Authorization' : 'Bearer ' + "IncorretAccessToken"}
    response = client.get("/login/verify-token", headers=headers)
    assert response.status_code == 401
