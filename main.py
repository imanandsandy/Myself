import os
import json
import logging
import subprocess
from flask import Flask, render_template, request, redirect, jsonify
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from waitress import serve
from globals import dep_path, get_url

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)

scheduler = BackgroundScheduler()

# Paths
JOB_COMPLETED_PATH = os.path.join(dep_path, "job_completed.json")

def get_config_files():
    """Retrieve all config files (config_1.json, config_2.json, etc.)"""
    return sorted([f for f in os.listdir(dep_path) if f.startswith("config_") and f.endswith(".json")])

def load_config(config_file):
    """Reads tasks from the given config file"""
    config_path = os.path.join(dep_path, config_file)
    logging.info(f"Loading config from {config_path}")

    if not os.path.exists(config_path):
        logging.error(f"Config file {config_file} not found!")
        return []

    try:
        with open(config_path, "r") as file:
            return json.load(file)
    except Exception as e:
        logging.error(f"Error reading config file {config_file}: {e}")
        return []

def save_config(config_file, tasks):
    """Saves tasks to the selected config file"""
    config_path = os.path.join(dep_path, config_file)
    try:
        with open(config_path, "w") as file:
            json.dump(tasks, file, indent=4)
    except Exception as e:
        logging.error(f"Error saving config to {config_file}: {e}")

def write_completed_task(task, status):
    """Stores executed job details in job_completed.json"""
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
        logging.error(f"Error writing to completed jobs file: {e}")

def execute_task(task):
    """Executes a shell command"""
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

def schedule_tasks(config_file):
    """Schedules all tasks from the selected config file"""
    scheduler.remove_all_jobs()
    tasks = load_config(config_file)
    for task in tasks:
        trigger = CronTrigger.from_crontab(task["cron"])
        scheduler.add_job(execute_task, trigger, args=[task])

scheduler.start()

@app.route("/crystal-onyxscheduler-srv/home", methods=["GET"])
def index():
    config_files = get_config_files()
    selected_config = request.args.get("config", "config_1.json")
    tasks = load_config(selected_config)

    completed_jobs = []
    if os.path.exists(JOB_COMPLETED_PATH):
        try:
            with open(JOB_COMPLETED_PATH, "r") as file:
                completed_jobs = json.load(file)
        except json.JSONDecodeError:
            completed_jobs = []
        except Exception as e:
            logging.error(f"Error reading completed jobs file: {e}")

    return render_template("index.html", tasks=tasks, completed_jobs=completed_jobs, config_files=config_files, selected_config=selected_config, base_url=get_url())

@app.route("/crystal-onyxscheduler-srv/add", methods=["POST"])
def add_task():
    selected_config = request.form["config_file"]
    data = request.form
    new_task = {
        "name": data["name"],
        "command": data["command"],
        "cron": data["cron"]
    }

    tasks = load_config(selected_config)
    tasks.append(new_task)
    save_config(selected_config, tasks)
    schedule_tasks(selected_config)

    return redirect(get_url() + f"/home?config={selected_config}")

@app.route("/crystal-onyxscheduler-srv/delete/<config>/<name>")
def delete_task(config, name):
    tasks = load_config(config)
    tasks = [task for task in tasks if task["name"] != name]
    save_config(config, tasks)
    schedule_tasks(config)

    return redirect(get_url() + f"/home?config={config}")

if __name__ == "__main__":
    serve(app, host="0.0.0.0", port=8039, url_scheme="https", threads=8)
