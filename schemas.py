from pydantic import BaseModel, ConfigDict, Field, field_validator, EmailStr
from datetime import datetime, date
from models import Priority

class ProjectBase(BaseModel):
    name: str = Field(min_length=3,max_length=50)
    @field_validator("name")
    @classmethod
    def validate_name(cls,value: str):
        value = value.strip()
        if not value:
            raise ValueError('Project name cannot be empty') 
        return value
    
    description: str | None = Field(default=None,max_length=255)
    category: str | None = Field(default=None,max_length=50)
    
class TaskBase(BaseModel):
    title: str = Field(min_length=3,max_length=100) 
    @field_validator("title")
    @classmethod
    def validate_title(cls,value):
        value = value.strip()
        
        if not value:
            raise ValueError(
                "Title cannot be empty"
            )
        return value      
    
    description: str | None = Field(default=None,max_length=255)
    priority: Priority = Priority.MEDIUM
    completed: bool = False
    due_date: date | None = None 

class RegisterRequest(BaseModel):
    username: str = Field(min_length=3,max_length=50)
    @field_validator("username")
    @classmethod
    def validate_username(cls,value):
        value = value.strip()
        if not value:
            raise ValueError(
                "Username cannot be empty"
            )
        return value    
    email: EmailStr            
    password: str = Field(min_length=8,max_length=255)
    @field_validator("password")
    def validate_password(cls,value):
        if value != value.strip():
            raise ValueError(
                "Password must not contain leading or trailing whitespace."
            )
        if value.isspace():
            raise ValueError(
                "Password cannot consist only of whitespaces"
            )    
        return value   
    
    bio: str | None = None
    
class RegisterResponse(BaseModel):
    id: int
    username: str
    email: str
    bio: str | None
    created_at: datetime 
    
    model_config = ConfigDict(from_attributes=True)   

class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8,max_length=255)
    @field_validator("password")
    def validate_password(cls,value):
        if value != value.strip():
            raise ValueError(
             "Password must not contain leading or trailing whitespace."
            )
        if value.isspace():
            raise ValueError(
                "Password cannot consist only of whitespaces"
            )    
        return value 
  
class TokenResponse(BaseModel):
    access_token: str
    token_type: str


class ProjectCreate(ProjectBase):
    pass
    
class ProjectUpdate(ProjectBase):
    name: str | None = Field(
        default=None,
        min_length=3,
        max_length=50
    )

    
class ProjectResponse(BaseModel):
   
    id: int
    name: str
    description: str | None = None
    category: str | None = None
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
    
class PaginatedProjectsResponse(BaseModel):
    items: list[ProjectResponse]
    page: int
    limit: int
    total: int
    total_pages: int
    has_next: bool
    has_previous: bool    
    
  
class TaskCreate(TaskBase):
    pass
    
class TaskUpdate(TaskBase):
    title: str | None = None
    
    
class TaskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    description: str | None = None
    completed: bool
    priority: Priority
    due_date: date | None = None
    created_at: datetime
    

class TaskListResponse(BaseModel):
    items: list[TaskResponse]
    page: int
    limit: int
    total: int
    total_pages: int
    has_next: bool
    has_previous: bool
    
        