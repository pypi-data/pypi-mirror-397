#
#   Imandra Inc.
#
#   scenario_cmd.py
#

import typer

from ..state.state import State
from ..utils.load import load_state

from typing import Annotated


app = typer.Typer()

@app.command(name="summary", help="Summary of the available scenarios")
def summary():
    """ 
    """
    
    state = load_state()

@app.command(name="view", help="View a specific scenario")
def view(
    sc_id : int,
    scenario_name : str
    ):
    """
    """
    
    state = load_state()

@app.command(name="rm", help="Remove a scenario")
def rm_scenario():
    """ 
    """
    
    state = load_state()

@app.command(name="add", help="Add a scenario")
def add_scenario(
        name : Annotated[str, typer.Argument(help="Name to be given to the scenario, must be unique")] 
    ):
    """ 
    """
    state = load_state()

@app.command(name="edit", help="Edit a scenario")
def edit_scenario():
    """ 
    """
    
    state = load_state()

@app.command(name="search", help="Search for a particular scenario by predicate/transition functions")
def search(q : str):
    """ 
    """

    state = load_state()