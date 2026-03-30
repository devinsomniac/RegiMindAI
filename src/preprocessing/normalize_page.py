# from pathlib import Path
# import json
# from utils.normalize import normalize_text

# def main():
#     #Accessing the project root
#     project_root = Path(__file__).resolve().parents[2]
#     #Accesing the data path
#     data_path = project_root / "data" / "processed" / "handbook_pages.json"

#     '''Loading the json file'''
#     #Checking whether file exist
#     if not data_path.exists():
#         raise FileNotFoundError(f"No data found in {data_path}")

#     #Loading the json/ raw data pages
#     with data_path.open("r",encoding="utf-8") as f:
#         pages = json.load(f)

#     if pages:
#         print(f"Loaded {len(pages)} from {data_path}")
#     else:
#         print("No data found")        


#     '''Normalizing the text like removing spaces,
#       new lines ,changing bullet types'''
#     for p in pages:
#         p['text'] = normalize_text(p['text'])
#     print("Normalization has been done")

#     output_path_normalize = project_root / "data" / "processed" / "handbook_pages_normalize.json"
#     with output_path_normalize.open("w",encoding="utf-8") as f:
#         json.dump(pages,f,ensure_ascii=False,indent=2)
#         print(f"Saved cleaned pages to {output_path_normalize}")


# if __name__ == "__main__":
#     main()


import json
from pathlib import Path

def main():
    #Accessing Project root
    project_root = Path(__file__).resolve().parents[2]
    #Now accessing extracted text from pdf - handbook_pages
if __name__ == "__main__":
    main()