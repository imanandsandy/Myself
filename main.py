import os
import json
import logging
import subprocess
from flask import Flask, render_template, request, redirect, jsonify
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from waitress import serve
from globals import CONFIG_DIR, JOB_COMPLETED_PATH, url  # Import global paths

# Flask App
app = Flask(__name__)

# Scheduler
scheduler = BackgroundScheduler()

# Logging
logging.basicConfig(level=logging.INFO)

def get_config_files():
    """Returns a list of available config files in CONFIG_DIR"""
    if not os.path.exists(CONFIG_DIR):
        os.makedirs(CONFIG_DIR)
    return [f for f in os.listdir(CONFIG_DIR) if f.startswith("config_") and f.endswith(".json")]

def load_config(config_file):
    """Reads a single config file"""
    config_path = os.path.join(CONFIG_DIR, config_file)
    if not os.path.exists(config_path):
        logging.error(f"Config file {config_file} not found!")
        return []
    with open(config_path, "r") as file:
        try:
            return json.load(file)
        except json.JSONDecodeError:
            logging.error(f"Config file {config_file} is corrupted.")
            return []

def write_completed_task(task, status):
    """Write completed job details to job_completed.json"""
    if not os.path.exists(JOB_COMPLETED_PATH):
        completed_jobs = []
    else:
        with open(JOB_COMPLETED_PATH, "r") as file:
            try:
                completed_jobs = json.load(file)
            except json.JSONDecodeError:
                completed_jobs = []

    completed_jobs.append({
        "name": task["name"],
        "command": task["command"],
        "cron": task["cron"],
        "status": status
    })

    with open(JOB_COMPLETED_PATH, "w") as file:
        json.dump(completed_jobs, file, indent=4)

def execute_task(task):
    """Executes a shell command and logs output"""
    command = task["command"]
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            logging.info(f"Executed {task['name']}: {result.stdout.strip()}")
            write_completed_task(task, "Success")
        else:
            logging.error(f"Failed {task['name']}: {result.stderr.strip()}")
            write_completed_task(task, "Failed")
    except Exception as e:
        logging.error(f"Error executing {task['name']}: {e}")
        write_completed_task(task, "Error")

def schedule_tasks():
    """Schedule all tasks from all config files"""
    scheduler.remove_all_jobs()
    config_files = get_config_files()

    for config_file in config_files:
        tasks = load_config(config_file)
        for task in tasks:
            trigger = CronTrigger.from_crontab(task["cron"])
            scheduler.add_job(execute_task, trigger, args=[task])

# Start Scheduler
scheduler.start()
schedule_tasks()

# Web UI Routes
@app.route(f"{url}/home")
def index():
    config_files = get_config_files()
    selected_config = request.args.get("config", config_files[0] if config_files else None)
    tasks = load_config(selected_config) if selected_config else []
    
    completed_jobs = []
    if os.path.exists(JOB_COMPLETED_PATH):
        with open(JOB_COMPLETED_PATH, "r") as file:
            try:
                completed_jobs = json.load(file)
            except json.JSONDecodeError:
                completed_jobs = []

    return render_template("index.html", config_files=config_files, selected_config=selected_config, tasks=tasks, completed_jobs=completed_jobs)

@app.route(f"{url}/add", methods=["POST"])
def add_task():
    """Add a new task to a selected config file"""
    data = request.form
    selected_config = data.get("config_file")
    new_task = {
        "name": data["name"],
        "command": data["command"],
        "cron": data["cron"]
    }
    
    tasks = load_config(selected_config)
    tasks.append(new_task)
    
    with open(os.path.join(CONFIG_DIR, selected_config), "w") as file:
        json.dump(tasks, file, indent=4)

    schedule_tasks()
    return redirect(f"{url}/home?config={selected_config}")

@app.route(f"{url}/delete/<name>/<config>")
def delete_task(name, config):
    """Delete a task from a selected config file"""
    tasks = load_config(config)
    tasks = [task for task in tasks if task["name"] != name]
    
    with open(os.path.join(CONFIG_DIR, config), "w") as file:
        json.dump(tasks, file, indent=4)

    schedule_tasks()
    return redirect(f"{url}/home?config={config}")

if __name__ == "__main__":
    serve(app, host="0.0.0.0", port=8039, url_scheme='https', threads=8)
