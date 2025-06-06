chrome.storage.local.get('token', (data) => {
  const ip = '192.168.5.102';

  // Injetar estilo básico para inputs, botões e mensagens
  const style = document.createElement('style');
  style.textContent = `
    body{
      background-color: #111;
    }
    #login, #status {
      font-family: Arial, sans-serif;
      color: white;
      background-color: #111;
      padding: 16px;
      border-radius: 8px;
      width: 280px;
      margin: auto;
      margin-top: 20px;
      display: flex;
      flex-direction: column;
      size: 20px;
      gap: 10px;
    }
    input[type="text"], input[type="password"] {
      padding: 8px;
      border-radius: 6px;
      border: none;
      font-size: 1rem;
      width: 100%;
      box-sizing: border-box;
      height: 38px;
    }

    input[type="button"] {
      padding: 10px 0;
      border-radius: 6px;
      border: none;
      background-color: #4caf50;
      color: white;
      font-weight: 600;
      cursor: pointer;
      font-size: 1rem;
      transition: background-color 0.3s ease;
    }
    input[type="button"]:hover {
      background-color: #45a049;
    }
    #back {
      background-color: #222;
      width: 40px;
      font-size: 1.2rem;
      font-weight: bold;
      align-self: flex-start;
    }
    #back:hover {
      background-color: #555;
    }
    #auth {
      color: #ff6666;
      font-weight: bold;
      min-height: 20px;
    }
    p {
      margin: 0 0 10px 0;
      font-weight: bold;
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

    let logged = document.getElementById('login');
    logged.innerHTML = "<p>Usuário logado!</p>";

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
    let login_div = document.getElementById('login');
    login_div.innerHTML = ''; // Limpar antes de criar

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
    let login_div = document.getElementById('login');
    login_div.innerHTML = ''; // limpar antes

    let back = document.createElement('input');
    back.id = "back";
    back.type = "button";
    back.value = "<";
    
    let username_tag = document.createElement('input');
    username_tag.id = "username";
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
