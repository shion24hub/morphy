import typer

from .cmd import make, show, update, remove

app = typer.Typer()
app.add_typer(update.app, name="update")
app.add_typer(make.app, name="make")
app.add_typer(show.app, name="show")
app.add_typer(remove.app, name="remove")