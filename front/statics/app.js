function setupLoginEventHandlers() {
    const loginForm = document.querySelector("form[name='login']");
    if (loginForm) {
        // Cuando se hace click en login se valida si los datos enviados coinciden con los guardados
        loginForm.addEventListener("submit", function(event){
            event.preventDefault();
    
            var username = document.getElementById("username").value;
            var password = document.getElementById("password").value;
    
            // Preparar los datos como form-urlencoded
            var formData = new URLSearchParams();
            formData.append('username', username);
            formData.append('password', password);
            
            fetch('/login/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: formData,
                credentials : 'include' // Importante incluir las credenciales 
            })
            .then(response => {
                if(response.ok) {
                    return response.json(); // Retornar la respuesta si sale bien
                } else {
                    return response.json().then(err =>{
                        document.getElementById("error-message-login").innerText = "Contraseña o nombre de usuario incorrectos";
                        document.getElementById("error-message-login").style.display = "block"; // Asegura que el mensaje de error sea visible.
                        throw new Error('Inicio de sesión fallido');
                    });
                }
            })
            .then(data => {
                console.log('Success:', data);
                localStorage.setItem('token', data.access_token); 
                localStorage.setItem('username', data.username);
                // Guarda el token y el username en el almacenamiento local
                return fetch('/dashboard', { // Hacemos un GET del html a renderizar 
                    method: 'GET',
                    headers: {
                        'Authorization': 'Bearer ' + localStorage.getItem('token') // Importante incluir el token para que se valide 
                    },
                    credentials: 'include' // Mantiene las cookies con la solicitud 
                });
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('La respuesta de la red no fue ok');
                }
                return response.text(); // Retornamos la respuesta como texto ya que el servidor nos retorna un HTML
            })
            .then(html => {
                // Reemplazamos el html del body por el html enviado por el endpoint de la API
                document.body.innerHTML = html; 
                document.getElementById("body").classList.replace("loginBody", "dash-body");
                setupDashboardEventHandlers(localStorage.getItem('username'));
            })
            .catch(error => {
                    console.error('Error al cargar el dashboard:', error);
                });
                
            });
        }

        // Cuando se hace click en signup se muestra el formulario de signup
        const signupButton = document.getElementById('signup-button');
        if (signupButton) {
            signupButton.addEventListener('click', function(){
                fetch('/sign_up', {
                    method: 'GET'
                })
                .then(response => response.text())
                .then(signUphtml => {
                    document.body.innerHTML = signUphtml;
                    document.getElementById('body').classList.replace('loginBody', 'signup-body');
                    setupSignupEventHandlers();
                });
            });
        }   
}

function setupSignupEventHandlers() {

    const signupForm = document.querySelector("form[name='signup']");
    if (signupForm) {
        //
        signupForm.addEventListener("submit", function(event) {
            event.preventDefault(); // Previene el envío tradicional del formulario.
            
            // Obtenemos los datos ingresados por el usuario
            var username = document.getElementById("username").value;
            var email = document.getElementById("email").value;
            var password = document.getElementById("password").value;
            var confirmPassword = document.getElementById("confirm-password").value;
    
            // Verifica si las contraseñas coinciden.
            if (password !== confirmPassword) {
                document.getElementById("error-message").innerText = "Las contraseñas no coinciden";
                document.getElementById("error-message").style.display = "block"; // Asegura que el mensaje de error sea visible.
            } else {
                // Si las contraseñas coinciden, se envían los datos al servidor
                fetch('http://localhost:8000/users/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        username: username,
                        email: email,
                        password: password
                    }),
                })
                .then(response => response.json())
                .then(data => {
                    console.log('Success:', data);
                    everywhereToLogin('signup-body')
                })
                .catch((error) => {
                    console.error('Error:', error);
                    // Aquí puedes manejar errores de la petición, como mostrar un mensaje al usuario.
                });
    
                // Limpia el mensaje de error si previamente se mostró uno.
                document.getElementById("error-message").style.display = "none";
            }
        });
    }

    const gobackButton = document.getElementById('goback-button');
    if (gobackButton) {
        gobackButton.addEventListener('click', function(){
            everywhereToLogin('signup-body')
        });
    }
}

function everywhereToLogin(bodyName) {
    fetch('/', {
        method:'GET'
    })
    .then(response => response.text())
    .then(loghtml => {
        document.body.innerHTML = loghtml;
        document.getElementById('body').classList.replace(bodyName, 'loginBody');
        setupLoginEventHandlers();
    });
}

// Defino la función del manejador fuera del alcance del evento click para que pueda eliminar
// el event listener previo y agregar uno nuevo
let formSubmitHandler = null;

