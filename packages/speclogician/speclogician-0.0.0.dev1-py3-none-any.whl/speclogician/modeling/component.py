#
#   Imandra Inc.
#
#   component.py
#

import uuid
from pydantic import BaseModel, Field

class ModelComponent(BaseModel):
    """
    """

    comp_id : str = Field(default_factory=lambda: str(uuid.uuid4())) # assigned task ID, new one created if not provided
    