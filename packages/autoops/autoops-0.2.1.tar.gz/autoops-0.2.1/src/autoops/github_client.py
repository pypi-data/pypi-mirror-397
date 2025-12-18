import requests
from .config import GITHUB_TOKEN, REPO_OWNER, REPO_NAME

BASE_URL = "https://api.github.com"

def get_failed_workflows():
    url = f"{BASE_URL}/repos/{REPO_OWNER}/{REPO_NAME}/actions/runs"
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    }
    r = requests.get(url, headers=headers)
    r.raise_for_status()
    runs = r.json()["workflow_runs"]
    return [run for run in runs if run["conclusion"] == "failure"]