
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
        pb_config.set_AMK_Encoder(pblib.AMK_CARD)
        pb2cnf = Pb2cnf(pb_config)

        cnf_formula=[]
        max_var=pb2cnf.encode_at_most_k(inputs,bound,cnf_formula,inputs[0]+1)
        for clause in cnf_formula:
                cnf.add_clause(clause)