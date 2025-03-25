

class VariableFactory:
    VARIABLE_START = "START"
    VARIABLE_RUN = "RUN"
    VARIABLE_SUM="SUM"
    VARIABLE_AUX="AUX"
    VARIABLE_CONSUMPTION="CONSUMPTION"
    _factory=None

    def __init__(self):
        self.reset()

    @classmethod
    def get_variable_factory(cls):
        if cls._factory is None:
            cls._factory = cls()
        return cls._factory

    def _get_variable (self, key_name):
         if key_name not in self.var_map:
            self.var_map[key_name] = self.var_count
            self.var_count += 1
         return self.var_map[key_name]
    def start(self,activity_id,time):
        return self._get_variable(f"{self.VARIABLE_START}_{activity_id}_{time}")
    def run(self,activity_id,time):
        return self._get_variable(f"{self.VARIABLE_RUN}_{activity_id}_{time}")

    def aux(self,time):
        return self._get_variable(f"{self.VARIABLE_AUX}_{time}")

    def sum(self,resource_id,time,id):
        return self._get_variable(f"{self.VARIABLE_SUM}_{resource_id}_{time}_{id}")
    
    def consume(self,activity_id,resource_id,time,consume_id):
        return self._get_variable(f"{self.VARIABLE_CONSUMPTION}_{activity_id}_{resource_id}_{time}_{consume_id}")

    def reset(self):
        self.var_count = 1
        self.var_map = {}


