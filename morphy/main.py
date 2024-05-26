import typer
from rich import print

from .cmd import update, make

app = typer.Typer()
app.add_typer(update.app, name="update")
app.add_typer(make.app, name="make")


@app.command()
def test():
    print("This is Morphy CLI. Can you hear me?")
