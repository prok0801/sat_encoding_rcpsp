def export_schedule_to_xlsx(
        schedule, variables, clauses, status, tasks, resources, relations, start_task_id,
        output_file, append=False):
    """
    Export schedule data to an Excel (.xlsx) file with consistent formatting and plain unique sequential task IDs.

    Args:
        schedule (list): List of scheduled tasks.
        variables (int): Number of variables in the SAT problem.
        clauses (int): Number of clauses in the SAT problem.
        status (str): SAT or UNSAT status of the solution.
        tasks (list): List of tasks.
        resources (list): List of resources.
        relations (list): List of relations.
        start_task_id (int): Starting ID for the task numbering.
        output_file (str): Path to output Excel file.
        append (bool): Whether to append to file or overwrite.
    """
    # Define column headers
    headers = ['Task ID', 'Problem', 'Type', 'Status', 'Time', 'Variables', 'Clauses']

    # Derive 'Problem' field: Format tasks-resources-relations
    num_tasks = len(tasks)
    num_resources = len(resources)
    num_relations = len(relations)
    problem_field = f"{num_tasks}-{num_resources}-{num_relations}"

    # Prepare data rows
    excel_data = []
    current_task_id = start_task_id  # Start numbering from the provided ID

    for task in schedule:
        # Calculate execution time
        execution_time = task['end_time'] - task['start_time']

        # Append row data as a list
        row = [
            current_task_id,  # Task ID
            problem_field,  # Problem
            'bcc',  # Type
            status,  # Status (SAT/UNSAT)
            execution_time,  # Execution Time
            variables,  # Number of Variables
            clauses  # Number of Clauses
        ]
        excel_data.append(row)
        current_task_id += 1

    # Initialize Excel workbook or load existing one
    if append and os.path.exists(output_file):
        # Load an existing workbook
        workbook = load_workbook(output_file)
        sheet = workbook.active
        starting_row = sheet.max_row + 1  # Start appending after the last row
    else:
        # Create a new workbook
        workbook = Workbook()
        sheet = workbook.active
        starting_row = 1

        # Write headers in the first row
        for col_num, header in enumerate(headers, 1):  # Enumerate starts at index 1
            col_letter = get_column_letter(col_num)
            sheet[f"{col_letter}{starting_row}"] = header
        starting_row += 1  # Move to the first row for data

    # Write data rows
    for row_num, row_data in enumerate(excel_data, starting_row):
        for col_num, cell_data in enumerate(row_data, 1):  # Enumerate starts at index 1
            col_letter = get_column_letter(col_num)
            sheet[f"{col_letter}{row_num}"] = cell_data

    # Save the Excel file
    workbook.save(output_file)

    # Return the last current task ID
    return current_task_id
