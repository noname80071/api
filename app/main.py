from fastapi import FastAPI
from routers import auth, tests  # Импортируем маршрутизатор

app = FastAPI()

# Подключаем маршрутизатор
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(tests.router, prefix='/tests', tags=['tests'])