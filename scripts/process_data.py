import pandas as pd
import os
from sqlalchemy import create_engine

def process_isco_data(file_path):
    # Read the excel file
    print(f"Reading data from {file_path}...")
    df = pd.read_excel(file_path)
    
    # Strip whitespace from column names to ensure exact matches
    df.columns = df.columns.str.strip()
    
    # Determine the ISCO code column name
    expected_col = 'isco_08_code'
    
    # Find the actual column name (handling potential case/space variations)
    code_col = None
    for col in df.columns:
        if expected_col.lower() in col.lower() or ('isco' in col.lower() and 'code' in col.lower()):
            code_col = col
            break
            
    if not code_col:
        # Fallback to exact match or raise error
        if expected_col in df.columns:
            code_col = expected_col
        else:
            raise ValueError(f"Could not find a column resembling '{expected_col}'. Available columns: {df.columns.tolist()}")

    print(f"Using column '{code_col}' as the ISCO Code column.")

    # Ensure the code column is treated as a string
    # Remove any '.0' if pandas parsed it as a float
    df['Cleaned Code'] = df[code_col].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
    
    # Filter out empty or 'nan' values that might have been loaded
    df = df[df['Cleaned Code'] != 'nan']

    # 1. Create a column for "part of which hierarchy" (Parent Code) by removing the last digit
    df['Parent Code'] = df['Cleaned Code'].apply(lambda x: x[:-1] if len(x) > 1 else None)
    
    # 2. Label the hierarchy based on the code length
    def label_hierarchy(code):
        length = len(code)
        if length == 1:
            return 'Major Group'
        elif length == 2:
            return 'Sub-Major Group'
        elif length == 3:
            return 'Minor Group'
        elif length == 4:
            return 'Unit Group'
        else:
            return 'Unknown'
            
    df['Hierarchy Level'] = df['Cleaned Code'].apply(label_hierarchy)
    
    # You can drop the temporary 'Cleaned Code' column if you want, 
    # but it's useful to keep if the original had mixed types.
    
    # Rename columns: replace spaces with underscores and convert to lowercase
    df.columns = df.columns.str.lower().str.replace(' ', '_')
    code_col = code_col.lower().replace(' ', '_')
    
    return df, code_col

def process_csv_data(file_path):
    print(f"Reading data from {file_path}...")
    df = pd.read_csv(file_path)
    # Rename columns: replace spaces with underscores and convert to lowercase
    df.columns = df.columns.str.lower().str.replace(' ', '_')
    return df

if __name__ == "__main__":
    # Set up paths relative to this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_file = os.path.join(script_dir, '..', 'data', 'ISCO-08 EN Structure and definitions.xlsx')
    db_file = os.path.join(script_dir, '..', 'data', 'unmapped.db')
    
    engine = create_engine(f"sqlite:///{db_file}")
    
    if not os.path.exists(input_file):
        print(f"Error: Input file not found at {input_file}")
    else:
        # Process the data
        df, code_col_name = process_isco_data(input_file)
        
        print("\n--- Processing Complete ---")
        print("Sample of the new columns:")
        print(df[[code_col_name, 'parent_code', 'hierarchy_level']].head(10))
        
        # Save to a SQLite database
        table_name = "isco_skills"
        df.to_sql(table_name, con=engine, if_exists="replace", index=False)
        print(f"\nSaved processed dataset to table '{table_name}' in {db_file}")

    # Process Frey & Osborne CSV files and the new full datasets
    csv_files = {
        'frey_osborne_isco': 'frey_osborne_isco.csv',
        'frey_osborne_lmic': 'frey_osborne_lmic.csv',
        'lmic_automation_calibration_full': 'lmic_automation_calibration_full.csv',
        'lmic_sector_automation_risk_full': 'lmic_sector_automation_risk_full.csv',
        'wic_automation_combined_full': 'wic_automation_combined_full.csv',
        'wittgenstein_education_projections_full': 'wittgenstein_education_projections_full.csv'
    }
    
    for table_name, filename in csv_files.items():
        csv_path = os.path.join(script_dir, '..', 'data', filename)
        if not os.path.exists(csv_path):
            print(f"Error: CSV file not found at {csv_path}")
        else:
            df_csv = process_csv_data(csv_path)
            df_csv.to_sql(table_name, con=engine, if_exists="replace", index=False)
            print(f"Saved {filename} to table '{table_name}' in {db_file}")
