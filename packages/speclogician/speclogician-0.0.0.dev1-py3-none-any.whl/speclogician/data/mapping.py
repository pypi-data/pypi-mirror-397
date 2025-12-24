#
#   Imandra Inc.
#
#   mapping.py
#

from pydantic import BaseModel
from typing import Dict

from enum import StrEnum

class ElementType(StrEnum):
    ArtifactType = 'data_artifact'
    ComponentType = 'model_component'

class ArtifactMap(BaseModel):
    """
    Map between artifacts and model components. We maintain two structures to 
    handle potentially large datasets (e.g. massive logs)
    """

    art_to_comp_map : Dict[str, list[str]] = {}
    comp_to_art_map : Dict[str, list[str]] = {}

    def add_connection (self, art_id : str, comp_id : str):
        """
        Add a link between artifact and model component
        """
        if art_id not in self.art_to_comp_map:
            self.art_to_comp_map[art_id] = []
        
        if comp_id not in self.art_to_comp_map[art_id]:
            self.art_to_comp_map[art_id].append(comp_id)

        if comp_id not in self.comp_to_art_map:
            self.comp_to_art_map[comp_id] = []
        
        if art_id not in self.comp_to_art_map[comp_id]:
            self.comp_to_art_map[comp_id].append(art_id)        

    def rem_connection (self, artifact_id : str, comp_id : str):
        """
        Remove a connection
        """

        if artifact_id in self.art_to_comp_map:
            if comp_id in self.art_to_comp_map[artifact_id]:
                self.art_to_comp_map[artifact_id].remove(comp_id)
        else:
            return False

        if comp_id in self.comp_to_art_map:
            if artifact_id in self.comp_to_art_map[comp_id]:
                self.comp_to_art_map[comp_id].remove(artifact_id)
    
    def rem_element (self, elem_type : ElementType, str_id : str):
        """
        Remove element from the both maps
        """
        
        if elem_type == ElementType.ArtifactType:
            if str_id in self.art_to_comp_map:
                del self.art_to_comp_map[str_id]
                for comp_id in self.comp_to_art_map.keys():
                    if str_id in self.comp_to_art_map[comp_id]:
                        self.comp_to_art_map[comp_id].remove(str_id)
        else:
            if str_id in self.comp_to_art_map:
                del self.comp_to_art_map[str_id]
                for art_id in self.art_to_comp_map.keys():
                    if str_id in self.art_to_comp_map[art_id]:
                        self.art_to_comp_map[art_id].remove(str_id)

    def get_arts_for_component(self, comp_id : str) -> list[str]:
        """
        Return linked artifacts for a model component
        """
        if comp_id in self.comp_to_art_map:
            return self.comp_to_art_map[comp_id]
        return []

    def get_comp_for_artifact(self, art_id : str) -> list[str]:
        """
        Return linked model components for an artifact
        """

        if art_id in self.art_to_comp_map:
            return self.art_to_comp_map[art_id]
        return []