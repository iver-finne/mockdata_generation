import os
import pandas as pd

def convert_xlsx_to_csv(directory):
    xlsx_files = [f for f in os.listdir(directory) if f.endswith('.xlsx')]
    
    for xlsx_file in xlsx_files:
        subdirectory = os.path.splitext(xlsx_file)[0]
        if not os.path.exists(subdirectory):
            os.makedirs(subdirectory)
        
        with pd.ExcelFile(xlsx_file) as xls:
            for i, sheet_name in enumerate(xls.sheet_names):
                df = pd.read_excel(xls, sheet_name)
                
                csv_file = f"{subdirectory}/{subdirectory}_page{i+1}.csv"
                
                df.to_csv(csv_file, index=False)
                print(f"Saved {csv_file}")

convert_xlsx_to_csv('.')


