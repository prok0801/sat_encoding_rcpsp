from sat_2025.scheduler.mapping import Mapper
from sat_2025.scheduler.algorithm import FowardAlgorithm
from sat_2025.scheduler.algorithm import RCPSPAlgorithm
from pathlib import Path
import json

def sat_solve_2025(input_json_path):
    bcc_mode = True
    json_file=Path(input_json_path)
    if json_file.exists():
        text_data,tasks,relations,consumptions,resources=convert_json_to_base(input_json_path)
        problem_field=f"{len(tasks)}-{len(resources)}-{len(relations)}"
        file_name=json_file.stem
        ago_type="2025_bcc"

        mapper = Mapper.get_mapper()
        project = mapper.load_data(text_data)


        # Create algorithm instances
        fwd = FowardAlgorithm(project)
        rcpsp = RCPSPAlgorithm(project, bcc_mode)

        # Run calculations
        fwd.calculate()
        status,time_solve,variables,clauses=rcpsp.calculate()

        return{
            "file_name": file_name,
            "problem_field": problem_field,
            "ago_type": ago_type,
            "status": status,
            "time_solve": time_solve,
            "variables": variables,
            "clauses": clauses
        }

    
    


def convert_json_to_base(json_path):
    json_file = Path(json_path)
    if json_file.exists():
        json_string = json_file.read_text(encoding="utf-8")
        json_data = json.loads(json_string)
    
    tasks = json_data.get("activities", [])
    relations = json_data.get("relations", [])
    consumptions = json_data.get("consumptions", [])
    resources = json_data.get("resources", [])
    max_time=json_data.get("max_time", [])

    lines = []
    lines.append(f"project;0;{max_time};test")
    for task in tasks:
        lines.append(f"task;{task['id']};{task['duration']};{task['name']}")
    
    # Process relations
    for relation in relations:
        lines.append(f"aob;{relation['task_id_1']};{relation['task_id_2']};{relation['relation_type']}")
    
    for consumption in consumptions:
        lines.append(f"consumption;{consumption['task_id']};{consumption['resource_id']};{consumption['amount']}")


    for resource in resources:
        lines.append(f"resource;{resource['id']};{resource['capacity']};{resource['name']}")
    print("\n".join(lines))
    return "\n".join(lines),tasks,relations,consumptions,resources
