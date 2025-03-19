from sat_based_2014.scheduler.encoding.VariableFactory import VariableFactory

class BCCEncoderSequentialCounter:
    _encoder = None

    def __init__(self):
        self.variable_factory = VariableFactory.get_variable_factory()

    def encode_resources_with_sequential_counter(self, solver, maxTime: int, activities: list, resources: list):
        
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

                if terms:
                    self.add_sequential_counter(solver, terms, capacity)

    def add_sequential_counter(self, solver, variables, k):
        """
        Sequential Counter Encoding:
        - Cho danh sách các biến `variables`
        - Ràng buộc số lượng biến `True` tối đa là `k`
        """
        n = len(variables)
        if n <= k:
            return  

        s = [[solver.new_var() for _ in range(k)] for _ in range(n)]

        solver.add_clause([-variables[0], s[0][0]])  
        
        for i in range(1, n):
            solver.add_clause([-variables[i], s[i][0]])  
            solver.add_clause([-s[i-1][0], s[i][0]]) 

    
        for i in range(1, n):
            for j in range(1, k):
                solver.add_clause([-variables[i], -s[i-1][j-1], s[i][j]]) 
                solver.add_clause([-s[i-1][j], s[i][j]])  

        for j in range(k):
            solver.add_clause([-s[n-1][j]])  
