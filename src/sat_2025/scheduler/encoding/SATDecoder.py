# scheduler/encoding/sat_decoder.py

from ..encoding.VariableFactory import VariableFactory

class SATDecoder:
    _decoder = None  # Biến singleton

    def __init__(self):
        self.variable_factory = VariableFactory.get_variable_factory()

    @classmethod
    def get_decoder(cls):

        if cls._decoder is None:
            cls._decoder = SATDecoder()
        return cls._decoder

    def decode(self, project, model):

        if model is None:
            return

        for value in model:
            if value > 0:
                variable = self.variable_factory.get_key_by_value(value)
                if variable and variable[0] == VariableFactory.VARIABLE_START:
                    activity = project.get_activity_by_id(variable[1])
                    print(f"{activity} Startpunkt: {variable[2]}")
                    
