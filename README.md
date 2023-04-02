# Processing xDD Data

Requirements:

```bash
$ pip install spacy==3.5.1
$ python -m spacy download en_core_web_sm
```

Code for preprocessing the files in the three topics: biomedical, geoarchive and molecular_physics. Only useful if you have access to the xDD data.

Each topic is associated with a topic directory and each of those has the same structure:

| directory     | description                                                       |
| ------------- | ----------------------------------------------------------------- |
| text          | raw text fromn xDD, from simple pdf extract                       |
| scienceparse  | parsed pdf into json via https://github.com/allenai/science-parse |
| processed_doc | doc structure parsing from the text and the scieneparse documents |
| processed_ner | running spaCy named entity recognition on processed_doc           |
| processed_pos | separate layer to store other basic information from spCy         |
| processed_es  | merging all the above in JSON load for Elastic Search             |

Each directory also has a .bibjson file with metadata and for each directory there is a sister file with docids.

The content in `text` and `scienceparse` was given to us by Ian Ross from xDD. We are probably not at liberty to redistribute that content. 

The document structure processing was done using the code in [https://github.com/lapps-xdd/xdd-docstructure](https://github.com/lapps-xdd/xdd-docstructure), spacyProcessing was done with `ner.py` in this repository.

As of early April 2023, sizes of directories were as follows:

| topic             | layer         | files | size   |
| ------------------| ------------- | ----- | ------ |
| biomedical        | text          | 10000 |  496MB |
|                   | scienceparse  |  9994 |  552MB |
|                   | processed_doc | 10000 |  414MB |
|                   | processed_ner |  9995 |   12MB |
|                   | processed_pos |  9995 |  935MB |
| geoarchive        | text          | 13789 | 3184MB |
|                   | scienceparse  | 13743 | 3069MB |
|                   | processed_doc | 13789 | 2235MB |
|                   | processed_ner | 13789 |   31MB |
|                   | processed_pos | 13789 | 1319MB |
| molecular_physics | text          | 10000 |  384MB |
|                   | scienceparse  |  9997 |  299MB |
|                   | processed_doc | 10000 |  341MB |
|                   | processed_ner |  9998 |    9MB |
|                   | processed_pos |  9998 |  791MB |

