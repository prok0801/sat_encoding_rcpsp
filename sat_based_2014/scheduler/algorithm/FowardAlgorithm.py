# Assuming the following imports reflect your project structure:
from ..data.Activity import Activity
from ..data.Relation import Relation
from ..data.RelationType import RelationType
from .Algorithm import Algorithm

class FowardAlgorithm(Algorithm):
    VIRTUAL_MILESTONE_START = "project_start_virtual"
    VIRTUAL_MILESTONE_END = "project_end_virtual"

    def __init__(self, project):
        """
        Initializes the FowardAlgorithm with the given project.
        """
        super().__init__(project)
        self.virtual_start_id = -1
        self.virtual_end_id = -1
        self.first = None  # Virtual start milestone (Activity)
        self.last = None   # Virtual end milestone (Activity)

    def calculate(self):
        """
        Performs the forward scheduling algorithm.
        It adds virtual milestones, sets the early start date for the project,
        embeds the forward pass into the project schedule, and finally removes
        the virtual milestones.
        """
        self.add_virtual_milestones()
        # Assuming project.get_wat() returns the project's work arrival time (start time)
        print(self.project.get_wat())
        self.first.set_early_start_date(self.project.get_wat())
        self.project.embed_forwards(self.first)
        self.remove_virtual_milestones(self.first, self.last)

    def add_virtual_milestones(self):
        """
        Adds virtual start and end milestones to the project.
        These milestones are used to simplify scheduling computations.
        """
        activities = self.project.get_activities()
        starts = []  # Activities with no predecessors
        ends = []    # Activities with no successors
        max_id = 0

        for activity in activities:
            if len(activity.get_predecessors()) == 0:
                starts.append(activity)
            if len(activity.get_successors()) == 0:
                ends.append(activity)
            if activity.get_id() > max_id:
                max_id = activity.get_id()

        self.virtual_start_id = max_id + 1
        self.virtual_end_id = max_id + 2

        # Create virtual milestones with 0 duration.
        self.first = Activity(self.virtual_start_id, 0, FowardAlgorithm.VIRTUAL_MILESTONE_START)
        self.project.add_activity(self.first)
        self.last = Activity(self.virtual_end_id, 0, FowardAlgorithm.VIRTUAL_MILESTONE_END)
        self.project.add_activity(self.last)

        # Connect the virtual start to all activities that have no predecessors.
        for activity in starts:
            # Create a relation from the virtual start to the activity.
            Relation(self.first, activity, RelationType.FS)
        
        # Connect all activities that have no successors to the virtual end.
        for activity in ends:
            # Create a relation from the activity to the virtual end.
            Relation(activity, self.last, RelationType.FS)

    def remove_virtual_milestones(self, first, last):
        """
        Removes the virtual milestones from the project's list of activities.
        """
        activities = self.project.get_activities()
        if first in activities:
            activities.remove(first)
        if last in activities:
            activities.remove(last)
