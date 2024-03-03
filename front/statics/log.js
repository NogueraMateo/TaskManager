document.addEventListener("DOMContentLoaded", function(){
    document.querySelector("form").addEventListener("submit", function(event){
        event.preventDefault();

        var username = document.getElementById("username").value;
        var password = document.getElementById("password").value;

        // Preparar los datos como form-urlencoded
        var formData = new URLSearchParams();
        formData.append('username', username);
        formData.append('password', password);
        
        fetch('http://localhost:8000/login/', {
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
                throw new Error('Inicio de sesión fallido'); 
            }
        })
        .then(data => {
            console.log('Success:', data);
            localStorage.setItem('token', data.access_token); // Guarda el token en el almacenamiento local
            fetch('http://localhost:8000/dashboard', { // Hacemos un GET del html a renderizar 
                method: 'GET',
                headers: {
                    'Authorization': 'Bearer ' + localStorage.getItem('token') // Importante incluir el token para que se valide 
                },
                credentials: 'include' // Mantiene las cookies con la solicitud 
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('La respuesta de la red no fue ok');
                }
                return response.text(); // Retornamos la respuesta como texto ya que el servidor nos retorna un HTML
            }).then(html => {
                // Aquí, 'html' es una cadena que contiene el HTML enviado desde el servidor
                document.body.innerHTML = html; 
                document.getElementById("body").classList.replace("loginBody", "dash-body");
                document.getElementById("add-task").addEventListener("click", function() { // Mostramos el formulario para agregar una nueva tarea
                    var formulario = document.getElementById("formulario");
                    if (formulario.style.display === "none") {
                      formulario.style.display = "block";
                      document.getElementsByClassName('form')[0].addEventListener('submit', function(event) {
                        // Si ocurre un evento submit cuando el display del formulario es block, enviamos los datos
                        // de la nueva tarea
                        event.preventDefault();
                        fetch(`http://localhost:8000/users/${data.username}` , {
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
                                var newdiv = document.createElement("div")
                                newdiv.className = "task"
                                var title = document.createElement("p");
                                title.textContent = taskData.title;
                                var description = document.createElement("p")
                                description.innerText = taskData.description
                                var date = document.createElement("p")
                                date.innerText = taskData.date_of_creation
                                newdiv.appendChild(title);
                                newdiv.appendChild(description);
                                newdiv.appendChild(date);

                                taskContainer.appendChild(newdiv);
                                formulario.style.display = "none"; // Por ultimo aseguramos de cerrar el formulario 
                            });
                        });
                    })
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
                    let emailInput = document.getElementById('useremail');
                    emailInput.value = data.email;
                    let tasks = data.tasks;
                    let taskContainer = document.getElementsByClassName('list-tasks')[0];
                    for (let task of tasks){
                        var newdiv = document.createElement("div")
                        newdiv.className = "task"
                        var title = document.createElement("p");
                        title.textContent = task.title;
                        var description = document.createElement("p")
                        description.innerText = task.description
                        var date = document.createElement("p")
                        date.innerText = task.date_of_creation
                        newdiv.appendChild(title);
                        newdiv.appendChild(description);
                        newdiv.appendChild(date);

                        taskContainer.appendChild(newdiv);
                    };
                });// Reemplaza el contenido del body con el nuevo HTML
                // O puedes elegir un elemento específico para actualizar, por ejemplo:
                // document.getElementById('someElementId').innerHTML = html;
            }).catch(error => {
                console.error('Error al cargar el dashboard:', error);
            });
            
        });
    });

    // -------------------------------- Sign up code -----------------------------------------
    document.getElementById('signup-button').addEventListener('click', function(){
        fetch('http://localhost:8000/sign_up', {
            method: 'GET'
        })
        .then(response => response.text())
        .then(signUphtml => {
            document.body.innerHTML = signUphtml;
            document.getElementById('body').classList.replace('loginBody', 'signup-body');
            document.querySelector("form").addEventListener("submit", function(event) {
                event.preventDefault(); // Previene el envío tradicional del formulario.
        
                var username = document.getElementById("username").value;
                var email = document.getElementById("email").value;
                var password = document.getElementById("password").value;
                var confirmPassword = document.getElementById("confirm-password").value;
        
                // Verifica si las contraseñas coinciden.
                if (password !== confirmPassword) {
                    document.getElementById("error-message").innerText = "Las contraseñas no coinciden";
                    document.getElementById("error-message").style.display = "block"; // Asegura que el mensaje de error sea visible.
                } else {
                    // Si las contraseñas coinciden, envía los datos al servidor.
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
                        // Aquí puedes manejar la respuesta del servidor.
                        // Por ejemplo, redirigir al usuario a la página de inicio de sesión o mostrar un mensaje de éxito.
                    })
                    .catch((error) => {
                        console.error('Error:', error);
                        // Aquí puedes manejar errores de la petición, como mostrar un mensaje al usuario.
                    });
        
                    // Opcional: limpia el mensaje de error si previamente se mostró uno.
                    document.getElementById("error-message").style.display = "none";
                }
            });
            document.getElementById('goback-button').addEventListener('click', function(){
                fetch('/', {
                    method:'GET'
                })
                .then(response => response.text())
                .then(loghtml => {
                    document.body.innerHTML = loghtml;
                    document.getElementById('body').classList.replace('signup-body', 'loginBody');
                });
            });
        });
    });
});
