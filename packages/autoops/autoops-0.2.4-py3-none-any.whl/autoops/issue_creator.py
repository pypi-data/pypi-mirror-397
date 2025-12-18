import requests
from .config import GITHUB_TOKEN, REPO_OWNER, REPO_NAME

def create_issue(run, analysis):
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/issues"
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    }
    payload = {
        "title": f"CI Failure: {run['name']}",
        "body": analysis
    }
    requests.post(url, headers=headers, json=payload)