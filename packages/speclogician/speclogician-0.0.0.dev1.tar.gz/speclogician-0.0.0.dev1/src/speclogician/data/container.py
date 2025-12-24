#
#   Imandra Inc.
#
#   container.py
#

from pydantic import BaseModel

from .traces import TestTrace, LogTrace
from .refs import DocRef, SrcCodeRef

class ArtifactSummaryInfo(BaseModel):
    """ """
    pass

class ArtifactContainer(BaseModel):
    """ 
    Artifact container
    """

    test_traces : list[TestTrace] = []
    log_traces : list[LogTrace] = []
    doc_ref : list[DocRef] = []
    src_code : list[SrcCodeRef] = []


    def info(self):
        """
        """

        return {'hello': 123}

    def add(self):
        """ """
        pass
    