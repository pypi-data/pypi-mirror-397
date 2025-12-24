#
#   Imandra Inc.
#
#   domain.py
#

import re
from typing import List
from pydantic import BaseModel

from rich.table import Table
from rich.syntax import Syntax

from .predicates import StatePredicate, ActionPredicate, Transition
from .report import DomainModelReport

from enum import Enum

from dotenv import load_dotenv
load_dotenv("../.env")

IML_TYPE_REGEX = re.compile(
    r"""
    ^\s*type\s+                    # 'type' keyword
    (?P<name>[a-zA-Z_][a-zA-Z0-9_]*)  # type name
    \s*=                            # '=' sign
    """,
    re.MULTILINE | re.VERBOSE,
)

def strip_iml_comments(text: str) -> str:
    """Remove OCaml-style (* ... *) and // comments."""
    # Remove block comments
    text = re.sub(r"\(\*.*?\*\)", "", text, flags=re.DOTALL)
    # Remove line comments
    text = re.sub(r"//.*", "", text)
    return text

def extract_declared_types(iml_text: str) -> List[str]:
    """Return all declared type names in an IML file."""
    clean = strip_iml_comments(iml_text)
    return [m.group("name") for m in IML_TYPE_REGEX.finditer(clean)]

class PredicateType(Enum):
    STATE = 1
    ACTION = 2

class DomainModel(BaseModel):
    """ 
    The domain model
    """

    base_status : str = "UNKOWN" # IML status
    base : str = "" # Includes type definitions and other things...

    transitions : list[Transition] = [] # 'state * action -> state' tansition functions
    state_preds : list[StatePredicate] = [] # 'state -> bool' predicates
    action_preds : list[ActionPredicate] = [] # 'state * action -> bool' predicates

    def pred_exists(self, name:str) -> bool:
        """
        Does this predicate exist?
        """
        if next ((p for p in self.state_preds if p.name == name), None) is not None:
            return True    
        return next ((p for p in self.action_preds if p.name == name), None) is not None
    
    def trans_exists(self, name:str) -> bool:
        """ """
        return next ((t for t in self.transitions if t.name == name), None) is not None

    def state_specified(self) -> bool:
        """
        Return True if the `state` type is properly specified
        """
        return self.base_has_type('state')
    
    def action_specified(self) -> bool:
        """
        Return True if the `action` is properly specified
        """
        return self.base_has_type('action')

    def base_has_type(
            self, 
            type_name : str
        ) -> bool:
        """
        Check whether the base model has a specified type
        """

        declared_types = extract_declared_types(self.base)
        return type_name in declared_types
    
    def set_base (
            self, 
            new_base : str, 
            do_check : bool = True) -> None | DomainModelReport:
        """
        """
        self.base = new_base

        if do_check:
            return self.report()
        return None

    def report(self) -> DomainModelReport:
        """
        Generate a DomainModelReport
        """

        return DomainModelReport()

    def to_iml(self):
        """
        Create a consolidated IML model
        """
        state_predicates    = "\n".join(map(lambda x: x.to_iml(), self.state_preds))
        action_predicates   = "\n".join(map(lambda x: x.to_iml(), self.action_preds))
        transitions         = "\n".join(map(lambda x: x.to_iml(), self.transitions))
     
        return f"""
(* Domain Model *)

(* Base *)
{self.base}

(* State predicates *)
{state_predicates}

(* Action predicates *)
{action_predicates}

(* Transitions *)
{transitions}
"""

    def __rich__ (self):
        """
        Return a nice table we can visualize
        """
        t = Table(title="Domain model")

        t.add_column("Attribute", "Value")
        t.add_row("Base", Syntax(self.base, "OCaml"))
        t.add_row("State predicates", Syntax("\n".join(map(lambda x: x.to_iml(), self.state_preds)) , "OCaml"))
        t.add_row("Action predicates", Syntax("\n".join(map(lambda x: x.to_iml(), self.action_preds)), "OCaml"))
        t.add_row("Transitions", Syntax("\n".join(map(lambda x: x.to_iml(), self.transitions)) , "OCaml"))

        return t
    
if __name__ == "__main__":

    # 
    m = DomainModel(
        base_status = "UNKNOWN"
    )
    m.set_base("type state = int\ntype action = int")

    print (f"State is specified: {m.state_specified()}")
    print (f"Action is specified: {m.action_specified()}")

