
from algorithm.sat.bcc.validation import print_validation_result, validate_input_data, validate_schedule
from algorithm.sat.bcc.bcc_algo import decode_solution,solve_rcpsp
from utils.helper import parse_input,export_schedule_to_xlsx
import time
from pathlib import Path

def sat_bcc(input_path,xlsx_output_path):
    # Parse datasets
    datasets = parse_input(input_path)
    xlsx_path = Path(xlsx_output_path)
    if xlsx_path.exists():
        xlsx_path.unlink()
    
    for idx, (tasks, relations, consumptions, resources,file_path) in enumerate(datasets):
        dataset_index = idx + 1

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
        
        export_schedule_to_xlsx(
            variables=variables,
            clauses=clauses,
            status=status,
            tasks=tasks,
            resources=resources,
            relations=relations,
            task_id=dataset_index,
            output_file=xlsx_output_path,
            time_solve=time_solve,
            ago_type="n_bcc",
            file_name=file_path.stem
            )
                


