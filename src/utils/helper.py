import json
from pathlib import Path
import traceback

class DataProcessor:
    FLAG = {
        "PROJECT_INFORMATION": "PROJECT INFORMATION:",
        "RESOURCES": "RESOURCES:",
        "PRECEDENCE_RELATIONS": "PRECEDENCE RELATIONS:",
        "REQUESTS_DURATIONS": "REQUESTS/DURATIONS:",
        "RESOURCE_AVAILABILITIES": "RESOURCEAVAILABILITIES"
    }

    def __init__(self, input_dir, output_dir):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.reset_data()


     
    def reset_data(self):
        
        self.data = {
            'project_info': {},
            'resources': {},
            'precedence_relations': [],
            'job_details': [],
            'resource_availabilities': []
        }
    def parse_dataset_file(self, file_path):
        current_section = None

        with open(file_path, 'r') as f:
            for line_num, line in enumerate(f, 1):
                try:
                    line = line.strip()
                    if not line or line.startswith(("*****", "-----", "pronr.", "jobnr.", "R 1")):
                        continue

                    section = self._get_section(line)
                    if section:
                        current_section = section
                        continue

                    self._parse_line(line, current_section)
                except Exception as e:
                    print(f"⚠️  Warning: Error parsing line {line_num} in file {file_path}: {line}")
                    print(f"   → Error details: {str(e)}")

        return self.data

    def _get_section(self, line):
        for key, value in self.FLAG.items():
            if value in line:
                return key.lower()
        return None

    def _parse_line(self, line, section):
        if section == 'project_information':
            keys = ['pronr', 'jobs', 'rel_date', 'duedate', 'tardcost', 'mpm_time']
            self.data['project_info'] = dict(zip(keys, map(int, line.split())))

        elif section == 'resources':
            if ':' in line:
                key, value = map(str.strip, line.split(':', maxsplit=1))
                self.data['resources'][key] = value

        elif section == 'precedence_relations':
            numbers = list(map(int, line.split()))
            self.data['precedence_relations'].append({
                "job": numbers[0],
                "modes": numbers[1],
                "successors": numbers[4:] if len(numbers) > 4 else []
            })

        elif section == 'requests_durations':
            numbers = list(map(int, line.split()))
            self.data['job_details'].append({
                'job': numbers[0],
                'mode': numbers[1],
                'duration': numbers[2],
                'resource_requirements': dict(zip(["R1", "R2", "R3", "R4"], numbers[-4:]))
            })

        elif section == 'resource_availabilities':
            self.data['resource_availabilities']=list(map(int, line.split()))

    def determine_relation_type(self, job1, job2):
        for relation in self.data['precedence_relations']:
            if relation['job'] == job1 and job2 in relation['successors']:
                successors = relation['successors']
                pos = successors.index(job2)
                if pos == 0:
                    return 'es'
                if pos == len(successors) - 1:
                    return 'ee'
                prev_job = successors[pos - 1]
                return 'ss' if prev_job < job2 else 'se'
        return 'es'

    def format_json_content(self):
        activities = []
        relations = []
        consumptions = []
        resources = []
        max_time = 0

        for job in self.data['job_details']:
            job_id, duration = job['job'], job['duration']
            activities.append({"id": job_id, "duration": duration, "name": f"Task {job_id}"})
            max_time += duration

        for rel in self.data['precedence_relations']:
            job_id = rel['job']
            for succ in rel['successors']:
                relations.append({
                    "task_id_1": job_id,
                    "task_id_2": succ,
                    "relation_type": self.determine_relation_type(job_id, succ)
                })

        for job in self.data['job_details']:
            resource_requirements = job['resource_requirements']
            max_resource = max(resource_requirements.values())
            if max_resource > 0:
                max_resource_id = max(resource_requirements, key=resource_requirements.get)
                consumptions.append({
                    "task_id": job["job"],
                    "resource_id": list(resource_requirements.values()).index(max_resource) ,
                    "amount":-max_resource
                })

        for resource_id, capacity in enumerate(self.data['resource_availabilities']):
            resources.append({"id": resource_id, "capacity": capacity, "name": f"Resource {resource_id}"})

        return json.dumps({
            "activities": activities,
            "relations": relations,
            "consumptions": consumptions,
            "resources": resources,
            "max_time": max_time
        }, indent=2)

    def handle(self):
        if not self.input_dir.exists():
            print(f"Error: Input directory '{self.input_dir}' does not exist.")
            return
        self.output_dir.mkdir(parents=True, exist_ok=True)

        for smt_file in self.input_dir.rglob("*.sm"):
            try:
                rel_path = smt_file.relative_to(self.input_dir)
                output_dir = self.output_dir / rel_path.parent
                output_dir.mkdir(parents=True, exist_ok=True)
            
                self.reset_data()
                self.parse_dataset_file(smt_file)
                json_content = self.format_json_content()
                
                txt_file = output_dir / f"{smt_file.stem}.json"
                with open(txt_file, 'w', encoding='utf-8') as f:
                    json.dump(json.loads(json_content), f, indent=2)
                print(f"✅ Successfully converted {smt_file} → {txt_file}")
            except Exception as e:
                print(f"❌ Error processing {smt_file}: {str(e)}")
                print(traceback.format_exc())

# Example usage:
# processor = DataProcessor("input_directory", "output_directory")
# processor.handle()
