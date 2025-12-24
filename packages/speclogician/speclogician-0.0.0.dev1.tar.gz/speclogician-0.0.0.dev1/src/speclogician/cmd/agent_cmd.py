#
#   Imandra Inc.
#
#   agent_cmd.py
#

import typer
import os
from pathlib import Path
from typing import Annotated

from rich.progress import track

from ..llms.overlay import Overlays
from ..agent.funcs import process_test_file
from ..state.state import State
from ..utils import console
from ..utils.load import load_overlays, load_state

app = typer.Typer()


@app.command(help="Add a single file to the formalization state")
def proc_test_file (
        filepath : Annotated[str, typer.Argument()],
        overlay_name : Annotated[str, typer.Argument(help="Overlay to use. It should also contain the file extension we'll use")]
    ):

    overlays = load_overlays()
    state = load_state()
    
    tgt_path = Path(filepath).parent / filepath

    overlay = overlays.get(overlay_name)
    if overlay is None:
        console.print(f":warning: Could not find an overlay named {overlay_name}!")
        return
    
    try: 
        process_test_file(tgt_path, state, overlay)
    except Exception as e:
        console.print(f"🛑 Caught an error when adding file: {e}")
        return
    
    # Add the state definition here

    typer.secho(f"✅ Successfully added {filepath} to the formalization state!")

@app.command(help="Run full cycle formalization for a specified directory")
def proc_test_dir (
        dirpath : Annotated[str, typer.Argument(help="Target directory with tests that should be formalized")],
        overlay_name : Annotated[str, typer.Argument(help="Overlay to use. It should also contain the file extension we'll use")],
        clean : Annotated[bool, typer.Option(help="Should we override any tests from these files already present in the state?")] = False
    ):
    
    state = load_state()

    overlays = load_overlays()
    overlay = overlays.get(overlay_name)

    if overlay is None:
        typer.secho(f"🛑 Could not find an overlay named {overlay_name}!", err=True)
        return
    
    filepaths = os.listdir(dirpath)
    filepaths = list(filter(lambda x: x.endswith(overlay.ext.strip()), filepaths))

    console.print(f"Identified {len(filepaths)} to process")

    count = 0

    for i in track(range(len(filepaths)), description=f"Processing {dirpath}..."):

        try:
            process_test_file(Path(filepaths[i]), state, overlay)
        except Exception as e:
            console.print(f"Failed on {filepaths[i]}: {e}")

        count += 1

    console.print(f":robot:Processed {count} files!")

    try:
        state.save(dirpath)
    except Exception as e:
        typer.echo(f"🛑 Caught error when saving the formalization state: {e}")
        return
 
    typer.secho(f"✅ Successfully saved the formalization state to {dirpath}")