function setupDashboardEventHandlers(username) {

    const addTaskButton = document.getElementById('add-task')
    if (addTaskButton) {
        addTaskButton.addEventListener("click", function() { // Mostramos el formulario para agregar una nueva tarea
            const formulario = document.getElementById("formulario");
            const formElement = document.getElementsByClassName('form')[0];
            if (formulario.style.display === "none") {
              formulario.style.display = "block";

              if (!formSubmitHandler){
                formSubmitHandler = function(event) {
                    event.preventDefault();
                    fetch(`http://localhost:8000/users/${username}` , {
                        method : 'GET' // Necesitamos obtener el id del usuario para agregar su tarea
                    })
                    .then(response => response.json())
                    .then(userData => {
                        // Obtenemos los valores de los campos de textarea
                        var title = document.getElementById('titleUpd').value; 
                        var description = document.getElementById('description').value;
                        fetch(`http://localhost:8000/users/${userData.id}/tasks/`, { // Hacemos un post para que se agregue la tarea
                            method: 'POST',
                            headers: {
                                // Importante incluir el token ya que esta es una ruta protegida 
                                'Content-Type': 'application/json',
                                'Authorization': 'Bearer ' + localStorage.getItem('token')
                            },
        
                            body: JSON.stringify({
                                title: title,
                                description: description
                            }),
                            credentials:'include'
                        })
                        .then(response => {
                            if (!response.ok) {
                                throw new Error('Failed to create task')
                            }
                            return response.json();
                        })

                        // Si todo sale bien renderizamos la nueva tarea en el html 
                        .then(taskData => {
                            console.log(taskData)
                            let taskContainer = document.getElementsByClassName('list-tasks')[0];
                            var newdiv = newTaskContainer(taskData);
                            addEventToNewTask(newdiv, taskData.id)
                            taskContainer.appendChild(newdiv);
                            formulario.style.display = "none"; // Por ultimo aseguramos de cerrar el formulario 
                            });
                        });
                    };
                }
              
                formElement.removeEventListener('submit', formSubmitHandler);

                formElement.addEventListener('submit', formSubmitHandler)
            } else {
              formulario.style.display = "none";
            }
          });
          
        document.getElementById("description").addEventListener("click", function(event) {
            var textarea = event.target;
            // Establece el punto de selección al inicio del texto
            textarea.selectionStart = 0;
            textarea.selectionEnd = 0;
            // Opcional: coloca el scroll al inicio si el texto es largo
            textarea.scrollTop = 0;
          });

        let usern = document.getElementsByTagName('span');
        usern[0].innerHTML = username;
        fetch(`http://localhost:8000/users/${username}`, {
            method : 'GET'
        })
        .then(response => response.json())
        .then(data => {
            localStorage.setItem('username', data.username)
            localStorage.setItem('email', data.email)
            localStorage.setItem('id', data.id)
            let emailInput = document.getElementById('useremail');
            emailInput.value = data.email;
            let tasks = data.tasks;
            let taskContainer = document.getElementsByClassName('list-tasks')[0];
            for (let task of tasks){
                var newdiv = newTaskContainer(task)
                addEventToNewTask(newdiv, task.id)
                taskContainer.appendChild(newdiv);
            };
        });
        
        document.getElementById('update-button').addEventListener('click', function() {
            const updateForm = document.getElementById('update-info-form')

            if (updateForm.style.display === 'none'){
                updateForm.style.display = 'block'

                document.getElementById('email').value = localStorage.getItem('email')
                document.getElementById('username').value = localStorage.getItem('username')
            } 
            else {
                updateForm.style.display = 'none'
            }
        });

        document.getElementById('logout').addEventListener('click', () => {
            localStorage.removeItem('token');
            everywhereToLogin('dash-body');
        })

        const formToUpdateUser = document.querySelector("form[name='update-userinfo']");
        if (formToUpdateUser) {
            formToUpdateUser.addEventListener('submit', function(event) {
                event.preventDefault();
                let updatedData = {}

                let updatedUsername = document.getElementById('username').value;
                let updatedEmail = document.getElementById('email').value;
                let updatedPassword = document.getElementById('password').value;
                let knowemail = true;
                let knowusername = true;

                // Solamente enviamos los datos que el usuario cambió en el formulario
                if (updatedUsername !== localStorage.getItem('username')) {
                    updatedData.username = updatedUsername;
                    knowusername = false
                }

                if (updatedEmail !== localStorage.getItem('email')) {
                    updatedData.email = updatedEmail;
                    knowemail = false
                }

                if (updatedPassword) {
                    updatedData.password = updatedPassword;
                }

                fetch(`/users/${localStorage.getItem('id')}`, {
                    method : 'PUT',
                    headers : {
                        'Content-Type' : 'application/json',
                        'Authorization' : `Bearer ${localStorage.getItem('token')}`
                    },
                    body : JSON.stringify(updatedData),
                    credentials: 'include'
                })
                .then(response => response.json())
                .then(data => {
                    console.log('message:', data);
                    // Actualizamos los datos del usuario en el dashboard
                    if (!knowusername) {
                        usern[0].innerHTML = updatedUsername;
                    }
                    if (!knowemail) {
                        document.getElementById('useremail').value = updatedEmail;
                    }
                    document.getElementById('update-info-form').style.display = 'none';
                });
            });
        }

        const openSectionButton = document.getElementById('hamburger-menu')
        openSectionButton.addEventListener('click', function () {
            document.getElementById('user-section').style.display = 'flex'
            document.getElementById('close-section').style.display = 'block'
        })

        window.addEventListener('resize', function() {
            var width = window.innerWidth || document.documentElement.clientWidth || document.body.clientWidth;
            if (width > 600) {
              document.getElementById('close-section').style.display = 'none';  
            }
          });

    }
}



