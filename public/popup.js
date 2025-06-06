chrome.storage.local.get('token', (data) => {
  const ip = '192.168.5.102';

  // Injetar estilo básico para inputs, botões e mensagens
  const style = document.createElement('style');
  style.textContent = `
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }

    body {
        background-color: black;
        color: white;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        height: 100vh;
        width: 100vw;
        padding: 10px;
        overflow: hidden;
    }

    #login-form {
        background: rgba(255, 255, 255, 0.05);
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 0 10px rgba(255, 255, 255, 0.1);
        width: 100%;
        max-width: 300px;
        display: flex;
        flex-direction: column;
        gap: 12px;
    }

    input[type="text"],
    input[type="password"] {
        padding: 8px 12px;
        font-size: 0.95rem;
        border-radius: 8px;
        border: none;
        background-color: #222;
        color: white;
        outline-offset: 2px;
        transition: outline-color 0.3s ease;
    }

    input[type="text"]:focus,
    input[type="password"]:focus {
        outline: 2px solid #4caf50;
    }

    input[type="button"] {
        padding: 10px;
        background-color: #333;
        border: none;
        border-radius: 8px;
        color: white;
        font-weight: 600;
        cursor: pointer;
        transition: background-color 0.3s ease;
        user-select: none;
        font-size: 0.95rem;
    }

    input[type="button"]:active {
        background-color: rgb(76, 175, 79);
    }

    #msg {
        color: #f44336;
        font-weight: 600;
        text-align: center;
        min-height: 1.2em;
        font-size: 0.85rem;
        user-select: none;
    }

    #back {
        position: absolute;
        top: 10px;
        left: 10px;
        padding: 6px 10px;
        font-size: 1rem;
        background-color: #222;
        border: none;
        border-radius: 6px;
        color: white;
        cursor: pointer;
        transition: background-color 0.3s ease;
    }

    #back:active {
        background-color: rgb(76, 175, 79);
    }
    p {
      font-size: 0.9rem;
      color: #4caf50;
      font-weight: 600;
      text-align: center;
      margin-top: 10px;
      user-select: none;
    }
`;
  document.head.appendChild(style);

  function logged_body() {
    chrome.runtime.sendMessage({ action: "login" }, (res) => {
      if (chrome.runtime.lastError) {
        console.error("Erro ao enviar solicitação de login para o servidor:", chrome.runtime.lastError.message);
      } else {
        console.log('Login efetuado com sucesso');
      }
    });

    let logged = document.getElementById('login-form');
    logged.innerHTML = ""
    logged.innerHTML = "<p>Usuário logado</p>";

    let logout = document.createElement('input');
    logout.type = "button";
    logout.id = "logout";
    logout.value = "Logout";
    logout.addEventListener("click", () => {
      chrome.storage.local.remove('token', () => {
        logged.innerHTML = '';
        unlogged_body();
      });
    });

    logged.appendChild(logout);
  }

  function unlogged_body() {
    let login_div = document.getElementById('login-form');
    login_div.innerHTML = '';

    let username_tag = document.createElement('input');
    username_tag.id = "username";
    username_tag.type = "text";
    username_tag.placeholder = "Usuário";

    let password_tag = document.createElement('input');
    password_tag.id = "password";
    password_tag.placeholder = "Senha";
    password_tag.type = "password";

    let submit = document.createElement('input');
    submit.id = "login";
    submit.value = "Login";
    submit.type = "button";

    let signup = document.createElement('input');
    signup.id = "register";
    signup.value = "Cadastrar";
    signup.type = "button";

    let wrong_credentials = document.createElement('div');
    wrong_credentials.id = "auth";

    login_div.appendChild(username_tag);
    login_div.appendChild(password_tag);
    login_div.appendChild(submit);
    login_div.appendChild(signup);
    login_div.appendChild(wrong_credentials);

    submit.addEventListener('click', () => {
      const username = username_tag.value.trim();
      const password = password_tag.value.trim();

      if (!username || !password) {
        wrong_credentials.innerText = "Preencha usuário e senha.";
        return;
      }
      wrong_credentials.innerText = '';

      fetch(`http://${ip}:5000/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        credentials: 'include',
        body: JSON.stringify({ usuario: username, senha: password })
      })
        .then(response => response.json())
        .then(res => {
          if (res.status) {
            chrome.storage.local.set({ token: res.token });
            login_div.innerHTML = "";
            logged_body();
          } else {
            wrong_credentials.innerText = "Usuário ou senha incorretos.";
            console.log(res.msg)
          }
        })
        .catch(error => {
          console.error("Erro na requisição:", error);
          wrong_credentials.innerText = "Erro na conexão com o servidor.";
        });
    });

    signup.addEventListener('click', () => {
      login_div.innerHTML = '';
      signup_page();
    });
  }

  function signup_page() {
    let login_div = document.getElementById('login-form');
    login_div.innerHTML = ''; // limpar antes

    let back = document.createElement('input');
    back.id = "back";
    back.type = "button";
    back.value = "<";
    
    let username_tag = document.createElement('input');
    username_tag.id = "username";
    username_tag.type = "text";
    username_tag.placeholder = "Usuário";

    let password_tag = document.createElement('input');
    password_tag.id = "password";
    password_tag.placeholder = "Senha";
    password_tag.type = "password";

    let submit = document.createElement('input');
    submit.id = "submit";
    submit.value = "Cadastrar";
    submit.type = "button";

    let wrong_credentials = document.createElement('div');
    wrong_credentials.id = "auth";

    login_div.appendChild(back);
    login_div.appendChild(username_tag);
    login_div.appendChild(password_tag);
    login_div.appendChild(submit);
    login_div.appendChild(wrong_credentials);

    submit.addEventListener('click', () => {
      const username = username_tag.value.trim();
      const password = password_tag.value.trim();

      if (!username || !password) {
        wrong_credentials.innerText = "Preencha usuário e senha.";
        return;
      }
      wrong_credentials.innerText = '';

      fetch(`http://${ip}:5000/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ usuario: username, senha: password })
      })
        .then(response => response.json())
        .then(res => {
          if (res.status) {
            chrome.storage.local.set({ token: res.token });
            login_div.innerHTML = "";
            logged_body();
          } else {
            wrong_credentials.innerText = "Usuário já existe.";
          }
        })
        .catch(error => {
          console.error("Erro na requisição:", error);
          wrong_credentials.innerText = "Erro na conexão com o servidor.";
        });
    });

    back.addEventListener('click', () => {
      login_div.innerHTML = '';
      unlogged_body();
    });
  }

  // Inicialização:
  if (data.token) {
    logged_body();
  } else {
    unlogged_body();
  }
});
