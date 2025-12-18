import requests
from .config import GITHUB_TOKEN, REPO_OWNER, REPO_NAME

def create_issue(run, analysis):
    """Create a GitHub issue with AI-generated analysis"""
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/issues"
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    }
    
    # Create a more descriptive title
    title = f"🔴 CI Failure: {run['name']} - {run['event']} event"
    
    payload = {
        "title": title,
        "body": analysis,
        "labels": ["ci-failure", "automated", "ai-analyzed"]
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        issue = response.json()
        print(f"✅ Created issue #{issue['number']}: {issue['html_url']}")
        return issue
    except Exception as e:
        print(f"❌ Failed to create issue: {str(e)}")
        return None