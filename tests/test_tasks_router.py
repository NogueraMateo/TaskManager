from .fake_database import db_session,client_with_db_override
import pytest

def test_read_user_tasks(client_with_db_override):
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

    tasks = [
        {"title": "Buy some food on wednesday for the meeting",
        "description" : "Important to buy meat, chicken and cheese"},
        {"title": "Start studying for the test on thursday",
        "description" : "Limits and Trigonometric identities"},
        {"title": "Buy the tickets for the trip to Atlanta",
        "description" : "3 tickets in first class"}
        ]
    
    for task in tasks:
        response = client.post(f"users/{user_id}/tasks/", json=task, headers=headers)
        assert response.status_code == 201

    response = client.get("/tasks", headers=headers)
    assert response.status_code == 200
    assert len(response.json()) == 3


def test_update_task(client_with_db_override):
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

    task = {"title": "Buy some food on wednesday for the meeting",
        "description" : "Important to buy meat, chicken and cheese"}
    
    response = client.get(f"/users/{user_data['username']}", headers=headers)
    user_id = response.json().get('id')

    response = client.post(f"users/{user_id}/tasks/", json=task, headers=headers)
    assert response.status_code == 201

    task_completed = {
        "completed" : True
    }

    response = client.put("/tasks/1",headers={"Authorization" : "Bearer " + "wrongAccessToken"} , json=task_completed)
    assert response.status_code == 401
    
    response = client.put("/tasks/1", headers=headers, json=task_completed)
    assert response.status_code == 200
    assert "completed" in response.json()
    assert response.json().get('completed') == True


def test_delete_task(client_with_db_override):
    client = client_with_db_override

    # Creating an user
    user_data = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "testpassword"
    }
    response = client.post("/users/", json=user_data)
    assert response.status_code == 201
    user_id = response.json().get("id")
    
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

    task = {
        "title": "Buy some food on wednesday for the meeting",
        "description" : "Important to buy meat, chicken and cheese"
    }
    response = client.post(f"users/{user_id}/tasks/", json=task, headers=headers)
    assert response.status_code == 201

    user_data2 = {
        "email": "test@example2.com",
        "username": "testuser2",
        "password": "testpassword2"
    }
    response = client.post("/users/", json=user_data2)
    assert response.status_code == 201

    # Logging in from antoher user account and trying to delete a task that belongs to other user
    login_data2 = {
        "username": "testuser2",
        "password": "testpassword2"
    }

    response = client.post("/login/", data=login_data2)
    assert response.status_code == 200
    assert "access_token" in response.json()
    access_token = response.json().get('access_token')
    
    headers = {
        "Authorization" : "Bearer " + access_token
    }

    response = client.delete("/tasks/1", headers=headers)
    assert response.status_code == 403
    assert response.json().get("detail") == "Not authorized to delete this task"


    # Logging in and deleting the task properly 
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

    response = client.delete("/tasks/1", headers=headers)
    assert response.status_code == 200
    assert "id" in response.json()
    assert response.json().get('id') == 1