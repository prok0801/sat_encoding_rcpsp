# scheduler/encoding/sat_encoder.py

from math import pow
from ..encoding.BCCEncoder import BCCEncoder
from ..encoding.VariableFactory import VariableFactory
from ..log.Log import Log  # Adjust this import as needed

class SATEncoder:
    _encoder = None  # Singleton instance

    def __init__(self):
        self.variable_factory = VariableFactory.get_variable_factory()
        self.counter_encoder = BCCEncoder.get_bcc_encoder()

    @classmethod
    def get_encoder(cls):
        if cls._encoder is not None:
            return cls._encoder
        cls._encoder = SATEncoder()
        return cls._encoder

    def encode(self, solver, project, maxTime: int, bccMode: bool):
        try:
            self.encode_unique_start_instant(solver, maxTime, project.get_activities())
            self.encode_start_in_time(solver, maxTime, project.get_activities())
            self.encode_runtime(solver, maxTime, project.get_activities())
            self.encode_work_load(solver, maxTime, project.get_activities())
            self.encode_relations(solver, maxTime, project.get_relations())
            Log.d("test")
            if bccMode:
                self.encode_resources_with_cardinalities(solver, maxTime,
                                                         project.get_activities(),
                                                         project.get_resources())
            else:
                self.encode_resources_with_powerset(solver, maxTime,
                                                    project.get_activities(),
                                                    project.get_resources())
        except Exception as e:
            # In Java, ContradictionException was caught.
            # Here we print the traceback.
            import traceback
            traceback.print_exc()

    def encode_unique_start_instant(self, solver, maxTime: int, activities: list):
        for activity in activities:
            self.encode_unique_start_instant_for_activity(solver, maxTime, activity)

    def encode_unique_start_instant_for_activity(self, solver, maxTime: int, activity):
        # Encode "at least one start"
        clause = [self.variable_factory.start(activity.get_id(), t) for t in range(maxTime)]
        solver.add_clause(clause)
        # Encode "at most one start"
        for time1 in range(maxTime):
            for time2 in range(time1 + 1, maxTime):
                binary_clause = [self.neg(self.variable_factory.start(activity.get_id(), time1)),
                                 self.neg(self.variable_factory.start(activity.get_id(), time2))]
                solver.add_clause(binary_clause)

    def encode_start_in_time(self, solver, maxTime: int, activities: list):
        for activity in activities:
            self.encode_start_in_time_for_activity(solver, maxTime, activity)

    def encode_start_in_time_for_activity(self, solver, maxTime: int, activity):
        # Forbid start times too late to finish within project span.
        for time in range(maxTime - int(activity.get_duration()) + 1, maxTime):
            fact = [self.neg(self.variable_factory.start(activity.get_id(), time))]
            solver.add_clause(fact)

    def encode_runtime(self, solver, maxTime: int, activities: list):
        for activity in activities:
            self.encode_runtime_for_activity(solver, maxTime, activity)

    def encode_runtime_for_activity(self, solver, maxTime: int, activity):
        for time in range(maxTime):
            literal = self.variable_factory.start(activity.get_id(), time)
            # Before start: not running
            for j in range(time):
                binary_clause = [self.neg(literal), self.neg(self.variable_factory.run(activity.get_id(), j))]
                solver.add_clause(binary_clause)
            # During run: running
            for j in range(time, time + int(activity.get_duration())):
                binary_clause = [self.neg(literal), self.variable_factory.run(activity.get_id(), j)]
                solver.add_clause(binary_clause)
            # After run: not running
            for j in range(time + int(activity.get_duration()), maxTime):
                binary_clause = [self.neg(literal), self.neg(self.variable_factory.run(activity.get_id(), j))]
                solver.add_clause(binary_clause)

    def encode_work_load(self, solver, maxTime: int, activities: list):
        assumptions = []
        for time in range(maxTime):
            encVar = self.variable_factory.aux(time)
            assumptions.append(encVar)
            implication_one = [self.neg(encVar)]
            for activity in activities:
                implication_one.append(self.variable_factory.run(activity.get_id(), time))
                implication_two = [encVar, self.neg(self.variable_factory.run(activity.get_id(), time))]
                solver.add_clause(implication_two)
            solver.add_clause(implication_one)
        # Encode: -e(t) -> -e(t+1)
        for i in range(len(assumptions) - 1):
            clause = [assumptions[i], self.neg(assumptions[i + 1])]
            solver.add_clause(clause)

    def encode_relations(self, solver, maxTime: int, relations: list):
        for relation in relations:
            first = relation.get_first()
            second = relation.get_second()
            rel_type = relation.get_type()
            # Assuming the enum has names "FS", "SS", "FF", "SF"
            if rel_type.name == "FS":
                self.encode_relation_type_fs(solver, maxTime, first, second)
            elif rel_type.name == "SS":
                self.encode_relation_type_ss(solver, maxTime, first, second)
            elif rel_type.name == "FF":
                self.encode_relation_type_ff(solver, maxTime, first, second)
            elif rel_type.name == "SF":
                self.encode_relation_type_sf(solver, maxTime, first, second)
            else:
                raise ValueError("Relation type is unknown")

    def encode_relation_type_fs(self, solver, maxTime: int, first, second):
        # B does not start before A finishes
        for time in range(maxTime):
            literal = self.variable_factory.start(first.get_id(), time)
            for k in range(0, time + int(first.get_duration())):
                binary_clause = [self.neg(literal), self.neg(self.variable_factory.start(second.get_id(), k))]
                solver.add_clause(binary_clause)

    def encode_relation_type_ss(self, solver, maxTime: int, first, second):
        # B does not start before A starts
        for time in range(maxTime):
            literal = self.variable_factory.start(first.get_id(), time)
            for k in range(time):
                binary_clause = [self.neg(literal), self.neg(self.variable_factory.start(second.get_id(), k))]
                solver.add_clause(binary_clause)

    def encode_relation_type_ff(self, solver, maxTime: int, first, second):
        # B does not finish before A finishes
        for time in range(maxTime):
            if time + int(first.get_duration()) - int(second.get_duration()) > 0:
                literal = self.variable_factory.start(first.get_id(), time)
                for k in range(0, time + int(first.get_duration()) - int(second.get_duration())):
                    binary_clause = [self.neg(literal), self.neg(self.variable_factory.start(second.get_id(), k))]
                    solver.add_clause(binary_clause)

    def encode_relation_type_sf(self, solver, maxTime: int, first, second):
        # B does not finish before A starts
        for time in range(maxTime):
            if time - int(second.get_duration()) > 0:
                literal = self.variable_factory.start(first.get_id(), time)
                for k in range(0, time - int(second.get_duration()) + 2):
                    binary_clause = [self.neg(literal), self.neg(self.variable_factory.start(second.get_id(), k))]
                    solver.add_clause(binary_clause)

    def check_resource_scarcity(self, activities: list, resources: list) -> bool:
        for resource in resources:
            sum_consumption = 0
            for activity in activities:
                consumption = activity.get_consumption(resource)
                if consumption is not None:
                    sum_consumption += consumption
            if resource.get_capacity() + sum_consumption < 0:
                return True
        return False

    def encode_resources_with_powerset(self, solver, maxTime: int, activities: list, resources: list):
        powerset = [[]]
        resource_conflicts = []
        for activity in activities:
            new_ps = []
            for subset in powerset:
                new_ps.append(subset)
                new_subset = subset.copy()
                new_subset.append(activity)
                # If new_subset is not already in resource_conflicts, try to encode consumption.
                if new_subset not in resource_conflicts:
                    resource_conflict = self.encode_consumption(solver, maxTime, new_subset, resources)
                else:
                    resource_conflict = False
                if not resource_conflict:
                    new_ps.append(new_subset)
                else:
                    resource_conflicts.append(new_subset)
            powerset = new_ps

    def encode_consumption(self, solver, maxTime: int, combination: list, resources: list) -> bool:
        if not combination:
            return False
        for resource in resources:
            consumption_sum = 0
            for activity in combination:
                consumption = activity.get_consumption(resource)
                if consumption is not None and consumption < 0:
                    consumption_sum += consumption
            # consumption_sum is assumed negative.
            if resource.get_capacity() + consumption_sum < 0:
                self.encode_resource_conflict(solver, maxTime, combination)
                return True
        return False

    def encode_resource_conflict(self, solver, maxTime: int, combination: list):
        for time in range(maxTime):
            clause = [self.neg(self.variable_factory.run(activity.get_id(), time))
                      for activity in combination]
            solver.add_clause(clause)

    def encode_resources_with_cardinalities(self, solver, maxTime: int, activities: list, resources: list):
        for time in range(maxTime):
            for activity in activities:
                consum_vars = self.get_consume_variables_for_activity_at_instant(activity, time)
                for consum_var in consum_vars:
                    binary_clause = [self.neg(self.variable_factory.run(activity.get_id(), time)), consum_var]
                    solver.add_clause(binary_clause)
            for resource in resources:
                consum_vars_resource = self.get_consume_variables_for_resource_at_instant(resource, activities, time)
                # print(consum_vars_resource)
                self.consum_to_string(consum_vars_resource)
                if consum_vars_resource:
                    bound = resource.get_capacity()
                    self.counter_encoder.gen_less_than_constraint(solver, bound, consum_vars_resource,
                                                                    resource.get_id(), time)

    @staticmethod
    def get_consume_variables_for_activity_at_instant(activity, instant: int) -> list:
        consum_variables = []
        for resource in activity.get_all_consumption().keys():
            consumption = activity.get_consumption(resource)
            if consumption is not None:
                for i in range(-consumption):
                    # Get a consumption variable from the variable factory.
                    consum_variables.append(VariableFactory.get_variable_factory().consume(
                        activity.get_id(), resource.get_id(), instant, i))
        return consum_variables

    @staticmethod
    def get_consume_variables_for_resource_at_instant(resource, activities: list, instant: int) -> list:
        consum_variables = []
        for activity in activities:
            consumption = activity.get_consumption(resource)
            if consumption is not None:
                for i in range(-consumption):
                    consum_variables.append(VariableFactory.get_variable_factory().consume(
                        activity.get_id(), resource.get_id(), instant, i))
        return consum_variables

    def get_assumptions(self, current: int, maxTime: int) -> list:
        assumptions = []
        for i in range(current, maxTime):
            assumptions.append(self.neg(self.variable_factory.aux(i)))
        return assumptions

    def reset(self):
        self.variable_factory.clear_variables()

    def consum_to_string(self, consums: list):
        for consum in consums:
            Log.d(self.variable_factory.get_string_from_id(consum))

    def consum_to_string_with_prefix(self, x, consums: list):
        result = "\n" + self.variable_factory.get_string_from_id(x)
        for consum in consums:
            result += self.variable_factory.get_string_from_id(consum) + ","
        Log.d(result)   

    def neg(self, var: int) -> int:
        return -var
