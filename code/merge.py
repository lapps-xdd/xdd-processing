"""Create document for ES database

Takes the JSON created by the document parser (which itself used the output of ScienceParse),
tranforms it into a more proper format for the AskMe database and adds in the named entities.

Usage:

$ python merge [LIMIT]

Use LIMIT to limit the maximum number of files to process for each topic.


TODO:
- merge in term lists
- Merge in any information from the metadata API

"""

import os, sys, json
from collections import Counter
from io import StringIO
from tqdm import tqdm
from config import TOPICS_DIR, TOPICS

# A limit on how much data we want to put on the search engine for each file,
# now this is set to the same number as for spaCy processing.
MAX_SIZE = 50000

# In addition, we enter short versions of the abstract and text fields, with just the
# data that will be returned from the database. This is quite low now, but we will want
# to increase this because it will be all that we have to run NLP on when ranking.
SUMMARY_SIZE = 1000


def process_topics(limit: int):
    for topic in TOPICS:
        process_topic(topic, limit=limit)

def process_topic(topic: str, limit: int):
    sp_dir = os.path.join(TOPICS_DIR, topic, 'scienceparse')
    doc_dir = os.path.join(TOPICS_DIR, topic, 'processed_doc')
    ner_dir = os.path.join(TOPICS_DIR, topic, 'processed_ner')
    out_dir = os.path.join(TOPICS_DIR, topic, 'processed_mer')
    os.makedirs(out_dir, exist_ok=True)
    print(f'\nLoading {sp_dir}...')
    print(f'Adding {ner_dir}...')
    print(f'Writing to {out_dir}...\n')
    docs = os.listdir(doc_dir)
    with open(f'log-merger-{topic}.log', 'w') as log:
        for doc in tqdm(sorted(docs)[:limit]):
            # print(f'{doc}')
            # scienceparse file format:  54b4324ee138239d8684aeb2_input.pdf.json
            # processed_doc file format: 54b4324ee138239d8684aeb2.json
            # processed_ner file format: 54b4324ee138239d8684aeb2.json
            sp_obj = load_json(sp_dir, doc[:-5] + '_input.pdf.json')
            doc_obj = load_json(doc_dir, doc)
            ner_obj = load_json(ner_dir, doc)
            try:
                merged_obj = merge(doc, sp_obj, doc_obj, ner_obj)
                if valid_merger(merged_obj):
                    with open(os.path.join(out_dir, doc), 'w') as fh:
                        json.dump(merged_obj, fh, indent=2)
                else:
                    log.write(f'{doc} -- object from merger was not complete\n')
                    #with open(os.path.join(out_dir, doc), 'w') as fh:
                    #    json.dump(merged_obj, fh, indent=2)
            except Exception as e:
                log.write(f'{doc} -- {e}\n')

def load_json(topic_dir: str, doc: str):
    """Return the JSON content of the file, but allow prior processing to not have
    created the desired file and return an empty dictionary in that case."""
    fname = os.path.join(topic_dir, doc)
    try:
        with open(fname) as fh:
            return json.load(fh)
    except FileNotFoundError:
        return {}

def merge(doc: str, sp_obj: dict, doc_obj: dict, ner_obj: dict):
    """Merge ScienceParse, DocumentParser and NER results into one JSON file, collecting
    all data that we want to load into ElasticSearch. Uses abstract and metadata from the
    first, the text from the second, and the entities from the third."""
    merged_obj = {}
    merged_obj['name'] = get_name(doc)
    merged_obj['title'] = get_meta('title', sp_obj)
    merged_obj['year'] = get_meta('year', sp_obj)
    merged_obj['authors'] = get_meta('authors', sp_obj)
    abstract = get_abstract(doc_obj)
    merged_obj['abstract'] = abstract
    merged_obj['abstract_summary'] = abstract[:SUMMARY_SIZE]
    text = StringIO()
    for section in doc_obj['sections']:
        if section['heading'] is not None:
            text.write(f'{section["heading"].strip()}\n\n')
        text.write(f'{section["text"].strip()}\n\n')
    merged_obj['text'] = text.getvalue()[:MAX_SIZE]
    merged_obj['text_summary'] = merged_obj['text'][:SUMMARY_SIZE]
    merged_obj['entities'] = ner_obj.get('entities', {})
    return merged_obj

def get_name(doc: str):
    return os.path.splitext(doc)[0]

def get_meta(field: str, json_obj: dict):
    return json_obj.get('metadata', {}).get(field) 

def get_abstract(doc_obj: dict):
    abstract_obj = doc_obj.get('abstract')
    return abstract_obj.get('abstract', '') if abstract_obj is not None else ''

def valid_merger(merged_obj: dict):
    for field in ('title', 'year', 'authors'):
        if not merged_obj[field]:
            return False
    return True


if __name__ == '__main__':

    limit = int(sys.argv[1]) if len(sys.argv) > 1 else sys.maxsize
    process_topics(limit)
