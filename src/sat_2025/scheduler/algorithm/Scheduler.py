import sys
from .Algorithm import Algorithm

from ..log.Log import Log

from ..mapping.Mapper import Mapper
from .FowardAlgorithm import FowardAlgorithm
from .RCPSPAlgorithm import RCPSPAlgorithm

def main():
    # Default values
    bcc_mode = True
    project_path = "C:/Users/Admin/Desktop/sat_based_solution/server.project"

    # Process command-line arguments (excluding the script name)
    args = sys.argv[1:]
    i = 0
    while i < len(args):
        arg = args[i]
        if arg == "-bcc":
            bcc_mode = True
        elif arg == "-pow":
            bcc_mode = False
        elif arg == "-logPath":
            i += 1
            if i < len(args):
                Log.set_log_path(args[i])
            else:
                print("Error: -logPath requires a following argument")
                sys.exit(1)
        elif arg == "-project":
            i += 1
            if i < len(args):
                project_path = args[i]
            else:
                print("Error: -project requires a following argument")
                sys.exit(1)
        i += 1

    # Log the project path
    Log.i(project_path)

    # Read the project using the mapper
    mapper = Mapper.get_mapper()
    project = mapper.read_project(project_path)

    # Print out the project details.
    print("Project Name:", project.get_name())
    print("WAT:", project.get_wat())
    print("WET:", project.get_wet())
    print("\nActivities:")
    for activity in project.get_activities():
        # Assuming your Activity class defines get_id(), get_duration(), get_name()
        print(f"  ID: {activity.get_id()}, Duration: {activity.get_duration()}, Name: {activity.get_name()}")
    
    print("\nRelations:")
    for relation in project.get_relations():
        # Assuming your Relation class implements __str__() appropriately.
        print(f"  {relation}")
    
    print("\nResources:")
    for resource in project.get_resources():
        # Assuming your Resource class defines get_id(), get_capacity(), get_name()
        print(f"  ID: {resource.get_id()}, Capacity: {resource.get_capacity()}, Name: {resource.get_name()}")

    # Create algorithm instances
    fwd = FowardAlgorithm(project)
    rcpsp = RCPSPAlgorithm(project, bcc_mode)

    # Run calculations
    fwd.calculate()
    rcpsp.calculate()

if __name__ == "__main__":
    main()
