from sat.data.project import Project


def  validate_project(schedule,project:Project):
    max_time=project.max_time
    validation_results = {
        'task_coverage': {'passed': True, 'details': []},
        'time_windows': {'passed': True, 'details': []},
        'precedence': {'passed': True, 'details': []},
        'resources': {'passed': True, 'details': []}
    }
    # 1. Check if all tasks are scheduled exactly once
    scheduled_task_ids = {task['task_id'] for task in schedule}
    original_task_ids = {task.id for task in project.activities}

    if scheduled_task_ids != original_task_ids:
        validation_results['task_coverage']['passed'] = False
        missing_tasks = original_task_ids - scheduled_task_ids
        extra_tasks = scheduled_task_ids - original_task_ids
    if missing_tasks:
        validation_results['task_coverage']['details'].append(
            f"Missing tasks in schedule: {missing_tasks}")
    if extra_tasks:
        validation_results['task_coverage']['details'].append(
            f"Extra tasks in schedule: {extra_tasks}")
    else:
        validation_results['task_coverage']['details'].append(
            "All tasks are scheduled exactly once")
    # 2. Check if all tasks are within the maximum time windows
    for task in schedule:
        if task['start_time'] < 0:
            validation_results['time_windows']['passed'] = False
            validation_results['time_windows']['details'].append(
                f"Task {task['task_id']} starts before time 0")
        if task['end_time'] > max_time:
            validation_results['time_windows']['passed'] = False
            validation_results['time_windows']['details'].append(
                f"Task {task['task_id']} ends after max time {max_time}")

        # Verify task duration
        original_duration = next(t.duration for t in project.activities if t.id == task['task_id'])
        if task['end_time'] - task['start_time'] != original_duration:
            validation_results['time_windows']['passed'] = False
            validation_results['time_windows']['details'].append(
                f"Task {task['task_id']} duration mismatch: "
                f"scheduled {task['end_time'] - task['start_time']}, "
                f"required {original_duration}")
    if validation_results['time_windows']['passed']:
        validation_results['time_windows']['details'].append(
            "All tasks are within their allowed time windows and have correct durations")
    task_times = {task['task_id']: (task['start_time'], task['end_time'])
                for task in schedule}
    precedence_checked = 0
    for relation in project.relations:
        precedence_checked += 1
        pred_task = relation.activity_id_1
        succ_task = relation.activity_id_2
        if task_times[pred_task][1] > task_times[succ_task][0]:
            validation_results['precedence']['passed'] = False
            validation_results['precedence']['details'].append(
                f"Precedence violation: Task {pred_task} must finish before "
                f"Task {succ_task} starts")
    if validation_results['precedence']['passed']:
        validation_results['precedence']['details'].append(
            f"All {precedence_checked} precedence relations are satisfied")
    # 4. Check resource constraints
    resource_usage = {res.id :[0] * max_time for res in project.resources}

    # Calculate resource usage over time

    for task in schedule:
        task_resources = task.get('resources_consumed', [])
        for res in task_resources:
            resource_id = res['resource_id']
            amount = abs(res['amount'])
            for t in range(task['start_time'], task['end_time']):
                resource_usage[resource_id][t] += amount
    # Check if resource usage exceeds capacity
    resources_checked = 0
    for resource in project.resources:
        resources_checked += 1
        res_id = resource.id
        capacity = resource.capacity
        max_usage = max(resource_usage[res_id])

        if max_usage > capacity:
            validation_results['resources']['passed'] = False
            for t, usage in enumerate(resource_usage[res_id]):
                if usage > capacity:
                    validation_results['resources']['details'].append(
                        f"Resource {res_id} overused at time {t}: "
                        f"usage {usage} > capacity {capacity}")
        else:
            validation_results['resources']['details'].append(
                f"Resource {res_id} usage is within capacity (max usage: {max_usage}/{capacity})")
    if validation_results['resources']['passed']:
        validation_results['resources']['details'].insert(
            0, f"All {resources_checked} resources are within their capacity limits")
    is_valid = all(result['passed'] for result in validation_results.values())
    return is_valid, validation_results                