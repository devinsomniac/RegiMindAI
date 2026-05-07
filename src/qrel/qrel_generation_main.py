import json
import pandas as pd
from pathlib import Path
from src.qrel.convert_qa_to_json import convert_gold_qa_xlsx_to_json
from src.qrel.build_qrels import build_qrels


def main():
    """
    Orchestrator for the qrel(Query Relevance Judgements) generation pipeline.
    Here we will : 
    - Convert the gold QA xlsx into qa_pairs.json
    - Load qa_pairs.json and chunks.json
    - Build draft qrels (keyword-overlap mapping)
    - Save qrels_DRAFT.json and qrels_review.csv
    
    After running this, open qrels_review.csv in Excel/Sheets,
    verify the 'relevant' column, then run finalize_qrels.py.
    """
    #Accessing the project root
    PROJECT_ROOT = Path(__file__).resolve().parents[2]

    print("=-=-=-=-=-=-=- Converting to json -=-=-=-=-=-=-")
    #Converting the xlsx file of gold qa dataset into json
    convert_gold_qa_xlsx_to_json()
    print("=-=-=-=-=-=-=- Converting to json -=-=-=-=-=-=-")

    #Now we will load the converted json file for qrel generation
    QA_PATH = PROJECT_ROOT  / "data" / "qa" / "qa_pairs.json"
    #Loading our processed chunk path
    CHUNK_PATH = PROJECT_ROOT / "data" / "processed" / "chunks.json"

    #Opening and reading qa pair file
    print("Loading the Question and answer poirs : ")
    with QA_PATH.open("r",encoding="utf-8") as f:
        qa_pairs = json.load(f)
    print(f"  {len(qa_pairs)} QA pairs loaded")

    #Opening and reading chunks file
    print("Loading the Question and answer poirs : ")
    with CHUNK_PATH.open("r",encoding="utf-8") as f:
        chunks = json.load(f)
    print(f"  {len(chunks)} chunks loaded")     


    #Generated qrels and also review rows from qrels for manual validation
    qrels, review_rows = build_qrels(qa_pairs,chunks)

    #Creating qrels output folder if it doesn't exist
    QREL_OUTPUT_DIR = PROJECT_ROOT / "data" / "qrels"
    QREL_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    
    #Saving draft qrels in the qrel_DRAFT.json file
    QREL_OUTPUT_PATH = PROJECT_ROOT / QREL_OUTPUT_DIR / "qrels_DRAFT.json"
    with QREL_OUTPUT_PATH.open("w",encoding="utf-8") as f:
        json.dump(qrels,f,indent=2)
    print(f"Saved: {QREL_OUTPUT_PATH}")    

    #Saving csv of review rows as qrels_review.csv
    QREL_REVIEW_OUTPUT_PATH = PROJECT_ROOT / QREL_OUTPUT_DIR / "qrels_review.csv"
    pd.DataFrame(review_rows).to_csv(QREL_REVIEW_OUTPUT_PATH,index=False)
    print(f"Saved: {QREL_REVIEW_OUTPUT_PATH}")


if __name__ == "__main__":
    main()