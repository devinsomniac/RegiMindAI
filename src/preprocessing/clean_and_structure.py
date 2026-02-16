import re
import json
from pathlib import Path



'''Function to clean the text like removing \\n and other cleaning'''
def normalize_text(text:str) -> str:
    text = text.replace("\r","")
    #replacing more than 3 newline into 2 new lines
    text = re.sub(r"\n{3,}","\n\n",text)
    #Removing multiple spaces/tabs
    text = re.sub(r"[ \t]{2,}"," ",text)
    return text.strip()


'''Function to remove junk lines like page number and all'''
#Matching all the numbers with optional spaces
RE_JUST_NUMBER = re.compile(r"^\s*\d{1,4}\s*$")
#Matching all the words matching "page" or "Pages"
RE_PAGE_WORD = re.compile(r"^\s*page\s*$", re.I)
def remove_junk_lines(text:str) -> str:
    #making an array for lines in text
    lines = [ln.strip() for ln in text.splitlines()]
    #Array to keep clean lines
    kept = []
    for ln in lines:
        if not ln:
            continue
        if RE_JUST_NUMBER.match(ln):
            continue
        if RE_PAGE_WORD.match(ln):
            continue
        kept.append(ln)

    return "\n".join(kept).strip()

'''Function to remove useless pages like contents, few words etc'''
def is_useless_pages(text:str)->bool:
    #If not text
    if not text:
        return True
    #If number of words are less than 80
    if len(text.split())<20:
        return True
    #Very few alphabats , mostly numbers and symbols
    alpha_chars = sum(c.isalpha() for c in text)
    if alpha_chars / len(text) < 0.3:
        return True
    return False

'''Function to remove TOC and other things'''
def is_toc_page(text: str) -> bool:
    t = text.lower()

    # direct TOC markers
    if "contents" in t or "table of contents" in t:
        return True
    # dotted leader style lines are common in TOC
    dotted_lines = sum(1 for line in text.splitlines() if "...." in line)
    if dotted_lines >= 3:
        return True

    return False

'''Function to create chunks from cleaned json'''
def chunk_text(text:str,chunk_size : int = 800 , overlap:int = 100):
    #An empty list to contain chunks
    chunks = []
    start = 0
    #The loop will continue until the end of the whole text
    while start < len(text):
        #Basically counting the chunk size
        end = start + chunk_size
        #Slicing from the text from start to end-1(as end does not include)
        chunk = text[start:end]
        #Adding the chunks into the list
        chunks.append(chunk)
        #Re-calculating the start with overlap
        start = end-overlap
    return chunks

def main():
    #Accessing the project root
    project_root = Path(__file__).resolve().parents[2]
    #Accessing the data 
    data_path = project_root / "data" / "processed" / "handbook_pages.json"

    #Error handling if no file found
    if not data_path.exists() :
        raise FileNotFoundError(f"No file found in {data_path}")
    
    #Opening the json file
    with data_path.open("r",encoding="utf-8") as f:
        pages = json.load(f)

    #Sanity check
    print(f"Loaded {len(pages)} pages from {data_path}")   

    #Normslizing text
    for p in pages:
        p["text"] = normalize_text(p.get("text",""))
        p["text"] = remove_junk_lines(p["text"])

    #Removing useless pages
    cleaned_pages = []
    for p in pages:
        if is_useless_pages(p["text"]):
            continue
        if is_toc_page(p["text"]):
            continue
        cleaned_pages.append(p)
    
    
    #Creating chunks
    all_chunks = []  
    for p in cleaned_pages:
        policy = p["policy"]
        source_file = p["source_file"]
        page = p["page"]
        text = p["text"]

        chunks = chunk_text(text)

        for i,chunk in enumerate(chunks):
            chunk_dict = {
                "policy" : policy,
                "source_file" : source_file,
                "page" : page,
                "chunk_id" : f"{source_file}_p{page}_c{i}",
                "text" : chunk
            }

            all_chunks.append(chunk_dict)

    #Creating all_chunks json file
    out_put_path = project_root / "data" / "processed" / "handbook_chunks.jsonl"
    with out_put_path.open("w",encoding="utf-8") as f:
        for chunk in all_chunks:
            f.write(json.dumps(chunk,ensure_ascii=False) + "\n")
    print(f"Saved {len(all_chunks)} chunks to {out_put_path}")        


if __name__ == "__main__":
    main()


