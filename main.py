import os
import json
import logging
from flask import Flask, render_template, request, redirect, jsonify
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

# Configure logging
logging.basicConfig(level=logging.INFO)

# Flask App
app = Flask(__name__)

# Scheduler
scheduler = BackgroundScheduler()

# Root directory
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILES = [f for f in os.listdir(ROOT_DIR) if f.startswith("config_") and f.endswith(".json")]
JOB_COMPLETED_PATH = os.path.join(ROOT_DIR, "job_completed.json")

# Load config from a specific file
def load_config(config_file):
    config_path = os.path.join(ROOT_DIR, config_file)
    logging.info(f"Loading config from {config_path}")
    if not os.path.exists(config_path):
        logging.error("Config file not found!")
        return []
    try:
        with open(config_path, "r") as file:
            return json.load(file)
    except Exception as e:
        logging.error(f"Error reading config file: {e}")
        return []

# Save config to a specific file
def save_config(config_file, tasks):
    config_path = os.path.join(ROOT_DIR, config_file)
    try:
        with open(config_path, "w") as file:
            json.dump(tasks, file, indent=4)
    except Exception as e:
        logging.error(f"Error saving config file: {e}")

# Write completed jobs to a single file
def write_completed_task(task, status):
    if not os.path.exists(JOB_COMPLETED_PATH):
        completed_jobs = []
    else:
        try:
            with open(JOB_COMPLETED_PATH, "r") as file:
                completed_jobs = json.load(file)
        except json.JSONDecodeError:
            completed_jobs = []
        except Exception as e:
            logging.error(f"Error reading completed jobs file: {e}")
            completed_jobs = []
    
    completed_jobs.append({
        "name": task["name"],
        "command": task["command"],
        "cron": task["cron"],
        "status": status
    })
    
    try:
        with open(JOB_COMPLETED_PATH, "w") as file:
            json.dump(completed_jobs, file, indent=4)
    except Exception as e:
        logging.error(f"Error writing completed jobs file: {e}")

# Execute task
def execute_task(task):
    command = task["command"]
    try:
        result = os.system(command)
        if result == 0:
            logging.info(f"Executed {task['name']}: Success")
            write_completed_task(task, "Success")
        else:
            logging.error(f"Failed {task['name']}: Error")
            write_completed_task(task, "Failed")
    except Exception as e:
        logging.error(f"Error executing {task['name']}: {e}")
        write_completed_task(task, "Error")

# Schedule all tasks
def schedule_tasks():
    scheduler.remove_all_jobs()
    for config_file in CONFIG_FILES:
        tasks = load_config(config_file)
        for task in tasks:
            trigger = CronTrigger.from_crontab(task["cron"])
            scheduler.add_job(execute_task, trigger, args=[task])
    scheduler.start()

# Health Check
@app.route("/crystal-onyxscheduler-srv/heartbeat", methods=["GET"])
def heartbeat():
    return jsonify({"status": "healthy"})

# Home page with task list
@app.route("/crystal-onyxscheduler-srv/home")
def index():
    selected_config = request.args.get("config", "config_1.json")
    tasks = load_config(selected_config)
    completed_jobs = []
    if os.path.exists(JOB_COMPLETED_PATH):
        try:
            with open(JOB_COMPLETED_PATH, "r") as file:
                completed_jobs = json.load(file)
        except json.JSONDecodeError:
            completed_jobs = []
    return render_template("index.html", tasks=tasks, completed_jobs=completed_jobs, config_files=CONFIG_FILES, selected_config=selected_config)

# Add new task
@app.route("/crystal-onyxscheduler-srv/add", methods=["POST"])
def add_task():
    data = request.form
    config_file = data.get("config_file", "config_1.json")
    new_task = {
        "name": data["name"],
        "command": data["command"],
        "cron": data["cron"]
    }
    tasks = load_config(config_file)
    tasks.append(new_task)
    save_config(config_file, tasks)
    schedule_tasks()
    return redirect(f"/crystal-onyxscheduler-srv/home?config={config_file}")

# Delete task
@app.route("/crystal-onyxscheduler-srv/delete/<name>")
def delete_task(name):
    config_file = request.args.get("config", "config_1.json")
    tasks = load_config(config_file)
    tasks = [task for task in tasks if task["name"] != name]
    save_config(config_file, tasks)
    schedule_tasks()
    return redirect(f"/crystal-onyxscheduler-srv/home?config={config_file}")

if __name__ == "__main__":
    schedule_tasks()
    app.run(debug=True)
