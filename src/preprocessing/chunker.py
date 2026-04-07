from __future__ import annotations
import re
import uuid

'''
Work of this module
1. Detect section Headers like 14.5.3, 9.4, .1, .2 as split points
2. Each section becomes one chunk
3. If a section exceeds MAX_CHUNK_TOKENS, split with overlap
4. If adjacent sections are tiny, merge them
5. Calendar records pass through as it is (already atomic)
6. Each chunk carries metadata (source, page, section heading)
'''


'''-=-=--=-=-==--=--== Calender Chunking -=-==----=-=-=-=--=--='''

def chunk_calender(rec:dict)->list[dict]:
    """
    Calendar records are already atomic so we will pass through with chunk metadata.
    """
    #Making a tuple of text to store calender data
    text = (
        f"Module: {rec.get('module_code', '')} - {rec.get('module_name', '')}\n"
        f"Assessment: {rec.get('assessment_title', '')} ({rec.get('assessment_type', '')})\n"
        f"Weight: {rec.get('weight', '')}%\n"
        f"Hand Out Date: {rec.get('hand_out_date', 'Not set')}\n"
        f"Hand In Date: {rec.get('hand_in_date', 'Not set')}\n"
        f"Feedback Date: {rec.get('feedback_date', 'Not set')}"
    )
    #Making chunk id
    chunk_id = str(uuid.uuid4())[:8]
    return[{
        "chunk_id": chunk_id,
        "text": text,
        "policy_source": rec.get("policy_source", "Assessment Calendar.xlsx"),
        "policy_name": rec.get("policy_name", "Assessment Calendar"),
        "page": None,
        "section_number": "",
        "section_heading": "Assessment Deadline",
        "chunk_index": 0,
        "total_sub_chunks": 1,
    }]

'''-=-=-=-=-=-==-  PDF Chunking -=-=---=-=-=-=-=-'''

#-=-=-=-=-=-=--= PDF chunk config -=--=--=-=--=--=-=-

#Rough estimate: 1 token ≈ 4 characters for English text
CHARS_PER_TOKEN = 5
#Max chunk size in tokens - embedding models work best under 512
MAX_CHUNK_TOKENS = 450
# 2250 chars
MAX_CHUNK_CHARS = MAX_CHUNK_TOKENS * CHARS_PER_TOKEN  
#Min chunk size - sections smaller than this get merged with neighbors
MIN_CHUNK_TOKENS = 50
# 200 chars
MIN_CHUNK_CHARS = MIN_CHUNK_TOKENS * CHARS_PER_TOKEN  
#Overlap between sub-chunks when splitting oversized sections
OVERLAP_TOKENS = 80
# 320 chars
OVERLAP_CHARS = OVERLAP_TOKENS * CHARS_PER_TOKEN  


'''Since we will be doing section wise chunking, so we need to detect the section
which we will do using detecting the heading
'''
#Regesx expression to capture headings in all text
#We are using re.MULTILINE so that it checks every start of each line
#(?:Section\s+)? - optional to match like Section 3
#(\d{1,2}(?:\.\d{1,2}){0,3}|\.\d{1,2}) to capture like 
'''
1
1.1
1.1.1
'''
#OR
'''
.1
.2
'''
#(?:\s*[-–.]?\s*) - Non Capturing 0 or more whitespace then any of one - or -- or . which is optional and again space like 1. 
#([^\n]{0,200}) - Anything except new line upto 200 chars like Definition of Academic Misconduct
_SECTION_HEADER = re.compile(r"^(?:Section\s+)?(\d{1,2}(?:\.\d{1,2}){0,3}|\.\d{1,2})(?:\s*[-–.]?\s*)([A-Z][^\n]{2,140})", re.MULTILINE)
#Splitting sentence based on space and punctuation and positive look behind
_SENTENCE_SPLIT = re.compile(r"(?<!e\.g)(?<!i\.e)(?<!Dr)(?<!Mr)(?<!Ms)(?<=[.!?])\s+")


def _fix_split_headings(text:str)->str:
    '''Function to detect and correct to feed in prev regex
    like some of the headings are 2. \n Introduction which we will convert into single line
    '''
    #At first detect are we in new line or start of text using (\n|\A)
    #Then we search for number like 2. or 2.1. or something similar
    #Them 0 or more space then new line and again 0 or more spaces
    #Then actual heading text
    #Then we are replacing the match with group 2 - (\d+(?:\.\d+)*) + "." + group 3 - ([A-Z])
     # Fix numbered headings split across lines: "2.\nDefinition" → "2. Definition"
    text = re.sub(
        r"(\n|\A)(\d+(?:\.\d+)*)\.\s*\n\s*([A-Z])",
        r"\n\2. \3",
        text
    )
    # Fix sub-clause headings split across lines: ".4\nCollusion" → ".4 Collusion"
    text = re.sub(
        r"(\n|\A)(\.\d{1,2})\s*\n\s*([A-Z])",
        r"\n\2 \3",
        text
    )
    return text


