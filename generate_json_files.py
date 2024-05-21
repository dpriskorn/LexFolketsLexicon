import os
import shutil
import json
from typing import List

from pydantic import BaseModel

from main import Word


class LexiconProcessor(BaseModel):
    jsonl_path: str = "data/folkets_lexicon_v2.jsonl"
    words: List[Word] = []

    def _load_words(self):
        with open(self.jsonl_path, mode="r", encoding="utf-8") as file:
            for line in file:
                word = json.loads(line.strip())
                self.words.append(word)

    def output_to_individual_json_files(self, directory_path: str = "data/v2"):
        self._load_words()
        # Remove existing directory if it exists
        shutil.rmtree(directory_path, ignore_errors=True)
        # Create the directory if it doesn't exist
        os.makedirs(directory_path, exist_ok=False)

        # Create subdirectories for words, idioms, and examples
        word_dir = os.path.join(directory_path, "word")
        idiom_dir = os.path.join(directory_path, "idiom")
        example_dir = os.path.join(directory_path, "example")
        os.makedirs(word_dir, exist_ok=False)
        os.makedirs(idiom_dir, exist_ok=False)
        os.makedirs(example_dir, exist_ok=False)

        # Iterate over each Word and write it to a separate JSON file
        for word in self.words:
            # Save word to JSON file
            word_file_path = os.path.join(word_dir, f"{word['id_']}.json")
            with open(word_file_path, mode="w", encoding="utf-8") as file:
                json.dump(word, file, ensure_ascii=False)

            # Save idioms to JSON files
            for idiom in word.get('idioms', []):
                idiom_file_path = os.path.join(idiom_dir, f"{idiom['id_']}.json")
                with open(idiom_file_path, mode="w", encoding="utf-8") as file:
                    json.dump(idiom, file, ensure_ascii=False)

            # Save examples to JSON files
            for example in word.get('examples', []):
                example_file_path = os.path.join(example_dir, f"{example['id_']}.json")
                with open(example_file_path, mode="w", encoding="utf-8") as file:
                    json.dump(example, file, ensure_ascii=False)

# Example usage:
processor = LexiconProcessor()
processor.output_to_individual_json_files()
