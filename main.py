import os
import json
import logging
import subprocess
from flask import Flask, render_template, request, redirect, jsonify
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from waitress import serve

# Flask App
app = Flask(__name__)

# Configure Logging
LOG_FILE = "scheduler.log"
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Scheduler
scheduler = BackgroundScheduler()

# Config Path
CONFIG_PATH = "config.json"

def load_config():
    """Reads the schedule configuration from config.json"""
    if not os.path.exists(CONFIG_PATH):
        logging.error("Config file not found!")
        return []
    with open(CONFIG_PATH, "r") as file:
        return json.load(file)

def save_config(tasks):
    """Save tasks to config.json"""
    with open(CONFIG_PATH, "w") as file:
        json.dump(tasks, file, indent=4)

def execute_task(task):
    """Executes a shell command and logs output"""
    command = task["command"]
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        logging.info(f"Executed {task['name']}: {result.stdout.strip()}")
    except Exception as e:
        logging.error(f"Failed to execute {task['name']}: {e}")

def schedule_tasks():
    """Schedule all tasks from config.json"""
    scheduler.remove_all_jobs()
    tasks = load_config()
    for task in tasks:
        trigger = CronTrigger.from_crontab(task["cron"])
        scheduler.add_job(execute_task, trigger, args=[task])

# Start Scheduler
scheduler.start()
schedule_tasks()

# Health Check Endpoint
@app.route("/crystal-onyxscheduler-service/heartneat", methods=['GET'])
def heartbeat():
    return jsonify({"status": "healthy"})

# Web UI Routes
@app.route("/")
def index():
    tasks = load_config()
    return render_template("index.html", tasks=tasks)

@app.route("/add", methods=["POST"])
def add_task():
    """Add a new task"""
    data = request.form
    new_task = {
        "name": data["name"],
        "command": data["command"],
        "cron": data["cron"]
    }
    tasks = load_config()
    tasks.append(new_task)
    save_config(tasks)
    schedule_tasks()
    return redirect("/")

@app.route("/delete/<name>")
def delete_task(name):
    """Delete a task"""
    tasks = load_config()
    tasks = [task for task in tasks if task["name"] != name]
    save_config(tasks)
    schedule_tasks()
    return redirect("/")

@app.route("/logs")
def logs():
    """View Logs"""
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as file:
            logs = file.readlines()
    else:
        logs = ["No logs found."]
    return render_template("logs.html", logs=logs)

if __name__ == "__main__":
    serve(app, host="0.0.0.0", port=8039, url_scheme='https', threads=8)
