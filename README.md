# Processing xDD Data

Code for preprocessing the files in the three topics: biomedical, geoarchive and molecular_physics. Only useful if you have access to the xDD data.

Each topics is associated with a data directory and each directory has the same structure:

| directory     | description                                                       |
| ------------- | ----------------------------------------------------------------- |
| text          | raw text fromn xDD, from simple pdf extract                       |
| scienceparse  | parsed pdf into json via https://github.com/allenai/science-parse |
| processed_doc | doc structure parsing from the text and the scieneparse documents |
| processed_ner | running spaCy named entity recognition on processed_doc           |
| processed_es  | merging all the above in JSON load for Elastic Search             |

Each directory also has a .bibjson file with metadata.

The content in `text` and `scienceparse` was given to us by Ian Ross from xDD. We are probably not at liberty to redistribute that content. 

The document structure processing was done using the code in [https://github.com/lapps-xdd/xdd-docstructure](https://github.com/lapps-xdd/xdd-docstructure). 