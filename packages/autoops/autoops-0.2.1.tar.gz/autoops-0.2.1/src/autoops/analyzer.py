def analyze_logs(run):
    return (
        f"CI workflow '{run['name']}' failed.\n\n"
        "Suggested checks:\n"
        "- Dependency versions\n"
        "- Missing environment variables\n"
        "- Failing tests"
    )