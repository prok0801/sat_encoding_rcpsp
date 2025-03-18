from utils.data_processor import DataProcessor
from sat_based_2014.bcc_2014 import convert_json_to_base_2014

# processor = DataProcessor("assets/dataset", "assets/input")


res,tasks,relations,consumptions,resources=convert_json_to_base_2014("/Users/2noscript/workspace/do-more/RCPSP_SAT-Encoding/assets/input/j120.sm.tgz/j1201_1.json")
# processor.handle()


with open("test.txt", "w", encoding="utf-8") as f:
    f.write(res)