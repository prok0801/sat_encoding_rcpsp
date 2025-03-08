# scheduler/encoding/sat_decoder.py

from ..encoding.VariableFactory import VariableFactory
from ..log.Log import Log  # Adjust the import if your Log is elsewhere

class SATDecoder:
    _decoder = None  # Singleton instance

    def __init__(self):
        self.variable_factory = VariableFactory.get_variable_factory()

    @classmethod
    def get_decoder(cls):
        """
        Returns the singleton SATDecoder instance.
        """
        if cls._decoder is not None:
            return cls._decoder
        cls._decoder = SATDecoder()
        return cls._decoder

    def decode(self, project, model):
        """
        Decodes a SAT solver model and logs the start time for activities.
        
        :param project: A Project instance.
        :param model: A list of integers representing the SAT solver's model.
        """
        if model is None:
            return

        for value in model:
            if value > 0:
                # Retrieve the variable key (a list of integers) for the given model variable.
                variable = self.variable_factory.get_key_by_value(value)
                if variable[0] == VariableFactory.VARIABLE_START:
                    activity = project.get_activity_by_id(variable[1])
                    Log.i(str(activity) + " starting point: " + str(variable[2]))
