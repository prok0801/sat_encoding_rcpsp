
from algorithm.sat.bcc.validation import print_validation_result, validate_input_data, validate_schedule
from algorithm.sat.bcc.bcc_algo import decode_solution,solve_rcpsp
from utils.helper import parse_input,export_schedule_to_xlsx

def sat_bcc(input_path,xlsx_output_path):
    # Parse datasets
    datasets = parse_input(input_path)

    output_file = xlsx_output_path
    first_write = True
    next_task_id = 1

    for idx, (tasks, relations, consumptions, resources) in enumerate(datasets):
        dataset_index = idx + 1

        print(f"\nĐang xử lý tệp dữ liệu {dataset_index}:")
        print("Tasks:")
        for task in tasks:
            print(task)
        print("\nRelations:")
        for relation in relations:
            print(relation)
        print("\nConsumptions:")
        for consumption in consumptions:
            print(consumption)
        print("\nResources:")
        for resource in resources:
            print(resource)

        # Validate input data
        if validate_input_data(tasks, relations, consumptions, resources):
            print("Input data is valid.")
        else:
            print("Input data is invalid.")
            continue

        # Solve RCPSP problem
        max_time = 600
        model, vf, variables, clauses, status = solve_rcpsp(max_time, tasks, relations, consumptions, resources)

        # Add logging
        print(f"\nProblem Statistics:")
        print(f"Number of variables: {variables}")
        print(f"Number of clauses: {clauses}")
        print(f"Solution status: {status}")

        if status == "SAT" and model is not None:
            # Decode solution
            decoded_schedule = decode_solution(tasks, model, vf, consumptions)
            is_valid, validation_errors = validate_schedule(
                decoded_schedule, tasks, relations, consumptions, resources, max_time
            )
            print_validation_result(is_valid, validation_errors)

            # Export SAT result to CSV
            next_task_id = export_schedule_to_xlsx(
                schedule=decoded_schedule,
                variables=variables,
                clauses=clauses,
                status=status,
                tasks=tasks,
                resources=resources,
                relations=relations,
                start_task_id=next_task_id,
                output_file=output_file,
                append=not first_write
            )
            first_write = False
        else:
            # Export UNSAT result to CSV (no schedule)
            print("No valid solution found; exporting UNSAT to CSV.")
            # Export UNSAT
            export_schedule_to_xlsx(
                schedule=[],
                variables=variables,
                clauses=clauses,
                status=status,
                tasks=tasks,
                resources=resources,
                relations=relations,
                start_task_id=next_task_id,
                output_file=output_file,
                append=not first_write
            )
            first_write = False

