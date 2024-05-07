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
from typing import List

from bs4 import BeautifulSoup
from pydantic import BaseModel
from tqdm import tqdm
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
    value: str # these are hyphenated by '|'
    saldo_id: str
    examples: List[Example] = []  # Default to empty list for examples
    definition: str
    idioms: List[Idiom] = []  # Default to empty list for idioms
    inflections: List[str] = []  # Default to empty list for inflections
    synonyms: List[str] = []  # Default to empty list for synonyms

    @property
    def get_lexical_category(self):
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
        saldo_id = soup.see.get("value", "") if soup.see else ""
        examples = [Example.from_soup(example, value) for example in soup.find_all("example")]
        definition = soup.definition.get("value", "") if soup.definition else ""
        idioms = [Idiom.from_soup(idiom, value) for idiom in soup.find_all("idiom")]
        inflections = [inflection.get("value", "") for inflection in soup.find_all("inflection")]
        synonyms = [synonym.get("value", "") for synonym in soup.find_all("synonym")]
        return cls(
            comment=comment,
            word_class=word_class,
            lang=lang,
            value=value,
            saldo_id=saldo_id,
            examples=examples,
            definition=definition,
            idioms=idioms,
            inflections=inflections,
            synonyms=synonyms
        )

    @property
    def word_without_vertical_line(self):
        return self.value.replace("|", "")

    @property
    def word_with_middle_dots(self):
        """This is used in Wikidata to separate sylables"""
        return self.value.replace("|", "·")


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
                ['Type', 'Value', 'Value with middle dots', 'Lexical Category', 'Word Class', 'Language', 'Saldo ID',
                 'Definition', 'Examples', 'Idioms',
                 'Inflections', 'Synonyms', 'Comment'])
            # Write rows for each word
            for word in self.words:
                examples_joined = "|".join([example.value for example in word.examples])
                idioms_joined = "|".join([idiom.value for idiom in word.idioms])
                inflections_joined = "|".join([inflection for inflection in word.inflections])
                synonyms_joined = "|".join([synonym for synonym in word.synonyms])
                lexical_category = word.get_lexical_category
                writer.writerow(
                    ['Word', word.word_without_vertical_line, word.word_with_middle_dots, lexical_category,
                     word.word_class, word.lang, word.saldo_id,
                     word.definition, examples_joined, idioms_joined, inflections_joined, synonyms_joined,
                     word.comment])

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

    def count_words_without_lexical_category(self):
        count = sum(1 for word in self.words if word.word_class == "")
        return count


wc = WordsContainer.from_file("folkets_sv_en_public.xml")
wc.words_to_csv()
wc.idioms_to_csv()
wc.examples_to_csv()
words_count = wc.count_words()
idioms_count = wc.count_idioms()
examples = wc.count_examples()
count_words_without_lexical_category = wc.count_words_without_lexical_category()

print("Number of words:", words_count)
print("Number of words missing a lexical category:", count_words_without_lexical_category)
print("Number of idioms:", idioms_count)
print("Number of examples:", examples)