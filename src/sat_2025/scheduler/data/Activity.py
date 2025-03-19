# scheduler/data/activity.py

class Activity:
    """
    Represents a task/activity in a project.
    Activities with 0 duration are considered milestones.
    """

    def __init__(self, id: int, duration: int, name: str = "", resource_consumption: dict = None):
        """
        Initializes a new Activity.

        :param id: The unique identifier of the activity.
        :param duration: The duration of the activity (> 0).
        :param name: The name of the activity.
        :param resource_consumption: A dictionary mapping Resource objects to consumption amounts.
        """
        self.id = id
        self.duration = duration
        self.name = name
        self.early_start_date = 0
        self.early_end_date = 0
        self.resource_consumption = resource_consumption if resource_consumption is not None else {}
        self.successors = []      # List of Relation objects
        self.predecessors = []    # List of Relation objects

    def get_duration(self) -> int:
        """Returns the duration of the activity."""
        return self.duration

    def get_id(self) -> int:
        """Returns the id of the activity."""
        return self.id

    def get_consumption(self, resource):
        """
        Returns the consumption for a given resource.

        :param resource: A Resource instance.
        :return: The consumption value or None if not set.
        """
        return self.resource_consumption.get(resource)

    def get_all_consumption(self) -> dict:
        """
        Returns the complete resource consumption mapping.

        :return: A dictionary of resource consumption.
        """
        return self.resource_consumption

    def add_consumption(self, resource, consumption: int):
        """
        Adds (or updates) the consumption for a given resource.

        :param resource: A Resource instance.
        :param consumption: The consumption value.
        """
        self.resource_consumption[resource] = consumption

    def get_name(self) -> str:
        """Returns the name of the activity."""
        return self.name

    def __str__(self) -> str:
        return f"Activity [id={self.id}, duration={self.duration}, name={self.name}]"

    def add_successor(self, relation):
        """
        Adds a successor relation to the activity.

        :param relation: A Relation object representing a successor link.
        """
        self.successors.append(relation)

    def add_predecessor(self, relation):
        """
        Adds a predecessor relation to the activity.

        :param relation: A Relation object representing a predecessor link.
        """
        self.predecessors.append(relation)

    def get_successors(self) -> list:
        """Returns the list of successor relations."""
        return self.successors

    def get_predecessors(self) -> list:
        """Returns the list of predecessor relations."""
        return self.predecessors

    def set_early_start_date(self, time: int):
        """
        Sets the early start date and computes the early end date based on duration.

        :param time: The start time.
        """
        self.early_start_date = time
        self.early_end_date = time + self.get_duration()

    def set_early_end_date(self, time: int):
        """
        Sets the early end date and computes the early start date based on duration.

        :param time: The end time.
        """
        self.early_end_date = time
        self.early_start_date = time - self.get_duration()

    def get_early_start_date(self) -> int:
        """Returns the early start date."""
        return self.early_start_date

    def get_early_end_date(self) -> int:
        """Returns the early end date."""
        return self.early_end_date
