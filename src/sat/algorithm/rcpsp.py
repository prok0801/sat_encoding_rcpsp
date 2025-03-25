from pysat.solvers import Glucose3
from sat.data.project import Project
from sat.encoding.sat_encoder import SatEncoder
from sat.encoding.sat_decoder import SatDecoder
from sat.encoding.variable_factory import VariableFactory

class RcpspAlogithm:
    def __init__(self, project:Project):
        self.project = project
        self.cnf = self._init_solver()
        self.encoder = SatEncoder.get_sat_encoder()
        self.decoder= SatDecoder.get_sat_decoder()
        self.vr=VariableFactory.get_variable_factory()


    def calculate(self):
        self.encoder.handle(self.cnf,self.project)
        self.solve_problem()

    def solve_problem(self):
        if self.cnf.solve():
            print("Solution found!")
            model = self.cnf.get_model()
            print(len(self.vr.var_map.values()))
            print(f"Number of variables: {self.cnf.nof_vars()}")
            # print(model)
        else:
            print("No solution found.")
            
    def _init_solver(self):
        cnf = Glucose3()
        cnf.conf_budget(3600 * 1000)
        return cnf
    
    def _reset(self):
        self.cnf.reset()
        self.vr.reset()






