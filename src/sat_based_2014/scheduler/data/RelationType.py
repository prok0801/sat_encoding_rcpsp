# scheduler/data/relation_type.py

from enum import Enum

class RelationType(Enum):
    FS = "fs"
    SS = "ss"
    SF = "sf"
    FF = "ff"

    def get_text(self) -> str:
        """Returns the text associated with this relation type."""
        return self.value

    @staticmethod
    def from_string(text: str):
        """
        Returns the corresponding RelationType for the given text (ignoring case).
        Returns None if no match is found.
        """
        if text is not None:
            try:
                return RelationType(text.lower())
            except ValueError:
                return None
        return None

# Example usage:
if __name__ == '__main__':
    # Test get_text method
    rt = RelationType.FS
    print(rt.get_text())  # Output: "fs"

    # Test from_string method
    print(RelationType.from_string("Ss"))  # Output: RelationType.SS
    print(RelationType.from_string("unknown"))  # Output: None
