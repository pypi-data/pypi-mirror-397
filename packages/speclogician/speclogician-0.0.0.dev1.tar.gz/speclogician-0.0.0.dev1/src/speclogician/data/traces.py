#
#   Imandra Inc.
#
#   trace.py
#

from .artifact import TraceArtifact

class TestTrace (TraceArtifact):
    """
    Test trace formalization
    """    

    name : str # Test case name
    filepath : str # Original test filepath
    language : str # Language of the original source code
    contents : str # Original test contents
    time : str # Time when this done

    # Contain 

class LogTrace(TraceArtifact):
    """
    Log tace formalization
    """

    filename : str # 
    contents : str # Contents of the log entry

    # Formalized entry
    given : str
    when : str
    then : str

    