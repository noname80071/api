from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, validator
from sqlalchemy.orm import Session
from datetime import datetime, date
from models import Test, get_db
from auth_utils import decode_token
from fastapi.security import OAuth2PasswordBearer

router = APIRouter()

# Объект для извлечения токена из заголовка Authorization
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")



# Модель для входных данных теста
class TestIn(BaseModel):
    title: str
    theme: str
    description: str
    answer: str
    teacher_id: int
    date_deadline: date

# ✅ GET-запрос для получения теста по ID (доступен всем)
@router.get("/{test_id}")
def get_test(test_id: int, db: Session = Depends(get_db)):
    test = db.query(Test).filter(Test.id == test_id).first()
    if not test:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Тест не найден"
        )
    return {
        "id": test.id,
        "title": test.title,
        "theme": test.theme,
        "description": test.description,
        "answer": test.answer,
        "teacher_id": test.teacher_id,
        "date_deadline": test.date_deadline
    }


# ✅ DELETE-запрос для удаления теста по ID (доступен только преподавателям)
@router.delete("/delete/{test_id}")
def delete_test(test_id: int, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    # Проверяем токен и роль пользователя
    token_data = decode_token(token)
    if token_data.role != "преподаватель":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Только преподаватели могут удалять тесты"
        )
    
    # Проверяем, существует ли тест
    test = db.query(Test).filter(Test.id == test_id).first()
    if not test:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Тест не найден"
        )
    
    # Удаляем тест
    db.delete(test)
    db.commit()
    return {"message": "Тест успешно удален"}

# Эндпоинт для создания нового теста
@router.post('/new')
def new(test: TestIn, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    # Декодируем токен и проверяем роль
    token_data = decode_token(token)
    if token_data.role != 'преподаватель':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Только преподаватели могут создавать тесты"
        )

    # Проверяем, существует ли тест с таким же названием
    db_test = db.query(Test).filter(Test.title == test.title).first()
    if db_test:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Тест уже существует'
        )

    # Создаем новый тест
    new_test = Test(
        title=test.title,
        theme=test.theme,
        description=test.description,
        answer=test.answer,
        teacher_id=token_data.login,  # Используем логин преподавателя как идентификатор
        date_deadline=test.date_deadline
    )
    db.add(new_test)
    db.commit()
    db.refresh(new_test)
    
    return {"message": "Тест добавлен"}
