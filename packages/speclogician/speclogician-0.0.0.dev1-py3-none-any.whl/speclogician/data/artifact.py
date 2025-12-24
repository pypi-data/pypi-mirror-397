#
#   Imandra Inc.
#
#   artifact.py
#

import uuid
from pydantic import BaseModel, Field

class Artifact(BaseModel):
    """
    """
    art_id : str = Field(default_factory=lambda: str(uuid.uuid4())) # assigned task ID, new one created if not provided

class TraceArtifact(Artifact):
    
    given : str
    when : str
    then : str

    valid_iml : bool = False