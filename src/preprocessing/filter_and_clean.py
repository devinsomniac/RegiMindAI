from __future__ import annotations
import re
from copy import deepcopy
import unicodedata
'''configurable thresholds'''
# drop pages with fewer meaningful chars
MIN_CONTENT_CHARS = 80       
# if ≥45% of lines look like TOC - skip page   
TOC_LINE_RATIO_THRESHOLD = 0.45
#Need atleast 4 lines to judge TOC
TOC_MIN_LINES = 4  


'''-=-=-=-=-=-=-=-=-=-=-=-Core patterns-=-=-=-=-=-=-=-=-='''

# Repeated header/footer strings found across the handbook pages
_HEADERS_PATTERN : list[re.Pattern] = [
    #using (?i) for case-insensetive matching
    #using \s+ for one or more white spaces
    #using (?:for\s+) for non-capturing i.e it wont saved for later used and using ? for making it optional
    #Uisng \s* to match 0 or more white scace
    re.compile( r"(?i)student\s+handbook\s+(?:for\s+)?2025\s*/?\s*26", re.IGNORECASE),
    re.compile(r"(?i)^computer\s+science\s+and\s+informatics\s*$", re.MULTILINE),
    # Cardiff University logo alt-text sometimes extracted
    re.compile(r"(?i)^CARDIFF\s*UNIVERSITY\s*$", re.MULTILINE),
    re.compile(r"(?i)^PRIFYSGOL\s*$", re.MULTILINE),
    re.compile(r"(?i)^C\s*A\s*E?\s*R\s*D\s*Y\s*[DBb]\s*$", re.MULTILINE),

]

#We need to remove 
_SINGLE_PAGE_NUMBER = re.compile(r"^\s*(?:page\s*)?\d{1,3}\s*$",re.IGNORECASE | re.MULTILINE)

# TOC-style line:  "SOME HEADING    12" or "Some heading............12"
_TOC_LINE = re.compile(
    # dots leader
    #Example - INTRODUCTION ............................. 5
    r"^.{3,80}\s*\.{2,}\s*\d{1,3}\s*$"   
    r"|"
    # wide whitespace gap before number
    #Examplem - Academic Regulations                     19
    r"^.{3,80}\s{3,}\d{1,3}\s*$",         
    re.MULTILINE,
)


# Hyphenation at line break  e.g. "pro-\ngramme" → "programme"
_HYPHEN_LINEBREAK = re.compile(r"(\w)-\s*\n\s*(\w)")

# 3 or more new lines
_EXCESS_NEWLINES = re.compile(r"\n{3,}")

# Collapse runs of spaces (not newlines)
_EXCESS_SPACES = re.compile(r"[^\S\n]{2,}")


#Normalizing all kind of bullets
_BULLET_NORMALIZE = re.compile(r"(?:^|\n)\s*[•●■◦▪‣]\s*",re.MULTILINE)

# PDF ligatures to normal chars
# After ingestion, PDFs sometimes store "fi" "fl" etc as single weird
# Unicode characters that look normal but break search matching.
# Curly quotes, em dashes, and non-breaking spaces also cause issues.
# This map converts all of them to plain ASCII equivalents.
_LIGATURE_MAP = {
    "\ufb01": "fi",
    "\ufb02": "fl",
    "\ufb03": "ffi",
    "\ufb04": "ffl",
    "\u2019": "'",
    "\u2018": "'",
    "\u201c": '"',
    "\u201d": '"',
    "\u2013": "-",
    "\u2014": "-",
    "\u2026": "...",
    "\u00a0": " ",
}
_LIGATURE_RE = re.compile("|".join(re.escape(k) for k in _LIGATURE_MAP))


''' -=-=-=-=-=-=-=-=-=-=- Our Helper functions -=-=-=-=-=-=-=-=-=-=-=-'''

def _replace_ligatures(text: str) -> str:
    #Finding any ligature character in text using the compiled regex pattern
    #When found, the lambda looks it up in _LIGATURE_MAP and swaps it with the normal version
    return _LIGATURE_RE.sub(lambda m: _LIGATURE_MAP[m.group()], text)

def _normalise_unicode(text: str) -> str:
    #First normalizing unicode so characters like é are stored consistently (not as separate pieces)
    text = unicodedata.normalize("NFC", text)
    #Then replacing all the ligature characters with their plain ASCII versions
    text = _replace_ligatures(text)
    return text

def _is_toc_page(text:str)->bool:
    '''Return True if the page looks like a table-of-contents '''
    #Making a list of all lines in the given text
    lines = [ln for ln in text.split("\n") if ln.strip()]
    #Checking the number of lines in the text - because if less then 4 lines - is not TOC
    if len(lines)< TOC_MIN_LINES:
        return False
    #Number of all the lines, which matches _TOC_LINE regex
    toc_hits = sum(1 for ln in lines if _TOC_LINE.search(ln))
    #Returning True if the % of match is more than 45% else false 
    return (toc_hits/len(lines))>= TOC_LINE_RATIO_THRESHOLD


