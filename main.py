import json
import logging
import subprocess
import os
from flask import Flask, render_template, request, redirect, jsonify
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from waitress import serve
from globals import dep_path, get_url

app = Flask(__name__)

# Configure Logging
logging.basicConfig(level=logging.INFO)

# Scheduler
scheduler = BackgroundScheduler()

# Directory for config files
CONFIG_DIR = os.path.join(dep_path, "configs")
JOB_COMPLETED_PATH = os.path.join(dep_path, "job_completed.json")

def load_configs():
    """Reads all schedule configurations from CONFIG_DIR"""
    configs = []
    if not os.path.exists(CONFIG_DIR):
        os.makedirs(CONFIG_DIR)
    
    for file in os.listdir(CONFIG_DIR):
        if file.endswith(".json"):
            config_path = os.path.join(CONFIG_DIR, file)
            try:
                with open(config_path, "r") as f:
                    configs.extend(json.load(f))
            except Exception as e:
                logging.error(f"Error reading {file}: {e}")
    return configs

def save_config(filename, tasks):
    """Save tasks to a specific config file"""
    config_path = os.path.join(CONFIG_DIR, filename)
    try:
        with open(config_path, "w") as file:
            json.dump(tasks, file, indent=4)
    except Exception as e:
        logging.error(f"Error saving {filename}: {e}")

def write_completed_task(task, status):
    """Write completed job details to job_completed.json"""
    completed_jobs = []
    if os.path.exists(JOB_COMPLETED_PATH):
        try:
            with open(JOB_COMPLETED_PATH, "r") as file:
                completed_jobs = json.load(file)
        except json.JSONDecodeError:
            completed_jobs = []
        except Exception as e:
            logging.error(f"Error reading completed jobs file: {e}")
    
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
    """Schedule all tasks from config files"""
    scheduler.remove_all_jobs()
    tasks = load_configs()
    for task in tasks:
        trigger = CronTrigger.from_crontab(task["cron"])
        scheduler.add_job(execute_task, trigger, args=[task])
    scheduler.start()

schedule_tasks()

@app.route("/crystal-onyxscheduler-srv/heartbeat", methods=['GET'])
def heartbeat():
    return jsonify({"status": "healthy"})

@app.route("/crystal-onyxscheduler-srv/home")
def index():
    tasks = load_configs()
    completed_jobs = []
    if os.path.exists(JOB_COMPLETED_PATH):
        try:
            with open(JOB_COMPLETED_PATH, "r") as file:
                completed_jobs = json.load(file)
        except json.JSONDecodeError:
            completed_jobs = []
        except Exception as e:
            logging.error(f"Error reading completed jobs file: {e}")
    return render_template("index.html", tasks=tasks, completed_jobs=completed_jobs, base_url=get_url())

@app.route("/crystal-onyxscheduler-srv/add", methods=["POST"])
def add_task():
    """Add a new task"""
    data = request.form
    new_task = {
        "name": data["name"],
        "command": data["command"],
        "cron": data["cron"]
    }
    filename = data.get("config_file", "config_1.json")
    config_path = os.path.join(CONFIG_DIR, filename)
    tasks = []
    if os.path.exists(config_path):
        try:
            with open(config_path, "r") as file:
                tasks = json.load(file)
        except json.JSONDecodeError:
            tasks = []
    tasks.append(new_task)
    save_config(filename, tasks)
    schedule_tasks()
    return redirect(get_url() + "/home")

@app.route("/crystal-onyxscheduler-srv/delete/<name>")
def delete_task(name):
    """Delete a task"""
    for file in os.listdir(CONFIG_DIR):
        if file.endswith(".json"):
            config_path = os.path.join(CONFIG_DIR, file)
            try:
                with open(config_path, "r") as f:
                    tasks = json.load(f)
                tasks = [task for task in tasks if task["name"] != name]
                save_config(file, tasks)
            except Exception as e:
                logging.error(f"Error modifying {file}: {e}")
    schedule_tasks()
    return redirect(get_url() + "/home")

if __name__ == "__main__":
    serve(app, host="0.0.0.0", port=8039, url_scheme='https', threads=8)
