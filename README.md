
# 📝 TaskMaster

TaskMaster is an intuitive and efficient task manager that enables users to register, log in, and manage their daily tasks.

## 🚀 Features
- 🗝 Sign up with email, username and password
- Log in with username and password (Authentication)
- Passwords are all hashed in the database
- If the user is authorized can:
    - Create a new task
    - Mark a task as completed
    - Delete a task
    - Update his info (Email, username and/or password)
    - Log out 
- The user sesion is valid until the token generated when logging in expires
## 🛠️ Main Technologies
- **`Python`**
- **`FastAPI`**
- **`SQL`**
- **`JavaScript`**
- **`CSS`**
- **`HTML`**
## 🎨 Process
First, I selected a project that would allow me to showcase the key aspects of back-end development. After considering various options, I chose to create a task manager. 

I began by developing the API and the database models with SQLAlchemy, and testing the endpoints with Postman and Swagger UI. Once the API was complete, I was pleased with my work, but I wanted to provide a way for others to interact with the project easily, without the need to use Postman to manually send requests. Therefore, I decided to build a straightforward yet functional interface using JavaScript, CSS, and HTML, despite my primary focus on back-end development.

Additionally, I conducted thorough tests on the endpoints to ensure their reliability and functionality.

## 📚 What I learned

#### 🧠 SQLAlchemy (ORM)
I learned to use SQLAlchemy in order to interact with the database without writing SQL queries directly. Also it allows me to use diferent database systems without changing the code.
####  ✔️ TestClient (testing)
I found out how to simulate HTTP requests to my API, which allowed me to test my endpoints as if they were being accessed by a real client.
#### 🎡 DOM 
In order to implement an interface to the people to interact with my project I learned how to manipulate the DOM using JavaScript and I felt really good learning the front-end bases.

## 📈  How can it be improved? 
- In the login section, it'll be nice if the user could login with his google account directly. 
- In the dashboard section, if you consider that updating the whole task like the title and the description instead of only marking it as completed would be useful, then you could easily implement it by making some modifications in the front-end, because there is alredy an endpoint implemented for it, and it's named **`update_task`**.
- A better design would be great.

## 🏃 Running the project
Follow these stepts to run the project in your local environment: 

- Clone the repository to your local machine 
- Run `pip install -r requirements.txt` in the project directory to install the required dependencies.
- Run `uvicorn back.main:app --reload` to get the project started
- Open `http://localhost:8000`(or the address shown in your console) in your web browser to view the app.






