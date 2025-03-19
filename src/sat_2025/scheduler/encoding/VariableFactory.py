# scheduler/encoding/variable_factory.py


class VariableFactory:
    VARIABLE_START = 1
    VARIABLE_RUN = 2
    VARIABLE_AUX = 3
    VARIABLE_SUM = 4
    VARIABLE_CARRY = 5
    VARIABLE_CONSUMPTION = 6

    _factory = None
    _variables = {}
    _count = 2

    def __init__(self):
        """Constructor riêng tư để duy trì Singleton."""
        if VariableFactory._factory is not None:
            raise Exception("This class is a singleton!")
        self._variables = {}
        self._count = 2

    @classmethod
    def get_variable_factory(cls):
        """Trả về thể hiện duy nhất của VariableFactory."""
        if cls._factory is None:
            cls._factory = VariableFactory()
        return cls._factory

    def _get_variable(self, *args):
        """Tạo hoặc lấy biến dựa trên danh sách tham số."""
        key = tuple(args)
        if key not in self._variables:
            self._variables[key] = self._count
            self._count += 1
        return self._variables[key]

    def start(self, activity_id, time):
        """Tạo biến START."""
        return self._get_variable(self.VARIABLE_START, activity_id, time)

    def run(self, activity_id, time):
        """Tạo biến RUN."""
        return self._get_variable(self.VARIABLE_RUN, activity_id, time)

    def aux(self, id):
        """Tạo biến AUX."""
        return self._get_variable(self.VARIABLE_AUX, id, id)

    def sum(self, resource_id, time, id):
        """Tạo biến SUM."""
        return self._get_variable(self.VARIABLE_SUM, resource_id, time, id)

    def carry(self, resource_id, time, id):
        """Tạo biến CARRY."""
        return self._get_variable(self.VARIABLE_CARRY, resource_id, time, id)

    def consume(self, activity_id, resource_id, time, consume_id):
        """Tạo biến CONSUME."""
        return self._get_variable(self.VARIABLE_CONSUMPTION, activity_id, resource_id, time, consume_id)

    def clear_variables(self):
        """Xóa tất cả các biến."""
        self._variables.clear()
        self._count = 2

    def get_key_by_value(self, value):
        """Tìm key dựa trên giá trị."""
        for key, val in self._variables.items():
            if val == value:
                return list(key)
        return None

    def get_string_from_id(self, id):
        """Chuyển đổi ID thành chuỗi mô tả biến."""
        result = ""
        if id < 0:
            id = -id
            result += "!"

        entry = self.get_key_by_value(id)
        if entry is None:
            return "keine Variable gefunden"

        if entry[0] == self.VARIABLE_START:
            result += f"s({entry[1]}, {entry[2]})"
        elif entry[0] == self.VARIABLE_RUN:
            result += f"x({entry[1]}, {entry[2]})"
        elif entry[0] == self.VARIABLE_AUX:
            result += f"e({entry[1]})"
        elif entry[0] == self.VARIABLE_CARRY:
            result += f"carry({entry[1]}, {entry[2]}, {entry[3]})"
        elif entry[0] == self.VARIABLE_SUM:
            result += f"sum({entry[1]}, {entry[2]}, {entry[3]})"
        elif entry[0] == self.VARIABLE_CONSUMPTION:
            result += f"consume({entry[1]}, {entry[2]}, {entry[3]}, v({entry[1]}, {entry[2]}) = {entry[4]})"
        else:
            result += "0"

        return result

    def size(self):
        return len(self._variables)
