
from algorithm.sat.bcc.validation import print_validation_result, validate_input_data, validate_schedule
from algorithm.sat.bcc.bcc_algo import decode_solution,solve_rcpsp
from utils.helper import parse_input,export_schedule_to_xlsx
import time
from pathlib import Path
import json

def sat_bcc(input_path,xlsx_output_path):

    datasets = parse_input(input_path)
    xlsx_path = Path(xlsx_output_path)
    if xlsx_path.exists():
        xlsx_path.unlink()
    
    for idx, (tasks, relations, consumptions, resources,file_path) in enumerate(datasets):
        file_index = idx + 1

        print(f"\nĐang xử lý {file_path}:")

        # Validate input data
        if validate_input_data(tasks, relations, consumptions, resources):
            print("Input data is valid.")
        else:
            print("Input data is invalid.")
            continue

        # Solve RCPSP problem
        max_time = 600

        start_time_solve=time.time()
        model, vf, variables, clauses, status = solve_rcpsp(max_time, tasks, relations, consumptions, resources)
        end_time_solve=time.time()
        time_solve=end_time_solve - start_time_solve
        # Add logging
        print(f"\nProblem Statistics:")
        print(f"Number of variables: {variables}")
        print(f"Number of clauses: {clauses}")
        print(f"Solution status: {status}")

        if status == "SAT" :
            decoded_schedule = decode_solution(tasks, model, vf, consumptions)
            is_valid, validation_errors = validate_schedule(
                decoded_schedule,
                tasks,
                relations,
                consumptions,
                resources,
                max_time
            )
            print_validation_result(is_valid, validation_errors)
        
        problem_field=f"{file_index}-{len(tasks)}-{len(resources)}-{len(relations)}"

        export_schedule_to_xlsx(
            variables=variables,
            clauses=clauses,
            status=status,
            output_file=xlsx_output_path,
            time_solve=time_solve,
            ago_type="n_bcc",
            file_name=file_path.stem,
            problem_field=problem_field
            )
                



def sat_bcc_solve(input_json_path):
    max_time = 600
    json_file=Path(input_json_path)
    if json_file.exists():
        data = json.loads(json_file.read_text(encoding="utf-8"))
        tasks = data.get("activities", [])
        relations = data.get("relations", [])
        consumptions = data.get("consumptions", [])
        resources = data.get("resources", [])

        if validate_input_data(tasks, relations, consumptions, resources):
            print("Input data is valid.")
            start_time_solve=time.time()
            model, vf, variables, clauses, status = solve_rcpsp(
                max_time, tasks, relations, consumptions, resources
            )
            end_time_solve=time.time()
            time_solve=end_time_solve - start_time_solve

            print(f"\nProblem Statistics:")
            print(f"Number of variables: {variables}")
            print(f"Number of clauses: {clauses}")
            print(f"Solution status: {status}")


            if status == "SAT" :
                decoded_schedule = decode_solution(tasks, model, vf, consumptions)
                is_valid, validation_errors = validate_schedule(
                    decoded_schedule,
                    tasks,
                    relations,
                    consumptions,
                    resources,
                    max_time
                )
            print_validation_result(is_valid, validation_errors)
            problem_field=f"{len(tasks)}-{len(resources)}-{len(relations)}"
            file_name=json_file.stem
            ago_type="n_bcc"
            
            return file_name,problem_field,ago_type,status,time_solve,variables,clauses
        
        else:
            print("Input data is invalid.")
            return

                    
        