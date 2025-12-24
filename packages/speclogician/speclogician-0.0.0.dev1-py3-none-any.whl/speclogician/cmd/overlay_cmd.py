#
#   Imandra Inc.
#   
#   overlay_cmd.py
#

from typing import Annotated
from rich import print as printr
import typer

from ..utils.load import load_overlays

app = typer.Typer()

@app.command(name="list", help="list the available overlays")
def list_():
    overlays = load_overlays()
    overlays.list_overlays()

@app.command(name="view", help="View individual template")
def view(
        name : Annotated[str, typer.Argument(help="Name of the template to view")]
    ):

    overlays = load_overlays()
    if name not in overlays.names():
        typer.secho(f"🛑 No template with name {name} found!", err=True)
        return
    
    printr(overlays.get(name))
