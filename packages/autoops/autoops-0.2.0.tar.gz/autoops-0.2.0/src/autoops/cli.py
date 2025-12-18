import typer
from .poller import start_polling

app = typer.Typer()

@app.command()
def run():
    """Start AutoOps in fully automatic polling mode."""
    start_polling()

if __name__ == "__main__":
    app()