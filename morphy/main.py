from typing import Annotated
import os

import typer
from rich import print

from . import config
from .cmd import make, remove, show, update

app = typer.Typer()
app.add_typer(update.app, name="update")
app.add_typer(make.app, name="make")
app.add_typer(show.app, name="show")
app.add_typer(remove.app, name="remove")


@app.callback()
def callback() -> None:
    """
    Morphy CLI Callback.
    If the project directory ($HOME/.morphy) does not exist, create it including the storage directory.
    Also, create a configuration file (morphy.ini) in the project directory.
    
    """
    if not os.path.exists(config.PROJECT_DIR):
        print("\n[bold green]<-- Morphy CLI Callback -->[/bold green]\n")
        print("The Morphy's project directory does NOT seem to exist.")
        print("If you are running this app for the first time, no problem.")
        print(
            "If not, the directory may have been accidentally deleted. Please check.\n"
        )

        print("Create a new project directory at $HOME/.morphy.")
        os.makedirs(config.PROJECT_DIR, exist_ok=True)
        print("    - Done.")

        print("Create a new storage directory at $HOME/.morphy/storage.")
        os.makedirs(config.DEFAULT_STORAGE_DIR, exist_ok=True)
        print("    - Done.")

        inifile = os.path.join(config.PROJECT_DIR, "morphy.ini")
        with open(inifile, "w") as f:
            f.write(f"[PATHS]\n")
            f.write(f"PROJECT_DIR = {config.PROJECT_DIR}\n")
            f.write(f"STORAGE_DIR = {config.DEFAULT_STORAGE_DIR}\n")

        print("\nIf you want to change the storage directory, use `morphy cs`.")
        print("All processes are completed.")
        print("\n[bold green]<-- Morphy CLI Callback -->[/bold green]\n")


@app.command("cs", help="Change the storage directory path.")
def change_storage_path(
    to: Annotated[str, typer.Argument(..., help="New storage directory path")]
) -> None:
    """
    An implementation of the edit command of the Morphy CLI.
    Change the storage directory path in the configuration file (morphy.ini).
    
    """

    y_or_n = typer.prompt(
        f"Do you really want to change the storage directory path to {to}? (y/n)"
    )
    if y_or_n.lower() != "y":
        print("Canceled.")
        return
    
    inifile = os.path.join(config.PROJECT_DIR, "morphy.ini")
    with open(inifile, "r") as f:
        lines = f.readlines()
    
    with open(inifile, "w") as f:
        for line in lines:
            if line.startswith("STORAGE_DIR"):
                f.write(f"STORAGE_DIR = {to}\n")
            else:
                f.write(line)
    
    print("The storage directory path has been changed.")
    print("All processes are completed.")
