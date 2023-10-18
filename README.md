# Processing xDD Data

Code for processing the files in the three topics: biomedical, geoarchive and molecular_physics. Only useful if you have access to the xDD data.

Each topic is associated with a topic directory and each of those has the same structure:

| directory     | description                                                            |
| ------------- | ---------------------------------------------------------------------- |
| text          | raw text fromn xDD, from simple pdf extract                            |
| scienceparse  | parsed pdf into json via https://github.com/allenai/science-parse      |
| processed_doc | doc structure parsing from the text and the scienceparse documents     |
| processed_ner | running spaCy named entity recognition on processed_doc                |
| processed_pos | separate layer to store other basic information from spaCy             |
| processed_mer | merging all the above as a first preparation for Elastic Search import |

Each directory also has a .bibjson file with metadata and for each directory there is a sister file with docids.

The content in `text` and `scienceparse` was given to us by Ian Ross from xDD, we cannot redistribute that content.

The document structure processing was done using the code in [https://github.com/lapps-xdd/xdd-docstructure](https://github.com/lapps-xdd/xdd-docstructure).

> Note that the code in `xdd-docstructre` puts document structure results in a directory named `processed`. This code assumes that document structure parsing results are in `processed_doc`, so you will have to change the name of the directory.

There are several processing steps:

1. document structure parsing (done elsewhere, see above)
2. running some NLP like NER
3. generating term lists (not yet integrated here)
4. merging all the above
5. preparing the files that will be import into the database



### Running tagging named entity extraction

To create the contents of `processed_ner` and `processed_pos` use the script `ner.py` in this repository. This script requires spaCy to run.

```bash
$ pip install spacy==3.5.1
$ python -m spacy download en_core_web_sm
```

To run the script do

```bash
$ python ner.py [LIMIT]
```

If LIMIT is not used than all files for all topics are processed.


### Merging

To create the content in `processed_mer` use `merge.py`, which also takes an optional LIMIT parameter:

```bash
$ python merge.py [LIMIT]
```


### Preparing the database files

Created from the merged data with `prepare_elastic.py`:

```bash
$ python prepare_elastic.py
```

Creates three files in the current directory: `elastic-biomedical.json`, `elastic-geoarchive.json` and `elastic-molecular_physics.json`. Each of them has pairs of lines as required by ElasticSearch (the second line is spread out over a couple of lines for clarity, it really is only one line, otherwise ElasticSearch fails to load it):

```json
{"index": {"_id": "54b4324ee138239d8684aeb2"}}}
{
  "topic": "biomedical",
  "name": "54b4324ee138239d8684aeb2",
  "year": 2010,
  "title": "Nanomechanical properties of modern and fossil bone",
  "authors": ["Sara E. Olesiak", "Matt Sponheimer", "Jaelyn J. Eberle", "Michelle L. Oyen"],
  "abstract": "Relatively little is known about how diagenetic processes affect ...",
  "abstract_summary": "...",
  "text": "...",
  "text_summary": "..."
}
```

### Notes on data sizes

As of early April 2023, the sizes of source data (text and scienceparse) were as follows:

|              | biomedical         | geoarchive            | molecular_physics  |
| -------------| -------------------| --------------------- | ------------------ |
| text         | 1000 files - 496Mb | 13789 files - 3,184Mb | 1000 files - 384Mb |
| scienceparse | 9994 files - 552Mb | 13743 files - 3,069Mb | 997 files - 299Mb  |
| merged       | 8017 files - 277Mb | 3488 files - 175Mb    | 7892 files - 242Mb |

The size after document processing was either in the same ballpark or up to 30% smaller because text that did not seem like language was removed. The processed\_pos directories were generated from the processed\_doc directories and were about twice as large for biomedical and molecular\_physics, but 60% of the size for the geoarchive topic. The latter happened because only the first 30K of data in each file was processed. And more text was truncated for geoarchive since the average file size in that topic was 162Kb, as opposed to 41Kb for biomedical and 34Kb for molecular\_physics. For merging we only kept files that had title, author and year fields.

You can see some of the exact sizes by running `python analyze.py`.

