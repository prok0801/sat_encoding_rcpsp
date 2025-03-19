# scheduler/data/project.py

class Project:
    """
    Represents a project that contains activities, relations, and resources.
    """

    def __init__(self, name: str, wat: int, wet: int):
        """
        Initializes a new Project.

        :param name: The name of the project.
        :param wat: The project start time (Work Arrival Time).
        :param wet: The project end time (Work End Time).
        """
        self.name = name
        self.wat = wat
        self.wet = wet
        self.activities = []  # List to store Activity objects.
        self.relations = []   # List to store Relation objects.
        self.resources = []   # List to store Resource objects.

    def get_activities(self):
        """
        Returns the list of activities.
        """
        return self.activities

    def get_relations(self):
        """
        Returns the list of relations.
        """
        return self.relations

    def get_resources(self):
        """
        Returns the list of resources.
        """
        return self.resources

    def get_activity_by_id(self, id: int):
        """
        Returns the activity with the given id, or None if not found.
        """
        for activity in self.activities:
            if activity.get_id() == id:
                return activity
        return None

    def get_resource_by_id(self, id: int):
        """
        Returns the resource with the given id, or None if not found.
        """
        for resource in self.resources:
            if resource.get_id() == id:
                return resource
        return None

    def get_name(self) -> str:
        """
        Returns the name of the project.
        """
        return self.name

    def add_activity(self, activity):
        """
        Adds an activity to the project.

        :param activity: An Activity object.
        """
        self.activities.append(activity)

    def add_resource(self, resource):
        """
        Adds a resource to the project.

        :param resource: A Resource object.
        """
        self.resources.append(resource)

    def add_relation(self, relation):
        """
        Adds a relation to the project.

        :param relation: A Relation object.
        """
        self.relations.append(relation)

    def get_wat(self) -> int:
        """
        Returns the project start time (WAT).
        """
        return self.wat

    def get_wet(self) -> int:
        """
        Returns the project end time (WET).
        """
        return self.wet

    def embed_forwards(self, first):
        """
        Performs a forward embedding starting from the given activity.
        It calls embed_forwards() on every relation that starts from the given activity.

        :param first: An Activity object.
        """
        for relation in first.get_successors():
            relation.embed_forwards()

    def __str__(self):
        return f"RCPSPProject [activities={self.activities}, relations={self.relations}, resources={self.resources}]"
