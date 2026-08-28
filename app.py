from fastapi import FastAPI, Depends, HTTPException, Query, BackgroundTasks
from schemas import (RegisterRequest, LoginRequest,RegisterResponse, TokenResponse, ProjectCreate, ProjectResponse, PaginatedProjectsResponse,
                     ProjectUpdate,TaskCreate,TaskResponse,TaskListResponse,TaskUpdate)
from database import get_db
from auth import password_hash, create_access_token, get_current_user
from models import User, Project, Task
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from math import ceil
from services.email import send_welcome_email
from exceptions import (
    ProjectNotFound,
    TaskNotFound,
    UserAlreadyExists,
    InvalidCredentials,
)
from handlers import register_app_handlers
app = FastAPI(
    title="Task Management API",
    description="API for managing tasks and projects",
    version="1.0.0",
)

register_app_handlers(app)


SORT_FIELDS = {
    "name": Project.name,
    "created_at": Project.created_at,
    "category": Project.category,
}
TASK_SORT_FIELDS = {
    "title": Task.title,
    "created_at": Task.created_at
}
 

@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/register", status_code=201,response_model=RegisterResponse)
async def register(request: RegisterRequest, background_tasks: BackgroundTasks, db: AsyncSession = Depends(get_db)):
    existing =  await db.execute(
        select(User).where(User.email == request.email)
    )
    user = existing.scalar_one_or_none()
    
    if user:
        raise UserAlreadyExists()
    

    hashed_password = password_hash.hash(request.password)
    
    new_user = User(
        username=request.username,
        email=request.email,
        hashed_password=hashed_password
    )
    
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    background_tasks.add_task(
        send_welcome_email,
        new_user.email,
        new_user.username
    )
    
    return new_user

@app.post("/login", status_code=200)
async def login(request: LoginRequest, db: AsyncSession = Depends(get_db)):
    user = await db.execute(select(User).where(User.email == request.email))
    
    user = user.scalar_one_or_none()
    
    if not user:
        raise InvalidCredentials()
    
    if not password_hash.verify(
        request.password,
        user.hashed_password
    ):
        raise InvalidCredentials()
    
    token = create_access_token(request.email)
    
    return TokenResponse(
        access_token=token,
        token_type="Bearer"
    )      
  