def _split_into_sections(text:str)->list[dict]:
    """
    Split text into sections based on numbered headings.
    Returns a list of dicts with 'heading' and 'body' keys.
    """
    #Listing all the match for headings
    matches = list(_SECTION_HEADER.finditer(text))

    #If no heading found in the rec, it would make a split without any heading
    if not matches:
        return [{"heading":"","section_number" : "","body":text.strip()}]
    
    #Empty list to store sections
    sections = []

    '''
    preamble is the text which is present before any heading like
    Some intro text here.\n\n14.5 Marking\nWe aim to return marks.
    So we capture text from 0th index to start of first match-not included
    '''
    preamble = text[:matches[0].start()].strip()
    #If such text exist then we will create a rec without heading and section number
    if preamble:
        sections.append({
            "heading": "",
            "section_number": "",
            "body": preamble
        })

    for i,match in enumerate(matches):
        #From the list of matches we will store the section number which is group 1 in our regex - group(1) = section number like "14.5.3" or ".1"
        section_number = match.group(1)
        #From the list of matches we will store the section heading which is group 2 in our regex - group(2) = heading text like "Resits" or "Plagiarism"
        heading_text = match.group(2)
        start_body = match.end()
        end_body = matches[i+1].start() if i+1 < len(matches) else len(text)
        body = text[start_body:end_body].strip()

        sections.append({
            "heading": heading_text,
            "section_number": section_number,
            "body": body
        })

    return sections    


def _merge_small_sections(sections:list[dict])->list[dict]:
    """
    Merging adjacent tiny sections (below MIN_CHUNK_CHARS) into one chunk.
    
    Walks left to right. If the previous section is too small, the current
    section gets merged into it. After the loop, if the last section is
    still too small, it gets merged into the one before it.
    """
    #If section is empty then retuen empty only, no need to continue
    if not sections:
        return sections
    
    #Saving the copy first section in the merged
    merged = [sections[0].copy()]

    #Looping all the sections from 1st index
    for section in sections[1:]:
        #Storing the last entry of merge list
        prev = merged[-1]
        #Size of last entry as we check whether its small, iof yes we will merge with current one else 
        prev_size = len(prev['body'])

        #If prev section is too small (less then threshold to termed as small section)
        if prev_size<MIN_CHUNK_CHARS:
            if section['heading']:
                separator = f"\n\n{section['section_number']} {section['heading']}\n"
            else:
                separator = "\n\n"
            prev['body'] = prev['body'] + separator + section['body']
            # If previous had no heading and current one has then we will add the headding of current one to prev
            if not prev["heading"] and section["heading"]:
                prev["heading"] = section["heading"]
                prev["section_number"] = section["section_number"]
        #If prev is big enough then we will add the current in the list as it is
        else:
            merged.append(section.copy())               
    #After merging and all if the last one is less then min chunk chars
    if len(merged)>1 and len(merged[-1]['body'])<MIN_CHUNK_CHARS:
        #We take out the last section
        last = merged.pop()
        if last['heading']:
            separator = f"\n\n{last['section_number']} {last['heading']}\n"
        else:
            separator = "\n\n"
        #We will merge the taken out last with the current last with separator
        merged[-1]['body'] = merged[-1]['body']+separator+last['body']       

    return merged

def _split_oversized(text:str)->list[str]:
    """
    Split text that exceeds MAX_CHUNK_CHARS into smaller pieces
    with overlap, breaking at sentence boundaries.
    
    Uses the last 2 sentences as overlap instead of raw character count
    so context breaks happen at natural boundaries.
    """
    # If text is less or equal max chunk chars, no splitting needed
    if len(text) <= MAX_CHUNK_CHARS:
        return [text]
    #Spluitting sentences from text based on regex we made
    sentences = _SENTENCE_SPLIT.split(text)

    #Actual chunk list if over sized
    chunks = []
    #To store chunk
    current_chunk = ""

    for sentence in sentences:
        # If adding this sentence would exceed max, save current and start new
        if len(current_chunk) + len(sentence) > MAX_CHUNK_CHARS and current_chunk:
            chunks.append(current_chunk.strip())
            split_sentences = current_chunk.split(". ")
            #Leaving 2 sentences behind to keep context
            overlap_text = ". ".join(split_sentences[-2:])
            current_chunk = overlap_text + " " + sentence
        else:
            if current_chunk:
                current_chunk = current_chunk + " " + sentence
            else:
                current_chunk = sentence
    #After creating chunk if any last small chunk left then will add it to main chunk
    if current_chunk.strip():
        chunks.append(current_chunk.strip())
 
    return chunks                




