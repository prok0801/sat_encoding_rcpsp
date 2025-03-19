from itertools import combinations
from sat_based_2014.scheduler.encoding.VariableFactory import VariableFactory

class BCCEncoderCNF:

    def __init__(self):
        pass

    def encode_resources_with_cnf(self, solver, maxTime: int, activities: list, resources: list):
        
        def var(i, t):
            return i * maxTime + t + 1  

        for r in resources:
            capacity = r["capacity"]

            for t in range(maxTime):
                terms = []

                for i in range(1, len(activities) + 1):
                    duration = activities[i - 1]["duration"]
                    for start_time in range(max(0, t - duration + 1), t + 1):
                        terms.append(var(i, start_time))

                if terms and len(terms) > capacity:
                    # Tạo tổ hợp các nhóm có kích thước (capacity + 1)
                    for over_capacity_group in combinations(terms, capacity + 1):
                        solver.add_clause([-x for x in over_capacity_group])  
