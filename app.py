import os
import json
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

DATA_FILE = "tasks.json"
tasks = []
next_id = 1

def load_tasks():
    global tasks, next_id
    try:
        with open(DATA_FILE, "r") as f:
            tasks = json.load(f)
            if tasks:
                next_id = max(task["id"] for task in tasks) + 1
    except FileNotFoundError:
        tasks = []

def save_tasks():
    with open(DATA_FILE, "w") as f:
        json.dump(tasks, f)

load_tasks()

# ----------------- REST API -----------------
@app.route("/tasks", methods=["GET"])
def get_tasks():
    return jsonify(tasks)

@app.route("/tasks", methods=["POST"])
def add_task():
    global next_id
    data = request.get_json()
    if not data or "title" not in data or not data["title"].strip():
        return jsonify({"error": "Title is required"}), 400
    task = {"id": next_id, "title": data["title"].strip(), "completed": False}
    tasks.append(task)
    next_id += 1
    save_tasks()
    return jsonify(task), 201

@app.route("/tasks/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    for task in tasks:
        if task["id"] == task_id:
            task["completed"] = not task["completed"]
            save_tasks()
            return jsonify(task)
    return jsonify({"error": "Task not found"}), 404

@app.route("/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    global tasks
    new_tasks = [t for t in tasks if t["id"] != task_id]
    if len(new_tasks) == len(tasks):
        return jsonify({"error": "Task not found"}), 404
    tasks = new_tasks
    save_tasks()
    return jsonify({"message": "Deleted"})

# ----------------- Frontend -----------------
@app.route("/")
def home():
    return render_template("index.html")

from datetime import datetime

# обработка GET-запроса
@app.route("/tasks", methods=["GET"])
def get_tasks():
    # сортировка: сначала по приоритету (1-высокий), затем по дедлайну
    sorted_tasks = sorted(tasks, key=lambda x: (x.get('priority', 3), x.get('deadline', '9999-12-31')))
    return jsonify(sorted_tasks)

# добавление новой задачи
@app.route("/tasks", methods=["POST"])
def add_task():
    global next_id
    data = request.get_json() # получаем данные, которые прислал браузер
    if not data or "title" not in data or not data["title"].strip():
        return jsonify({"error": "Title is required"}), 400
    
    # создаем словарь (объект) задачи
    task = {
        "id": next_id,
        "title": data["title"].strip(),
        "completed": False,
        "priority": int(data.get("priority", 3)), # записываем важность (по умолчанию 3 - низкая)
        "deadline": data.get("deadline") # записываем дату (если она есть)
    
    }
    # добавляем в общий список
    tasks.append(task)
    next_id += 1
    save_tasks() # записываем в файл tasks.json
    return jsonify(task), 201
 #дальше сохранение и ответ сервера


# ----------------- Run -----------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)