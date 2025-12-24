#
#   Imandra Inc.
#
#   agent.py
#


import sys
from pathlib import Path

from ..state.state import State
from ..llms.llmtools import test_formalizer
from ..llms.overlay import Overlay

def process_test_file ( 
        path : Path,
        state : State,
        overlay : Overlay
    ) -> State:
    """
    Process a file state to the state
    """

    try:
        tf = test_formalizer (str(path), overlay, state)
    except Exception as e:
        raise Exception (f"Failed to process test file: []")

    return state.add_test_formalization(tf)
