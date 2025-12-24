#
#   Imandra Inc.
#
#   load.py
#

import os
import sys
from rich.prompt import Prompt
from pathlib import Path

from ..state.state import State
from ..llms.overlay import Overlays
from .__init__ import console

def load_state():
    """ """
    new_state = State.from_dir(dirpath=os.getcwd())
    if new_state is None:
        answer = Prompt.ask(
            prompt="⚠️ Couldnt find a state in current directory. Create a new one?", 
            choices = ["Yes", "No"],
            console=console,
            case_sensitive=False,
            default="Yes"
            )

        if answer == 'No':
            console.print("Goodbye!")
            sys.exit(0)
        
        console.print("Creating a new state!")

        state = State()
        state.save(os.getcwd())
        return state
    
    else:
        return new_state

def load_overlays():
    """
    """    
    return Overlays.from_dir(str(Path(os.path.abspath(__file__)).parent / "../../overlays"))
