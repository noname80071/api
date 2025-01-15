from sqlalchemy import create_engine, Column, Integer, String, Text, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Настройка базы данных
DATABASE_URL = "sqlite:///./test.db"  # SQLite база данных

Base = declarative_base()
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Модели
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    login = Column(String, unique=True, index=True)
    password = Column(String)
    FIO = Column(Text)
    identification_number = Column(Integer)
    role = Column(String)

class Test(Base):
    __tablename__ = 'tests'
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    theme = Column(String)
    description = Column(Text)
    answer = Column(String)
    teacher_id = Column(Integer)
    date_deadline = Column(Date)

# Функция для создания таблицы
def create_database():
    Base.metadata.create_all(bind=engine)

# Функция для получения сессии базы данных
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Создание таблиц при старте
create_database()
