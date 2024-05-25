import typer
from rich import print

app = typer.Typer()

@app.command("item")
def update():
    print("Update item command is called.")

    