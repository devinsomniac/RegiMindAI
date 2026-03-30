from pathlib import Path
from tqdm import tqdm
import fitz
import re

def infer_policy_name(file_path:str)-> str:
    '''
    Getting the cleaned file name from file path like
    Academic-Integrity-Policy.pdf to Academic Integrity Policy
    '''
    #Removing any file extension like .pdf 
    name = file_path.stem
    #Replaceing "-" and "_" with single space
    name = name.replace("-"," ").replace("_"," ")
    #Replacing multiple space with single space 
    name = re.sub(r"\s+"," ",name).strip()
    #Returning fresh space
    return name

def basic_cleaning(text:str)->str:
    '''Basic cleaning of raw text extracted from fitz
        like 
        - removing carriage returns of wondows
        - removing null bytes
        - replacing multiple space/tabs to single space
        - replacing 3+ newlines to 2 
    '''
    #Replaceing carriage return
    text = text.replace("\r","")
    #Removing null bytes
    text = text.replace("\x00","")
    #substititing more than 2 space and tab to one single space
    text = re.sub(r"[ \t]+"," ",text)
    #substituting 3 or more new lines to 2
    text = re.sub(r"\n{3,}","\n\n",text)

    #Returning cleaned space free from start and end text
    return text.strip()

def extract_pages_from_pdf(pdf_path:Path)->list[dict]:
    '''Looping through all pdfs
    Using PyMuPDF extraxting each page from pdf and creating a json for 
    each page and all the json creates a singler list

    Output schema per record:
    {
        "policy_name" : str,
        "policy_source" : str,
        "page"  : int,
        "text" : str
    }
    '''

    #Checking whether there is a pdf exist or not
    #We can use exists() because its a Path object
    if not pdf_path.exists():
        raise FileNotFoundError(f"No pdf found in th {pdf_path} path")
    
    #Creating empty list to store the records
    records = []
    #Getting cleaned policy name
    policy_name = infer_policy_name(pdf_path)

    #Opening the pdf using fitz
    doc = fitz.open(pdf_path)

    try:
        for page_index in tqdm(range(len(doc)), desc=f"Extracting {pdf_path.name}",unit="page"):
            #Getting each page
            page = doc.load_page(page_index)
            #Extracting text
            text = page.get_text("text")
            #Basic cleaning of extracted text
            text = basic_cleaning(text)
            #Creating json
            records.append({
                "policy_name" : policy_name,
                "policy_source" : pdf_path.name,
                "page" : page_index+1,
                "text" : text
            })
    #Closing doc            
    finally:
        doc.close()

    return records        
