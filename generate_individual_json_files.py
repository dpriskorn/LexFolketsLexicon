import os
import json
import shutil


def output_to_individual_json_files(jsonl_file_path: str, directory_path: str = "data/v2"):
    # Remove existing directory if it exists
    if os.path.exists(directory_path):
        shutil.rmtree(directory_path, ignore_errors=True)

    # Create the directory
    os.makedirs(directory_path, exist_ok=False)

    # Read from the JSONL file and output individual JSON files
    with open(jsonl_file_path, 'r', encoding='utf-8') as f:
        for line in f:
            data = json.loads(line)
            word_id = data.get("id_")
            if word_id:
                file_path = os.path.join(directory_path, f"{word_id}.json")
                with open(file_path, 'w', encoding='utf-8') as json_file:
                    json.dump(data, json_file, ensure_ascii=False)
            else:
                print("Invalid data format: Missing 'id' field.")


# Example usage:
output_to_individual_json_files("data/folkets_lexicon_v2.jsonl", "data/v2")
