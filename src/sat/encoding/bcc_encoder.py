
from sat.encoding.variable_factory import VariableFactory
from pypblib import pblib
from pypblib.pblib import PBConfig, Pb2cnf


class BCCEncoder:
    _encoder = None
    def __init__(self):
        self.vr=VariableFactory.get_variable_factory()

    @classmethod
    def get_bcc_encoder(cls):
        if cls._encoder is None:
            cls._encoder = BCCEncoder()
        return cls._encoder
    
    def gen_less_than_constraint_pblib_amk_card(self,cnf, bound, inputs, resource_id, time):
        pb_config=PBConfig()
        pb_config.set_PB_Encoder(pblib.AMK_CARD)
        pb2cnf = Pb2cnf(pb_config)

        cnf_formula=[]
        weights = [1] * len(inputs)
        max_var=pb2cnf.encode_both(weights,inputs,bound,bound,cnf_formula,self.vr.var_count)
        for clause in cnf_formula:
                cnf.add_clause(clause)