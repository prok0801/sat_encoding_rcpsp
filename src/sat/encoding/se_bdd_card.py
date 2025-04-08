from sat.encoding.variable_factory import VariableFactory
from sat.data.project import Project
from sat.data.activity import Activity
from sat.data.relation import Relation
from sat.data.resource import Resource
from sat.data.relation_type import RelationType
from sat.data.consumption import Consumption
from typing import List
from pypblib.pblib import PBConfig, Pb2cnf ,AMK_CARD,AMK_BDD


class SatEncoderBddCard:
    _sat_encoder = None
    def __init__(self):
        self.vr = VariableFactory.get_variable_factory()
    
    @classmethod 
    def  get_sat_encoder(cls):
        if cls._sat_encoder is None:
            cls._sat_encoder = SatEncoderBddCard()
        return cls._sat_encoder

    def handle(self,cnf, project:Project):

        max_time =project.max_time
        activities = project.activities
        relations = project.relations
        resources = project.resources
        consumption=project.consumptions

        self._encode_unique_Start_instant(cnf,max_time,activities)
        self._encode_start_in_time(cnf,max_time,activities)
        self._encode_runtime(cnf,max_time,activities)
        self._encode_work_load(cnf,max_time,activities)
        self._encode_relations(cnf,max_time,activities,relations)
        self._encode_resources_with_cardinalities(cnf,max_time,activities,resources,consumption)

    # Ràng buộc 1: Mỗi công việc chỉ bắt đầu một lần
    def _encode_unique_Start_instant(self, cnf, max_time: int, activities: List[Activity]):
        pbConfig = PBConfig()
        pbConfig.set_AMK_Encoder(AMK_BDD)

        for activity in activities:
            activity_id = activity.id
            var=[]
            formula=[]
            pb2 = Pb2cnf(pbConfig)
            for t in range(max_time):
                var.append(self.vr.start(activity_id, t))

            max_var=pb2.encode_at_least_k(var,1,formula,self.vr.var_count)
            max_var = pb2.encode_at_most_k(var, 1, formula, max_var + 1)
            self.vr.var_count=max_var + 1

            for clause in formula:
                cnf.add_clause(clause)
                
    def _encode_start_in_time(self, cnf, max_time: int, activities: List[Activity]):
        # Each activity must start within the given time frame
        for activity in activities:
            activity_id = activity.id
            activity_duration = activity.duration
            # Calculate the start time range once
            start_range = range(max_time - activity_duration + 1, max_time)
            for t in start_range:
                cnf.add_clause([-self.vr.start(activity_id, t)])
 
    def _encode_runtime(self, cnf, max_time: int, activities: List[Activity]):
        # Mỗi công việc chỉ được thực hiện trong thời gian cho trước
        for activity in activities:
            activity_id = activity.id
            activity_duration = activity.duration
            for t in range(max_time):
                literal = self.vr.start(activity_id, t)
                # trước thời điểm t ko có công viêc nào được thực hiện
                for before_running_time in range(t):
                    cnf.add_clause([-literal, -self.vr.run(activity_id, before_running_time)])
                # công việc hoạt động trong khoảng thời gian cho trước
                for running_time in range(t, t + activity_duration):
                    cnf.add_clause([-literal, self.vr.run(activity_id, running_time)])
                # sau thời điểm t ko có công việc nào được thực hiện
                for after_running_time in range(t + activity_duration, max_time):
                    cnf.add_clause([-literal, -self.vr.run(activity_id, after_running_time)])
                    
    def _encode_work_load(self, cnf, max_time: int, activities: List[Activity]):
        # Introduce new variables for every time t that encode if any activity is running
        assumptions = [self.vr.aux(t) for t in range(max_time)]
        
        for t, encVar in enumerate(assumptions):
            implication_one = [-encVar]
            for activity in activities:
                activity_id = activity.id
                run_var = self.vr.run(activity_id, t)
                implication_one.append(run_var)
                cnf.add_clause([encVar, -run_var])
            cnf.add_clause(implication_one)

        # Encode implications: -e(t) -> -e(t+1) == e(t) or -e(t+1)
        for i in range(max_time - 1):
            cnf.add_clause([assumptions[i], -assumptions[i + 1]])


    def _encode_relations(self,cnf,max_time: int,activities:List[Activity],Relations:List[Relation]):
        for relation in Relations:
            activity_id_1 = relation.activity_id_1
            activity_id_2 = relation.activity_id_2
            relation_type = relation.relation_type
            activity_1=self._find_activity_by_id(activities,activity_id_1)
            activity_2=self._find_activity_by_id(activities,activity_id_2)
            if activity_1 is None or activity_2 is None:
                print("Error: Activity not found")
                continue
            activity_1_duration=activity_1.duration
            activity_2_duration=activity_2.duration

            if relation_type == RelationType.FS:
                 # B does not start before A finishes
                for t in range(max_time):
                    literal = self.vr.start(activity_id_1, t)
                    for k in range(0, t + activity_1_duration):
                        cnf.add_clause([-literal, -self.vr.start(activity_id_2, k)])
            elif relation_type == RelationType.SS:
                # B does not start before A starts
                for t in range(max_time):
                    literal = self.vr.start(activity_id_1, t)
                    for k in range(t):
                        cnf.add_clause([-literal, -self.vr.start(activity_id_2, k)])
            elif relation_type == RelationType.FF:
                # B does not finish before A finishes
                for t in range(max_time):
                    literal = self.vr.start(activity_id_1, t)
                    if t + activity_1_duration - activity_2_duration >0:
                        for k in range(0,t + activity_1_duration - activity_2_duration):
                            cnf.add_clause([-literal, -self.vr.start(activity_id_2, k)])
            elif relation_type == RelationType.SF:
                # B does not start before A finishes
                for t in range(max_time):
                    if max_time - activity_2_duration > 0:
                        literal = self.vr.start(activity_id_1, t)
                        for k in range(0,t - activity_2_duration +2):
                            cnf.add_clause([-literal, -self.vr.start(activity_id_2, k)])
                
    def _find_activity_by_id(self,activities:List[Activity],activity_id:int):
        for activity in activities:
            if activity.id == activity_id:
                return activity
        return None

    def _encode_resources_with_cardinalities(self,cnf,max_time:int,activities:List[Activity],resources:List[Resource],consumptions:List[Consumption]):
        for t in range(max_time):
            for activity in activities:
                activity_id=activity.id
                consumption=self._find_consumption_by_activity_id(activity_id,consumptions)
                if consumption is None:
                    continue
                consume_vars=self._get_consume_variables_for_activity_at_instant(activity,consumption,t)
                for consume_var in consume_vars:
                    cnf.add_clause([-self.vr.run(activity_id,t),consume_var])
            pb_config=PBConfig()
            pb_config.set_PB_Encoder(AMK_CARD)
            for resource in resources:
                resource_id=resource.id
                bound=resource.capacity
                consumption_vars_resource=self._get_consume_variables_for_resource_at_instant(resource_id,consumptions,t)
                if consumption_vars_resource:
                    pb2cnf = Pb2cnf(pb_config)
                    cnf_formula=[]
                    # weights = [1] * len(consumption_vars_resource)
                    max_var=pb2cnf.encode_at_most_k(consumption_vars_resource,bound,cnf_formula,self.vr.var_count)
                    self.vr.var_count=max_var+1
                    for clause in cnf_formula:
                            cnf.add_clause(clause)

    def _get_consume_variables_for_activity_at_instant(self,activity:Activity,consumption:Consumption,instant_time:int):
        consumption_vars=[]
        for i in range(-consumption.amount):
            consumption_vars.append(self.vr.consume(consumption.activity_id,consumption.resource_id,instant_time,i))
        return consumption_vars

    def _find_consumption_by_activity_id(self,activity_id:int,consumptions:List[Consumption]):
        for consumption in consumptions:
            if consumption.activity_id==activity_id:
                return consumption
        return None
    def _get_consume_variables_for_resource_at_instant(self,resource_id:int,consumptions:List[Consumption],instant_time:int):
        consumption_vars=[]
        for consumption in consumptions:
            if consumption.resource_id==resource_id:
                for i in range (-consumption.amount):
                    consumption_vars.append(self.vr.consume(consumption.activity_id,consumption.resource_id,instant_time,i))
        return  consumption_vars      

     
        
