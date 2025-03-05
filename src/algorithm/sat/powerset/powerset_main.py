from sat_solver.sat_algorithms.powerset.powerset_algo import solve_rcpsp, decode_solution, export_schedule_to_xlsx
from sat_solver.sat_algorithms.input_parser import parse_input
from sat_solver.sat_algorithms.powerset.validation import validate_input_data, validate_schedule, print_validation_result

def main():
    # Parse datasets
    datasets = parse_input("../../../../../../solve_input/output_txt")

    output_file = "powerset.xlsx"  # Final output file
    first_write = True  # Flag to manage 'write' or 'append' mode
    next_task_id = 1  # Initialize the global task ID counter

    for idx, (tasks, relations, consumptions, resources) in enumerate(datasets):
        dataset_index = idx + 1  # Dataset index (1-based for better readability)

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

        # Validate the input data
        if validate_input_data(tasks, relations, consumptions, resources):
            print("Dữ liệu đầu vào hợp lệ.")
        else:
            print("Dữ liệu đầu vào không hợp lệ.")
            continue

        # Solve the RCPSP problem
        max_time = 350
        model, vf, solver, status = solve_rcpsp(max_time, tasks, relations, consumptions, resources)

        if status == "SAT" and model is not None:
            # Decode the solution
            decoded_schedule = decode_solution(tasks, model, vf, consumptions)
            is_valid, validation_errors = validate_schedule(
                decoded_schedule, tasks, relations, consumptions, resources, max_time
            )
            print_validation_result(is_valid, validation_errors)

            # Export the schedule to CSV
            next_task_id = export_schedule_to_xlsx(
                schedule=decoded_schedule,
                solver=solver,
                vf=vf,
                status=status,
                tasks=tasks,
                resources=resources,
                relations=relations,
                start_task_id=next_task_id,  # Pass the current task ID
                output_file=output_file,
                append=not first_write  # Append after first dataset
            )
            first_write = False  # After first iteration, always append
        else:
            # Export UNSAT result to CSV (no schedule)
            print("No valid solution found; exporting UNSAT to CSV.")
            export_schedule_to_xlsx(
                schedule=[],
                solver=solver,
                vf=vf,
                status=status,
                tasks=tasks,
                resources=resources,
                relations=relations,
                start_task_id=next_task_id,  # Pass the current task ID
                output_file=output_file,
                append=not first_write  # Append after first dataset
            )
            first_write = False

if __name__ == "__main__":
    main()