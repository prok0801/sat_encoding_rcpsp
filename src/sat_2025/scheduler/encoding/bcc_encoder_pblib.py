# from pysat.solvers import Glucose3
from sat_2025.scheduler.encoding.VariableFactory import VariableFactory
from pypblib import pblib
from pypblib.pblib import PBConfig, Pb2cnf



class BCCEncoderPblib:
    _encoder = None

    def __init__(self):
        self.variable_factory = VariableFactory.get_variable_factory()
        self.pb_config = PBConfig()
        self.pb_config.set_AMK_Encoder(pblib.AMK_CARD)
        self.pb2cnf = Pb2cnf(self.pb_config)



     # bound ~ k
    # inputs ~ list of literals
    def gen_less_than_constraint(self, solver, bound, inputs, resource_id, time):

        if inputs:
            cnf_formula=[]
            max_var=self.pb2cnf.encode_at_most_k(inputs,bound,cnf_formula,inputs[0]+1)
          
            for clause in cnf_formula:
                solver.add_clause(clause)
        


