import logging
from typing import List, Dict

def validate_input_data(tasks: List[Dict], relations: List[Dict],
                         consumptions: List[Dict], resources: List[Dict]) -> bool:
    """
    Validate the input data before solving the RCPSP problem

    :param tasks: List of task dictionaries
    :param relations: List of precedence relations
    :param consumptions: List of resource consumption details
    :param resources: List of resource details
    :return: True if input is valid, False otherwise
    """
    # Configure logging
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(levelname)s: %(message)s')
    logger = logging.getLogger(__name__)

    validation_passed = True

    # 1. Task Validation
    if not tasks:
        logger.error("No tasks defined")
        validation_passed = False

    for task in tasks:
        # Check task duration is positive
        if task.get('duration', 0) <= 0:
            logger.error(f"Invalid duration for task {task.get('id')}: {task.get('duration')}")
            validation_passed = False

    # 2. Precedence Relations Validation
    task_ids = {task['id'] for task in tasks}
    for relation in relations:
        if relation['task_id_1'] not in task_ids:
            logger.error(f"Invalid first task in relation: {relation['task_id_1']}")
            validation_passed = False
        if relation['task_id_2'] not in task_ids:
            logger.error(f"Invalid second task in relation: {relation['task_id_2']}")
            validation_passed = False

    # 3. Resource Validation
    for resource in resources:
        if resource.get('capacity', 0) <= 0:
            logger.error(f"Invalid resource capacity for resource {resource.get('id')}")
            validation_passed = False

    # 4. Consumption Validation
    consumption_task_ids = {cons['task_id'] for cons in consumptions}
    if not consumption_task_ids.issubset(task_ids):
        invalid_tasks = consumption_task_ids - task_ids
        logger.error(f"Consumption defined for non-existent tasks: {invalid_tasks}")
        validation_passed = False

    return validation_passed

