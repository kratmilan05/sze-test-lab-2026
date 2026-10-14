from flask import Flask, jsonify, request

app = Flask(__name__)

# In-memory data store
todos = [
    {"id": 1, "task": "Learn TDD", "done": False},
    {"id": 2, "task": "Build a Flask API", "done": True},
]

@app.route('/')
def index():
    """
    Welcome endpoint.
    """
    return "Welcome"

@app.route('/todos', methods=['GET', 'POST'])
def handle_todos():
    """
    Handles fetching all to-dos (GET) and creating a new to-do (POST).
    """
    if request.method == 'POST':
        if not request.json or 'task' not in request.json:
            return jsonify({"error": "Missing task data"}), 400

        new_todo = {
            'id': _get_next_id(),
            'task': request.json['task'],
            'done': False
        }
        todos.append(new_todo)
        return jsonify(new_todo), 201

    return jsonify(todos)


@app.route('/todos/<int:todo_id>', methods=['GET', 'PUT', 'DELETE'])
def handle_single_todo(todo_id):
    """
    Handles GET, PUT, and DELETE requests for a single to-do item by its ID.
    """
    todo = next((item for item in todos if item["id"] == todo_id), None)

    if not todo:
        return jsonify({"error": f"Todo with id {todo_id} not found"}), 404

    if request.method == 'GET':
        return jsonify(todo), 200

    if request.method == 'PUT':
        if not request.json:
            return jsonify({"error": "Missing JSON body"}), 400

        todo.update(request.json)
        return jsonify(todo), 200

    if request.method == 'DELETE':
        todos.remove(todo)
        return '', 204


def _get_next_id():
    """
    A helper function to get the next ID for a new todo.
    """
    if not todos:
        return 1
    return max(item['id'] for item in todos) + 1