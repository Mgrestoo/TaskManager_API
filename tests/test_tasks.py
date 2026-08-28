from models import Project, Task, User


async def test_create_task(authenticated_client, db, test_user):
    project = Project(
        name="Test Project",
        owner_id=test_user.id,
    )

    db.add(project)
    await db.commit()
    await db.refresh(project)

    response = await authenticated_client.post(
        f"/projects/{project.id}/tasks",
        json={
            "title": "Build API",
            "description": "Implement the task endpoint",
            "priority": "HIGH",
            "due_date": "2026-08-20",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["title"] == "Build API"
    assert data["priority"] == "HIGH"
    assert data["due_date"] == "2026-08-20"

    task = await db.get(Task, data["id"])

    assert task is not None
    assert task.project_id == project.id
    
async def test_create_task_project_not_found(authenticated_client):
    response = await authenticated_client.post(
        "/projects/999999/tasks",
        json={
            "title": "Build API",
        },
    )

    assert response.status_code == 404 
    
async def test_create_task_in_other_users_project(
    authenticated_client,
    db,
):
    other_user = User(
        username="otheruser",
        email="other@example.com",
        hashed_password="test-hash",
    )

    db.add(other_user)
    await db.commit()
    await db.refresh(other_user)

    project = Project(
        name="Private Project",
        owner_id=other_user.id,
    )

    db.add(project)
    await db.commit()
    await db.refresh(project)

    response = await authenticated_client.post(
        f"/projects/{project.id}/tasks",
        json={
            "title": "Unauthorized Task",
        },
    )

    assert response.status_code == 404  
    
async def test_create_task_default_priority(
    authenticated_client,
    db,
    test_user,
):
    project = Project(
        name="Test Project",
        owner_id=test_user.id,
    )

    db.add(project)
    await db.commit()
    await db.refresh(project)

    response = await authenticated_client.post(
        f"/projects/{project.id}/tasks",
        json={
            "title": "Build API",
        },
    )

    assert response.status_code == 201
    assert response.json()["priority"] == "MEDIUM"         
 
async def test_list_tasks(authenticated_client, db, test_user):
    project = Project(
        name="Test Project",
        owner_id=test_user.id,
    )

    db.add(project)
    await db.commit()
    await db.refresh(project)

    tasks = [
        Task(title="Task One", project_id=project.id),
        Task(title="Task Two", project_id=project.id),
        Task(title="Task Three", project_id=project.id),
    ]

    db.add_all(tasks)
    await db.commit()

    response = await authenticated_client.get(
        f"/projects/{project.id}/tasks"
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data["items"]) == 3
    assert data["total"] == 3
    assert data["page"] == 1
    assert data["limit"] == 10
    assert data["total_pages"] == 1
    assert data["has_next"] is False
    assert data["has_previous"] is False    
    
async def test_list_tasks_pagination(
    authenticated_client,
    db,
    test_user,
):
    project = Project(
        name="Test Project",
        owner_id=test_user.id,
    )
    
    db.add(project)
    await db.commit()
    await db.refresh(project)
    
    for i in range(15):
        db.add(
            Task(
                title=f"Task {1}",
                project_id=project.id,
            )
        ) 
    await db.commit()
    
    response = await authenticated_client.get(
        f"/projects/{project.id}/tasks?page=1&limit=10"
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert len(data["items"]) == 10
    assert data["total"] == 15
    assert data["total_pages"] == 2
    assert data["has_next"] is True
    assert data["has_previous"] is False
