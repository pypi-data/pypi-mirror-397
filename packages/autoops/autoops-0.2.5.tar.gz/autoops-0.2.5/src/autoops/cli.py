from .config import validate_config
from .poller import start_polling

def main():
    """
    AutoOps – Fully automatic AI DevOps agent.
    """
    try:
        validate_config()  # Validate config before starting
        print("🔁 AutoOps polling GitHub for CI failures...")
        start_polling()
    except ValueError as e:
        print(str(e))
        return 1
    except KeyboardInterrupt:
        print("\n👋 AutoOps stopped")
        return 0

if __name__ == "__main__":
    main()
