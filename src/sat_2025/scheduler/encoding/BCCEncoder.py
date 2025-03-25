# from pysat.solvers import Glucose3
from sat_2025.scheduler.encoding.VariableFactory import VariableFactory


class BCCEncoder:
    _encoder = None

    def __init__(self):
        self.variable_factory = VariableFactory.get_variable_factory()

    @classmethod
    def get_bcc_encoder(cls):
        if cls._encoder is None:
            cls._encoder = cls()
        return cls._encoder

    def gen_half_adder(self, solver, a, b, sum, carry):
        solver.add_clause([a, -b, sum])
        solver.add_clause([-a, b, sum])
        solver.add_clause([-a, -b, carry])

    def gen_full_adder(self, solver, a, b, c, sum, carry):
      
        solver.add_clause([a, b, -c, sum])
        solver.add_clause([a, -b, c, sum])
        solver.add_clause([-a, b, c, sum])
        solver.add_clause([-a, -b, -c, sum])
        solver.add_clause([-a, -b, carry])
        solver.add_clause([-a, -c, carry])

    def gen_par_counter(self, solver, input, output, resource_id, time):
        m = self.ilog2(len(input))
        if len(input) == 1:
            output.append(input[0])
            return output

        p_end = (2 ** m) - 1

        a_inputs, b_inputs = input[:p_end], input[p_end:-1]
        a_outputs, b_outputs = [], []

        a_outputs = self.gen_par_counter(solver, a_inputs, a_outputs, resource_id, time)
        if b_inputs:
            b_outputs = self.gen_par_counter(solver, b_inputs, b_outputs, resource_id, time)

        m_min = min(len(a_outputs), len(b_outputs))
        carry = input[-1]

        for i in range(m_min):
            sum = self.variable_factory.sum(resource_id, time, i)
            next_carry = self.variable_factory.carry(resource_id, time, i)
            self.gen_full_adder(solver, a_outputs[i], b_outputs[i], carry, sum, next_carry)
            output.append(sum)
            carry = next_carry

        for i in range(m_min, len(a_outputs)):
            sum = self.variable_factory.sum(resource_id, time, i)
            next_carry = self.variable_factory.carry(resource_id, time, i)
            self.gen_half_adder(solver, a_outputs[i], carry, sum, next_carry)
            output.append(sum)
            carry = next_carry

        output.append(carry)
        return output

    def gen_less_than_constraint(self, solver, bound, inputs, resource_id, time):
        clause = []
        outputs = self.gen_par_counter(solver, inputs, [], resource_id, time)
        
        if bound & 1 == 0:
            clause.append([-outputs[0]])
        bound >>= 1

        for i in range(1, len(outputs)):
            if bound & 1 == 1:
                for c in clause:
                    c.append(-outputs[i])
            else:
                clause.append([-outputs[i]])
            bound >>= 1

        for c in clause:
            solver.add_clause(c)

    def ilog2(self, number):
        log = -1
        while number > 0:
            number >>= 1
            log += 1
        return log
