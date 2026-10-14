from flask import Flask, jsonify, request

app = Flask(__name__)

# In-memory data store
todos = [
    {"id": 1, "task": "Learn TDD", "done": False},
    {"id": 2, "task": "Build a Flask API", "done": True},
]


@app.route('/')
def index():
    return "Welcome"


@app.route('/todos', methods=['GET', 'POST'])
def manage_todos():
    if request.method == 'GET':
        return jsonify(todos)

    payload = request.get_json(silent=True) or {}
    task = payload.get('task')
    if not task:
        return jsonify({"error": "Missing task data"}), 400

    new_todo = {
        'id': max((todo['id'] for todo in todos), default=0) + 1,
        'task': task,
        'done': False,
    }
    todos.append(new_todo)
    return jsonify(new_todo), 201
