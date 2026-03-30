from pathlib import Path
import json

from .extract_pdf_to_text import extract_pages_from_pdf
from .extract_xlxs_to_text import extract_calender
'''
Task of this ingestion.py : 
                -Orchestrate the full ingestion pipeline.
                -Routes each file to the correct extractor
                -Merges all records into a single list
                -Saves the output to data/processed/all_records.json

EXTRACTORS:
   extract_pdf_to_text.py  ->  prose policy PDFs  (fitz)
   extract_calendar.py     ->  Assessment Calendar xlsx  (pandas)

'''


# The calendar xlsx filename — handled separately from PDFs
CALENDAR_FILENAME = "Assessment Calendar.xlsx"


def run_ingestion(raw_dir:Path,output_file:Path)->None:
    '''
    Main ingestion function. Loops over data/raw/, routes each file to
    the correct extractor, merges all records, and saves to all_records.json.
    Args:
        raw_dir     : Path to data/raw/ directory containing PDFs + xlsx
        output_file : Path to save the merged all_records.json
 
    Raises:
        FileNotFoundError : if raw_dir does not exist
    '''
    if not raw_dir.exists():
        raise FileNotFoundError(f"No file found in {raw_dir}")
    
    #Creating an empty list to store all dict of info from pdfs and xlsx
    all_records = []
    
    '''The pdf extraxtion part'''
    
    #Sorting the pdf paths
    pdf_paths = sorted(raw_dir.glob("*.pdf"))

    #Sanity check whether there is pdf file or not
    if not pdf_paths:
        print("Warning : No PDF files found in raw directory.")

    for pdf_path in pdf_paths:
        print(f"Extraxting {pdf_path}")
        #Sendong each pdf path to pdf extraction module
        pages_records = extract_pages_from_pdf(pdf_path)
        #Adding the records(list) we got from that to our main record list
        all_records.extend(pages_records)
        print(f"{len(pages_records)} pages extrated")


    '''The xlsx extraxtion part'''
    #Getting the calender path
    calender_path = raw_dir / CALENDAR_FILENAME
    #Sanity check whether calender is available or not
    if not calender_path.exists():
        print(f"No calender file exist is {calender_path}")
    else:
        print(f"Extraxting {calender_path.name}")
        #Extraxting the calender data using calander extraxtion module
        calender_records = extract_calender(calender_path)
        #Appending the calender records to the main records
        all_records.extend(calender_records)
        print(f"{len(calender_records) }assessment records extracted.")

    '''Saving merged file into output file'''
    #Making the output file if not made yet
    output_file.parent.mkdir(parents=True, exist_ok=True)

    #Opening the output file for writting and saving the json inside
    with output_file.open("w",encoding="utf-8") as f:
        json.dump(all_records,f,ensure_ascii=False,indent=2)

    print(f"\nIngestion Completed and saved into {output_file}\n")

def main():
    #Getting the whole project root
    project_root = Path(__file__).resolve().parents[2]
    #Raw data directory
    raw_dir = project_root / "data" / "raw"
    #Output file where the processed data will be saved
    output_file = project_root / "data" / "processed" / "all_records.json"

    #Running ingestion engine
    run_ingestion(raw_dir,output_file)

if __name__ == "__main__":
    main()