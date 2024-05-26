import typer

from .cmd import make, update

app = typer.Typer()
app.add_typer(update.app, name="update")
app.add_typer(make.app, name="make")