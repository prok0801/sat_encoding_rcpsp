from pysat.solvers import Glucose3
from sat.data.project import Project
from sat.encoding.sat_decoder import SatDecoder
from sat.encoding.variable_factory import VariableFactory

from sat.encoding.se_bdd_bdd import SatEncoderBddBdd
from sat.encoding.se_bdd_nsc import SatEncoderBddNsc
from sat.encoding.se_bdd_card import SatEncoderBddCard
from sat.encoding.se_card_bdd import SatEncoderCardBdd
from sat.encoding.se_card_card import SatEncoderCardCard
from sat.encoding.se_card_nsc import SatEncoderCardNsc
from sat.encoding.se_powerset import SatEncoderPowerset
from  sat.validate import  validate_project
import threading
import time

class TimeLimitExpired(Exception):
    pass

def timeout(func, args=(), kwargs={}, timeout_duration=1, default=None):
    class InterruptableThread(threading.Thread):
        def __init__(self):
            threading.Thread.__init__(self)
            self.result = None

        def run(self):
            try:
                self.result = func(*args, **kwargs)
            except Exception as e:
                self.result = default

    it = InterruptableThread()
    it.start()
    it.join(timeout_duration)
    if it.is_alive():  # Note: changed isAlive() to is_alive() for newer Python versions
        raise TimeLimitExpired()
    else:
        return it.result

class RcpspAlogithm:
    def __init__(self, project:Project):
        self.project = project
        self.cnf = self._init_solver()
        self.decoder= SatDecoder.get_sat_decoder()
        self.vr=VariableFactory.get_variable_factory()


    def calculate(self,type_encoder:str):
        
        if type_encoder == "bdd_bdd":
            sat_encoder = SatEncoderBddBdd.get_sat_encoder()
        elif type_encoder == "bdd_nsc":
            sat_encoder = SatEncoderBddNsc.get_sat_encoder()
        elif type_encoder == "bdd_card":
            sat_encoder = SatEncoderBddCard.get_sat_encoder()
        elif type_encoder == "card_bdd":
            sat_encoder = SatEncoderCardBdd.get_sat_encoder()
        elif type_encoder == "card_card":
            sat_encoder = SatEncoderCardCard.get_sat_encoder()
        elif type_encoder == "card_nsc":
            sat_encoder = SatEncoderCardNsc.get_sat_encoder()
        elif type_encoder=="powerset":
            sat_encoder=SatEncoderPowerset.get_sat_encoder()
        
        start_time = time.time()
        try:
            timeout(
                sat_encoder.handle,
                args=(self.cnf, self.project),
                timeout_duration=900
            )
            result = self.solve_problem()
            end_time = time.time()
            result['time'] = round(end_time - start_time, 3)
        except TimeLimitExpired:
            result = {
                'vars': self.cnf.nof_vars(),
                'clauses': self.cnf.nof_clauses(),
                'status': 'timeout',
                'time': 900,
            }
        self._reset()
        return result

    
    def solve_problem(self):
        status="unsat"
        if self.cnf.solve():
            status="sat"
            try:
                schedule = self.decoder.handle(self.cnf, self.project)
                # is_valid, validation_results =validate_project(schedule,self.project)
                # print("is_valid",is_valid)
                print("schedule",schedule)
            except Exception as e:
                status="error"
                print(e)
            
        result = {
            'vars': self.cnf.nof_vars(),
            'clauses': self.cnf.nof_clauses(),
            'status': status,
        }
        return result

            
    def _init_solver(self):
        cnf = Glucose3()
        cnf.conf_budget(3600 * 1000)
        # cnf.get_model()
        return cnf
    
    def _reset(self):
        self.cnf=self._init_solver()
        self.vr.reset()






