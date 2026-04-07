import json
from pathlib import Path

from src.preprocessing.filter_and_clean import clean_records
from src.preprocessing.chunker import chunk_records

def run_preprocessing(processed_uncleaned:Path,processed_dir:Path)->None:
    """
    Full preprocessing pipeline: clean -> chunk -> save.
 
    Args:
        input_path : Path to all_records.json from ingestion
        output_dir : Directory to save cleaned_records.json and chunks.json
    """


    '''-=-=-=-=-=-===-=-=-=-=- filter and cleaning service -=-=--=-=-=-=-=-===-=-=--=-'''

    #Sanity check , whether processed uncleaned file exist
    if not processed_uncleaned.exists():
        raise FileNotFoundError(f"No file found at {processed_uncleaned}.")

    #Opening the json file
    with processed_uncleaned.open("r",encoding="utf-8") as f:
        raw_uncleaned_records = json.load(f)
    print(f"Loaded {len(raw_uncleaned_records)} records from {processed_uncleaned}")

    #Feeding raw data to the the filter and cleaning engine
    cleaned = clean_records(raw_uncleaned_records)
    print(f"After cleaning: {len(cleaned)} records remain ")

    #Making the output path to save the cleaned records if not exist
    processed_dir.mkdir(parents=True,exist_ok=True)
    #Making the output file if not exist
    cleaned_path = processed_dir / "cleaned_all_records.json"
    #Opening the file and writting the cleaned records
    with cleaned_path.open("w",encoding="utf-8") as f:
        #Saving the new json file
        json.dump(cleaned,f,ensure_ascii=False,indent=2)
    print(f"Saved cleaned records to {cleaned_path}")


    '''-=-=-=-=-=-===-=-=-=-=- chunking service -=-=--=-=-=-=-=-===-=-=--=-'''
    chunks = chunk_records(cleaned)
    print(f"Generated {len(chunks)} chunks")

    # Saving chunks
    chunks_path = processed_dir / "chunks.json"
    with chunks_path.open("w", encoding="utf-8") as f:
        json.dump(chunks, f, ensure_ascii=False, indent=2)

    print(f"Saved chunks to {chunks_path}")
    

def main():
    #Accessing the project root
    project_root = Path(__file__).resolve().parents[2]
    #Acessing processed json file - all uncleaned records
    processed_uncleaned = project_root / "data" / "processed" / "all_records.json"
    #Processed_cleaned_chunked_dir
    processed_dir =  project_root / "data" / "processed"
    #Pre processing engine
    run_preprocessing(processed_uncleaned,processed_dir)


if __name__ == "__main__":
    main()