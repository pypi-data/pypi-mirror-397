#
#   Imandra Inc.
#
#   change.py
#   

from pydantic import BaseModel
# from typing import Optional

class ModelChange(BaseModel):
    """
    """

    def short_str(self):
        return ""

    def __str__ (self):
        return ""

class DomainModelBaseEdit(BaseModel):
    """
    """
    new_base_src : str

    def short_str(self):
        """ """
        return ''

    def __str__ (self):
        return ""

class PredicateAdd(BaseModel):
    """
    """
    pred_type : str
    pred_name : str
    pred_src : str

    def short_str(self):
        """ """
        return f''

    def __str__(self):
        return ""

class PredicateEdit(BaseModel):
    """
    """
    pred_name : str
    pred_src : str

    def short_str(self):
        return f'PredicateEdit: name={self.pred_name}'

    def __str__(self):
        return f'PredicateEdit: {self.pred_name}'
    
class PredicateRemove(BaseModel):
    """
    """
    pred_name : str

    def short_str(self):
        return f'PredicateRemove: name = {self.pred_name}'

    def __str__(self):
        return "PredicateRemove"

class TransitionAdd(BaseModel):
    """
    """
    pred_name : str
    pred_src : str

    def short_str(self):
        return f''

    def __str__(self):
        return "TransitionAdd: "
    
class TransitionEdit(BaseModel):
    """
    """
    tran_name : str
    tran_src : str

    def short_str(self):
        return f''

    def __str__(self):
        return "TransitionEdit: "

class TransitionRemove(BaseModel):
    """ """
    tran_name : str

    def short_str(self):
        return ''

    def __str__(self):
        return "TransitionRemove: "

class ScenarioAdd(ModelChange):
    """
    Add a new scenario
    """
    name : str

    def __str__(self):
        return ""

class ScenarioEdit(ModelChange):
    """
    Edit a scenario
    """
    scenario_name : str

    def short_str(self):
        return f''
    
    def __str__(self):
        return ''

class ScenarioRemoved(ModelChange):
    """
    Remove a scenario
    """
    scenario_name : str

    def short_str(self):
        return ''

    def __str__(self):
        return ""

if __name__ == "__main__":

    from ..utils import console

    console.print(ScenarioAdd(name="new_name"))
    console.rule()

    console.print(ScenarioEdit(scenario_name="hello"))
    console.rule()

    console.print(ScenarioRemoved(scenario_name=""))
    console.rule()

