from pathlib import Path
import json


def main():
    #Accesing the root of the project
    project_root = Path(__file__).resolve().parents[2]
    #
    input_path = project_root / "data" /"processed" / "handbook_pages.json"

    if not input_path :
        raise FileNotFoundError(f"Missing input file in {input_path}")

    with input_path.open("r",encoding = "utf-8") as f:
        pages = json.load(f)

    print("File loaded")




if __name__ == "__main__":
    main()