from .config import load_env
from .poller import start_polling

def main():
    """
    AutoOps – Fully automatic AI DevOps agent.
    """
    load_env()  # ✅ load .env FIRST
    print("🔁 AutoOps polling GitHub for CI failures...")
    start_polling()

if __name__ == "__main__":
    main()
