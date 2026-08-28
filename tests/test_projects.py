from models import Project, User


async def test_get_project(authenticated_client, db, test_user):
    project = Project(
        name="Trading API",
        owner_id=test_user.id
    )
    
    db.add(project)
    await db.commit()
    await db.refresh(project)
    
    response = await authenticated_client.get(
        f"/projects/{project.id}"
    )
    
    assert response.status_code == 200
    
    data = response.json()
    
    assert data["id"] == project.id
    assert data["name"] == "Trading API"
   
async def test_get_project_not_found(authenticated_client):
    response = await authenticated_client.get("/projects/999")
    
    assert response.status_code == 404
    assert response.json()["message"] == "Project not found"

async def test_user_cannot_access_other_users_project(authenticated_client, db, test_user):
    other_user = User(
        username="otheruser",
        email="other@example.com",
        hashed_password="test-hash"
    )
    db.add(other_user)
    await db.commit()
    await db.refresh(other_user)
    
    other_project = Project(
        name="Private Project",
        owner_id=other_user.id
    )
    
    db.add(other_project)
    await db.commit()
    await db.refresh(other_project)
    
    response = await authenticated_client.get(
        f"/projects/{other_project.id}"
    )
    
    assert response.status_code == 404
 
async def test_create_project(authenticated_client, db, test_user):
    data = {
        "name":"Trading API",
        "category":"Finance"
    }  
    
    response = await authenticated_client.post(
        "/projects",
        json=data
    )
    
    assert response.status_code == 201
    
    data = response.json()
    
    assert data["name"] == "Trading API"
    assert data["category"] == "Finance"
    assert data["id"] is not None
    
    project = await db.get(Project, data['id'])
    assert project is not None
    assert project.owner_id == test_user.id   
    
async def test_create_project_invalid_name(authenticated_client):
    response = await authenticated_client.post(
        "/projects",
        json={
            "name":"ab",
            "category":"Finance"
        }
    )   
    
    assert response.status_code == 422
    
async def test_create_project_missing_name(authenticated_client):
    response = await authenticated_client.post(
        "/projects",
        json={
            "category": "Finance",
        },
    )

    assert response.status_code == 422  
    
async def test_create_project_unauthenticated(client):
    response = await client.post(
        "/projects",
        json={
            "name": "Trading API",
            "category": "Finance",
        },
    )
    assert response.status_code == 401    
 
async def test_update_project(authenticated_client, db, test_user):
    project = Project(
        name="Old Name",
        category="Old Category",
        owner_id=test_user.id
    )    
    
    db.add(project)
    await db.commit()
    await db.refresh(project)
    
    response = await authenticated_client.patch(
        f"/projects/{project.id}",
        json={
            "name": "New Name"
        },
    )
    
    assert response.status_code == 200
    
    data = response.json()
    
    assert data['name'] == "New Name"
    assert data['category'] == "Old Category"
    

async def test_update_project_not_found(authenticated_client):
    response = await authenticated_client.patch(
        "/projects/999999",
        json={"name": "New Name"},
    )

    assert response.status_code == 404    
 
async def test_update_other_users_project(authenticated_client, db, test_user):
    
    other_user = User(
        username="otheruser",
        email="other@example.com",
        hashed_password="test-hash"
    )
    
    db.add(other_user)
    await db.commit()
    await db.refresh(other_user)
    
    project = Project(
        name="Private Project",
        owner_id=other_user.id
    )  
    
    db.add(project)
    await db.commit()
    await db.refresh(project)
    
    response = await authenticated_client.patch(
        f"/projects/{project.id}",
        json={
            "name": "Hacked"
        },
    )
    
    assert response.status_code == 404
    await db.refresh(project)
    
    assert project.name == "Private Project"
    
async def test_update_project_invalid_name(authenticated_client, db, test_user):
    project = Project(
        name="Valid Name",
        owner_id=test_user.id,
    )

    db.add(project)
    await db.commit()
    await db.refresh(project)

    response = await authenticated_client.patch(
        f"/projects/{project.id}",
        json={"name": "ab"},
    )

    assert response.status_code == 422
    
async def test_delete_project(authenticated_client, db, test_user):
    project = Project(
            name="Valid Name",
            owner_id=test_user.id,
        )
    
    db.add(project)
    await db.commit()
    await db.refresh(project)
    
    response = await authenticated_client.delete(
        f"/projects/{project.id}"
    )
    
    assert response.status_code == 204
    
    assert await db.get(Project, project.id) is None
 
async def test_delete_project_not_found(authenticated_client):
    response = await authenticated_client.delete(
        "/projects/999"
    )    
        
        
    assert response.status_code == 404    
 
async def test_delete_other_users_project(
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

    response = await authenticated_client.delete(
        f"/projects/{project.id}"
    )

    assert response.status_code == 404
    assert await db.get(Project, project.id) is not None
