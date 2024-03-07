from .fake_database import db_session, client_with_db_override
import pytest   

def test_create_user(client_with_db_override):
    client = client_with_db_override

    # Creating an user
    user_data = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "testpassword"
    }
    response = client.post("/users/", json=user_data)
    assert response.status_code == 201, response.text
    assert response.json().get('username') == user_data['username']
    assert response.json().get('email') == user_data['email'] 
    assert 'password' not in response.json()


    # Trying to create an user with a registered email
    user_data = {
        "email": "test@example.com",
        "username": "testuser2",
        "password": "testpassword2"
    }
    response = client.post("/users/", json=user_data)
    assert response.status_code == 400, response.text
    assert response.json().get('detail') == 'Email alredy registered'


    # Trying to create an user with a registered username
    user_data = {
        "email": "test2@example.com",
        "username": "testuser",
        "password": "testpassword2"
    }
    response = client.post("/users/", json=user_data)
    assert response.status_code == 400, response.text
    assert response.json().get('detail') == 'Username alredy registered'


    # Trying to create an user without filling password field
    user_data = {
        "email": "test2@example.com",
        "username": "testuser2",
        "password": ""
    }

    response = client.post("/users/", json=user_data)
    assert response.status_code == 400, response.text
    assert response.json().get('detail') == 'Password should be at least 7 characters'

    # Trying to create an user without filling password field
    user_data = {
        "email": "test2@example.com",
        "username": "",
        "password": "testuser"
    }

    response = client.post("/users/", json=user_data)
    assert response.status_code == 400, response.text
    assert response.json().get('detail') == 'Username should be at least 5 characters'


def test_read_user(client_with_db_override):
    client = client_with_db_override

    # Creating an user
    user_data = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "testpassword"
    }
    response = client.post("/users/", json=user_data)
    assert response.status_code == 201

    # Logging in 
    login_data = {
        "username": "testuser",
        "password": "testpassword"
    }
    response = client.post("/login/", data=login_data)
    assert response.status_code == 200
    assert "access_token" in response.json()
    access_token = response.json().get('access_token')

    headers = {
        "Authorization" : "Bearer " + access_token
    }

    response = client.get(f'/users/{user_data["username"]}', headers=headers)
    assert response.status_code == 200, response.text
    assert "id" in response.json()
    assert "tasks" in response.json()
    assert user_data["username"] == response.json().get('username')


    # Trying to get user info with wrong access_token
    headers = {
        "Authorization" : "Bearer " + "wrong access token"
    }
    response = client.get(f'/users/{user_data["username"]}', headers=headers)
    assert response.status_code == 401, response.text


    # Trying to get user info with usernames that don't match
    headers = {
        "Authorization" : "Bearer " + access_token
    }
    response = client.get(f'/users/wrongUsername', headers=headers)
    assert response.status_code == 401, response.text
    assert response.json().get('detail') == "Unauthorized to read this user"


def test_create_task_for_user(client_with_db_override):
    client = client_with_db_override

    # Creating an user
    user_data = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "testpassword"
    }
    response = client.post("/users/", json=user_data)
    assert response.status_code == 201

    # Logging in 
    login_data = {
        "username": "testuser",
        "password": "testpassword"
    }
    response = client.post("/login/", data=login_data)
    assert response.status_code == 200
    assert "access_token" in response.json()
    access_token = response.json().get('access_token')
    
    headers = {
        "Authorization" : "Bearer " + access_token
    }

    response = client.get(f"/users/{user_data['username']}", headers=headers)
    user_id = response.json().get('id')

    task = {
        "title": "Buy some food on wednesday for the meeting",
        "description" : "Important to buy meat, chicken and cheese"
    }
    response = client.post(f"users/{user_id}/tasks/", json=task, headers=headers)
    assert response.status_code == 201
    assert "id" in response.json()
    assert "date_of_creation" in response.json()
    assert "completed" in response.json()
    assert response.json().get('completed') is not True

    # Creating another user and checking that other user cannot create tasks to other user
    user_data2 = {
        "email": "test@example2.com",
        "username": "testuser2",
        "password": "testpassword2"
    }
    response = client.post("/users/", json=user_data2)
    assert response.status_code == 201

    # From the first user we created we are going to try to create a task to the second user created
    response = client.post("users/2/tasks/", json=task, headers=headers)
    assert response.status_code == 401
    assert response.json().get('detail') == 'Unauthorized'


def test_delete_user(client_with_db_override):
    client = client_with_db_override

    # Creating an user
    user_data = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "testpassword"
    }
    response = client.post("/users/", json=user_data)
    assert response.status_code == 201

    # Logging in 
    login_data = {
        "username": "testuser",
        "password": "testpassword"
    }
    response = client.post("/login/", data=login_data)
    assert response.status_code == 200
    assert "access_token" in response.json()
    access_token = response.json().get('access_token')

    headers = {
        "Authorization" : "Bearer " + access_token
    }

    # Creating another user and checking that other user cannot delete other user's account
    user_data2 = {
        "email": "test@example2.com",
        "username": "testuser2",
        "password": "testpassword2"
    }
    response = client.post("/users/", json=user_data2)
    assert response.status_code == 201

    # From the first user we created we are going to try to delete the second user account
    response = client.delete("/users/2", headers=headers)
    assert response.status_code == 401
    assert response.json().get('detail') == "Unauthorized to delete this user"

    # Deleting the user properly
    response = client.delete("/users/1", headers=headers)
    assert response.status_code == 200
    response = client.get("/users/testuser", headers=headers)
    assert response.status_code == 401
    assert response.json().get('detail') == 'Could not validate credentials'

def test_update_user(client_with_db_override):
    client = client_with_db_override

    # Creating an user
    user_data = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "testpassword"
    }
    response = client.post("/users/", json=user_data)
    assert response.status_code == 201

    # Creating another user
    user_data2 = {
        "email": "test2@example.com",
        "username": "testuser2",
        "password": "testpassword2"
    }
    response = client.post("/users/", json=user_data2)
    assert response.status_code == 201

    # Logging in 
    login_data = {
        "username": "testuser",
        "password": "testpassword"
    }

    response = client.post("/login/", data=login_data)
    assert response.status_code == 200
    assert "access_token" in response.json()
    access_token = response.json().get('access_token')
    
    headers = {
        "Authorization" : "Bearer " + access_token
    }

    # Updating the user with an email alredy in use by other user
    update_data = {
        "email" : "test2@example.com"
    }
    response = client.put("/users/1", headers= headers, json=update_data)
    assert response.status_code == 400
    assert response.json().get('detail') == "Email alredy registered, please use a different one"

    # Updating the user with an username alredy in use by other user
    update_data = {
        "username" : "testuser2",
    }

    response = client.put("/users/1", headers= headers, json=update_data)
    assert response.status_code == 400
    assert response.json().get('detail') == "Username in use, please pick another username"

    # Updating the user properly
    update_data = {
        "email" : "testingemail@email.com",
        "username" : "testinguser"
    } 
    response = client.put("/users/1", headers=headers, json=update_data)
    assert response.status_code == 200
    assert response.json().get("username") == "testinguser"
    assert response.json().get("email") == "testingemail@email.com"


    