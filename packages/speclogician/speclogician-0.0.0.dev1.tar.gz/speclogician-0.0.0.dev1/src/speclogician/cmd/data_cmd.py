#
#   Imandra Inc.
#
#   data_cmd.py
#   

import typer
from typing import Annotated

app = typer.Typer()

@app.command(name="list")
def data_list():
    """
    List the available data sources
    """
    pass

tests_app = typer.Typer()
@tests_app.command(name="tests")
def list (
        max_num_tests : Annotated[int, typer.Argument(help="Maximum number of tests to displayed")]
    ):
    pass
