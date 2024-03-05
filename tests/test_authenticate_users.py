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
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    yield session
    transaction.rollback()
    session.close()
    connection.close()


@pytest.fixture(scope="function")
def client_with_db_override(db_session):
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

    # Crear un usuario
    user_data = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "testpassword"
    }
    response = client.post("/users/", json=user_data)  # Asegúrate de reemplazar la ruta correctamente
    assert response.status_code == 201, response.text

    # Iniciar sesión
    login_data = {
        "username": user_data["username"],
        "password": user_data["password"],
    }
    response = client.post("/login/", data=login_data)
    assert response.status_code == 200, response.text
    assert "access_token" in response.json()
    assert response.json().get('username') == login_data.get("username")