def chunk_pdf(rec:dict)->list[dict]:
    """
    Chunk a single PDF record using section-aware splitting.
    Returns a list of chunk dicts with text and metadata.
    """
    #pdf text
    text = rec.get("text","Unknown")
    #pdf source
    policy_source =  rec.get("policy_source","Unknown")
    #Policy name
    policy_name = rec.get("policy_name")
    #page number of the pdf
    page = rec.get("page","Unknown")

    if not text:
        return []
    
    #Fixing the double line section number and heading
    text = _fix_split_headings(text)

    #Splitting the text based on sections
    '''
    [
        {
            "heading":"....",
            "Section Number": "....",
            "body" : "....."
        }
    ]
    '''
    sections = _split_into_sections(text)

    #Merging the text based on min chunk size
    '''
    [
        {
            "heading":"....",
            "Section Number": "....",
            "body" : "....."
        }
    ]
    '''
    sections = _merge_small_sections(sections)

    #Final chunk list
    chunks = []
    # Track the last full section number so .1 can become 2.1
    current_parent = ""

    for section in sections:
        heading = section['heading']
        section_num = section["section_number"]
        body = section["body"]

        # Resolve sub-clause numbers like .1 into full numbers like 2.1
        # by prepending the last seen parent section number
        if section_num.startswith(".") and current_parent:
            #.1 becomes 2.1 if 2 is the parent
            section_num = current_parent+section_num
        #If section number does not starts with . that means the number is parent    
        elif not section_num.startswith("."):
            current_parent = section_num

        # Prepend heading to body so the chunk has context
        #So each section including section number heading and body becomes whole chunk
        if heading:
            full_text = f"{policy_name}\nSection {section_num} {heading}\n{body}"
        else:
            full_text = body

        #Creating sub chunks
        sub_chunks = _split_oversized(full_text)

        for i, chunk_text in enumerate(sub_chunks):
            chunk_id = str(uuid.uuid4())[:8]
            chunks.append({
                "chunk_id": chunk_id,
                "text": chunk_text,
                "policy_source": policy_source,
                "policy_name": policy_name,
                "page": page,
                "section_number": section_num,
                "section_heading": heading,
                "chunk_index": i,
                "total_sub_chunks": len(sub_chunks),
            })
    return chunks    


def chunk_records(records : list[dict])->list[dict]:
    """
    Chunk all cleaned records using section-aware splitting for PDFs
    and pass-through for calendar records.
    Returns a flat list of chunk dicts ready for embedding.
    """
    #Empty list to store all the chunks
    all_chunks = []

    for rec in records:
        #Checking whether the record is calender or not
        is_calender = rec.get("policy_source","").endswith(".xlsx")
        #If calender than we will run chunk_calender engine
        if is_calender:
            chunks = chunk_calender(rec)
        #Else we will chunk_pdf engine    
        else:
            chunks = chunk_pdf(rec)

        all_chunks.extend(chunks)
    return all_chunks        


'''-=-=-=-=- Testing chunk -=-===-=-=---=-=='''
if __name__ == "__main__":
    import json
    from pathlib import Path

    cleaned_record_path = Path(__file__).resolve().parents[2] / "data" / "processed" / "cleaned_all_records.json"

    with cleaned_record_path.open("r", encoding="utf-8") as f:
        cleaned_filtered = json.load(f)

    print(f"Loaded {len(cleaned_filtered)} records from {cleaned_record_path.name}")

    chunked = chunk_records(cleaned_filtered)

    print(f"Generated {len(chunked)} chunks")

    pdf_chunks = [c for c in chunked if not c["policy_source"].endswith(".xlsx")]
    cal_chunks = [c for c in chunked if c["policy_source"].endswith(".xlsx")]
    print(f"  PDF chunks: {len(pdf_chunks)}")
    print(f"  Calendar chunks: {len(cal_chunks)}")

    if pdf_chunks:
        sizes = [len(c["text"]) for c in pdf_chunks]
        print(f"  Avg PDF chunk: {sum(sizes)/len(sizes):.0f} chars")
        print(f"  Min: {min(sizes)} chars | Max: {max(sizes)} chars")

    if pdf_chunks:
        sample = pdf_chunks[5] if len(pdf_chunks) > 5 else pdf_chunks[0]
        print(f"\n--- Sample PDF chunk ---")
        print(f"  Section: {sample['section_number']} {sample['section_heading']}")
        print(f"  Text: {sample['text'][:300]}")

    if cal_chunks:
        print(f"\n--- Sample Calendar chunk ---")
        print(f"  {cal_chunks[0]['text']}")