def validate_schedule(schedule, tasks, relations, consumptions, resources, max_time):
    """
    Validates RCPSP solution schedule.

    Param:
        schedule (list): List các tác vụ đã lên lịch với thời gian bắt đầu/kết thúc và mức sử dụng tài nguyên
        tasks (list): List các tác vụ đầu vào
        relations (list): Mối quan hệ ưu tiên giữa các nhiệm vụ
        consumptions (list): Mức tài nguyên tiêu thụ cho từng nhiệm vụ
        resources (list): List tài nguyên
        max_time (int): Thời gian tối đa

    Returns:
        tuple: (bool, dict) - (is_valid, validation_results)
    """
    validation_results = {
        'task_coverage': {'passed': True, 'details': []},
        'time_windows': {'passed': True, 'details': []},
        'precedence': {'passed': True, 'details': []},
        'resources': {'passed': True, 'details': []},
        'powerset': {'passed': True, 'details': []}  # New powerset validation section
    }

    # 1. Check if all tasks are scheduled exactly once
    scheduled_task_ids = {task['task_id'] for task in schedule}
    original_task_ids = {task['id'] for task in tasks}

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

    # 2. Check if all tasks are within the maximum time window
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
        original_duration = next(t['duration'] for t in tasks if t['id'] == task['task_id'])
        if task['end_time'] - task['start_time'] != original_duration:
            validation_results['time_windows']['passed'] = False
            validation_results['time_windows']['details'].append(
                f"Task {task['task_id']} duration mismatch: "
                f"scheduled {task['end_time'] - task['start_time']}, "
                f"required {original_duration}")

    if validation_results['time_windows']['passed']:
        validation_results['time_windows']['details'].append(
            "All tasks are within their allowed time windows and have correct durations")

    # 3. Check precedence relations (Finish-to-Start)
    task_times = {task['task_id']: (task['start_time'], task['end_time'])
                 for task in schedule}

    precedence_checked = 0
    for relation in relations:
        precedence_checked += 1
        pred_task = relation['task_id_1']
        succ_task = relation['task_id_2']
        if task_times[pred_task][1] > task_times[succ_task][0]:
            validation_results['precedence']['passed'] = False
            validation_results['precedence']['details'].append(
                f"Precedence violation: Task {pred_task} must finish before "
                f"Task {succ_task} starts")

    if validation_results['precedence']['passed']:
        validation_results['precedence']['details'].append(
            f"All {precedence_checked} precedence relations are satisfied")

    # 4. Check resource constraints
    resource_usage = {res['id']: [0] * max_time for res in resources}

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
    for resource in resources:
        resources_checked += 1
        res_id = resource['id']
        capacity = resource['capacity']
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

    # 5. Create task lookup for consumption values
    task_consumptions = {}
    for consumption in consumptions:
        task_id = consumption['task_id']
        if task_id not in task_consumptions:
            task_consumptions[task_id] = {}
        task_consumptions[task_id][consumption['resource_id']] = abs(consumption['amount'])

    # Powerset Resource Constraint Check
    from itertools import combinations

    def get_concurrent_tasks(time_point):
        """Get all tasks running at a specific time point"""
        return [task for task in schedule
                if task['start_time'] <= time_point < task['end_time']]

    powerset_violations = []
    combinations_checked = {}  # Store details of all combinations checked

    for t in range(max_time):
        concurrent_tasks = get_concurrent_tasks(t)
        if not concurrent_tasks:
            continue

        time_combinations = []
        # Check all possible combinations of concurrent tasks
        for r in range(1, len(concurrent_tasks) + 1):
            for task_combo in combinations(concurrent_tasks, r):
                # Check resource usage for this combination
                resource_usage = {}
                task_ids = [task['task_id'] for task in task_combo]

                for task in task_combo:
                    task_id = task['task_id']
                    if task_id in task_consumptions:
                        for res_id, amount in task_consumptions[task_id].items():
                            resource_usage[res_id] = resource_usage.get(res_id, 0) + amount

                # Record the combination details
                combination_detail = {
                    'tasks': task_ids,
                    'resource_usage': {},
                    'status': 'Valid'
                }

                # Check each resource
                for resource in resources:
                    res_id = resource['id']
                    usage = resource_usage.get(res_id, 0)
                    capacity = resource['capacity']
                    combination_detail['resource_usage'][res_id] = {
                        'usage': usage,
                        'capacity': capacity,
                        'available': capacity - usage
                    }

                    if usage > capacity:
                        combination_detail['status'] = 'Invalid'
                        violation = {
                            'time': t,
                            'resource_id': res_id,
                            'usage': usage,
                            'capacity': capacity,
                            'tasks': task_ids
                        }
                        powerset_violations.append(violation)

                time_combinations.append(combination_detail)

        if time_combinations:
            combinations_checked[t] = time_combinations

    if powerset_violations:
        validation_results['powerset']['passed'] = False
        for violation in powerset_violations:
            validation_results['powerset']['details'].append(
                f"Time {violation['time']}: Resource {violation['resource_id']} "
                f"overused by task combination {violation['tasks']} "
                f"(usage: {violation['usage']}, capacity: {violation['capacity']})")
    else:
        validation_results['powerset']['details'].append(
            "All task combinations respect resource capacity constraints")

    validation_results['powerset']['combinations_checked'] = combinations_checked

    # Overall validation result
    is_valid = all(result['passed'] for result in validation_results.values())
    return is_valid, validation_results

def print_validation_result(is_valid, validation_results):
    """
    Prints the validation results in a detailed, formatted way.
    """

    # Function to print section results
    def print_section(title, results):
        print(f"\n{title}")
        print("-" * len(title))
        if results['passed']:
            print("✓ PASSED")
        else:
            print("✗ FAILED")
        for detail in results['details']:
            print(f"  • {detail}")

        # Print detailed powerset combinations if available
        # if 'combinations_checked' in results:
            # print("\nDetailed Resource Usage Analysis:")
            # print("-------------------------------")
            # for time, combinations in results['combinations_checked'].items():
            #     print(f"\nTime {time}:")
            #     for combo in combinations:
            #         tasks_str = f"Tasks {combo['tasks']}"
            #         status_color = '✓' if combo['status'] == 'Valid' else '✗'
            #         print(f"\n  {status_color} {tasks_str}")
            #         print("    Resource Usage:")
            #         for res_id, usage in combo['resource_usage'].items():
            #             print(f"    - R{res_id}: {usage['usage']}/{usage['capacity']} "
            #                   f"(Available: {usage['available']})")

    # Print each validation section
    print_section("Task Coverage Check", validation_results['task_coverage'])
    print_section("Time Windows Check", validation_results['time_windows'])
    print_section("Precedence Relations Check", validation_results['precedence'])
    print_section("Resource Capacity Check", validation_results['resources'])
    print_section("Powerset Resource Constraint Check", validation_results['powerset'])

    # Print overall result
    print("\nĐánh giá tổng thể")
    print("=======================")
    if is_valid:
        print("✓ PASSED - Tất cả các ràng buộc đều được thỏa mãn")
    else:
        print("✗ FAILED - Một số ràng buộc bị vi phạm")