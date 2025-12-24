#  
#   Imandra Inc.
#
#   state_cmd.py
#

import typer
import sys
from typing import Annotated

from ..state.state import State
from ..utils import console
from ..utils.load import load_state

global state
state : State

app = typer.Typer()

@app.command(name="list", help="List all state instances")
def list_states (
        max_num_states : Annotated[int, typer.Argument(help="Maximum number of states")]=10
    ):
    """ 
    List the state instances
    """
    state = load_state()
    console.print(state.inst_list())

@app.command(name="set", help="Set current state to a specific idx in the list")
def set (
        state_idx : Annotated[int, typer.Argument(help="")]
    ):

    state = load_state()

    try:
        state.set_curr_state_idx (state_idx)
    except Exception as e:
        console.print(f"Caught error: {e}")
        sys.exit(0)

    console.print("Update current state idx to {state_idx}")

@app.command(name="summary", help="Provide summary of the current state instance")
def summary():
    """
    Provide a summary of the current state
    """

    state : State = load_state()
    console.print(state.curr_state().report())
