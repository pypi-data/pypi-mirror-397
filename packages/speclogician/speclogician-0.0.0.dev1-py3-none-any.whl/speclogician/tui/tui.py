#
#   Imandra Inc.
#
#   tui.py
#

from textual.app import App, ComposeResult
from textual.widgets import (
    Footer, Header, TabbedContent, TabPane,Static, ListView, ListItem, Label
)
from textual.reactive import reactive
from textual.containers import VerticalScroll

from ..modeling.model import TestFormalization, TLState, Scenario
from pathlib import Path

class FileItem (ListItem):
    def __init__(self, label: str) -> None:
        super().__init__()
        self.label = label

    def compose( self ) -> ComposeResult:
        yield Label(Path(self.label).name)


class DetailView(Static):
    """
    """

    tf : reactive[TestFormalization | None] = reactive(None, always_update=True)

    def watch_tf(self, _, tf:TestFormalization|None) -> None:
        """
        """
        if tf is None: return
        if not hasattr(self, 'view'): return

        self.view.update(tf.__rich__())

    def compose (self) -> ComposeResult:
        """
        """
        with VerticalScroll():
            self.view = Static("N/A")

            yield self.view

class PredicateList(Static):
    """
    """

    pred_list : reactive[ScenarioPredList | None] = reactive(None, always_update=True)

    def compose(self) -> ComposeResult:
        """ 
        """
        self.view = 

        yield self.view

class SpecLogicianApp(App):
    """
    """
    CSS_PATH = "box.tcss"

    def __init__ (self, tl_state : TLState, **kwargs):
        super().__init__ (**kwargs)

        self.tl_state = tl_state

    def compose(self) -> ComposeResult:
        """
        """

        yield Header()

        with TabbedContent(initial="scenarios"):

            with TabPane("Scenarios", id="scenarios"):
                self.items = ListView (
                    *[FileItem(t.filepath) for t in self.tl_state.tfs()],
                    classes="box",
                    id="items"
                )
                yield self.items 

                self.detail =  DetailView("hello", id="detail", classes="box")
                yield self.detail
            
            with TabPane("Domain Modle", id="model"):
                self.domain_model = Static(self.tl_state.rich_model())
                yield self.domain_model

            with TabPane("Concrete Scenarios", id="concrete"):
                self.concrete_scenarios = PredicateList()
                self.concrete_scenarios.pred_list = self.tl_state.concrete()
                yield self.concrete_scenarios

            with TabPane("Predicate Scenarios", id="predicates"):
                self.predicate_scenarios = PredicateList()
                self.predciate_scenarios.pred_list = self.tl_state.predicates()
                yield self.predicate_scenarios

            with TabPane("Abstract Scenarios", id="abstract"):
                self.abstract_predicates = PredicateList()
                self.abstract_predicates.pred_list = self.tl_state.abstract()
                yield self.abstract_predicates()

        yield Footer()

        # Initialize with first model
        if len(self.tl_state.tfs()) > 0:
            self.detail.tf = self.tl_state.tf_by_index(0)

    def action_show_tab(self, tab: str) -> None:
        """Switch to a new tab."""
        self.get_child_by_type(TabbedContent).active = tab

    def on_list_view_highlighted(self, event: ListView.Highlighted) -> None:
        """  """
        self.detail.tf = self.tl_state.tf_by_filepath(event.item.label)

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """ """
        self.detail.tf = self.tl_state.tf_by_index(event.index)

if __name__ == "__main__":
    sample_state = "../data/broadridge/integration/split_tests/tf_state.json"
    state = TLState.fromJSON(Path(sample_state).read_text())
    app = TestLogicianApp(state)
    app.run()
