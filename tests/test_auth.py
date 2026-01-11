import pytest
import json

def test_user_registration(client):
    """Test user registration"""
    response = client.post('/api/auth/register', json={
        'username': 'newuser',
        'email': 'newuser@example.com',
        'password': 'password123'
    })
    
    assert response.status_code == 201
    data = response.get_json()
    assert data['message'] == 'User registered successfully'

def test_duplicate_username_registration(client):
    """Test registration with duplicate username"""
    # Register first user
    client.post('/api/auth/register', json={
        'username': 'duplicateuser',
        'email': 'user1@example.com',
        'password': 'password123'
    })
    
    # Try to register with same username
    response = client.post('/api/auth/register', json={
        'username': 'duplicateuser',
        'email': 'user2@example.com',
        'password': 'password123'
    })
    
    assert response.status_code == 400

def test_user_login(client):
    """Test user login"""
    # Register user
    client.post('/api/auth/register', json={
        'username': 'loginuser',
        'email': 'loginuser@example.com',
        'password': 'password123'
    })
    
    # Login
    response = client.post('/api/auth/login', json={
        'username': 'loginuser',
        'password': 'password123'
    })
    
    assert response.status_code == 200
    data = response.get_json()
    assert 'access_token' in data
    assert 'refresh_token' in data

def test_invalid_login(client):
    """Test login with invalid credentials"""
    response = client.post('/api/auth/login', json={
        'username': 'nonexistent',
        'password': 'wrongpassword'
    })
    
    assert response.status_code == 401

def test_token_refresh(client, auth_headers):
    """Test token refresh"""
    response = client.post('/api/auth/refresh',
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.get_json()
    assert 'access_token' in data
