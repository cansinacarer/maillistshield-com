def test_home_page(client):
    """Test that the home page loads correctly"""
    response = client.get("/", follow_redirects=True)
    assert response.status_code == 200
