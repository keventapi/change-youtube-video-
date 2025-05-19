# Projeto: Controle Remoto para YouTube via Extensão + Flask

## Tecnologias e linguagens usadas

- **Node.js**
- **Python 3.x**

### Bibliotecas principais

- `flask`
- `flask-socketio`

---

## Como instalar as dependências

### Backend (Python):

1. Crie um ambiente virtual (opcional, mas recomendado):
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```

2. Instale as dependências com pip:
   ```bash
   pip install flask flask-socketio
   ```

### Frontend (Extensão):

1. Instale as dependências do Node.js:
   ```bash
   npm install
   ```

2. Para empacotar o código da extensão, sempre rode:
   ```bash
   npm run build
   ```

---

## Como rodar

### Backend:

Basta executar:
```bash
python server.py
```

### Extensão do Chrome:

1. Ative o **modo desenvolvedor** no Chrome.
2. Clique em **"Carregar sem compactação"** e selecione a pasta `dist` (lembre de rodar `npm run build` antes!).
3. **IMPORTANTE:** Altere as constantes `ip` pelo seu **IPv4 local**. Elas estão localizadas em:
   - `template/home.html`
   - `src/background.js`

> A extensão ainda está funcionando em **modo local**.

---

## Funcionalidades

- O botão **"Next"** simula `Shift + N`, pulando para o próximo vídeo que o YouTube já preparou.
- O botão com o símbolo de **pausar/despausar** funciona como esperado.
- A **barra de volume** ajusta o som do vídeo, mas está com um pequeno bug: o YouTube tenta restaurar o volume anterior, o que pode causar uma leve oscilação.
- Os **botões de recomendações** levam diretamente aos vídeos recomendados pelo YouTube. Antigamente apresentavam bugs, mas atualmente estão estáveis. Caso encontre algum problema, documente e envie feedback.
- A funcionalidade de **colar URL** era um protótipo e não está funcionando. O botão "enviar" também fazia parte dela.

---

## Observações

- A extensão **interage apenas com o YouTube**. Ela **não modifica ou interfere em outros sites**.


