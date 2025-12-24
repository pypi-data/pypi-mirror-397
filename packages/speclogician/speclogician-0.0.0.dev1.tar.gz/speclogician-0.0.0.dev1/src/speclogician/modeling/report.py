#
#   Imandra Inc.
#
#   report.py
#

from pydantic import BaseModel

class DomainModelReport(BaseModel):
    """
    Domain model report
    """
    pass

class ScenarioReport(BaseModel):
    """
    Scenario report
    """

    num_scenarios : int
    num_failed : int
    num_conflicted : int

class ModelReport(BaseModel):
    """
    """
    dmodel_report : DomainModelReport
    scenario_report : ScenarioReport

class ArtifactReport(BaseModel):
    """
    """
    pass