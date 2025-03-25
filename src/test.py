import json
from pysat.solvers import Glucose3
from pypblib import pblib
from pypblib.pblib import PBConfig, Pb2cnf

# Load JSON data
with open('/Users/2noscript/workspace/do-more/RCPSP_SAT-Encoding/assets/input/test.json') as f:
    data = json.load(f)

activities = data['activities']
relations = data['relations']
consumptions = data['consumptions']
resources = data['resources']
max_time = data['max_time']

# Initialize solver
solver = Glucose3()

# Function to create a variable for task j starting at time t
def var(j, t):
    return j * 1000 + t

# Constraint 1: Each task must start exactly once
for activity in activities:
    j = activity['id']
    duration = activity['duration']
    solver.add_clause([var(j, t) for t in range(max_time - duration + 1)])

# Constraint 2: Respect task dependencies
for relation in relations:
    task1 = relation['task_id_1']
    task2 = relation['task_id_2']
    relation_type = relation['relation_type']
    
    for t1 in range(max_time):
        for t2 in range(max_time):
            if relation_type == 'es':  # End-Start
                if t1 + activities[task1 - 1]['duration'] <= t2:
                    solver.add_clause([-var(task1, t1), var(task2, t2)])
            elif relation_type == 'ee':  # End-End
                if t1 + activities[task1 - 1]['duration'] <= t2 + activities[task2 - 1]['duration']:
                    solver.add_clause([-var(task1, t1), var(task2, t2)])

# Constraint 3: Resource usage constraints
pbConfig = PBConfig()
pbConfig.set_AMK_Encoder(pblib.AMK_CARD)
pb2 = Pb2cnf(pbConfig)

for resource in resources:
    r_id = resource['id']
    capacity = resource['capacity']
    
    for t in range(max_time):
        literals = []
        weights = []
        
        for consumption in consumptions:
            if consumption['resource_id'] == r_id:
                task_id = consumption['task_id']
                amount = -consumption['amount']
                
                for start_time in range(max(0, t - activities[task_id - 1]['duration'] + 1), t + 1):
                    literals.append(var(task_id, start_time))
                    weights.append(amount)
        
        if literals:
            formula = []
            max_var = pb2.encode_at_most_k(literals, capacity, formula, max_time * 1000 + t)
            for clause in formula:
                solver.add_clause(clause)

# Solve the problem
if solver.solve():
    model = solver.get_model()
    schedule = {activity['id']: next(t for t in range(max_time) if var(activity['id'], t) in model) for activity in activities}

    print("Optimal Schedule:")
    for j in sorted(schedule, key=schedule.get):
        print(f"Task {j} starts at time {schedule[j]}")
else:
    print("No feasible schedule found")