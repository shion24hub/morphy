import typer

from .cmd import make, update, show

app = typer.Typer()
app.add_typer(update.app, name="update")
app.add_typer(make.app, name="make")
app.add_typer(show.app, name="show")