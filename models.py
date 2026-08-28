from enum import Enum
from database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, DateTime, ForeignKey, Boolean, Date
from datetime import datetime,UTC, date
from sqlalchemy import Enum as SqlEnum



class Priority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"

class User(Base):
    __tablename__ = 'users'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50),unique=True,nullable=False,index=True)
    email: Mapped[str] = mapped_column(String(255),unique=True,nullable=False,index=True)
    hashed_password: Mapped[str] = mapped_column(String(255),nullable=False)
    bio: Mapped[str | None] = mapped_column(String(255),nullable=True)
    projects: Mapped[list['Project']] = relationship(back_populates='owner',cascade='all, delete-orphan')
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),default=lambda:datetime.now(UTC))

class Project(Base):
    __tablename__ = 'projects'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50),nullable=False)
    description: Mapped[str | None] = mapped_column(String(255),nullable=True)
    category: Mapped[str | None] = mapped_column(String(100),nullable=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey('users.id',ondelete='CASCADE'),index=True,nullable=False)
    owner: Mapped['User'] = relationship(back_populates='projects')
    tasks: Mapped[list['Task']] = relationship(back_populates='project',cascade='all, delete-orphan')
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),default=lambda:datetime.now(UTC))
   


class Task(Base):
    __tablename__ = 'tasks'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100),nullable=False)
    description: Mapped[str | None] = mapped_column(String(255),nullable=True)
    completed: Mapped[bool] = mapped_column(Boolean,default=False,nullable=False)
    priority: Mapped[Priority] = mapped_column(SqlEnum(Priority),default=Priority.MEDIUM,nullable=False)
    due_date: Mapped[date | None] = mapped_column(Date,nullable=True)
    project_id: Mapped[int] = mapped_column(ForeignKey('projects.id',ondelete='CASCADE'),index=True,nullable=False)
    project: Mapped['Project'] = relationship(back_populates='tasks')
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),default=lambda: datetime.now(UTC))
    
    