"""Pytest configuration and fixtures for the Mail List Shield test suite.

This module provides shared fixtures for testing the Flask application,
including application instance and test client setup.
"""

import pytest

from app import create_app, db


@pytest.fixture
def app_instance(scope="function"):
    """Create a Flask application instance for testing.

    Creates a new Flask app instance configured for testing.
    The app is yielded to the test and cleaned up afterward.

    Args:
        scope: The fixture scope (defaults to function-level).

    Yields:
        Flask: The Flask application instance configured for testing.
    """
    # Create and destroy a new Flask app instance for each test function
    app = create_app(test_config=True)

    yield app


@pytest.fixture
def client(app_instance):
    """Create a test client for the Flask application.

    Provides a test client that can be used to make requests
    to the application without running a server.

    Args:
        app_instance: The Flask application fixture.

    Yields:
        FlaskClient: The test client for making requests.
    """
    app_instance.testing = True
    with app_instance.test_client() as client:
        yield client
