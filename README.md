# PredictAI

Aplicação para monitoramento de máquinas através de sensores e análise preditiva.

## Como Baixar e Rodar o Projeto

Caso você tenha baixado (ou clonado) este projeto do GitHub, siga os passos abaixo para configurá-lo e executá-lo na sua máquina:

```bash
git clone https://github.com/felipedegodoy16/predictAI.git
cd predictAI
```

## Estrutura do Projeto

O projeto é dividido em duas partes principais:

- **[backend/](./backend)**: API REST construída com Django e Django Rest Framework (DRF), utilizando JWT para autenticação.
- **[frontend/](./frontend)**: Interface do usuário construída com Vue.js 3, Vite e Tailwind CSS para estilização moderna e responsiva.

---

## Como Executar

### Configurando o Backend

1. Navegue até a pasta `backend`:
   ```bash
   cd backend
   ```

2. Crie um ambiente virtual (recomendado):
   - **No Windows:** `python -m venv venv`
   - **No Linux/Mac:** `python3 -m venv venv`

3. Ative o ambiente virtual:
   - **No Windows (PowerShell/CMD):** `.\venv\Scripts\activate`
   - **No Git Bash (Windows) ou Linux/Mac:** `source venv/Scripts/activate` ou `source venv/bin/activate`

4. Instale as dependências do Python:
   ```bash
   pip install -r requirements.txt
   ```

5. Configure as variáveis de ambiente:
   - Na pasta `backend`, existe um arquivo chamado `.env.example`.
   - Crie um novo arquivo chamado `.env` no mesmo local e copie tudo de dentro de `.env.example` para ele.
   - O arquivo `.env` serve para armazenar credenciais sensíveis (como senhas de banco e e-mail). O arquivo `.env.example` mostra quais variáveis precisam ser preenchidas. Preencha o `.env` com suas próprias credenciais validas.

6. Execute as migrações para criar o banco de dados:
   ```bash
   python manage.py migrate
   ```

7. Inicie o servidor do backend:
   ```bash
   python manage.py runserver
   ```
O backend ficará rodando em `http://127.0.0.1:8000/`.

---

### Configurando o Frontend

Abra uma **nova janela ou aba de terminal** na raiz do projeto (deixe o backend rodando na anterior):

1. Navegue até a pasta `frontend`:
   ```bash
   cd frontend
   ```

2. Instale as dependências (você precisará ter o [Node.js](https://nodejs.org/) instalado):
   ```bash
   npm install
   ```

3. Inicie o servidor de desenvolvimento do frontend:
   ```bash
   npm run dev
   ```

O console mostrará o endereço (geralmente `http://localhost:5173/`). Abra este endereço em seu navegador.

---

## GitHub Repository

Este repositório está hospedado em: [https://github.com/felipedegodoy16/predictAI.git](https://github.com/felipedegodoy16/predictAI.git)
