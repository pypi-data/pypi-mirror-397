#   
#   Imandra Inc.
#
#   model_cmd.py
#

import typer
from typing import Annotated
from rich.syntax import Syntax

from ..utils import console
from ..utils.load import load_state

app = typer.Typer()

@app.command(name="summary", help="")
def summary():
    """
    """

    state = load_state()

    console.print(state.curr_state().model.report())

@app.command(name="code", help="Generate the IML code for the Domain Model")
def get_code(
        filepath : Annotated[str|None, typer.Option(help="Output filepath")] = None
    ):

    state = load_state()

    console.print(Syntax(state.curr_state().model.domain_model.to_iml(), "OCaml"))

    if filepath is not None:
        try:
            with open(filepath, 'w') as outfile:
                print(state.curr_state().model.domain_model.to_iml(), file=outfile)
        except Exception as e:
            console.print(f"🛑 Failed to write domain model to disk: {e}",)
            return

    console.print(f"✅ Successfully wrote domain model to disk: {filepath}")
