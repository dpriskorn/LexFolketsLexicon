import html
import json
import os
import shutil
import uuid
from typing import List

from bs4 import BeautifulSoup
from jsonlines import jsonlines
from pydantic import BaseModel

"""
Sources:
https://spraakbanken.gu.se/parole/Docs/SUC2.0-manual.pdf
https://www.diva-portal.org/smash/get/diva2:656074/FULLTEXT01.pdf
https://fileadmin.cs.lth.se/cs/Education/EDA171/Reports/2007/peter.pdf
"""
pos_mapping = {
    'abbrev': 'Q102786',    # abbreviation
    'jj': 'Q34698',  # adjective # see https://fileadmin.cs.lth.se/cs/Personal/Pierre_Nugues/ilppp/slides/ch07.pdf
    'rg': 'Q163875',  # cardinal number
    'prefix': 'Q134830', # prefix
    'article': 'Q103184', # article
    'suffix': 'Q102047', # suffix
    'hp': 'Q1050744', # relative pronoun
    'ps': 'Q1502460', # possessive pronoun

    'nn': 'Q1084',   # noun
    'av': 'Q34698',  # adjective
    'vb': 'Q24905',  # verb
    'pm': 'Q147276', # proper noun
    'ab': 'Q192420', # adverb
    'in': 'Q198061', # interjection
    'pp': 'Q168713', # preposition
    'nl': 'Q13164',  # numeral
    'pn': 'Q149667', # pronoun
    'sn': 'Q107715', # subjunction
    'kn': 'Q11376',  # conjunction
    'al': 'Q7247',   # article
    'ie': 'Q213443', # infinitive particle
    'mxc': 'Q4115189', # multiword prefix
    'sxc': 'Q59019669', # prefix
    'abh': 'Q15563735', # adverb suffix
    'avh': 'Q5307395',  # adjective suffix
    'nnh': 'Q4961746',  # noun suffix
    'nnm': 'Q724908',   # multiword noun
    'nna': 'Q1077132',  # noun, abbreviation
    'avm': 'Q729',      # multiword adjective
    'ava': 'Q25132092', # adjective, abbreviation
    'vbm': 'Q181714',   # multiword verb
    'vba': 'Q4231319',  # verb, abbreviation
    'pmm': 'Q188627',   # multiword proper noun
    'pma': 'Q24888353', # proper noun, abbreviation
    'abm': 'Q6734441',  # multiword adverb
    'aba': 'Q40482579', # adverb, abbreviation
    'pnm': 'Q10828648', # multiword pronoun
    'inm': 'Q69556741', # multiword interjection
    'ppm': 'Q30840955', # multiword preposition
    'ppa': 'Q32736580', # preposition, abbreviation
    'nlm': 'Q22069880', # multiword numeral
    'knm': 'Q69559303', # multiword conjunction
    'snm': 'Q69559308', # multiword subjunction
    'kna': 'Q69559304', # conjunction, abbreviation
    'ssm': 'Q69559307'  # multiword, clause
}


class Translatable(BaseModel):
    value: str
    translation: str = ""  # Default to empty string for translation

    @classmethod
    def from_soup(cls, soup):
        value = soup.get("value", "")
        # Decode HTML entities
        value = value.replace('&quot;', '')
        translation = soup.translation.get("value", "") if soup.translation else ""
        # Decode HTML entities
        translation = html.unescape(translation).replace('""', '"')
        return cls(value=value, translation=translation)


class Idiom(Translatable):
    pass


class Example(Translatable):
    pass


class Phonetic(BaseModel):
    ipa: str
    sound_file: str

    @property
    def mp3_file_url(self):
        """This links to the static mp3 file at Lexin"""
        return (f"http://lexin.nada.kth.se/sound/"
                f"{self.sound_file.replace('swf', 'mp3')}")


