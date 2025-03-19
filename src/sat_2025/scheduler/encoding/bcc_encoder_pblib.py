from sat_based_2014.scheduler.encoding.VariableFactory import VariableFactory
from pypblib.pblib import PBConfig, Pb2cnf
from pypblib import pblib

class BCCEncoderPblib:
    _encoder = None

    def __init__(self):
        self.variable_factory = VariableFactory.get_variable_factory()

    def encode_resources_with_cardinalities(self,solver, maxTime: int, activities: list, resources: list):
        
        pbConfig = PBConfig() 
        pbConfig.set_AMK_Encoder(pblib.AMK_CARD)  
        pb2 = Pb2cnf(pbConfig) 

        def var(i, t):
            return i * maxTime + t + 1  

        for r in resources:
            capacity = r["capacity"]

            for t in range(maxTime):
                terms = []
                coeffs = []

                for i in range(1, len(activities) + 1):
                    duration = activities[i - 1]["duration"]
                    for start_time in range(max(0, t - duration + 1), t + 1):
                        terms.append(var(i, start_time))
                        coeffs.append(1)  
                if terms:
                    constraint = pblib.PBConstraint(terms, coeffs, pblib.BOUND_ATMOST, capacity)
                    cnf_formula = pb2.encode(constraint).get_clauses()

                    for clause in cnf_formula:
                        solver.add_clause(clause)