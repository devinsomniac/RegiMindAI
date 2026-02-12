#Built-in library for working with JSON data (reading/writing)
import json
#Modern way to handle file paths (works across Windows/Mac/Linux)
from pathlib import Path
#Library for reading and extracting text from PDF files
import fitz
#Creates progress bars so you can see how long tasks will take
from tqdm import tqdm


#A function to change the file name like removing ".pdf" or "-" and taking first 3 words of the file name
def infer_policy_name(filename:str)->str:
    name = filename.replace(".pdf","").replace("-"," ")
    return " ".join(name.split()[:6])


def extract_all_pdf(raw_dir:Path):
    #Empty array to store extracted pdf
    records = []
    #Sorting pdf file alphabatical order
    pdfs = sorted(raw_dir.glob("*.pdf"))
    #Raise an error if no pdf found in the given path
    if not pdfs:
        raise FileNotFoundError(f"No PDFs found in {raw_dir}")
    
    for pdf_name in pdfs:
        policy_name = infer_policy_name(pdf_name.name)
        doc = fitz.open(pdf_name)

    
def main():
    #Finding the project root
    project_root = Path(__file__).resolve().parents[2]
    #The dir of raw data
    raw_dir = project_root / "data" / "raw"
    #Dir of of processed data
    processed_dir = project_root / "raw" /"processed"
    processed_dir.mkdir(parents=True,exist_ok=True)
    out_path = processed_dir / "handbook_pages.json" 

    pages = extract_all_pdf(raw_dir)
    




