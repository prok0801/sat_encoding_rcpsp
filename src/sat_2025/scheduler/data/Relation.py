# scheduler/data/relation.py

from ..data.RelationType import RelationType

class Relation:
    """
    Represents a relation between two activities with a specified type.
    When a Relation is created, it automatically registers itself with the
    involved activities.
    """
    def __init__(self, first, second, relation_type: RelationType):
        """
        Initializes a new Relation instance.

        :param first: The first Activity.
        :param second: The second Activity.
        :param relation_type: The relation type (an instance of RelationType).
        """
        self.first = first
        self.second = second
        self.type = relation_type

        # Register this relation with the activities.
        first.add_successor(self)
        second.add_predecessor(self)

    def get_first(self):
        """Returns the first activity."""
        return self.first

    def get_second(self):
        """Returns the second activity."""
        return self.second

    def get_type(self):
        """Returns the relation type."""
        return self.type

    def embed_forwards(self):
        """
        Adjusts the schedule of the second activity based on the relation type.
        Then, recursively propagates the adjustments to all successors of the second activity.
        """
        if self.type == RelationType.FS:
            if self.second.get_early_start_date() <= self.first.get_early_end_date():
                self.second.set_early_start_date(self.first.get_early_end_date())
        elif self.type == RelationType.FF:
            if self.second.get_early_end_date() <= self.first.get_early_end_date():
                self.second.set_early_end_date(self.first.get_early_end_date())
        elif self.type == RelationType.SS:
            if self.second.get_early_start_date() <= self.first.get_early_start_date():
                self.second.set_early_start_date(self.first.get_early_start_date())
        elif self.type == RelationType.SF:
            if self.second.get_early_end_date() <= self.first.get_early_start_date():
                self.second.set_early_end_date(self.first.get_early_start_date())

        # Recursively propagate the forward embedding to all successors of the second activity.
        for rel in self.second.get_successors():
            rel.embed_forwards()

    def __str__(self):
        return f"RelationActivity [first={self.first}, second={self.second}, type={self.type}]"
