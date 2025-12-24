#
#   Imandra Inc.
#
#   llmtools.py
#

import datetime, os, dotenv, sys, yaml, typer
from typing import Optional
from pathlib import Path
from ..data.reports import TestFormalization
from llms.overlay import Overlay

#from langchain_anthropic import ChatAnthropic
dotenv.load_dotenv("../.env")

llm = None 

#ChatAnthropic (
#    model_name="claude-sonnet-4-20250514",
#    api_key=os.environ["ANTHROPIC_API_KEY"],
#)


def test_formalizer (
        filepath : str,
        overlay : Overlay,
        domain_model : Optional[str] = "N/A",
        ) -> TestFormalization:
    """
    Returns a tuple of the logic and the type model
    """
    
    test_case = Path(filepath).read_text()
    try:
        generic_prompt = Path("../prompts/generic.md").read_text()
    except Exception as e:
        print(f"Failed to load in the generic prompt: {e}")
        sys.exit(0)

    prompt = f"""
{generic_prompt}

{overlay}

Domain model:
----
{domain_model}
----

Test case:
----
{test_case}
----
"""

    structured_model = llm.with_structured_output(FormalizationResponse)

    # Let's call the LLM
    try: 
        response : FormalizationResponse = structured_model.invoke(prompt)
    except Exception as e:
        typer.secho(f"Failed to make the LLM call: {e}", err=True)
        sys.exit(0)

    tf = TestFormalization(
        name = response.test_name_str,
        language = overlay.language,
        filepath = filepath,
        contents = test_case,
        time = str(datetime.datetime.now()),
        scenarios = response.scenarios,
        domain_model = response.domain_model,
    )

    return tf

def retry_test_formalization (
        tf : TestFormalization,
        model_response : str,
    ) -> TestFormalization:
    """
    Make the call again to 
    """

    return tf

if __name__ == "__main__":

    base_dir = "../data/gherkin"
    paths = os.listdir(base_dir)
    overlay = Overlay.from_file("../overlays/gherkin.yaml")
    domain_model : str = "N/A"
    
    responses : list[LLMResponse] = []

    for path in paths:
        r = test_formalizer(os.path.join(base_dir, paths[0]), overlay, domain_model)
        responses.append(r)
        domain_model = r.domain_model

    for r in responses:
        print (yaml.dump(r, default_flow_style=False))