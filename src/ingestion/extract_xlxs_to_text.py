from pathlib import Path
import pandas as pd


#Expected columns from xlsx for sanit check
EXPECTED_COLUMNS = {
    "Module Code",
    "Module",
    "Assessment Type",
    "Assessment Title",
    "Percentage",
    "Hand Out Date",
    "Hand In Date",
    "Feedback Date",
}

def date_format(value) -> str:
    # Handle empty cells
    if pd.isna(value) or str(value).strip() == "" or str(value).strip().lower() == "nan":
        return ""
    
    value_str = str(value).strip()
    
    # Case 1 — already a Timestamp e.g. "2025-10-06 00:00:00"
    try:
        return pd.to_datetime(value_str, format="%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d")
    except ValueError:
        pass
    
    # Case 2 — string format e.g. "Mon, 06 Oct 2025"
    try:
        return pd.to_datetime(value_str, format="%a, %d %b %Y").strftime("%Y-%m-%d")
    except ValueError:
        pass

    # Case 3 — let pandas infer the format as a last resort
    return pd.to_datetime(value_str).strftime("%Y-%m-%d")

def extract_calender(xlsx_path:Path)->list[dict]:
    '''
    Read the Assessment Calendar xlsx and return a list of assessment records.
    Each record schema:
    {
        "policy_name"      : str,  <- always "Assessment Calendar"
        "source"           : str,  <- original filename
        "module_code"      : str,  <- e.g. "CMT227"
        "module_name"      : str,  <- e.g. "Advanced Topics in NLP"
        "assessment_type"  : str,  <- e.g. "Portfolio"
        "assessment_title" : str,  <- e.g. "Advanced Topics in NLP Portfolio"
        "weight"           : int,  <- e.g. 60  (percentage as integer)
        "hand_out_date"    : str,  <- e.g. "2026-02-02" or "" if not set
        "hand_in_date"     : str,  <- e.g. "2026-05-07" or "" if not set
        "feedback_date"    : str,  <- e.g. "2026-06-08" or "" if not set
    }
    Args:
        xlsx_path: Path object pointing to the xlsx file.
    Returns:
        List of assessment dicts, one per row in the xlsx.
 
    Raises:
        FileNotFoundError : if xlsx_path does not exist.
        ValueError        : if expected columns are missing from the file.

    '''
    #If file not exist in the given path 
    if not xlsx_path.exists():
        raise FileNotFoundError(f"Calender xlsx file not found:{xlsx_path}")
    
    #Reading the actual excel file
    calender_dataframe = pd.read_excel(xlsx_path,dtype=str)

    #Sanity check if expected colum is not found
    missing = EXPECTED_COLUMNS - set(calender_dataframe.columns)
    #If any missing found
    if missing:
        raise ValueError(
            f"Calender xlsx is missing expected columns - {missing}\n"
            f"Found columns: {calender_dataframe.columns.tolist()}"
        )

    #creating empty list to store the data
    records = []

    #Looping through whole dataset
    for _,row in calender_dataframe.iterrows():
        records.append({
            "policy_name" : "Assessment calender",
            "policy_source" : xlsx_path.name,
            "module_code" : str(row['Module Code']).strip(),
            "module_name" : str(row['Module']).strip(),
            "assessment_type"  : str(row["Assessment Type"]).strip(),
            "assessment_title" : str(row["Assessment Title"]).strip(),
            "weight"           : int(row["Percentage"]),
            "hand_out_date"    : date_format(row["Hand Out Date"]),
            "hand_in_date"     : date_format(row["Hand In Date"]),
            "feedback_date"    : date_format(row["Feedback Date"]),
        })

    return records     
