import json
import fitz
from pathlib import Path
from tqdm import tqdm
import re

#function to get the clean name of the file
def infer_name(filename : str) -> str :
    #Changing the file name by replacing extension name and -
    name = filename.replace(".pdf","").replace("-"," ")
    return " ".join(name.split()[:6])

def normalize_text(text: str) -> str:
    text = text.replace("\r", "")
    # collapse 3+ newlines into 2 newlines
    text = re.sub(r"\n{3,}", "\n\n", text)
    # collapse multiple spaces/tabs
    text = re.sub(r"[ \t]{2,}", " ", text)
    return text.strip()

#function to extract all text from pdf
def extract_all_pdf(raw_dir:Path):
    #An empty list
    records = []
    #Sorting all files in ascending order
    pdfs = sorted(raw_dir.glob("*.pdf"))
    #Error clause if no pdf found
    if not pdfs:
        raise FileNotFoundError(f"No pdf found in {raw_dir}")
    
    #accessing each Path object fro the list of path object
    for pdf_path in pdfs :
        #Clean file name
        policy_name = infer_name(pdf_path.name)
        #Opening the document
        doc = fitz.open(pdf_path)

        #Accessing each page of the document
        for i in tqdm(range(len(doc)), desc=f"Extracting {pdf_path.name}"):
            #Loading each page
            page = doc.load_page(i)
            #Getting each page content
            text = normalize_text(page.get_text("text"))
            
            #Storing the content
            records.append({
                "policy":policy_name,
                "source_file" : pdf_path.name,
                "page" : i+1,
                "text" : text
            })
        doc.close()
    return records


def main():
    #Accessing the root of the project
    project_root = Path(__file__).resolve().parents[2]
    #Accesing the raw data directory
    raw_data = project_root / "data" / "raw"
    #The dir where our processed data will be saved
    processed_dir = project_root / "data" / "processed"
    processed_dir.mkdir(parents=True,exist_ok=True)

    out_path = processed_dir / "handbook_pages.json"

    pages = extract_all_pdf(raw_data)

    # Open the output file in write mode (UTF-8 encoding),
    # convert the Python list of dictionaries (pages) into JSON format,
    # and write it to disk in a readable (indented) structure.
    with out_path.open("w",encoding="utf-8") as f:
        json.dump(pages,f,ensure_ascii=False,indent=2)

    
    print(f"✅ Extracted {len(pages)} pages from {len(set(p['source_file'] for p in pages))} PDFs")
    print(f"📄 Saved to: {out_path}")


if __name__ == "__main__":
    main()        
