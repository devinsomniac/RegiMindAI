import pandas as pd
import json
from pathlib import Path

def convert_gold_qa_xlsx_to_json():
    '''Converting the qa xlsx file into json'''
    #Our project root
    PROJECT_ROOT = Path(__file__).resolve().parents[2]
    #The input path of the Gold dataset QA
    INPUT_PATH = PROJECT_ROOT / "data" / "qa" / "RegimindQA_GoldDataset.xlsx"
    #The converted json output path
    OUTPUT_PATH = PROJECT_ROOT / "data" / "qa" / "qa_pairs.json"
    print(f"Loaded xlsx file from: {INPUT_PATH}")

    #Loading the xlsx from input path
    df = pd.read_excel(INPUT_PATH)

    #Empty list to store qa object
    qa_pairs = []

    #Iterating through every row and saving into json template
    for _,row in df.iterrows():
        try:
            qa = {
                "question_id": f"q{int(row['id']):03d}",
                "question": str(row["question"]).strip(),
                "answer": str(row["answer"]).strip(),
                "source": str(row.get("source", "")).strip(),
                "question_type": str(row.get("question_type", "")).strip(),
                "difficulty": str(row.get("difficulty", "")).strip(),
                "cluster": str(row.get("cluster", "")).strip()
            }

            qa_pairs.append(qa)
        except Exception as e:
            
            print(f" Skipping row due to error: {e}")

    #Saving the final json into the output file        
    with OUTPUT_PATH.open("w",encoding="utf-8") as f:
        json.dump(qa_pairs,f,indent=2,ensure_ascii=False)

    #Logging 
    print("Conversion Complete!")
    print(f"Total QA pairs: {len(qa_pairs)}")
    print(f"Saved to: {OUTPUT_PATH}")
if __name__ == "__main__":
    convert_gold_qa_xlsx_to_json()