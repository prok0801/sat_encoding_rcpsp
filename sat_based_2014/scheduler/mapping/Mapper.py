import sys

from scheduler.data.Activity import Activity
from scheduler.data.Project import Project
from scheduler.data.Resource import Resource
from scheduler.data.Relation import Relation
from scheduler.data.RelationType import RelationType


class Mapper:
    _mapper = None  # Singleton instance

    def __init__(self):
        self.project = None

    @classmethod
    def get_mapper(cls):
        """
        Returns the singleton Mapper instance.
        """
        if cls._mapper is None:
            cls._mapper = Mapper()
        return cls._mapper

    def read_project(self, project_path: str) -> Project:
        """
        Reads a project from a file specified by project_path.
        """
        try:
            with open(project_path, 'r') as file:
                self.project = self.map_project(file)
        except IOError as e:
            print(f"Error reading project file: {e}", file=sys.stderr)
        return self.project

    def map_project(self, file_obj) -> Project:
        """
        Reads the file line by line and maps the contents into a Project.
        """
        activities = []
        resources = []
        consumptions = []
        relations = []

        for line in file_obj:
            line = line.strip()
            if line:  # skip empty lines
                self.map_line(line, activities, resources, relations, consumptions)

        if self.project is not None:
            # Add activities to the project
            for activity in activities:
                self.project.add_activity(activity)

            # Add resources to the project
            for resource in resources:
                self.project.add_resource(resource)

            # Create and add relations
            for triplet in relations:
                first = self.project.get_activity_by_id(triplet.first_id)
                second = self.project.get_activity_by_id(triplet.second_id)
                relation_type = triplet.type
                relation = Relation(first, second, relation_type)
                self.project.add_relation(relation)

            # Process consumptions
            for triplet in consumptions:
                activity = self.project.get_activity_by_id(triplet.first_id)
                resource = self.project.get_resource_by_id(triplet.second_id)
                consumption = triplet.consumption
                activity.add_consumption(resource, consumption)

        return self.project

    def map_line(self, line: str, activities: list, resources: list,
                 relations: list, consumptions: list):
        """
        Parses a single line of the project file and adds the parsed data
        to the appropriate lists.
        """
        parts = line.split(';')
        type_str = parts[0]

        if type_str == "project":
            # parts[3] is the project name.
            # In Java, the second and third parameters were 0 and Integer.MAX_VALUE;
            # here we use 0 and sys.maxsize.
            self.project = Project(parts[3], 0, sys.maxsize)
        elif type_str == "task":
            id_ = int(parts[1])
            duration = int(parts[2])
            activity = Activity(id_, duration, parts[3])
            activities.append(activity)
        elif type_str == "resource":
            id_ = int(parts[1])
            capacity = int(parts[2])
            resource = Resource(id_, parts[3], capacity)
            resources.append(resource)
        elif type_str == "consumption":
            activity_id = int(parts[1])
            resource_id = int(parts[2])
            consumption = int(parts[3])
            triplet = self._ConsumptionTriplet(activity_id, resource_id, consumption)
            consumptions.append(triplet)
        elif type_str == "aob":
            first_id = int(parts[1])
            second_id = int(parts[2])
            r_type = parts[3]
            relation_type = None
            if r_type == "aa":
                relation_type = RelationType.SS
            elif r_type == "ae":
                relation_type = RelationType.SF
            elif r_type == "ee":
                relation_type = RelationType.FF
            elif r_type == "ea":
                relation_type = RelationType.FS
            else:
                raise ValueError(f"Unknown relation type: {r_type}")
            triplet = self._RelationTriplet(first_id, second_id, relation_type)
            relations.append(triplet)
        else:
            raise ValueError(f"Unknown line type: {type_str}")

    class _RelationTriplet:
        """
        A simple helper class to store relation information.
        """
        def __init__(self, first_id: int, second_id: int, type):
            self.first_id = first_id
            self.second_id = second_id
            self.type = type

    class _ConsumptionTriplet:
        """
        A simple helper class to store consumption information.
        """
        def __init__(self, first_id: int, second_id: int, consumption: int):
            self.first_id = first_id
            self.second_id = second_id
            self.consumption = consumption