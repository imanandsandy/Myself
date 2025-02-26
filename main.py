import os

# Get the server environment from the environment variable
server_env = os.environ.get("SERVERENV", "NA")

# Define the deployment path based on the server environment
def get_url():
    if server_env == "DEV":
        return "https://crystal-dev.systems.uk.hsbc/onyxscheduler"
    elif server_env == "PROD":
        return "https://crystal.systems.uk.hsbc/onyxscheduler"
    else:
        return "/crystal-onyxscheduler-srv"

url = get_url()
dep_path = os.path.join("/opt/crystal/crystal-onyxscheduler-srv/", server_env)

# Directory where config files are stored
CONFIG_DIR = os.path.join(dep_path, "configs")
JOB_COMPLETED_PATH = os.path.join(dep_path, "job_completed.json")