function newTaskContainer(task) {
    var newdiv = document.createElement("div")
    newdiv.className = "task";
    newdiv.setAttribute('data-task-id', task.id);

    if (task.completed) {
        newdiv.style.opacity = '0.6';
    }

    var title = document.createElement("p");
    title.textContent = task.title;

    var description = document.createElement("p")
    description.innerText = task.description
                
    var date = document.createElement("p")
    date.innerText = task.date_of_creation
    newdiv.appendChild(title);
    newdiv.appendChild(description);
    newdiv.appendChild(date);
    return newdiv;
}

function addEventToNewTask(div, taskId) {
    div.addEventListener('click', function(event) {
        event.stopPropagation();
        
        if (div.style.opacity === '0.6') {
            showTaskMenu(taskId, true);
        } else {
            showTaskMenu(taskId);
        }
    });
}

function showTaskMenu(taskId, completed = false) {
    let del_container = document.getElementById('task-menu')
    del_container.style.display = 'block';
    
    window.onclick = function(event) {
        if (event.target === del_container) {
            del_container.style.display = 'none';
        }
    };
    
    const del_button = document.getElementById('delete-task');
    del_button.onclick = function(event) {
        event.stopPropagation();
        deleteTask(taskId);
        del_container.style.display = 'none';
    };

    let markCompletedButton = document.getElementById('complete-task');
    markCompletedButton.disabled = false;
    if (completed) {
        markCompletedButton.disabled = true;
    }
    markCompletedButton.onclick = function(event) {
        event.stopPropagation();
        markTaskCompleted(taskId);
        del_container.style.display = 'none'
    }
}

function markTaskCompleted(taskId) {
    fetch(`/tasks/${taskId}`, {
        method: 'PUT',
        headers: {
            'Content-Type' : 'application/json',
            'Authorization' : 'Bearer ' + localStorage.getItem('token')
        },
        body: JSON.stringify({
            completed: true
        }),
        credentials: 'include'
    }
    )
    .then(response => {
        if (!response.ok) {
            throw new Error('No se pudo marcar la tarea como completada')
        }
        return response.json()
    })
    .then(() => {
        document.querySelector(`[data-task-id="${taskId}"]`).style.opacity = '0.6';
    })
    .catch(error => {
        console.log(error)
    });
}

function deleteTask(taskId) {
    fetch(`/tasks/${taskId}`, {
        method: 'DELETE',
        headers: {
            'Authorization' : 'Bearer ' + localStorage.getItem('token')
        },
        credentials: 'include'
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('No se pudo eliminar la tarea');
        }
        return response.json()
    })
    .then(() => {
        // Implementar logica para actualizar el DOM
        document.querySelector(`[data-task-id="${taskId}"]`).remove();

    })
    .catch(error => {
        console.error('Error al eliminar la tarea', error);
    });
}

document.addEventListener('DOMContentLoaded', function() {
    // Obtiene el token almacenado en el localStorage si lo hay
    const token = localStorage.getItem('token');
    const username = localStorage.getItem('username');
    if (token) {
        fetch('/login/verify-token', {
            method: 'GET',
            headers: {
                'Authorization' : 'Bearer ' + token
            },
            credentials: 'include'
        })
        .then(response => {
            if (response.ok) {
                return fetch('/dashboard', {
                    method : 'GET',
                    headers: {
                        'Authorization' : 'Bearer ' + token
                    },
                    credentials: 'include'
                });
            } else {
                // Si el token no es válido
                localStorage.removeItem('token');
                throw new Error('El token no es válido o ha expirado');
            }
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('No se pudo cargar el dashboard');
            }
            return response.text();
        })
        .then(html => {
            document.body.innerHTML = html
            document.getElementById('body').classList.replace('loginBody', 'dash-body')
            setupDashboardEventHandlers(username);
        })
        .catch(error => {
            console.error(error);
            everywhereToLogin('dash-body')
        })
    } else {
        everywhereToLogin('dash-body')
    }
});