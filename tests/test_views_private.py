"""Tests for private views requiring authentication."""

import re


def test_dashboard_unauthenticated(client):
    """Test that unauthenticated users are redirected from dashboard"""
    response = client.get("/app", follow_redirects=True)

    # Check that the login page loads
    assert response.status_code == 200

    # Should redirect to login
    assert "/login" in response.request.path

    # Should have Login in the title
    assert re.search(rb"<title>.*Login.*</title>", response.data)
