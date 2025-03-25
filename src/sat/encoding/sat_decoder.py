from sat.encoding.variable_factory import VariableFactory
from sat.data.project import Project

class SatDecoder:
    _decoder=None
    def __init__(self):
        self.variable_factory = VariableFactory.get_variable_factory()

    @classmethod
    def get_sat_decoder(cls):
        if cls._decoder is None:
            cls._decoder = SatDecoder()
        return cls._decoder
    def handle (self, project:Project):
        pass 
