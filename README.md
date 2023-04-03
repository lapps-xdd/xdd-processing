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

As of early April 2023, the sizes of source data (text and scienceparse) were as follows:

|              | biomedical         | geoarchive            | molecular_physics  |
| -------------| -------------------| --------------------- | ------------------ |
| text         | 1000 files - 496Mb | 13789 files - 3,184Mb | 1000 files - 384Mb |
| scienceparse | 9994 files - 552Mb | 13743 files - 3,069Mb | 997 files - 299Mb  |

The size after document processing was either in the same ballpark or up to 30% smaller because text that did not seem like language was removed. The processed\_pos directories were generated from the processed\_doc directories and were about twice as large for biomedical and molecular\_physics, but 60% of the size for the geoarchive topic. The latter happened because only the first 30K of data in each file was processed. And more text was trunccated for geoarchive since the average file size in that topic was 162Kb, as opposed to 41Kb for biomedical and 34Kb for molecular\_physics

You can see the exact sizes by running `python analyze.py`.

