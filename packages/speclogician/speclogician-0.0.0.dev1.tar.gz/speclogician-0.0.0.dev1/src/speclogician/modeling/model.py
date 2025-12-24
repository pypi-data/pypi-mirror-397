    #
#   Imandra Inc.
#
#   model.py
#

from pydantic import BaseModel

from .report import (
    ModelReport, DomainModelReport, ScenarioReport
)
from .domain import DomainModel
from .scenario import Scenario 
from ..utils.imx import run_decomp

from imandrax_api_models import DecomposeRes, InstanceRes, VerifyRes

from ..state.change import (
    ModelChange, 
    DomainModelBaseEdit, 
    PredicateAdd, 
    PredicateEdit,
    PredicateRemove, 
    TransitionAdd, 
    TransitionEdit, 
    ScenarioAdd,
    ScenarioEdit,
    ScenarioRemoved
)

from ..utils import console

class PredicateDetails(BaseModel):
    """ 
    We use this to compute details on how the predicates are used, how to search for it, etc...
    """

    predicate : str # predicate itself
    num_given : int # number of times it appears in given
    num_when : int # number of times it appears in when
    num_complements : int # number of times the complement appears

    given_scenarios : list[Scenario] # Scenarios where the predicate appears in 'Given' clause
    where_scenarios : list[Scenario] # Scenarios where the predicate appears in 'Where' clause
    then_scenarios  : list[Scenario] # Scenarios where the predicate appears in 'Then' clause

class ModelSummaryInfo(BaseModel):
    """ """
    domain_iml_status : str

    preds_errored : int
    preds_total : int

    scenarios_total : int
    scenarios_errored : int
    
class Model(BaseModel):
    """
    A model is a combination of Domain Model and list of scenarios
    """

    domain_model : DomainModel = DomainModel() # Domain model
    scenarios : list[Scenario] = [] # The list of Scenarios

    def info(self) -> ModelSummaryInfo:
        """

        """
        
        preds_errored = 0
        scenarios_errored = 0
        
        msi = ModelSummaryInfo (
            domain_iml_status=self.domain_model.base_status,

            preds_total = len(self.domain_model.state_preds) + len(self.domain_model.action_preds),
            preds_errored = preds_errored,

            scenarios_total = len(self.scenarios),
            scenarios_errored = scenarios_errored
        )

        return msi

    def proc_change(self, change : ModelChange):
        """
        Process model change
        """
        if isinstance(change, DomainModelBaseEdit):
            self.domain_model.set_base(change.new_base_src)
        elif isinstance(change, PredicateAdd):
            pass
        elif isinstance(change, PredicateEdit):
            pass
        elif isinstance(change, PredicateRemove):
            pass
        elif isinstance(change, TransitionAdd):
            pass
        elif isinstance(change, TransitionEdit):
            pass
        elif isinstance(change, ScenarioAdd):
            pass
        elif isinstance(change, ScenarioEdit):
            pass
        elif isinstance(change, ScenarioRemoved):
            pass
        else:
            pass

    def scenario_model(self):
        """
        Synthesize a model from the scenarios
        """

        scenario_logic = ""
        for s in self.scenarios:
            scenario_logic += f"{s.full_model_to_iml()}\n"

        model = f"""
let scenarios (s : state) (a : action) = 
{scenario_logic} else
false
"""
        return model

    def scenario_complement(self, json_out:bool = False) -> None|DecomposeRes:
        """
        Perform region decomp on the model 
        """

        pred_str = ""

        for s in self.scenarios:
            pred_str += f"if (\n{s.pred_calls_to_iml()}\n) then true else\n"
        
        decomp_query = f"""
    
let complement (s : state) (a : action) = 
{pred_str}
false

let not_covered (s : state) (a : action) = 
    (complement s a) = false

let wrapper (s : state) (a : action) = 
    complement s a
[@@decomp top ~assuming:[%id not_covered] ()]
"""
        
        if not json_out:
            with console.status(":robot: [bold]Computing regions..."):        
                result = run_decomp(self.domain_model.to_iml(), decomp_query)
        else:
            result = run_decomp(self.domain_model.to_iml(), decomp_query)


        if not result.regions_str:
            if not json_out:
                console.print(":warning: Failed to compute regions...")
            return None

        if not json_out:
            console.print(f":robot::rocket: [bold]Computed: {len(result.regions_str)} regions!")        
            for idx, region_str in enumerate(result.regions_str):
                console.rule(f"[bold red]Region: {idx+1}")
                
                if region_str.constraints_str:
                    console.print("Constraints:")
                    for c in region_str.constraints_str:
                        console.print (f"    - {c}")
                            
                if region_str.model_str:
                    console.print("Sample model input:")
                    console.print(f"    - {region_str.model_str}")
            return None        
        else:
            return result

    def report(self) -> ModelReport:

        dmodel_report = self.domain_model.report()

        scenario_report = ScenarioReport(
#            num_scenarios=len(self.)
            num_scenarios = 0,
            num_conflicted = 0,
            num_failed= 0
        )

        return ModelReport(dmodel_report=dmodel_report, scenario_report=scenario_report)

    def check_logic(self):
        """
        Check that the resulting logic is correct
        """
        pass

    def rich_scenarios(self):
        """
        Return a table of scenarios 
        """
        pass

    def __rich__(self):
        """ """
        pass
