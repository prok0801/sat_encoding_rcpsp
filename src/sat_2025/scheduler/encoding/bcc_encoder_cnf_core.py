from itertools import combinations
from sat_2025.scheduler.encoding.VariableFactory import VariableFactory

class BCCEncoderCNF:

    def __init__(self):
        pass
        
    def encode_resources_with_cardinalities(self, solver, maxTime: int, activities: list, resources: list):
        
        def var(i, t):
            return i * maxTime + t + 1  
        
        print("_vao_")
        for r in resources:
            capacity = r.get_capacity()



            for t in range(maxTime):
                terms = []

                for i in range(1, len(activities) + 1):
                    duration = activities[i - 1].get_duration()
                    for start_time in range(max(0, t - duration + 1), t + 1):
                        terms.append(var(i, start_time))

                if terms and len(terms) > capacity:
                    # Tạo tổ hợp các nhóm có kích thước (capacity + 1)
                    for over_capacity_group in combinations(terms, capacity + 1):
                        solver.add_clause([-x for x in over_capacity_group])
        
        print("__end__")
