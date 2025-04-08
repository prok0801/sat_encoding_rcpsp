from sat.data.project  import Project
from  sat.algorithm.rcpsp import RcpspAlogithm
from pathlib import Path
from utils.helper import export_schedule_to_xlsx


directory_path=Path("assets/test")

arr_ago_type=["bdd_bdd","bdd_card","card_bdd","card_card","bdd_nsc","card_nsc"]
if directory_path.exists():
    for ago_type in arr_ago_type:
        for index, file_path in enumerate(directory_path.rglob("*.json")):

            p = Project(data_path=str(file_path))
            id=index+1

            file_name=file_path.stem
            problem_field=f"{len(p.activities)}-{len(p.resources)}-{len(p.relations)}"
            print(problem_field)
            rcpsp = RcpspAlogithm(p)    
            result=rcpsp.calculate(ago_type)
            print(file_name,result)
            export_schedule_to_xlsx(
                id=id,
                file_name=file_name,
                problem_field= problem_field,
                ago_type= ago_type,
                status= result['status'],
                time_solve= result['time'],
                variables= result['vars'],
                clauses= result['clauses'],
                output_file="bcc.xlsx")





