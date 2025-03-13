import sys
import os

# Ajouter le répertoire racine au PATH pour que 'app' soit détecté
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

import pytest
from app import app  # Assure-toi que 'app.py' est bien à la racine

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
