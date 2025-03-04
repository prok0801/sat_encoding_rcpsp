
from utils.helper import DataProcessor


# res=parse_dataset_file("/Users/2noscript/workspace/do-more/RCPSP_SAT-Encoding/assets/dataset/j30.sm.tgz/j301_1.sm")

# print(res)

processor = DataProcessor("assets/dataset","assets/input")
processor.handle()
