#
#   Imandra Inc.
#
#   refs.py
#

from .artifact import Artifact

class DocRef(Artifact):
    """
    Documentation reference
    """
    meta : str
    text : str
    
class SrcCodeRef(Artifact):
    """
    Source code reference
    """
    
    meta : str #
    language : str #
    file_path : str #
    src_code : str #
    iml_code : str # 