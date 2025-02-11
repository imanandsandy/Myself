import os
import json
import requests
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

# Load configuration
CONFIG_PATH = "config.json"

def load_config():
    """Reads the schedule configuration from config.json"""
    if not os.path.exists(CONFIG_PATH):
        print("Config file not found!")
        return []

    with open(CONFIG_PATH, "r") as file:
        return json.load(file)

# Task execution function
def execute_task(task):
    """Executes a task by calling an API endpoint"""
    url = task["url"]
    try:
        response = requests.get(url)
        print(f"Executed {task['name']}: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Failed to execute {task['name']}: {e}")

# Initialize scheduler
scheduler = BlockingScheduler()

# Load tasks and schedule them
tasks = load_config()
for task in tasks:
    cron_expr = task["cron"]  # Example: "0 * * * *" (every hour)
    trigger = CronTrigger.from_crontab(cron_expr)
    scheduler.add_job(execute_task, trigger, args=[task])

print("Scheduler started...")
try:
    scheduler.start()
except KeyboardInterrupt:
    print("Scheduler shutting down...")
