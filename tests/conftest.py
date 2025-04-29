import pytest

from app import create_app, db


@pytest.fixture
def app_instance(scope="function"):
    # Create and destroy a new Flask app instance for each test function
    app = create_app(test_config=True)

    yield app


@pytest.fixture
def client(app_instance):
    app_instance.testing = True
    with app_instance.test_client() as client:
        yield client
