
from utils.helper import export_schedule_to_xlsx
from pathlib import Path
from algorithm.sat.bcc.bcc_main import sat_bcc_solve
from sat_based_2014.bcc_2014 import sat_bcc_solve_2014

# processor = DataProcessor("assets/dataset","assets/input")
# processor.handle()


# res=parse_input("C:/Github for Lab/RCPSP_SAT-Encoding/assets/dataset/j30.sm.tgz")
# print(res)


def sat_bcc_test(input_path,xlsx_output_path):
    xlsx_path = Path(xlsx_output_path)
    directory_path = Path(input_path)
    if xlsx_path.exists():
        xlsx_path.unlink()
    if not directory_path.exists() or not directory_path.is_dir():
        print(f"Error: Directory {input_path} does not exist or is not a folder.\n")
        return None
    for index, file_path in enumerate(directory_path.rglob("*.json")):
        # print(file_path)
        result_n_bcc=sat_bcc_solve(file_path)
        result_old_bcc=sat_bcc_solve_2014(file_path)
        result_n_bcc['problem_field']=f"{index+1}-{result_n_bcc['problem_field']}"
        result_old_bcc['problem_field']=f"{index+1}-{result_old_bcc['problem_field']}"

        export_schedule_to_xlsx(**result_n_bcc,output_file=xlsx_output_path)
        export_schedule_to_xlsx(**result_old_bcc,output_file=xlsx_output_path)


# sat_bcc_test("assets/input/j30.sm.tgz","bcc.xlsx")    
sat_bcc_test("assets/test","bcc.xlsx")    



