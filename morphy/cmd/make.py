
import typer
from rich import print

app = typer.Typer()

@app.command('item')
def make():
    print('This is make item command. can you hear me?')