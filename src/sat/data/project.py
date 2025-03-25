from typing import Optional, List
from sat.data.relation import Relation
from sat.data.activity import Activity
from sat.data.resource import Resource
from sat.data.consumption import Consumption
from sat.data.relation_type import RelationType
from pathlib import Path
import json

class Project:
    relations: Optional[List[Relation]]
    activities: Optional[List[Activity]]
    resources: Optional[List[Resource]]
    consumptions: Optional[List[Consumption]]
    max_time: Optional[int]

    def __init__(self, data_path: str):
        data = self._read_json(data_path)
        if data is  None:
            print("File not found")
            return
        self.relations = [] 
        self.activities = []
        self.resources = []
        self.consumptions = []
        self.max_time = data.get("max_time")
        
        self._map_resources(data["resources"])
        self._map_activities(data["activities"])
        self._map_relations(data["relations"])
        self._map_consumptions(data["consumptions"])

    def _map_resources(self, resources_raw: list):
        for item in resources_raw:
            self.resources.append(Resource(**item))

    def _map_activities(self, activities_raw: list):
        for item in activities_raw:
            self.activities.append(Activity(**item))

    def _map_relations(self, relations_raw: list):
        for item in relations_raw:
            self.relations.append(Relation(activity_id_1=item["task_id_1"],
                                           activity_id_2=item["task_id_2"],
                                           relation_type=item["relation_type"]))
    
    def _get_relation_type(self ,relation_type: str):
        if relation_type in ["fs", "ea","es"]:
            return RelationType.FS
        elif relation_type in  ["ss","aa"]:
            return RelationType.SS
        elif relation_type in ["ae","se","sf"]:
            return RelationType.SF
        elif relation_type in ["ff","ee"]:
            return RelationType.FF
        else:
            return None
    
    def _map_consumptions(self, consumptions_raw: list):
        for item in consumptions_raw:
            self.consumptions.append(Consumption(resource_id=item["resource_id"],
                                                 activity_id=item["task_id"],
                                                 amount=item["amount"]))
    

    def _read_json(self, json_file_path: str):
        file =Path(json_file_path)
        if file.exists():
            data_string=file.read_text(encoding="utf-8")
            return json.loads(data_string)
        return None


        
