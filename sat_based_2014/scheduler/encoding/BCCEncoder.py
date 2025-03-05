# scheduler/encoding/bcc_encoder.py

from math import pow
# Import your variable factory; adjust the import path as needed.
from ..encoding.VariableFactory import VariableFactory


class BCCEncoder:
    _encoder = None  # Singleton instance

    def __init__(self):
        self.variableFactory = VariableFactory.get_variable_factory()

    @classmethod
    def get_bcc_encoder(cls):
        """Returns a singleton instance of BCCEncoder."""
        if cls._encoder is not None:
            return cls._encoder
        cls._encoder = BCCEncoder()
        return cls._encoder

    def gen_half_adder(self, solver, a: int, b: int, sum_var: int, carry: int):
        """
        Generates the half-adder constraints.
        
        Adds the following clauses:
            (a OR ¬b OR sum)
            (a OR ¬b OR sum)   # repeated as in the original Java code
            (¬a OR b OR sum)
            (¬a OR ¬b OR carry)
        """
        solver.add_clause([a, self.neg(b), sum_var])
        solver.add_clause([a, self.neg(b), sum_var])  # repeated clause
        solver.add_clause([self.neg(a), b, sum_var])
        solver.add_clause([self.neg(a), self.neg(b), carry])

    def gen_full_adder(self, solver, a: int, b: int, c: int, sum_var: int, carry: int):
        """
        Generates the full-adder constraints.
        
        Adds the following clauses:
            (a OR b OR ¬c OR sum)
            (a OR ¬b OR c OR sum)
            (¬a OR b OR c OR sum)
            (¬a OR ¬b OR ¬c OR sum)
            (¬a OR ¬b OR carry)
            (¬a OR ¬c OR carry)
        """
        solver.add_clause([a, b, self.neg(c), sum_var])
        solver.add_clause([a, self.neg(b), c, sum_var])
        solver.add_clause([self.neg(a), b, c, sum_var])
        solver.add_clause([self.neg(a), self.neg(b), self.neg(c), sum_var])
        solver.add_clause([self.neg(a), self.neg(b), carry])
        solver.add_clause([self.neg(a), self.neg(c), carry])

    def gen_par_counter(self, solver, input_list: list, output: list, resourceId: int, time: int) -> list:
        """
        Recursively generates a parallel counter.
        
        :param solver: The SAT solver instance.
        :param input_list: A list of integer variables representing inputs.
        :param output: A list to which output variables are appended.
        :param resourceId: An identifier for the resource.
        :param time: A time index.
        :return: The list of output variables.
        """
        m = self.ilog2(len(input_list))
        if len(input_list) == 1:
            output.append(input_list[0])
            return output

        p_end = (2 ** m) - 1

        # Split the input list into two parts.
        a_inputs = input_list[:p_end]
        b_inputs = input_list[p_end:len(input_list)-1]  # exclude the last element
        a_outputs = self.gen_par_counter(solver, a_inputs, [], resourceId, time)
        b_outputs = []
        if len(b_inputs) > 0:
            b_outputs = self.gen_par_counter(solver, b_inputs, [], resourceId, time)

        # Determine the minimum length among the two outputs.
        m_min = min(len(a_outputs), len(b_outputs)) if b_outputs else 0
        carry = input_list[-1]

        # Use a full adder for the overlapping bits.
        for i in range(m_min):
            sum_var = self.variableFactory.sum(resourceId, time, i)
            next_carry = self.variableFactory.carry(resourceId, time, i)
            self.gen_full_adder(solver, a_outputs[i], b_outputs[i], carry, sum_var, next_carry)
            output.append(sum_var)
            carry = next_carry

        # For the remaining bits in a_outputs, use a half adder.
        for i in range(m_min, len(a_outputs)):
            sum_var = self.variableFactory.sum(resourceId, time, i)
            next_carry = self.variableFactory.carry(resourceId, time, i)
            self.gen_half_adder(solver, a_outputs[i], carry, sum_var, next_carry)
            output.append(sum_var)
            carry = next_carry

        output.append(carry)
        return output

    def gen_less_than_constraint(self, solver, bound: int, inputs: list, resourceId: int, time: int):
        """
        Generates a "less than" constraint based on a given bound.
        
        This method uses a parallel counter to compare the sum of input bits
        against the bound and adds the resulting clauses to the solver.
        
        :param solver: The SAT solver instance.
        :param bound: The integer bound.
        :param inputs: A list of integer variables representing inputs.
        :param resourceId: An identifier for the resource.
        :param time: A time index.
        """
        clause = []  # Will hold a list of clauses (each clause is a list of ints)
        outputs = self.gen_par_counter(solver, inputs, [], resourceId, time)
        b = bound & 1
        if b != 1:
            clause.append([self.neg(outputs[0])])
        bound >>= 1  # Shift right by 1 (delete bit 0)

        for i in range(1, len(outputs)):
            bit_i = bound & 1
            if bit_i == 1:
                for sub_clause in clause:
                    sub_clause.append(self.neg(outputs[i]))
            else:
                clause.append([self.neg(outputs[i])])
            bound >>= 1

        for sub_clause in clause:
            solver.add_clause(sub_clause)

    def ilog2(self, number: int) -> int:
        """
        Computes the integer binary logarithm of a positive integer.
        
        :param number: A positive integer.
        :return: The floor of log2(number).
        """
        log_val = -1
        while number > 0:
            number //= 2
            log_val += 1
        return log_val

    def neg(self, var: int) -> int:
        """
        Returns the negation of a variable.
        
        In SAT encodings, negation is typically represented by multiplying by -1.
        """
        return -var
