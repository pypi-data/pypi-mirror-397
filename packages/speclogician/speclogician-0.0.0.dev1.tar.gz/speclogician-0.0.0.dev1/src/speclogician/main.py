#
#   Imandra Inc.
#
#   main.py
#

import typer
import os
from typing import Final
from pathlib import Path

from speclogician.cmd.agent_cmd import app as agent_app
from speclogician.cmd.data_cmd import app as data_app
from speclogician.cmd.model_cmd import app as model_app
from speclogician.cmd.overlay_cmd import app as overlay_app
from speclogician.cmd.scenario_cmd import app as scenario_app
from speclogician.cmd.state_cmd import app as state_app

from speclogician.utils import console


SL_HELP : Final = """
:robot: [bold deep_sky_blue1][italic]SpecLogician[/italic] is an AI framework for data-driven formal program specification synthesis, verification and analysis.[/bold deep_sky_blue1] :rocket:

Learn more at [bold italic deep_sky_blue1]https://www.speclogician.dev![/bold italic deep_sky_blue1]
"""

app = typer.Typer(
    name="SpecLogician",
    help=SL_HELP,
    rich_markup_mode="rich"
)

app.add_typer(agent_app     , name="agent"      , help="Agentic functions")
app.add_typer(overlay_app   , name="overlay"    , help="Available overlays")
app.add_typer(data_app      , name="data"       , help="Functions for data artifacts")
app.add_typer(model_app     , name="model"      , help="Functions related to model")
app.add_typer(scenario_app  , name="scenario"   , help="Scenario access and modification functions")
app.add_typer(state_app     , name="state"      , help="State access and modification functions")

@app.command(help="Run the TUI")
def tui ():
    """
    Launch the TUI view of the state
    """
    from tui.tui import SpecLogicianApp
    tui_app = SpecLogicianApp(state)
    tui_app.run()

@app.command(help="Generate a prompt for helping agents use SpecLogician")
def prompt():
    """
    Generate a prompt for helping CLI agents use SpecLogician
    """

    prompt_path = Path(os.path.abspath(__file__)).parent / "utils/prompt.md"

    try:
        contents = prompt_path.read_text()
    except Exception as e:
        console.print(f"🛑 Failed to read in the prompt contents: {e}")
        return
    
    console.rule("[bold]Start of SpecLogician prompt[/bold]")
    console.print(contents)
    console.rule("[bold]End of prompt[/bold]")

if __name__ == '__main__':
    app()
    import sys
    sys.exit(0)
    print ("hello")
    state.save(dirpath=os.getcwd())
