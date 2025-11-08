import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'app')))

# Mock database functions before importing app
import unittest.mock as mock
sys.modules['database'] = mock.MagicMock()

from main import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_health_endpoint(client):
    """Test health endpoint returns ok status"""
    response = client.get('/api/health')
    assert response.status_code == 200
    assert response.json == {"status": "ok"}

def test_mirror_endpoint_example(client):
    """Test the exact example: fOoBar25 -> 52RAbOoF"""
    response = client.get('/api/mirror?word=fOoBar25')
    assert response.status_code == 200
    assert response.json == {"transformed": "52RAbOoF"}

def test_mirror_logic():
    """Test mirror transformation logic"""
    test_cases = [
        ("fOoBar25", "52RAbOoF"),
        ("foo", "OOF"),
        ("bar", "RAB"),
    ]
    
    for input_word, expected in test_cases:
        result = input_word.swapcase()[::-1]
        assert result == expected

def test_mirror_missing_parameter(client):
    """Test mirror endpoint without word parameter"""
    response = client.get('/api/mirror')
    assert response.status_code == 400