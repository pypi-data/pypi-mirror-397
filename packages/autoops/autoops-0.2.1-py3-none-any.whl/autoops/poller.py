import time
from .github_client import get_failed_workflows
from .analyzer import analyze_logs
from .issue_creator import create_issue
from .state import load_state, save_state

def start_polling(interval=60):
    print("🔁 AutoOps polling GitHub for CI failures...")
    state = load_state()

    while True:
        for run in get_failed_workflows():
            if run["id"] in state["processed_runs"]:
                continue

            print(f"❌ Failure detected: {run['name']}")
            analysis = analyze_logs(run)
            create_issue(run, analysis)

            state["processed_runs"].append(run["id"])
            save_state(state)

            print("📌 GitHub issue created")

        time.sleep(interval)