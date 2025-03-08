# scheduler/encoding/variable_factory.py

class VariableFactory:
    # Class-level constants
    VARIABLE_START = 1
    VARIABLE_RUN = 2
    VARIABLE_AUX = 3
    VARIABLE_SUM = 4
    VARIABLE_CARRY = 5
    VARIABLE_CONSUMPTION = 6

    # Class-level variables shared by all instances
    _variables = {}   # maps tuple of ints to int
    _count = 2
    _factory = None   # Singleton instance

    def __init__(self):
        # No instance-specific initialization needed.
        pass

    @classmethod
    def get_variable_factory(cls):
        """Returns the singleton VariableFactory instance."""
        if cls._factory is not None:
            return cls._factory
        cls._factory = VariableFactory()
        return cls._factory

    def get_variable(self, *args: int) -> int:
        """
        Given a variable number of integer arguments, returns a unique variable
        identifier. If the combination has not been seen before, a new identifier
        is assigned.
        """
        # Use a tuple (which is hashable) as the key.
        key = tuple(args)
        if key in VariableFactory._variables:
            return VariableFactory._variables[key]
        # Assign a new variable id.
        variable = VariableFactory._count
        VariableFactory._count += 1
        VariableFactory._variables[key] = variable
        return variable

    def start(self, activityId: int, time: int) -> int:
        return self.get_variable(VariableFactory.VARIABLE_START, activityId, time)

    def run(self, activityId: int, time: int) -> int:
        return self.get_variable(VariableFactory.VARIABLE_RUN, activityId, time)

    def aux(self, id: int) -> int:
        return self.get_variable(VariableFactory.VARIABLE_AUX, id, id)

    def sum(self, resourceId: int, time: int, id: int) -> int:
        return self.get_variable(VariableFactory.VARIABLE_SUM, resourceId, time, id)

    def carry(self, resourceId: int, time: int, id: int) -> int:
        return self.get_variable(VariableFactory.VARIABLE_CARRY, resourceId, time, id)

    def consume(self, activityId: int, resourceId: int, time: int, consumeId: int) -> int:
        return self.get_variable(VariableFactory.VARIABLE_CONSUMPTION, activityId, resourceId, time, consumeId)

    def clear_variables(self):
        """Resets the variable dictionary and counter."""
        VariableFactory._variables = {}
        VariableFactory._count = 2

    def get_key_by_value(self, value: int):
        """
        Iterates over the stored variables and returns the key (as a list of ints)
        corresponding to the given value, or None if not found.
        """
        for key, var in VariableFactory._variables.items():
            if var == value:
                return list(key)
        return None

    def get_string_from_id(self, id: int) -> str:
        """
        Returns a string representation of a variable given its identifier.
        If the id is negative, it is prefixed with '!' to denote negation.
        """
        result = ""
        if id < 0:
            id = -id
            result += "!"
        entry = self.get_key_by_value(id)
        if entry is None:
            return "keine Variable gefunden"
        # Interpret the variable based on its type (the first element of the key).
        if entry[0] == VariableFactory.VARIABLE_START:
            result += f"s({entry[1]}, {entry[2]})"
        elif entry[0] == VariableFactory.VARIABLE_RUN:
            result += f"x({entry[1]}, {entry[2]})"
        elif entry[0] == VariableFactory.VARIABLE_AUX:
            result += f"e({entry[1]})"
        elif entry[0] == VariableFactory.VARIABLE_CARRY:
            result += f"carry({entry[1]}, {entry[2]}, {entry[3]})"
        elif entry[0] == VariableFactory.VARIABLE_SUM:
            result += f"sum({entry[1]}, {entry[2]}, {entry[3]})"
        elif entry[0] == VariableFactory.VARIABLE_CONSUMPTION:
            result += f"consume({entry[1]}, {entry[2]}, {entry[3]}, v({entry[1]}, {entry[2]}) = {entry[4]})"
        else:
            result += "0"
        return result

    def size(self) -> int:
        """Returns the number of variables stored."""
        return len(VariableFactory._variables)
