from pathlib import Path

import pytest
from pytest_bdd import scenarios, given, when, then, parsers

# Make the Flask app and its in-memory data store accessible to the tests
from lab_2_bdd.app import app, todos

# Constants
EXISTING_TODO = {"id": 2, "task": "Build a Flask API", "done": True}

FEATURE_PATH = Path(__file__).resolve().parent / "features" / "single_todo.feature"

# Scenarios
scenarios(str(FEATURE_PATH))

# Fixtures
@pytest.fixture
def client():
    """Provides a test client for the Flask application."""
    with app.test_client() as client:
        yield client

@pytest.fixture
def response(client):
    """A fixture to store the response from an API call."""
    return {}


# Given Steps
@given('the API has a to-do with id 2 and task "Build a Flask API"')
def setup_existing_todo():
    """Set up the initial state with a known to-do item."""
    global todos
    todos[:] = [
        {"id": 1, "task": "Learn TDD", "done": False},
        EXISTING_TODO,
    ]


@given('the API has a list of to-dos')
def setup_any_todos():
    """Set up the initial state with a generic list."""
    global todos
    todos[:] = [
        {"id": 1, "task": "Learn TDD", "done": False},
        {"id": 2, "task": "Build a Flask API", "done": True},
    ]


# When Steps
@when(parsers.parse('the user requests the to-do with id {todo_id}'))
def get_single_todo(client, response, todo_id):
    """Make a GET request to the /todos/<id> endpoint."""
    res = client.get(f'/todos/{todo_id}')
    response['data'] = res.get_json()
    response['status_code'] = res.status_code


# Then Steps
@then(parsers.parse('the response status code should be {status_code:d}'))
def check_status_code(response, status_code):
    """Check if the response status code is the expected one."""
    assert response['status_code'] == status_code


@then('the response should contain the details of the to-do with id 2')
def check_response_for_existing_todo(response):
    """Check the content of the response for a successful request."""
    assert response['data'] == EXISTING_TODO


@then('the response should contain a "not found" error message')
def check_response_for_not_found(response):
    """Check the content of the response for a 404 error."""
    assert 'error' in response['data']
    assert 'not found' in response['data']['error'].lower()
