#
#   Imandra Inc.
#
#   state.py
#

import os
from pathlib import Path
from pydantic import BaseModel

from rich.table import Table, Column
from rich.text import Text

from speclogician.modeling.model import Model
from speclogician.data.mapping import ArtifactMap
from speclogician.data.container import ArtifactContainer
from speclogician.state.change import ModelChange
from speclogician.modeling.report import ArtifactReport
from speclogician.utils import console



class StateReport(BaseModel):
    pass


class StateInstance(BaseModel):
    """
    State Instance class
    """

    state_idx : int
    model : Model = Model() # Latest domain model
    art_container : ArtifactContainer = ArtifactContainer() # This keeps us 
    art_map : ArtifactMap = ArtifactMap() # Artifact map

    changes : list[ModelChange] = []

    def get_matched_stats (self) -> dict[str, int]:
        """ 
        State has the info about mappings from data artifacts to model components and vice versa.
        We need to compute the stats here
        """

        stats : dict[str, int] = {}
        stats['scenarios_matched'] = 0
        stats['predicates_matched'] = 0
        stats['test_traces_matched'] = 0
        stats['log_traces_matched'] = 0
        stats['src_code_arts_matched'] = 0
        stats['doc_arts_matched'] = 0
 
        for s in self.model.scenarios:
            if s.comp_id in self.art_map.comp_to_art_map:
                stats['scenarios_matched'] += 1
        
        for p in self.model.domain_model.action_preds + self.model.domain_model.state_preds:
            if p.comp_id in self.art_map.comp_to_art_map:
                stats['predicates_matched'] += 1
        
        for tt in self.art_container.test_traces:
            if tt.art_id in self.art_map.art_to_comp_map:
                stats['test_traces_matched'] += 1
        
        for lt in self.art_container.log_traces:
            if lt.art_id in self.art_map.art_to_comp_map:
                stats['log_traces_matched'] += 1
        
        for sa in self.art_container.src_code:
            if sa.art_id in self.art_map.art_to_comp_map:
                stats['src_code_arts_matched'] += 1

        for dr in self.art_container.doc_ref:
            if dr.art_id in self.art_map.art_to_comp_map:
                stats['doc_arts_matched'] += 1
            
        return stats

    def summary(self) -> dict[str,int|str]:
        """ Return a dict with various StateInstance statistics """


        matched_stats = self.get_matched_stats()

        s : dict[str, int|str] = {}

        s['idx'] = str(self.state_idx)

        
        s['changes'] = ",\n".join(map (lambda x: x.short_str(), self.changes))
        
        model_info = self.model.info()

        s['domain_status'] = f"{model_info.domain_iml_status}"

        # Predicates 
        s['predicates'] = f"{model_info.preds_total} ({model_info.preds_errored}/45%; {matched_stats['predicates_matched']}/55%)"

        # Scenarios
        s['scenarios'] = f"{model_info.scenarios_total} ({model_info.scenarios_errored}/45%; {matched_stats['scenarios_matched']}/55%)"

        art_info = self.art_container.info()

        # Test traces
        s['test_data'] = "250 (122/45%; 100/55%)"
        s['log_data'] = "250 (122/45%; 100/55%)"
        s['src_code_arts'] = "1200 (450/500%)"
        s['doc_arts'] = "1200 (230/45%)"

        return s

    def short_summary(self):
        """ """
        return f'=> hello, again {1+1}'

    def report(self) -> StateReport:
        """
        Generate a full report
        """

        model_report = self.model.report()
        artifact_report = ArtifactReport()

        return StateReport (
            model_report=model_report, 
            artifact_report=artifact_report
        )

class InstancesList(BaseModel):
    """
    """
    states : list[StateInstance]

    def __rich__(self):
        """ """
        
        columns = [
            Column(header='State ID', justify="center")
            , Column(header='Changes', justify="center")
            , Column(header='Domain model', justify="center")
            , Column(header='Preds\n # (Errors, Used)', justify="center")
            , Column(header='Scenarios\n # (Errors, Used)', justify="center")
            , Column(header='Test traces\n # (Formalized, Matched)', justify="center")
            , Column(header='Log traces\n # (Formalized, Matched)', justify="center")
            , Column(header='Src code arts\n # (Matched)', justify="center")
            , Column(header='Doc arts\n # (Matched)', justify="center")
        ]

        t = Table (
            *columns
            , title="SpecLogician State List"
            , expand = True
            , highlight=True
            #, padding=(0, 1) # Optional padding adjustments
            , show_edge=False
            #, show_lines=True
        )

        for s in self.states[::-1]:
            ss = s.summary()
            t.add_row(
                Text(ss['idx']),
                Text(ss['changes']),
                Text(ss['domain_status']),
                Text(ss['predicates']),
                Text(ss['scenarios']),
                Text(ss['test_data']),
                Text(ss['log_data']),
                Text(ss['src_code_arts']),
                Text(ss['doc_arts'])
            )
        return t

class State(BaseModel):
    """
    TestLogician state (contains the various test formalizations)
    """

    instances : list[StateInstance] = []
    curr_state_idx : int = -1

    def set_curr_state_idx(self, new_idx:int) -> None:
        """
        Set the state instance cursor to `new_idx`
        """

        self.curr_state_idx = new_idx

    def curr_state(self) -> StateInstance:
        return self.instances[self.curr_state_idx]

    def inst_list(self):
        """ """
        return InstancesList(states=self.instances)

    def process_change(
            self,
            change : ModelChange,
            cut_new_instance : bool = True
        ):
        """ 
        Process change
        """

        self.curr_state().model.proc_change(change)

    def to_json(self):
        """
        """
        return self.model_dump_json()

    @staticmethod
    def from_json(j : str):
        """
        Load in the State value
        """
        return State.model_validate_json(j)
    
    def save(self, dirpath:str):
        """
        """
        with open(os.path.join(dirpath, 'sl_state.json'), 'w') as outfile:
            print(self.to_json(), file=outfile)

    @staticmethod
    def from_dir (dirpath:str):
        try:
            state_path = os.path.join(dirpath, "sl_state.json")
            data = Path(state_path).read_text()
            state = State.from_json(data)    
        except:
            return None
        
        return state

if __name__ == "__main__":

    states = [
        StateInstance(state_idx=1),
        StateInstance(state_idx=2),
        StateInstance(state_idx=3),
        StateInstance(state_idx=4),
        StateInstance(state_idx=5),
        StateInstance(state_idx=6)
    ]

    il = InstancesList(states=states)

    console.print(il.__rich__())