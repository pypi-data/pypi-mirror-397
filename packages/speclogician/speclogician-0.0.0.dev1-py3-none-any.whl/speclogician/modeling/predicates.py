#
#   Imandra Inc.
#
#   predicates.py
#


from .component import ModelComponent

class StatePredicate(ModelComponent):
    """
    """
    name : str # name of the predicate
    body : str # actual implementation

    def __str__ (self):
        """
        """
        return f"{self.name} s"

    def to_iml (self):
        """
        """
        return f"let {self.name} (s : state) : bool = \n {self.body}\n"

class ActionPredicate(ModelComponent):
    """
    Predicate involving a state and an action
    """
    name : str # name of the predicate
    body : str # body

    def __str__(self):
        """
        """
        return f"{self.name} s a"

    def to_iml(self):
        """
        Convert to IML here
        """
        return f"let {self.name} (s : state) (a : action) : bool = \n {self.body}\n"

class Transition(ModelComponent):
    """
    Transition functions are used to update the state
    """
    name : str # Name of the transition function
    body : str # Name of the 

    def __str__ (self):
        return f"{self.name} s a"

    def to_iml (self):
        """
        """
        return f"let {self.name} (s : state) (a : action) : state = \n {self.body}"
