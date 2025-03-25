from pydantic import BaseModel


class Relation(BaseModel):
    """
    Represents a relationship between two activities in a scheduling context.

    Attributes:
    ----------
    activity_id_1 : int
        Unique identifier for the first activity in the relation.
    activity_id_2 : int
        Unique identifier for the second activity in the relation.
    relation_type : str
        Type of the relation, describing how the activities are related.
    """
    activity_id_1: int
    activity_id_2: int
    relation_type: str