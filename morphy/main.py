from typing import Annotated
import typer
from rich import print

app = typer.Typer()

@app.command()
def test():
    print("This is Morphy CLI. Can you hear me?")

