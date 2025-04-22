def test_login_page_loads(client):
    """Test that the login page loads correctly"""
    response = client.get("/login", follow_redirects=True)
    assert response.status_code == 200
    assert b"Login" in response.data


def test_signup_page_loads(client):
    """Test that the signup page loads correctly"""
    response = client.get("/register", follow_redirects=True)
    assert response.status_code == 200
    assert b"Register" in response.data
