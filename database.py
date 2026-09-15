from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

# Создаем файл базы данных
DATABASE_URL = "sqlite:///./planner.db"

Base = declarative_base()

# --- ТАБЛИЦА ПОЛЬЗОВАТЕЛЕЙ ---
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)  # В учебных целях храним просто строку
    
    # Связь: один пользователь может иметь много задач
    tasks = relationship("Task", back_populates="owner")

# --- ТАБЛИЦА ЗАДАЧ ---
class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    category = Column(String)
    priority = Column(String)   # Будет приходить от ИИ
    time_est = Column(Float)    # Будет приходить от ИИ
    status = Column(String, default="todo") # todo, doing, done
    
    # Внешний ключ: привязываем задачу к ID пользователя
    user_id = Column(Integer, ForeignKey("users.id"))
    
    # Обратная связь
    owner = relationship("User", back_populates="tasks")

# Настройка подключения
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    # Создает все таблицы (tasks и users), если их еще нет
    Base.metadata.create_all(bind=engine)