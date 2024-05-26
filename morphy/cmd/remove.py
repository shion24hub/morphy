import typer
from rich import print

app = typer.Typer()

@app.command("item")
def remove():
    print('called remove command.')