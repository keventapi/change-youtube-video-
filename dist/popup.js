chrome.storage.local.get('token', (data) => {
  const ip = '192.168.5.102';

  function logged_body() {
    chrome.runtime.sendMessage({action: "login"}, (res) => {
      if (chrome.runtime.lastError) {
          console.error("erro ao enviar solicitação de login para o servidor:", chrome.runtime.lastError.message);
        }else {
          console.log('login efetuado com sucesso')
        }
    })

    let logged = document.getElementById('login')
    logged.innerHTML = "<p>Usuário logado!</p>";
    let logout = document.createElement('input')
    logout.type = "button"
    logout.id = "logout"
    logout.value = "logout"
    logout.addEventListener("click", () => {
      chrome.storage.local.remove('token', () => {
        logged.innerHTML = ''
        unlogged_body()
      })
    })
    logged.appendChild(logout)
  }

  function unlogged_body() {
    let username_tag = document.createElement('input');
    username_tag.id = "username";
    username_tag.placeholder = "Usuário";

    let password_tag = document.createElement('input');
    password_tag.id = "password";
    password_tag.placeholder = "Senha";
    password_tag.type = "password";

    let submit = document.createElement('input');
    submit.id = "submit";
    submit.value = "Login";
    submit.type = "button";

    let signup = document.createElement('input');
    signup.id = "signup";
    signup.value = "signup";
    signup.type = "button";

    let wrong_credentials = document.createElement('div');
    wrong_credentials.id = "auth";

    let login_div = document.getElementById('login');
    login_div.appendChild(username_tag);
    login_div.appendChild(password_tag);
    login_div.appendChild(submit);
    login_div.appendChild(signup)
    login_div.appendChild(wrong_credentials);


    submit.addEventListener('click', () => {
      let username = document.getElementById("username").value;
      let password = document.getElementById("password").value;
      fetch(`http://${ip}:5000/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        credentials: 'include',
        body: JSON.stringify({
          usuario: username,
          senha: password
        })
      })
      .then(response => response.json())
      .then((res) => {
        if (res.status) {
          chrome.storage.local.set({token: res.token});
          document.getElementById('login').innerHTML = "";
          logged_body();
        } else {
          document.getElementById('auth').innerText = "Usuário ou senha incorretos.";
        }
      })
      .catch((error) => {
        console.error("Erro na requisição:", error);
        document.getElementById('auth').innerText = "Erro na conexão com o servidor.";
      });
    });

    signup.addEventListener('click', () => {
      login_div.innerHTML = ''
      signup_page()
    })
  }

  function signup_page(){
    let back = document.createElement('input')
    back.id = "back"
    back.type = "button"
    back.value = "<"
    
    let username_tag = document.createElement('input');
    username_tag.id = "username";
    username_tag.placeholder = "Usuário";

    let password_tag = document.createElement('input');
    password_tag.id = "password";
    password_tag.placeholder = "Senha";
    password_tag.type = "password";

    let submit = document.createElement('input');
    submit.id = "submit";
    submit.value = "register";
    submit.type = "button";

    let wrong_credentials = document.createElement('div');
    wrong_credentials.id = "auth";

    let login_div = document.getElementById('login');
    login_div.appendChild(back)
    login_div.appendChild(username_tag);
    login_div.appendChild(password_tag);
    login_div.appendChild(submit);
    login_div.appendChild(wrong_credentials);
    


    submit.addEventListener('click', () => {
      let username = document.getElementById("username").value;
      let password = document.getElementById("password").value;
      fetch(`http://${ip}:5000/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        credentials: 'include',
        body: JSON.stringify({
          usuario: username,
          senha: password
        })
      })
      .then(response => response.json())
      .then((res) => {
        if (res.status) {
          chrome.storage.local.set({token: res.token});
          document.getElementById('login').innerHTML = "";
          logged_body();
        } else {
          document.getElementById('auth').innerText = "Usuário ja existe.";
        }
      })
      .catch((error) => {
        console.error("Erro na requisição:", error);
        document.getElementById('auth').innerText = "Erro na conexão com o servidor.";
      });
    });
    back.addEventListener('click', () => {
      login_div.innerHTML = ''
      unlogged_body()
    })
  }

  console.log(data)
  if (data.token) {
    logged_body();
  } else {
    unlogged_body();
  }
});