def _is_content_header(text:str)->bool:
    """Detect pages that are purely a 'Contents:' listing."""
    #Removing any white space in start or ending
    stripped_text = text.strip().lower()
    #Checking whether there is word "content"
    if stripped_text.startswith('contents'):
        lines = [ln.strip() for ln in text.split("\n") if ln.strip()]
        numbered = sum(1 for ln in lines if re.match(r"^\d",ln))
        return numbered / max(len(lines), 1) > 0.3
    return False

def _is_number_heavy_page(text: str) -> bool:
    """Detect TOC pages where section numbers and page numbers are on separate lines."""
    lines = [ln.strip() for ln in text.split("\n") if ln.strip()]
    if len(lines) < TOC_MIN_LINES:
        return False
    # Count lines that are just a number (page refs) or section number like 5.1, 14.7
    number_lines = sum(1 for ln in lines if re.match(r"^\d{1,3}(\.\d{1,2})?$", ln))
    # If more than 40% of lines are just numbers, it's a TOC
    return (number_lines / len(lines)) >= 0.45

def _stripping_header_footers(text:str)->str:
    '''Function to detect header footer and page numbers and remove them'''
    #If any pattern found in text then substitute with ""
    for pattern in _HEADERS_PATTERN:
        text = pattern.sub("",text)
    #Removing the page number
    text = _SINGLE_PAGE_NUMBER.sub("",text)
    return text

def _fix_hyphenation(text: str) -> str:
    """Re-joining words broken across lines by a hyphen."""
    return _HYPHEN_LINEBREAK.sub(r"\1\2", text)

def _normalise_whitespace(text: str) -> str:
    """Collapse excessive whitespace while preserving paragraph breaks."""
    #Substituting excess whitespacee with single space
    text = _EXCESS_SPACES.sub(" ", text)
    #Substituting more than 3 new line sinto 2 new lines
    text = _EXCESS_NEWLINES.sub("\n\n", text)
    return text.strip()

def _normalise_bullets(text: str) -> str:
    """Normalizing bullet characters to a simple dash for consistency."""
    return _BULLET_NORMALIZE.sub("\n- ", text)

def _strip_emails_urls_noise(text: str) -> str:
    """
    Removing 'mailto:' prefixes that appear as PDF artefacts.
    Keeping the email address itself — useful context for RAG.
    """
    text = re.sub(r"mailto:", "", text)
    return text

def _is_low_content(text: str) -> bool:
    """Return True if the cleaned text has too little meaningful content."""
    # Strip whitespace and punctuation to measure real content
    content = re.sub(r"[\s\-_=.,:;()|/\\]", "", text)
    return len(content) < MIN_CONTENT_CHARS



def _clean_text(text:str)->str:
    """
    Applying the full cleaning pipeline to a single text string.
    Returns the cleaned text and may be empty if the page was mostly noise.
    """
    text = _normalise_unicode(text)
    text = _stripping_header_footers(text)
    text = _fix_hyphenation(text)
    text = _strip_emails_urls_noise(text)
    text = _normalise_bullets(text)
    text = _normalise_whitespace(text)
    return text

''' -=-=-=-=-=-=-=-=- Main core driver function -=-=-=-=-=-=-=-=--='''
def clean_records(records : list[dict])->list[dict]:
    """
    Filter and clean a list of ingested records.
    Each record is expected to have at least a "text" key.
    Records that are TOC pages or have insufficient content after
    cleaning are dropped entirely.
    Returns a new list as the originals are not mutated.
    """

    #Empty list of dict to store new data
    cleaned : list[dict] = []

    #Looping through every page 
    for rec in records:
        #Getting the content of text key if exist or else default "" value
        text = rec.get("text","")

        '''skipping toc / contents page'''
        if _is_toc_page(text) or _is_content_header(text) or _is_number_heavy_page(text):
            print(f"  DROPPED (TOC): {rec.get('policy_source','?')} page {rec.get('page','?')}")
            continue

        '''cleaning the text'''
        text = _clean_text(text)

        '''skipping page if content is less than minimum threshhold'''
        #We cant loose the calender as it is merged with all json
        is_calendar = rec.get("policy_source", "").endswith(".xlsx")
        if not is_calendar and _is_low_content(text):
            print(f"  DROPPED (low content): {rec.get('policy_source','?')} page {rec.get('page','?')}")
            continue

        #Making exact copy of original record structure    
        new_rec = deepcopy(rec)
        #adding new text in the new record structure
        new_rec['text'] = text
        #Appending in the new record list
        cleaned.append(new_rec)
    return cleaned

'''-=-=-=-=-=-= Testing the cleaning -=-=-=-=-=-=-'''

if __name__ == '__main__':
    import json
    from pathlib import Path

    #Original Record path
    sample_path = Path(__file__).resolve().parents[2] /"data"/"processed"/'all_records.json'
    if not sample_path.exists():
        raise FileNotFoundError(f"No file found in {sample_path}")
    
    with sample_path.open("r",encoding="utf-8") as f:
        records = json.load(f)

    print(f"Loaded {len(records)} raw records")
    cleaned = clean_records(records)
    print(f"After cleaning: {len(cleaned)} records remain")





