from dataclasses import dataclass

# scheduler/data/resource.py

class Resource:
    """
    Represents a resource in the context of encoding.
    """

    def __init__(self, id: int, name: str, capacity: int):
        """
        Initializes a new Resource instance.

        :param id: The unique identifier of the resource.
        :param name: The name of the resource.
        :param capacity: The capacity of the resource.
        """
        self.id = id
        self.name = name
        self.capacity = capacity

    def get_id(self) -> int:
        """Returns the id of the resource."""
        return self.id

    def get_capacity(self) -> int:
        """Returns the capacity of the resource."""
        return self.capacity

    def get_name(self) -> str:
        """Returns the name of the resource."""
        return self.name

    def __str__(self) -> str:
        return f"Resource [id={self.id}, capacity={self.capacity}]"

    # Optional: make the class hashable so it can be used as a dictionary key.
    def __eq__(self, other):
        if isinstance(other, Resource):
            return self.id == other.id
        return False

    def __hash__(self):
        return hash(self.id)
