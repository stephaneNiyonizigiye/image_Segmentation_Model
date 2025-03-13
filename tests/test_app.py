import pytest
from app import app

@pytest.fixture
def client():
    """Create a test client."""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_index(client):
    """Test if the index page loads correctly."""
    response = client.get("/")
    assert response.status_code == 200
