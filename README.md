# Processing xDD Data

Code for processing xDD files, only useful if you have access to the xDD data.

The document structure processing was done using the code in [https://github.com/lapps-xdd/xdd-docstructure](https://github.com/lapps-xdd/xdd-docstructure).


There are several processing steps:

1. Document structure parsing (done using the code in [https://github.com/lapps-xdd/xdd-docstructure](https://github.com/lapps-xdd/xdd-docstructure)).
2. Extracting named entities with spaCy.
3. Generating term lists (done using the code in [https://github.com/lapps-xdd/xdd-terms](https://github.com/lapps-xdd/xdd-temrs)).
4. Merging document structure, named entities, temrs and metadata.
5. Preparing the file that will be imported into the database.


### 1. Document structure parsing

See [https://github.com/lapps-xdd/xdd-docstructure](https://github.com/lapps-xdd/xdd-docstructure).


### 2. Named entity extraction

Use the script `ner.py` in this repository, which requires spaCy to run.

```bash
$ pip install spacy==3.5.1
$ python -m spacy download en_core_web_sm
```

To run the script do

```bash
$ python ner.py --doc DIR1 --pos DIR2 --ner DIR3 [--limit N]
```

The input in DIR1 should have files with the output from the document structure parser. part-of-speech data is written to DIR 2 and named entities to DIR3. If LIMIT is used than nomore than N files wiil be processed.


### 3. Term extraction

See [https://github.com/lapps-xdd/xdd-terms](https://github.com/lapps-xdd/xdd-temrs).


### 4. Merging

Requires output from previous processing stages as well as a file with metadata.

```bash
$ python merge.py --scpa DIR1 --doc DIR2 --ner DIR3 --trm DIR4 --meta FILE --out DIR5 [--limit N]
```

For input we have ScienceParse results (DIR1), document parser results (DIR2), named entities (DIR3), terms (DIR4) and a metadata file. Output is written to DIR5. See merge.py for example usage.


### 5. Preparing the database file

Created from the merged data with `prepare_elastic.py`:

```bash
$ python prepare_elastic.py -i DIR1 -o DIR2 [--domain DOMAIN] [--limit N] 
```

Takes merged files from DIR1 and creates a file `elastic.json` in DIR2. The file has pairs of lines as required by ElasticSearch (the second line is spread out over a couple of lines for clarity, it really is only one line, otherwise ElasticSearch fails to load it):

```json
{"index": {"_id": "54b4324ee138239d8684aeb2"}}}
{
  "domain": "biomedical",
  "name": "54b4324ee138239d8684aeb2",
  "year": 2010,
  "title": "Nanomechanical properties of modern and fossil bone",
  "authors": ["Sara E. Olesiak", "Matt Sponheimer", "Jaelyn J. Eberle", "Michelle L. Oyen"],
  "abstract": "Relatively little is known about how diagenetic processes affect ...",
  "url": "http://www.sciencedirect.com/science/article/pii/S0022283609014053",
  "text": "...",
  "summary": "...",
  "terms": [...],
  "entities": {...}
}
```

<!--

### Notes on data sizes

As of early April 2023, the sizes of source data (text and scienceparse) were as follows:

|              | biomedical          | geoarchive            | molecular_physics   |
| -------------| --------------------| --------------------- | ------------------- |
| text         | 10000 files - 496Mb | 13789 files - 3,184Mb | 10000 files - 384Mb |
| scienceparse |  9994 files - 552Mb | 13743 files - 3,069Mb |  9997 files - 299Mb |
| merged       |  8017 files - 277Mb |  3488 files - 175Mb   |  7892 files - 242Mb |

The size after document processing was either in the same ballpark or up to 30% smaller because text that did not seem like language was removed. The processed\_pos directories were generated from the processed\_doc directories and were about twice as large for biomedical and molecular\_physics, but 60% of the size for the geoarchive topic. The latter happened because only the first 30K of data in each file was processed. And more text was truncated for geoarchive since the average file size in that topic was 162Kb, as opposed to 41Kb for biomedical and 34Kb for molecular\_physics. For merging we only kept files that had title, author and year fields.

You can see some of the exact sizes by running `python analyze.py`.

-->
