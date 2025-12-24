#
#   Imandra Inc.
#
#   sl_cmd.py
#

from cmd2 import Cmd

class SpecLogicianCmdApp(Cmd):
    """
    """

    def __init__ (self):
        """
        """
        Cmd.__init__(self, include_py=True)
   
        pass

    def do_data_view(self):
        """
        """
        pass

    def do_data_tests(self):
        """ """
        pass

    def do_data_tests_view(self):
        """
        """
        pass

    def do_scenario_view(self):
        """
        """
        pass

    def do_scenario_list (self):
        """
        """
        pass

    def do_scenario_update(self):
        """
        """
        pass

    def do_scenario_rm(self):
        """
        """
        pass

    def do_dmodel_view(self, _):
        """
        Print out the whole domain model
        """
        pass

    def do_dmodel_predicates_state(self, _):
        """ Print just the state predicates """
        pass

    def do_dmodel_predicates_action(self, _):
        """ """
        pass

    def do_dmodel_transitions(self, _):
        """ """
        pass

if __name__ == "__main__":
    import sys

    c = SpecLogicianCmdApp()
    sys.exit(c.cmdloop())