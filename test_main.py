import sqlite3
import pytest
from main import app, DATABASE  # Import your FastAPI app and database path
from fastapi.testclient import TestClient

# Create a TestClient for FastAPI app
client = TestClient(app)

# Helper function to clear the database (ensure clean tests)
def clear_database():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM events")  # Remove all rows
    conn.commit()
    conn.close()

# Pytest fixture to run setup and teardown for each test
@pytest.fixture(autouse=True)
def setup_and_teardown():
    """
    Clear the database before and after each test.
    """
    clear_database()
    yield
    clear_database()

def test_process_event_valid():
    """
    Test the process_event endpoint with valid input.
    """
    # Input data
    event_data = {
        "userid": "user123",
        "eventname": "level_completed"
    }

    # Call the process_event endpoint
    response = client.post("/process_event", json=event_data)

    # Assert that the response is successful
    assert response.status_code == 201
    assert response.json()["message"] == "Event processed successfully"

    # Validate data was inserted into the database
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT eventtimestamputc, userid, eventname FROM events")
    rows = cursor.fetchall()
    conn.close()

    # Verify the database contains the correct data
    assert len(rows) == 1
    assert rows[0][1] == "user123"  # userid
    assert rows[0][2] == "level_completed"  # eventname

def test_process_event_invalid_request():
    """
    Test the process_event endpoint with invalid input (missing eventname).
    """
    # Invalid input data (missing eventname)
    invalid_data = {
        "userid": "user123"
    }

    # Call the process_event endpoint
    response = client.post("/process_event", json=invalid_data)

    # Assert that the response fails with a 422 Unprocessable Entity
    assert response.status_code == 422
    assert "detail" in response.json()