@app.post("/projects", status_code=201, response_model=ProjectResponse)
async def create_project(request: ProjectCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    
    project = Project(
        name=request.name,
        category=request.category,
        description=request.description,
        owner_id=current_user.id
    )
    
    db.add(project)
    await db.commit()
    await db.refresh(project)
    
    return project      
        


@app.get("/projects", response_model=PaginatedProjectsResponse)
async def get_projects(page: int = Query(1, ge=1), limit: int = Query(10, ge=1, le=100),sort: str = Query(default="created_at"),search: str | None = Query(None), db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    offset = (page - 1) * limit
    
    is_descending = sort.startswith("-")
    
    sort_field = sort[1:] if is_descending else sort 
    
    column = SORT_FIELDS.get(sort_field)
    
    if column is None:
        raise HTTPException(
            status_code=400,
            detail="Invalid sort field"
        )
        
    ordered_column =  (column.desc() if is_descending else column.asc())     
        
    statement = (select(Project).where(Project.owner_id == current_user.id))
    
    if search:
        statement = statement.where(Project.name.ilike(f"%{search}%"))
    
    statement = statement.order_by(ordered_column)
    
    statement = statement.offset(offset).limit(limit)
        
        
    projects = await db.execute(statement)
    projects = projects.scalars().all()
    
    count_statement = select(func.count(Project.id)).where(Project.owner_id == current_user.id)
    total_projects =  await db.execute(count_statement)
    total_projects = total_projects.scalar()
    
    total_pages = ceil(total_projects / limit)
    has_next = page < total_pages
    has_previous = page > 1
    
    
    
    return {
            "items": projects,
            "page": page,
            "limit": limit,
            "total": total_projects,
            "total_pages": total_pages,
            "has_next": has_next,
            "has_previous": has_previous,
        }
         
@app.get("/projects/{project_id}", response_model=ProjectResponse)
async def get_project(project_id: int, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    
    result = await db.execute(
        select(Project)
        .where(Project.id==project_id, Project.owner_id==current_user.id)
        )
    
    project = result.scalar_one_or_none()
    
    if project is None:
        raise ProjectNotFound(project_id=project_id)
    return project    

@app.patch("/projects/{project_id}", response_model=ProjectResponse)
async def project_update(project_id: int,request: ProjectUpdate,current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    statement = select(Project).where(Project.id==project_id,Project.owner_id == current_user.id)
    result =  await db.execute(statement)
    
    project = result.scalar_one_or_none()
    if project is None:
        raise ProjectNotFound(project_id=project_id)
    
    update_data = request.model_dump(exclude_unset=True)
            
    for field, value in update_data.items():
        setattr(project,field,value)
    
    await db.commit()
    await db.refresh(project)    
        
    return project   

@app.delete("/projects/{project_id}", status_code=204)
async def project_delete(project_id: int, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    statement = select(Project).where(project_id == Project.id, Project.owner_id == current_user.id)
    result = await db.execute(statement)
    
    project = result.scalar_one_or_none()
    
    if project is None:
        raise ProjectNotFound(project_id=project_id)
    
    await db.delete(project)
    await db.commit()
    
    return None

@app.post("/projects/{project_id}/tasks", response_model=TaskResponse,status_code=201)
async def create_task(project_id: int,request: TaskCreate, db: AsyncSession = Depends(get_db),current_user: User = Depends(get_current_user)):
    statement = select(Project).where(Project.id==project_id,Project.owner_id==current_user.id)
    result = await db.execute(statement)
    project = result.scalar_one_or_none()
    
    if project is None:
        raise ProjectNotFound(project_id=project_id)
    
    task = Task(
        title=request.title,
        description=request.description,
        priority=request.priority,
        due_date=request.due_date,
        project=project
    )
    
    db.add(task)
    await db.commit()
    await db.refresh(task)
    
    return task
            
@app.get("/projects/{project_id}/tasks", response_model=TaskListResponse)
async def get_tasks(project_id: int,page: int = Query(1,ge=1),limit: int = Query(10, ge=1,le=100),sort: str = Query(default="created_at"),search: str | None = Query(None),current_user: User = Depends(get_current_user),db: AsyncSession = Depends(get_db)):
    offset = (page - 1) * limit
    
    statement = select(Project).where(Project.id==project_id,Project.owner_id==current_user.id)
    result = await db.execute(statement)
    project = result.scalar_one_or_none()
    
    if project is None:
        raise ProjectNotFound(project_id=project_id)
    
    is_descending = sort.startswith("-")
    sort_field = sort[1:] if is_descending else sort
    column = TASK_SORT_FIELDS.get(sort_field)
    if column is None:
            raise HTTPException(
                status_code=400,
                detail="Invalid sort field"
            )
            
    ordered_column =  (column.desc() if is_descending else column.asc())
        
    
    statement = select(Task).where(Task.project == project)
    
    if search:
        statement = statement.where(Task.title.ilike(f"%{search}%"))
    
    statement = (
        statement.order_by(ordered_column)
        .offset(offset)
        .limit(limit)
        )    
    result = await db.execute(statement)
    tasks = result.scalars().all()
    
    count_statement = select(func.count(Task.id)).where(Task.project_id == project_id)
    result = await db.execute(count_statement)
    total_tasks = result.scalar()
    
    total_pages = max(1,ceil(total_tasks / limit))
    has_next = page < total_pages
    has_previous  = page > 1
    
    
    return {
        "items": tasks,
        "page": page,
        "limit": limit,
        "total": total_tasks,
        "total_pages": total_pages,    
        "has_next": has_next,
        "has_previous": has_previous
    }   
 
@app.get("/tasks/{task_id}",response_model=TaskResponse)
async def get_task(task_id: int, current_user: User = Depends(get_current_user),db: AsyncSession = Depends(get_db)):
    
    statement = select(Task).join(Project).where(Task.id==task_id,Project.owner_id==current_user.id)
    
    result = await db.execute(statement)
    task = result.scalar_one_or_none()
    
    if task is None:
        raise TaskNotFound(task_id=task_id)
    
    return task    

@app.patch("/tasks/{task_id}",response_model=TaskResponse)
async def update_task(task_id: int, request:TaskUpdate, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    
    statement = (
        select(Task)
        .join(Project)
        .where(
            Task.id==task_id,
            Project.owner_id==current_user.id
        )
    )        
    
    result = await db.execute(statement)
    task = result.scalar_one_or_none()
    
    if task is None:
        raise TaskNotFound(task_id=task_id)
    
    update_data = request.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(task, field, value)
    
    await db.commit()
    await db.refresh(task)
    
    return task        
        
@app.delete("/tasks/{task_id}",status_code=204)
async def delete_task(task_id: int, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    statement = (
        select(Task)
        .join(Project)
        .where(
            Task.id==task_id,
            Project.owner_id==current_user.id
        )
    )        
    
    result = await db.execute(statement)
    task = result.scalar_one_or_none()
    
    if task is None:
        raise TaskNotFound(task_id=task_id)
    
    await db.delete(task)
    await db.commit()
    return    