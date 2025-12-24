#
#   Imandra Inc.
#
#   scenario.py
#

from rich.table import Table
from rich.syntax import Syntax

from pydantic import BaseModel
from .component import ModelComponent
from .predicates import (
    StatePredicate, 
    ActionPredicate,
    Transition
)
from .domain import DomainModel
from ..utils.imx import check_instance


class Scenario(ModelComponent):
    """ 
    Concrete clauses are direct translations of the test cases 
    """
    name : str

    given : list[str]
    when : list[str]
    then : list[str]

    # When we check the DomainModel and this is missing, 
    # we'll then set these fields
    preds_missing : list[str] = []
    trans_missing : list[str] = []

    # These contain consistency checks
    # TODO we'll expand these later with details on
    # why precisely they're inconsistent
    given_preds_consistent : bool = True
    when_preds_consistent : bool = True
    all_preds_consistent : bool = True

    def pred_calls_to_iml (self) -> str:
        """
        return &&'ed string of all predicates
        """

        given_str = "\n&& ".join(map(lambda x: f"{x} s", self.given))
        when_str = "\n&& ".join(map(lambda x: f"{x} s a", self.when))

        match (len(self.given), len(self.when)):
            case (0, 0): return ""
            case (_, 0): return given_str
            case (0, _): return when_str
            case (_, _): return f"{given_str} \n&& {when_str}"

    def check_state_preds (self, model:DomainModel) -> bool:
        """
        Check that the state predicates are consistent (i.e. there's an instance)
        """

        state_preds_str = "\n&& ".join(map(lambda x: f"{x} s", self.given))

        instance_query = f"""
let pred_check (s : state) = 
{state_preds_str}

instance(pred_check)
"""
        print (instance_query)

        return check_instance(model.to_iml(), instance_query)
    
    def check_action_preds (self, model:DomainModel) -> bool:
        """
        Check that the action predicates are consistent (i.e. there's an instance that satisfies them)
        """

        if len(self.when) == 0: return True

        action_preds_str = "\n&& ".join(map(lambda x: f"{x} s a", self.when))

        instance_query = f"""
let pred_check (s : state) (a : action) =
{action_preds_str}

instance(pred_check)
"""
        print (instance_query)

        return check_instance(model.to_iml(), instance_query)

    def check_all_preds(self, model:DomainModel) -> bool:
        """
        Will return True if there's an instance for all the 
        """

        if len(self.when) == 0 and len(self.given) == 0:
            return True
        
        instance_query = f"""

let pred_check (s : state) (a : action) =
{self.pred_calls_to_iml()} 

instance(pred_check)
"""

        return check_instance(model.to_iml(), instance_query)

    def check_preds (self, model:DomainModel):
        """ 
        Check the predicates and update their status
        """

        self.preds_missing = []
        for p in self.given + self.when:
            if not model.pred_exists(p):
                self.preds_missing.append(p)

        self.trans_missing = []
        for t in self.then:
            if not model.trans_exists(t):
                self.trans_missing.append(t)

        self.given_preds_consistent = self.check_state_preds(model)
        self.when_preds_consistent = self.check_action_preds(model)
        self.all_preds_consistent = self.check_all_preds(model)

    def eval_transition (self, state_val:str, act_val:str) -> str:
        """
        Given concrete state and action values, evaluate the set of transitions
        """

        if len(self.then) == 0: return state_val

        trans_iml = ""
        for t in self.then:
            trans_iml += f"\nlet s = {t} s a in"

        trans_iml += "\n"

        return ''

    def preds_to_iml (self):
        """
        Return IML code of just the predicates (both types) encoded in IML
        """
        given_str = "&& \n".join(map(str, self.given))
        when_str = "&& \n".join(map(str, self.when))

        s = f"""
{given_str}

{when_str}
"""     

        return s

    def full_model_to_iml(self):
        """
        Create the full model
        """
        given_str = "&& \n".join(map(str, self.given))
        when_str = "&& \n".join(map(str, self.when))
        then_str = "\n".join(map(str, self.then))

        s = f"""
(* Scenario: {self.name} *)
let given_true = 
{given_str} 
in let when_true = 
{when_str}
in if given_true && when_true then
({then_str})
"""
        return s
    
    def __rich__ (self):
        table = Table("Attribute", "Value", show_lines=True)

        table.add_row("Name", self.name)

        table.add_row("Given predicates", Syntax("\n".join(self.given), 'OCaml'))
        table.add_row("When predicates", Syntax("\n".join(self.when), 'OCaml'))
        table.add_row("Then transitions", Syntax("\n".join(self.then), 'OCaml'))

        return table

class FormalizationReponse(BaseModel):
    """ """
    test_name_str : str
    scenarios : list[Scenario]
    domain_model : str