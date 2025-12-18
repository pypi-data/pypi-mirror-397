# AutoOps 🚀

AutoOps is a fully automatic AI DevOps agent.
Just run:

    autoops run

It will:
- Monitor GitHub CI failures
- Analyze logs using Groq LLMs
- Automatically create GitHub issues

No webhooks. No ngrok. No setup command.

## Requirements
Create a `.env` file:

GITHUB_TOKEN=ghp_xxx
REPO_OWNER=your-username
REPO_NAME=your-repo
GROQ_API_KEY=groq_xxx

## Run
autoops run