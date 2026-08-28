class ProjectNotFound(Exception):
    def __init__(self,project_id: int):
        self.project_id = project_id
        super().__init__(f"Project {project_id} not found")

class TaskNotFound(Exception):
    def __init__(self, task_id: int):
        self.task_id = task_id
        super().__init__(f"Task {task_id} not found")

class UserAlreadyExists(Exception):
    def __init__(self,message: str="User already exists"):
        super().__init__(message)

class InvalidCredentials(Exception):
    def __init__(self,message: str="Invalid credentials"):
        super().__init__(message)
