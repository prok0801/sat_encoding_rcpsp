from pydantic import BaseModel


class Resource(BaseModel):
    """
    Represents a resource within a scheduling context.

    Attributes:
    ----------
    id : int
        Unique identifier for the resource.
    name : str
        Descriptive name of the resource.
    capacity : int
        Maximum capacity of the resource.
    """
    id: int
    name: str
    capacity: int