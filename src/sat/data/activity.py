from pydantic import BaseModel


class Activity(BaseModel):
    """
    Represents an activity within a scheduling context.

    Attributes:
    ----------
    id : int
        Unique identifier for the activity.
    name : str
        Descriptive name of the activity.
    duration : int
        Duration of the activity in time units.
    """
    id: int
    name: str
    duration: int