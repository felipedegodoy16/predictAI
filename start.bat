@echo off
echo Iniciando PredictAI...

echo Iniciando Backend...
start "Backend PredictAI" cmd /k "cd backend && venv\Scripts\activate && python manage.py runserver"

echo Iniciando Frontend...
start "Frontend PredictAI" cmd /k "cd frontend && npm run dev"

echo Tudo iniciado!
