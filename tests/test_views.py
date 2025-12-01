"""Tests for public views including home page and error pages."""


def test_home_page(client):
    """Test that the home page loads correctly"""
    response = client.get("/", follow_redirects=True)
    assert response.status_code == 200


def test_error_page(client):
    """Test that the error pages loads correctly"""
    response = client.get("/some-non-existent-directory", follow_redirects=True)
    assert response.status_code == 404
