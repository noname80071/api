from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from pydantic import BaseModel
from sqlalchemy.orm import Session
from models import User, get_db
from auth_utils import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    decode_token,
)

router = APIRouter()

# Создаем объект для извлечения токена из заголовка Authorization
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# Модели Pydantic для регистрации и токенов
class UserReg(BaseModel):
    login: str
    password: str
    FIO: str
    identification_number: int
    role: str

class UserLog(BaseModel):
    login: str
    password: str

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

# Эндпоинт для регистрации пользователя
@router.post("/register")
def register(user: UserReg, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.login == user.login).first()
    if db_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Пользователь уже зарегистрирован.")
    
    new_user = User(login=user.login, password=get_password_hash(user.password), FIO=user.FIO, identification_number=user.identification_number, role=user.role)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "Пользователь зарегистрирован"}

# Эндпоинт для логина
@router.post("/login", response_model=Token)
def login(user: UserLog, db: Session = Depends(get_db)):
    # Ищем пользователя в базе данных
    db_user = db.query(User).filter(User.login == user.login).first()
    
    # Проверяем существование пользователя и правильность пароля
    if not db_user or not verify_password(user.password, db_user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Неправильный логин или пароль")
    
    # Берем роль пользователя из базы данных
    role = db_user.role
    
    # Создаем токены с ролью
    access_token = create_access_token(data={"login": user.login, "role": role})
    refresh_token = create_refresh_token(data={"login": user.login, "role": role})
    
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

# Эндпоинт для получения информации о текущем пользователе
@router.get("/users/me")
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    token_data = decode_token(token)
    db_user = db.query(User).filter(User.login == token_data.login).first()
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return {"login": db_user.login, "role": db_user.role}

# Эндпоинт для обновления токенов
@router.post("/token/refresh", response_model=Token)
def refresh_token(refresh_token: str, db: Session = Depends(get_db)):
    try:
        token_data = decode_token(refresh_token)
        db_user = db.query(User).filter(User.login == token_data.login).first()
        if not db_user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

        access_token = create_access_token(data={"sub": db_user.login})
        new_refresh_token = create_refresh_token(data={"sub": db_user.login})
        return {"access_token": access_token, "refresh_token": new_refresh_token, "token_type": "bearer"}

    except HTTPException:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired refresh token")
                                                                                                                                                        