from ..mapping.Mapper import Mapper
from .RCPSPAlgorithm import RCPSPAlgorithm
from ..log.Log import Log
from io import StringIO
import openpyxl

def main():
    # Get the singleton Mapper instance.
    mapper = Mapper.get_mapper()
    
    # Load the Excel workbook.
    wb = openpyxl.load_workbook("project_file.xlsx")
    ws = wb.active

    # Convert each row in the worksheet into a semicolon-separated line.
    lines = []
    for row in ws.iter_rows(values_only=True):
        # Convert cell values to strings and ignore None values.
        row_values = [str(cell) for cell in row if cell is not None]
        if row_values:
            line = ";".join(row_values)
            lines.append(line)
    # Combine all lines into a single string.
    text_data = "\n".join(lines)
    
    # Create a StringIO stream to simulate a text file.
    project_file = StringIO(text_data)
    
    # Map the project using the mapper.
    project = mapper.map_project(project_file)

    # # Print out the project details.
    # print("Project Name:", project.get_name())
    # print("WAT:", project.get_wat())
    # print("WET:", project.get_wet())
    # print("\nActivities:")
    # for activity in project.get_activities():
    #     # Assuming your Activity class defines get_id(), get_duration(), get_name()
    #     print(f"  ID: {activity.get_id()}, Duration: {activity.get_duration()}, Name: {activity.get_name()}")
    
    # print("\nRelations:")
    # for relation in project.get_relations():
    #     # Assuming your Relation class implements __str__() appropriately.
    #     print(f"  {relation}")
    
    # print("\nResources:")
    # for resource in project.get_resources():
    #     # Assuming your Resource class defines get_id(), get_capacity(), get_name()
    #     print(f"  ID: {resource.get_id()}, Capacity: {resource.get_capacity()}, Name: {resource.get_name()}")
    
    # Set the log file path.
    Log.set_log_path("rcpsp_log.log")
    
    # Create the algorithm instance (using bcc_mode=True in this example).
    algorithm = RCPSPAlgorithm(project, bcc_mode=True)
    
    # Run the algorithm.
    algorithm.calculate()
    print("=================")

    for key, value in algorithm.__dict__.items():
        print(f"{key}: {value}")
        
    print("=================")

    print("Total number of clauses added:", algorithm.solver._clause_count)

if __name__ == "__main__":
    main()
