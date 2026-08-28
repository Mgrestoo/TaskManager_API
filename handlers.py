from fastapi import Request, FastAPI
from fastapi.responses import JSONResponse

from exceptions import (
    ProjectNotFound,
    TaskNotFound,
    UserAlreadyExists,
    InvalidCredentials,
)



async def project_not_found_handler(request: Request, exc: ProjectNotFound):
    return JSONResponse(
        status_code=404,
        content={"message": "Project not found"}
    )
    

async def task_not_found_handler(request: Request, exc: TaskNotFound):
    return JSONResponse(
        status_code=404,
        content={"message": "Task not found"}
    )


async def user_already_exists_handler(request: Request, exc: UserAlreadyExists):
    return JSONResponse(
        status_code=409,
        content={"message": str(exc)}
    )  
    

async def invalid_credentials_handler(request: Request, exc: InvalidCredentials):
    return JSONResponse(
        status_code=401,
        content={"message": str(exc)}
    )          
    
def register_app_handlers(app: FastAPI) -> None:
    app.add_exception_handler(ProjectNotFound, project_not_found_handler)
    app.add_exception_handler(TaskNotFound, task_not_found_handler)
    app.add_exception_handler(UserAlreadyExists, user_already_exists_handler)
    app.add_exception_handler(InvalidCredentials, invalid_credentials_handler)    