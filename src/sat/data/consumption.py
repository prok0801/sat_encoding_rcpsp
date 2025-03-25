from pydantic import BaseModel


class Consumption(BaseModel):
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
    activity_id: int
    resource_id: int
    amount: int