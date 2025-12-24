# 
#   Imandra Inc.
#
#   overlay.py
#


import yaml, os
from pydantic import BaseModel
from rich import print
from rich.console import Console
from typing import List, Optional
from rich.panel import Panel
from rich.table import Table
from rich.syntax import Syntax
from rich.markdown import Markdown
from rich.console import RenderableType

# ----------------------------
# Example field
# ----------------------------

class Example(BaseModel):
    source: str      # original snippet in the source DSL/language
    iml: str         # expected IML output


# ----------------------------
# Mapping section
# ----------------------------

class TitleMapping(BaseModel):
    type: str
    pattern: str
    extract: int


class SectionMapping(BaseModel):
    keywords: Optional[List[str]] = None
    chained_keywords: Optional[List[str]] = None
    section: Optional[str] = None
    transform: Optional[str] = None


class Mapping(BaseModel):
    title: TitleMapping
    given: SectionMapping
    when: SectionMapping
    then: SectionMapping


# ----------------------------
# Background
# ----------------------------

class Background(BaseModel):
    enabled: bool
    keywords: List[str]
    given_keywords: List[str]


# ----------------------------
# State configuration
# ----------------------------

class StateConfig(BaseModel):
    initial_name: str
    transition_prefix: str


# ----------------------------
# Rules and constraints
# ----------------------------

class Rules(BaseModel):
    state_transitions: List[str]
    predicates: List[str]


class YamlConstraints(BaseModel):
    double_quote_strings: bool
    escape_quotes: bool


# ----------------------------
# MAIN OVERLAY MODEL
# ----------------------------

class Overlay(BaseModel):
    language: str
    name: str
    description: str
    ext : str

    mapping: Mapping
    background: Background
    state: StateConfig
    rules: Rules
    yaml_constraints: YamlConstraints

    notes: List[str]

    # NEW: structured example consisting of source + IML
    example: Optional[Example] = None

    def to_yaml (self):
        data = self.model_dump()     # Pydantic → dict
        return yaml.safe_dump(data, sort_keys=False)

    # --------------------------------------------------
    # Rich pretty-printer
    # --------------------------------------------------
    def __rich__(self) -> RenderableType:
        root = Table.grid(padding=1)
        root.title = f"[bold cyan]Overlay ({self.language})[/bold cyan]"

        # Metadata
        meta = Table(show_header=False, box=None)
        meta.add_row("[bold]Name[/bold]", self.name)
        meta.add_row("[bold]Language[/bold]", self.language)
        meta.add_row("[bold]Description[/bold]", self.description)
        root.add_row(Panel(meta, title="Metadata", border_style="cyan"))

        # Mapping
        map_table = Table(show_header=True, header_style="bold magenta")
        map_table.add_column("Section")
        map_table.add_column("Keywords")
        map_table.add_column("Chained")
        map_table.add_column("Transform")

        def fmt(xs):
            return ", ".join(xs) if xs else ""

        map_table.add_row(
            "Title",
            f"{self.mapping.title.type} / {self.mapping.title.pattern}",
            "",
            f"extract={self.mapping.title.extract}",
        )

        for name, sec in [
            ("Given", self.mapping.given),
            ("When", self.mapping.when),
            ("Then", self.mapping.then),
        ]:
            map_table.add_row(
                name,
                fmt(sec.keywords),
                fmt(sec.chained_keywords),
                sec.transform or "",
            )

        root.add_row(Panel(map_table, title="Mapping", border_style="magenta"))

        # Background
        bg = Table(show_header=False, box=None)
        bg.add_row("[bold]Enabled[/bold]", str(self.background.enabled))
        bg.add_row("[bold]Keywords[/bold]", fmt(self.background.keywords))
        bg.add_row("[bold]Given Keywords[/bold]", fmt(self.background.given_keywords))
        root.add_row(Panel(bg, title="Background", border_style="green"))

        # State Config
        st = Table(show_header=False, box=None)
        st.add_row("[bold]Initial[/bold]", self.state.initial_name)
        st.add_row("[bold]Transition Prefix[/bold]", self.state.transition_prefix)
        root.add_row(Panel(st, title="State Config", border_style="yellow"))

        # Rules
        rules_t = Table(show_header=True, header_style="bold blue")
        rules_t.add_column("State Transitions")
        rules_t.add_column("Predicates")

        max_len = max(len(self.rules.state_transitions), len(self.rules.predicates))
        for i in range(max_len):
            left = self.rules.state_transitions[i] if i < len(self.rules.state_transitions) else ""
            right = self.rules.predicates[i] if i < len(self.rules.predicates) else ""
            rules_t.add_row(left, right)

        root.add_row(Panel(rules_t, title="Rules", border_style="blue"))

        # YAML Constraints
        yc = Table(show_header=False, box=None)
        yc.add_row("[bold]Double Quote Strings[/bold]", str(self.yaml_constraints.double_quote_strings))
        yc.add_row("[bold]Escape Quotes[/bold]", str(self.yaml_constraints.escape_quotes))
        root.add_row(Panel(yc, title="YAML Constraints", border_style="red"))

        # Notes
        notes_md = Markdown("\n".join(f"- {n}" for n in self.notes))
        root.add_row(Panel(notes_md, title="Notes", border_style="white"))

        # Structured Example
        if self.example:
            # Original source language
            source_block = Syntax(
                self.example.source,
                self.language,  # use overlay.language for syntax highlighting
                theme="monokai",
                line_numbers=False,
            )
            root.add_row(Panel(source_block, title="Example (Source)", border_style="bright_magenta"))

            # IML output
            iml_block = Syntax(
                self.example.iml,
                "ocaml",   # Imandra IML is OCaml-like
                theme="monokai",
                line_numbers=False,
            )
            root.add_row(Panel(iml_block, title="Example (IML)", border_style="bright_green"))

        return Panel(root, border_style="bright_white")
    
    @staticmethod
    def from_file(path:str) -> 'Overlay':
        """Load an overlay YAML file and parse it into the Overlay model."""
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        overlay : Overlay = Overlay.model_validate(data)
        return overlay

class Overlays(BaseModel):
    """
    """
    overlays : list[Overlay]

    def list_overlays(self):
        for o in self.overlays:
            print ('---' * 10)
            print (f"Name: {o.name}")
            print (f"Language: {o.language}")
            print (f"Description: {o.description}")

    def names(self) -> list[str]:
        return list(map(lambda x: x.name, self.overlays))

    def get(self, name:str) -> Overlay|None:
        if name in self.names():
            return next(filter(lambda x: x.name == name, self.overlays))
        else:
            return None

    @staticmethod
    def from_dir(dir_path:str) -> 'Overlays':
        overlays : list[Overlay] = []
        for file in os.listdir(dir_path):
            if file.endswith('.yaml'):
                overlays.append(Overlay.from_file(os.path.join(dir_path, file)))
        
        return Overlays(overlays=overlays)


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("[red]Usage: python load_overlay.py <overlay.yaml>[/red]")
        sys.exit(1)

    overlay_file = sys.argv[1]
    overlay = Overlay.from_file(overlay_file)

    console = Console()
    console.print(overlay)