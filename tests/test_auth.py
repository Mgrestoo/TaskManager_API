async def test_register_invalid_password(client):
    response = await client.post(
        "/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "abc"
            
        }
    )
    
    assert response.status_code == 422
    

async def test_login(client):
    await client.post(
        "/register",
            json={
                "username": "testuser",
                "email": "test@example.com",
                "password": "TestPassword123"
                
            }
    
    )    
    
    response = await client.post(
        "/login",
        json={
            "email": "test@example.com",
            "password": "TestPassword123"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["access_token"]
    assert data["token_type"] == "Bearer"
    
async def test_login_invalid_credentials(client):
    await client.post(
        "/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "TestPassword123",
        },
    )

    response = await client.post(
        "/login",
        json={
            "email": "test@example.com",
            "password": "WrongPassword123",
        },
    )

    assert response.status_code == 401
    assert response.json()["message"] == "Invalid credentials"
