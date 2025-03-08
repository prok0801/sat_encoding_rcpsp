from sat_based_2014.scheduler.mapping import Mapper
from sat_based_2014.scheduler.algorithm import FowardAlgorithm
from sat_based_2014.scheduler.algorithm import RCPSPAlgorithm
from pathlib import Path
import json

def sat_bcc_solve_2014(input_json_path):
    bcc_mode = True

    text_data=convert_json_to_base_2014(input_json_path)

    mapper = Mapper.get_mapper()
    # project = mapper.read_project(project_path)
    project = mapper.load_data(text_data)


    # Create algorithm instances
    # fwd = FowardAlgorithm(project)
    rcpsp = RCPSPAlgorithm(project, bcc_mode)

    # Run calculations
    # fwd.calculate()
    rcpsp.calculate()
    


def convert_json_to_base_2014(json_path):
    json_file = Path(json_path)
    if json_file.exists():
        json_string = json_file.read_text(encoding="utf-8")
        json_data = json.loads(json_string)
    
    lines = []
    lines.append("project;0;6147483647;test")
    for task in json_data.get("activities", []):
        lines.append(f"task;{task['id']};{task['duration']};{task['name']}")
    
    # Process relations
    for relation in json_data.get("relations", []):
        lines.append(f"aob;{relation['task_id_1']};{relation['task_id_2']};{relation['relation_type']}")
    
    for consumption in json_data.get("consumptions", []):
        lines.append(f"consumption;{consumption['task_id']};{consumption['resource_id']};{consumption['amount']}")


    for resource in json_data.get("resources", []):
        lines.append(f"resource;{resource['id']};{resource['capacity']};{resource['name']}")
    
    return "\n".join(lines)
