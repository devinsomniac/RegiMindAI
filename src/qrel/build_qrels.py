import re
import nltk
nltk.download("punkt")
nltk.download("stopwords")

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

STOPWORDS = set(stopwords.words("english")) | {
    "the", "and", "for", "that", "this", "with", "are", "was",
    "will", "can", "not", "but", "have", "has", "from", "they",
    "been", "would", "should", "could", "which", "their", "there",
    "what", "when", "where", "who", "how", "does", "your", "you",
    "its", "all", "any", "each", "other", "than", "into", "also",
    "may", "must", "shall", "such", "being", "more", "only",
    "student", "students", "university", "cardiff", "school",
    "programme", "module", "assessment"
}

'''-=-=-=-=-===- Tokenizer function where we are using word_tokenizer from nltk -=-===-==-=-=-=-=-=-=-'''
#We will tokenize each qa pair after removing stopwords 
def tokenizer(text:str)->list[str]:
    words = word_tokenize(text.lower())
    #return tokenised word if its alphanumeric and length is greater than 2 and not present in stopword list
    return [ w for w in words if w.isalnum() and len(w)>2 and w not in STOPWORDS]


'''-=-=-=-=-= Scorring based on relevance -=-=-=-=-=---=-'''
def score_chunk(q_tokens,a_tokens,c_tokens):
    """
    Scores how relevant a single chunk is to a QA pair.
    Answer overlap is weighted 3x more than question overlap because
    the answer tells us exactly what content the correct chunk should
    contain, while the question could match many unrelated chunks.
    """
     
    #Creating a set of all chunk tokens
    chunk_set = set(c_tokens)
    #Creatinf a set of all question tokens
    question_set = set(q_tokens)
    #Creating a set of all answer tokens
    answer_set = set(a_tokens)

    #Overlap of tokens of answers and chunk tokens
    answer_overlaps = len(answer_set & chunk_set)
    #Overlap of tokens of answers and chunk tokens
    question_overlaps = len(question_set & chunk_set)

    #Now questions are always always vague and answers is lesser
    #We give priority and relevance of answer with the chunk
    #So we give more importanec i.e multiply by 3
    return (3*answer_overlaps)+question_overlaps


'''-=-=-=-=-=- Finding the relevant chunks -=-==-===--=-=-=-=-='''
def find_relevant_chunks(qa,chunks,top_k = 5):
    #Tokenising the quiestion of the qa pair
    q_tokens = tokenizer(qa['question'])
    #Tokenizing the answer of the qa pair
    a_tokens = tokenizer(qa['answer'])

    #Empty list to store score of each chunk related to question answer
    scored = []
    #Looping through each chunks
    for chunk in chunks:
        #Tpkenizing each chunk text
        c_tokens = tokenizer(chunk['text'])
        #Finding relevance score with chunks and tokens
        score = score_chunk(q_tokens,a_tokens,c_tokens)

        if score>0:
            scored.append({
                "chunk_id":    chunk["chunk_id"],
                "policy_name": chunk.get("policy_name", ""),
                "page":        chunk.get("page"),
                "section":     chunk.get("section_heading", ""),
                "score":       score,
                "preview":     chunk["text"][:150].replace("\n", " ")
            })
    #Sorting score higher to lower
    scored.sort(key=lambda x: x["score"], reverse=True)
    #Returning top k high score
    return scored[:top_k]






def build_qrels(qa_pairs,chunks):
    """
    For each QA pair, finds the top 5 most relevant chunks
    and builds the qrels dict + review CSV rows.
    
    Auto-marks top 2 candidates as relevant (draft).
    You MUST review the output CSV and fix any wrong mappings.
    
    Args:
        qa_pairs: list of QA dicts (from qa_pairs.json)
        chunks: list of chunk dicts (from chunks.json)
    
    Returns:
        qrels: dict {question_id: {chunk_id: 0 or 1}}
        review_rows: list of dicts for the review CSV
    """



    '''
    #Empty object to store each object like
    qrels = {
    "q1": {
        "c1": 1,
        "c3": 1,
        "c2": 0
        },
    "q2": {
        "c5": 1,
        "c8": 0
        }
    }
    '''
    qrels = {}
    '''
    empty list To store reviews and score of relevance like
    review_rows = [
    {
        "question_id": "q1",
        "chunk_id": "c1",
        "score": 8,
        "relevant": 1
    },
    {
        "question_id": "q1",
        "chunk_id": "c2",
        "score": 2,
        "relevant": 0
    }
]
    '''
    review_rows = []

    for i,qa in enumerate(qa_pairs):
        #Top 5 relevant chunk with score
        candidates = find_relevant_chunks(qa,chunks,top_k = 5)
        #Creating a new object for each qa
        qrels[qa['question_id']] = {}

        #Since in candidates all chunks are sorted descending order so 
        #rank = position
        for rank, candidate in enumerate(candidates):
            # Auto-mark top 2 as relevant, rest as not relevant
            relevance = 1 if rank < 2 else 0

            #Entering qrel data
            qrels[qa['question_id']][candidate["chunk_id"]] = relevance
            review_rows.append({
                "question_id":    qa["question_id"],
                "question":       qa["question"][:100],
                "answer_preview": qa["answer"][:80],
                "cluster":        qa["cluster"],
                "rank":           rank + 1,
                "chunk_id":       candidate["chunk_id"],
                "policy_name":    candidate["policy_name"],
                "page":           candidate["page"],
                "section":        candidate["section"],
                "match_score":    candidate["score"],
                "chunk_preview":  candidate["preview"][:120],
                "relevant":       relevance   
            })
        #Progress bar of each qa pairs    
        if (i + 1) % 20 == 0:
            print(f"  Mapped {i+1}/{len(qa_pairs)} questions...")
    
    return qrels,review_rows            


