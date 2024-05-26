import typer
from rich import print

from .cmd import update

app = typer.Typer()
app.add_typer(update.app, name="update")


@app.command()
def test():
    print("This is Morphy CLI. Can you hear me?")
