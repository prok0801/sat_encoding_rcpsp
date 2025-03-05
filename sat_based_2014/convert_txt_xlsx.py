from openpyxl import Workbook

def convert_txt_to_xlsx(txt_file, xlsx_file):
    # Create a new workbook and select the active worksheet.
    wb = Workbook()
    ws = wb.active

    # Open and read the text file line by line.
    with open(txt_file, 'r') as f:
        for line in f:
            # Remove any trailing newline characters and split the line by semicolon.
            row = line.strip().split(';')
            ws.append(row)
    
    # Save the workbook to the specified Excel file.
    wb.save(xlsx_file)
    print(f"Conversion complete. '{txt_file}' has been converted to '{xlsx_file}'.")

if __name__ == "__main__":
    # Convert 'project_file.txt' to 'project_file.xlsx'
    convert_txt_to_xlsx("project_file.txt", "project_file.xlsx")




    