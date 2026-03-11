import re

# For deetcting URLs
RE_URL = re.compile(r"https?://\S+|www\.\S+")
# For detecting space or tabs more than 2
RE_MULTI_SPACES = re.compile(r"[ \t]{2,}")
#For detecting more than 3 newlines 
RE_MULTI_LINES = re.compile(r"\n{3,}")
# Split bullet markers that appear alone on a line
RE_DOT_NUMBER_ONLY = re.compile(r"^\.\d+\s*$")      
RE_LETTER_ONLY = re.compile(r"^[a-zA-Z]\)\s*$")     
RE_UNICODE_BULLET_ONLY = re.compile(r"^[•●▪]\s*$")  
# Bullet markers that appear with content on same line
RE_LETTER_BULLET = re.compile(r"^[a-zA-Z]\)\s+")    
RE_NUMBER_BULLET = re.compile(r"^\d+\.\s+")         
RE_UNICODE_BULLET = re.compile(r"^[•●▪]\s*")        
# Section / heading detection
RE_SECTION_HEADING = re.compile(r"^\d+(\.\d+)*\.?\s+[A-Z]")
RE_SECTION_ONLY = re.compile(r"^\d+(\.\d+)*\.?\s*$")
# Page-number-only lines
RE_JUST_NUMBER = re.compile(r"^\d{1,4}\s*$")


def normalize_text(text: str) -> str:
    # Remove carriage returns
    text = text.replace("\r", "")
    # Removes URLs
    text = RE_URL.sub("", text)
    #Getting all lines by splitting the text
    lines = text.splitlines()
    new_lines = []

    for ln in lines:
        #being safe for whitespace in start and end of line
        ln = ln.strip()
        # Keeping paragraph spacing
        if not ln:
            new_lines.append("")
            continue
        # Removing page numbers like "1", "12", "135"
        if RE_JUST_NUMBER.match(ln):
            continue
        # Preserve section-only lines like "2." or "4.3.2"
        if RE_SECTION_ONLY.match(ln):
            new_lines.append(ln)
            continue

        # Preserve section headings like "2. Definition..." or "4.1 The School Board"
        if RE_SECTION_HEADING.match(ln):
            new_lines.append(ln)
            continue

        # Convert marker-only bullet lines into a plain "-"
        if RE_DOT_NUMBER_ONLY.match(ln):
            new_lines.append("-")
            continue

        if RE_LETTER_ONLY.match(ln):
            new_lines.append("-")
            continue

        if RE_UNICODE_BULLET_ONLY.match(ln):
            new_lines.append("-")
            continue

        # Convert same-line bullets into standard "- "
        ln = RE_LETTER_BULLET.sub("- ", ln)
        ln = RE_NUMBER_BULLET.sub("- ", ln)
        ln = RE_UNICODE_BULLET.sub("- ", ln)

        new_lines.append(ln)

    # Merging lonely '-' with next content if it went to next line or beyond while extracting
    merged_lines = []
    i = 0

    #Checking every lines one by one
    while i < len(new_lines):
        #Current line
        current = new_lines[i].strip()
        #Whether current line is '-'
        if current == "-":
            #We will check for next to current(-) for content
            j = i + 1
            # if next of - is blank than go to next to next
            while j < len(new_lines) and not new_lines[j].strip():
                j += 1
            #Now here if we get contebt of - we merge here
            if j < len(new_lines):
                merged_lines.append(f"- {new_lines[j].strip()}")
                i = j + 1
                continue

        merged_lines.append(current)
        i += 1

    text = "\n".join(merged_lines)

    # Clean repeated spaces
    text = RE_MULTI_SPACES.sub(" ", text)

    # Clean repeated newlines
    text = RE_MULTI_LINES.sub("\n\n", text)

    return text.strip()