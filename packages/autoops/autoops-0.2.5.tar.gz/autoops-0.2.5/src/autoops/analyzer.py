import requests
from groq import Groq
from .config import GROQ_API_KEY, GROQ_MODEL, GITHUB_TOKEN, REPO_OWNER, REPO_NAME

def get_workflow_logs(run):
    """Fetch the actual workflow logs from GitHub"""
    try:
        # Get jobs for the workflow run
        jobs_url = run.get("jobs_url")
        headers = {
            "Authorization": f"Bearer {GITHUB_TOKEN}",
            "Accept": "application/vnd.github+json"
        }
        
        jobs_response = requests.get(jobs_url, headers=headers)
        jobs_response.raise_for_status()
        jobs = jobs_response.json().get("jobs", [])
        
        # Collect logs from failed jobs
        all_logs = []
        for job in jobs:
            if job.get("conclusion") == "failure":
                log_url = job.get("url") + "/logs"
                log_response = requests.get(log_url, headers=headers)
                if log_response.status_code == 200:
                    # Get last 3000 characters to focus on recent errors
                    logs = log_response.text[-3000:]
                    all_logs.append(f"Job: {job.get('name')}\n{logs}")
        
        return "\n\n".join(all_logs) if all_logs else "No logs available"
    except Exception as e:
        return f"Error fetching logs: {str(e)}"

def analyze_logs(run):
    """Analyze workflow failure using GroqAI to generate intelligent error descriptions"""
    try:
        # Fetch actual logs
        logs = get_workflow_logs(run)
        
        # Initialize Groq client
        client = Groq(api_key=GROQ_API_KEY)
        
        # Create prompt for AI analysis
        prompt = f"""You are an expert DevOps engineer analyzing a CI/CD failure.

Workflow Name: {run['name']}
Repository: {REPO_OWNER}/{REPO_NAME}
Run ID: {run['id']}
Conclusion: {run['conclusion']}

Workflow Logs:
{logs}

Please analyze this CI/CD failure and provide:
1. A clear summary of what went wrong
2. The root cause of the failure
3. Specific steps to fix the issue
4. Any relevant code snippets or configuration changes needed

Format your response in markdown for a GitHub issue."""
        
        # Call GroqAI for analysis
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert DevOps engineer who analyzes CI/CD failures and provides clear, actionable solutions."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            model=GROQ_MODEL,
            temperature=0.3,
            max_tokens=1500
        )
        
        # Extract AI-generated analysis
        ai_analysis = chat_completion.choices[0].message.content
        
        # Format the complete analysis
        analysis = f"""## 🤖 AI-Powered Analysis

{ai_analysis}

---

### Workflow Details
- **Workflow:** {run['name']}
- **Run ID:** {run['id']}
- **Status:** {run['conclusion']}
- **Repository:** {REPO_OWNER}/{REPO_NAME}
- **Run URL:** {run['html_url']}

*This issue was automatically created by AutoOps with AI-powered analysis.*
"""
        
        return analysis
        
    except Exception as e:
        # Fallback to basic analysis if AI fails
        return f"""## ⚠️ CI Workflow Failed

**Workflow:** {run['name']}
**Status:** {run['conclusion']}
**Repository:** {REPO_OWNER}/{REPO_NAME}

### Error
Failed to generate AI analysis: {str(e)}

### Basic Troubleshooting Steps
- Check the [workflow run logs]({run['html_url']})
- Review recent commits for breaking changes
- Verify environment variables and secrets
- Check dependency versions
- Review test failures

*This issue was automatically created by AutoOps.*
"""