from sat.encoding.variable_factory import VariableFactory
from sat.data.project import Project

class SatDecoder:
    _decoder=None
    def __init__(self):
        self.vr = VariableFactory.get_variable_factory()

    @classmethod
    def get_sat_decoder(cls):
        if cls._decoder is None:
            cls._decoder = SatDecoder()
        return cls._decoder
    def handle (self,cnf, project:Project):
        reverse_var_map = {v: k for k, v in self.vr .var_map.items()}
        model = cnf.get_model()
        positive_vars = set(abs(var) for var in model if var > 0)
        activity_start_times = {}

        for activity in project.activities:
            task_start_found = False
            for time in range(len(reverse_var_map)):
                start_var = self.vr.start(activity.id, time)
                if start_var in positive_vars:
                    activity_start_times[activity.id] = time
                    task_start_found = True
                    break
            if not task_start_found:
                 print(f"Warning: No start time found for task {activity.id}")

        sorted_tasks = sorted(project.activities, key=lambda x: activity_start_times.get(x.id, float('inf')))

        schedule = []
        for activity in sorted_tasks:
            start_time = activity_start_times.get(activity.id, None)
            if start_time is not None:
                end_time = start_time + activity.duration
                task_resources = []
                for consumption in project.consumptions:
                  if consumption.activity_id == activity.id:
                     task_resources.append({
                        "resource_id": consumption.resource_id,
                        'amount': consumption.amount
                     })
                
                schedule.append({
                    'task_id': activity.id,
                    'task_name': activity.name,
                    'start_time': start_time,
                    'end_time': end_time,
                    'duration': activity.duration,
                    'resources_consumed': task_resources
                })

        return schedule


