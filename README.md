# LexFolketsLexicon
This is a project to analyze and add identifiers for words 
from Folkets Lexicon to Wikidata.
A unique UUID-based identifier have been added to facilitate linking with Wikidata. 

## API
An API has been added for easy lookup. The goal is to upload it to Toolforge to facilitate
integration of the data into Wikidata via a property since 
this might be a good freely licensed source for Swedish and English lexemes to use.

## Versioning
The output jsonl is versioned v1, v2, etc.
The latest number is always consistent with the model in the code, 
old versions are kept for backwards compatibility.
For each new version, completely random ids are generated.

## Statistics
Number of words: 39407
Number of words with sound file: 21947
Number of words missing a lexical category: 7441
Number of words with a lexical category: 31966
Number of words with a lexical category and sound file: 21280
Number of idioms: 1944
Number of examples: 12574

## License
The source code is licensed under GPLv3+
The data directory files are CC-BY-SA 2.5

## Source
Original source is http://folkets-lexikon.csc.kth.se/folkets/
The data was downloaded during may 2023.
No updates to the dump seem to happen over time since the project is not maintained anymore.

## Development
Run the api:
`$ uvicorn api:app --reload`

Build pack:

Make sure pack-cli-bin and docker is installed from AUR:
```
$ pack build --builder tools-harbor.wmcloud.org/toolforge/heroku-builder:22 myimage
$ docker run -e PORT=8000 -p 8000:8000 --rm --entrypoint web myimage
# navigate to http://127.0.0.1:8000 to check that it works
```