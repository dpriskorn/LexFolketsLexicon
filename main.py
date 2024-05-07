# pseudo code
# the data is in a big XML file
# <word class="pp" comment="endast vid sifferuttryck" lang="sv" value="à"><translation comment="used only with numerical expressions" value="at" />
# <phonetic soundFile="à.swf" value="a" />
# <see type="saldo" value="à||à..1||à..pp.1" />
# <example value="två koppar kaffe à 8 kronor (styck)"><translation value="two cups of coffee at 8 kronor (each)" />
# </example>
# <definition value="till ett pris av"><translation value="at a price of" />
# </definition>
# lets use beautifulsoup and pydantic to extract what we want
import csv
import html
from typing import List, Optional
from pydantic import BaseModel
from bs4 import BeautifulSoup
from tqdm import tqdm


class Translatable(BaseModel):
    value: str
    word_value: str  # where this was found
    translation: str = ""  # Default to empty string for translation

    @classmethod
    def from_soup(cls, soup, word_value):
        value = soup.get("value", "")
        # Decode HTML entities
        value = value.replace('&quot;', '')
        translation = soup.translation.get("value", "") if soup.translation else ""
        # Decode HTML entities
        translation = html.unescape(translation).replace('""', '"')
        return cls(value=value, word_value=word_value, translation=translation)


class Idiom(Translatable):
    pass


class Example(Translatable):
    pass


class Word(BaseModel):
    comment: str
    word_class: str
    lang: str
    value: str
    saldo_id: str
    examples: List[Example] = []  # Default to empty list for idioms
    definition: str
    idioms: List[Idiom] = []  # Default to empty list for idioms

    @classmethod
    def from_soup(cls, soup):
        # Extracting attributes from BeautifulSoup object
        # TODO support translations of comment and definition also
        comment = soup.get("comment", "")
        word_class = soup.get("class", "")
        lang = soup.get("lang", "")
        value = soup.get("value", "")
        saldo_id = soup.see.get("value", "") if soup.see else ""
        examples = [Example.from_soup(example, value) for example in soup.find_all("example")]
        definition = soup.definition.get("value", "") if soup.definition else ""
        idioms = [Idiom.from_soup(idiom, value) for idiom in soup.find_all("idiom")]
        return cls(
            comment=comment,
            word_class=word_class,
            lang=lang,
            value=value,
            saldo_id=saldo_id,
            examples=examples,
            definition=definition,
            idioms=idioms
        )


class WordsContainer(BaseModel):
    words: List[Word]

    @classmethod
    def from_xml(cls, xml_content):
        # Parse the XML content using BeautifulSoup
        soup = BeautifulSoup(xml_content, "xml")
        # Extract all word instances from the XML
        word_instances = soup.find_all("word")
        # Create Word objects for each instance
        words = [Word.from_soup(word_instance) for word_instance in word_instances]
        return cls(words=words)

    @classmethod
    def from_file(cls, file_path):
        # Open the XML file and read its contents
        with open(file_path, "r") as file:
            xml_content = file.read()
        # Get the total number of lines in the file
        total_lines = sum(1 for line in open(file_path))
        # Create a progress bar
        with tqdm(total=total_lines, desc="Reading file") as pbar:
            # Create WordsContainer object from XML content
            words_container = cls.from_xml(xml_content)
            pbar.update(total_lines)  # Update progress bar to completion
        return words_container


    def words_to_csv(self, file_path: str = "words.csv"):
        with open(file_path, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            # Write header row for words
            writer.writerow(
                ['Type', 'Value', 'Comment', 'Word Class', 'Language', 'Saldo ID', 'Definition'])
            # Write rows for each word
            for word in self.words:
                writer.writerow(
                    ['Word', word.value, word.comment, word.word_class, word.lang, word.saldo_id,
                     word.definition])

    def idioms_to_csv(self, file_path: str = "idioms.csv"):
        with open(file_path, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            # Write header row for idioms
            writer.writerow(['Type', 'Value', 'Word Value'])
            # Write rows for each idiom
            for word in self.words:
                for idiom in word.idioms:
                    writer.writerow(['Idiom', idiom.value, idiom.word_value])

    def examples_to_csv(self, file_path: str = "examples.csv"):
        with open(file_path, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            # Write header row for idioms
            writer.writerow(['Type', 'Value', 'Word Value'])
            # Write rows for each idiom
            for word in self.words:
                for example in word.examples:
                    writer.writerow(['Example', example.value, example.word_value])
    def count_words(self):
        return len(self.words)

    def count_idioms(self):
        idiom_count = sum(len(word.idioms) for word in self.words)
        return idiom_count

    def count_examples(self):
        count = sum(len(word.examples) for word in self.words)
        return count

wc = WordsContainer.from_file("folkets_sv_en_public.xml")
wc.words_to_csv()
wc.idioms_to_csv()
wc.examples_to_csv()
words_count = wc.count_words()
idioms_count = wc.count_idioms()
examples = wc.count_examples()

print("Number of words:", words_count)
print("Number of idioms:", idioms_count)
print("Number of examples:", examples)