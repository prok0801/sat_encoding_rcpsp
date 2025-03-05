from ..mapping.Mapper import Mapper
from .RCPSPAlgorithm import RCPSPAlgorithm
from ..log.Log import Log

def main():
    # Get the singleton Mapper instance.
    mapper = Mapper.get_mapper()
    
    # Open and read the project data from "project_file.txt".
    with open("project_file.txt", "r") as project_file:
        project = mapper.map_project(project_file)

    # Set the log file path.
    Log.set_log_path("rcpsp_log.log")
    
    # Create the algorithm instance (using bcc_mode=True in this example)
    algorithm = RCPSPAlgorithm(project, bcc_mode=True)
    
    # Run the algorithm.
    algorithm.calculate()

if __name__ == "__main__":
    main()
