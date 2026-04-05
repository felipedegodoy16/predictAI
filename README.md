# PredictAI

Aplicação para monitoramento de máquinas através de sensores e análise preditiva.

## Estrutura do Projeto

O projeto é dividido em:

- **[backend/](./backend)**: API REST construída com Django e Django Rest Framework (DRF), utilizando JWT para autenticação.
- **[frontend/](./frontend)**: Interface do usuário construída com Vue.js 3, Vite e Tailwind CSS para estilização moderna e responsiva.

## Como Executar

### Backend

1. Navegue até a pasta `backend`.
2. Crie um ambiente virtual: `python -m venv venv`.
3. Ative o ambiente virtual e instale as dependências: `pip install -r requirements.txt`.
4. Configure as variáveis de ambiente no arquivo `.env`.
5. Execute as migrações: `python manage.py migrate`.
6. Inicie o servidor: `python manage.py runserver`.

### Frontend

1. Navegue até a pasta `frontend`.
2. Instale as dependências: `npm install`.
3. Inicie o servidor de desenvolvimento: `npm run dev`.

## GitHub Repository

Este repositório está hospedado em: [https://github.com/felipedegodoy16/predictAI.git](https://github.com/felipedegodoy16/predictAI.git)
