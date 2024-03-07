from .test_database import db_session,client_with_db_override
import pytest



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