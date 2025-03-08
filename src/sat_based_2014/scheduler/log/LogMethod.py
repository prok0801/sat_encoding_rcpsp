from enum import Enum

class LogMethod(Enum):
    UNIQUE_START_INSTANT = False
    START_IN_TIME = False
    RUNTIME = False
    WORKLOAD = False
    RELATION_TYPE_FS = False
    RELATION_TYPE_SS = False
    RELATION_TYPE_FF = False
    RELATION_TYPE_SF = False
    RESOURCE_CARDI = False
    RESOURCE_POWERSET = False
    BCC = False
    IMPLIES = False

    def get_log_status(self) -> bool:
        """
        Returns the boolean log flag associated with this LogMethod.
        """
        return self.value

# Example usage:
if __name__ == '__main__':
    # Test one of the enum members:
    lm = LogMethod.UNIQUE_START_INSTANT
    print(f"{lm.name} log status: {lm.get_log_status()}")