class Word(BaseModel):
    id_: str
    comment: str
    word_class: str
    lang: str
    value: str # these are hyphenated by '|'
    saldo_ids: List[str] = []  # Changed to List[str] to store multiple saldo_ids
    examples: List[Example] = []  # Default to empty list for examples
    definition: str
    idioms: List[Idiom] = []  # Default to empty list for idioms
    inflections: List[str] = []  # Default to empty list for inflections
    synonyms: List[str] = []  # Default to empty list for synonyms
    phonetic: Phonetic|None = None

    @property
    def get_lexical_category(self) -> str:
        if self.word_class in pos_mapping:
            return pos_mapping[self.word_class]
        elif not self.word_class:
            # we ignore this for now
            pass
        else:
            raise ValueError("No matching QID found for word class: {}".format(self.word_class))

    @classmethod
    def from_soup(cls, soup):
        # Extracting attributes from BeautifulSoup object
        # TODO support translations of comment and definition also
        comment = soup.get("comment", "")
        word_class = soup.get("class", "")
        lang = soup.get("lang", "")
        value = soup.get("value", "")
        saldo_ids = [see.get("value", "") for see in soup.find_all("see")]
        examples = [Example.from_soup(example) for example in soup.find_all("example")]
        definition = soup.definition.get("value", "") if soup.definition else ""
        idioms = [Idiom.from_soup(idiom) for idiom in soup.find_all("idiom")]
        inflections = [inflection.get("value", "") for inflection in soup.find_all("inflection")]
        synonyms = [synonym.get("value", "") for synonym in soup.find_all("synonym")]
        phonetic_tag = soup.find("phonetic")
        if phonetic_tag:
            phonetic = Phonetic(ipa=phonetic_tag.get("value", "") if phonetic_tag else "",
                                sound_file=phonetic_tag.get("soundFile", "")) if phonetic_tag else ""
        else:
            phonetic = None
        return cls(
            # Generate random 6 char id
            id_=str(uuid.uuid4())[:6],
            comment=comment,
            word_class=word_class,
            lang=lang,
            value=value,
            saldo_ids=saldo_ids,
            examples=examples,
            definition=definition,
            idioms=idioms,
            inflections=inflections,
            synonyms=synonyms,
            phonetic=phonetic
        )

    @property
    def word_without_vertical_line(self):
        return self.value.replace("|", "")

    @property
    def word_with_middle_dots(self):
        """This is used in Wikidata to separate sylables"""
        return self.value.replace("|", "·")

    @property
    def get_output_dict(self):
        """Populate the dict with content that makes sense for Wikidata"""
        dictionary = self.dict()
        if self.phonetic is not None and self.phonetic.sound_file:
            dictionary["phonetic"]["mp3"] = self.phonetic.mp3_file_url
        dictionary["lexical_category_qid"] = self.get_lexical_category
        dictionary["word_with_middle_dots"] = self.word_with_middle_dots
        dictionary["word_without_vertical_line"] = self.word_without_vertical_line
        # if self.value == "driva" and self.get_lexical_category == "Q24905":
        #     pprint(dictionary)
        #     exit()
        return dictionary


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
        # Create WordsContainer object from XML content
        words_container = cls.from_xml(xml_content)
        return words_container

    def count_words(self):
        return len(self.words)

    def count_idioms(self):
        idiom_count = sum(len(word.idioms) for word in self.words)
        return idiom_count

    def count_examples(self):
        count = sum(len(word.examples) for word in self.words)
        return count

    def count_words_with_lexical_category_and_sound_file(self):
        count = sum(1 for word in self.words if word.word_class != "" and word.phonetic and word.phonetic.sound_file != "")
        return count

    @property
    def count_words_with_sound_file(self):
        count = sum(1 for word in self.words if word.phonetic and word.phonetic.sound_file != "")
        return count

    def count_words_without_lexical_category(self):
        count = sum(1 for word in self.words if word.word_class == "")
        return count

    def output_to_jsonl(self, file_path: str = "data/folkets_lexicon_v2.jsonl"):
        with jsonlines.open(file_path, mode='w') as writer:
            for word in self.words:
                writer.write(word.get_output_dict)

    def output_to_individual_json_files(self, directory_path: str = "data/v2"):
        # Remove existing directory if it exists
        shutil.rmtree(directory_path, ignore_errors=True)
        # Create the directory if it doesn't exist
        os.makedirs(directory_path, exist_ok=False)

        # Iterate over each Word and write it to a separate JSON file
        for word in self.words:
            file_path = os.path.join(directory_path, f"{word.id_}.json")
            with open(file_path, mode='w', encoding='utf-8') as file:
                json.dump(word.get_output_dict, file, ensure_ascii=False, indent=4)



wc = WordsContainer.from_file("data/folkets_sv_en_public.xml")
wc.output_to_jsonl()
#wc.output_to_individual_json_files()

words_count = wc.count_words()
idioms_count = wc.count_idioms()
examples = wc.count_examples()
count_words_without_lexical_category = wc.count_words_without_lexical_category()
count_words_with_lexical_category_and_sound_file = wc.count_words_with_lexical_category_and_sound_file()

print("Number of words:", words_count)
print("Number of words with sound file:", wc.count_words_with_sound_file)
print("Number of words missing a lexical category:", count_words_without_lexical_category)
print("Number of words with a lexical category:", words_count - count_words_without_lexical_category)
print("Number of words with a lexical category and sound file:", count_words_with_lexical_category_and_sound_file)
print("Number of idioms:", idioms_count)
print("Number of examples:", examples)