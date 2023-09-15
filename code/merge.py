"""Create document for ES database

Takes the JSON created by the ScienceParser, tranforms it into the proper format
for the AskMe database and then adds in the named entities.

"""

import os, sys, json
from collections import Counter
from io import StringIO
from tqdm import tqdm
from config import TOPICS_DIR, TOPICS

# a limit on how much data we want to put on the search engine for each file,
# now this is set to the same number of as for spaCy processing
MAX_SIZE = 50000


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
            # print(f'{n:06}\t{doc}')
            # scienceparse file format:  54b4324ee138239d8684aeb2_input.pdf.json
            # processed_doc file format: 54b4324ee138239d8684aeb2.json
            # processed_ner file format: 54b4324ee138239d8684aeb2.json
            sp_obj = load_json(sp_dir, doc[:-5] + '_input.pdf.json')
            doc_obj = load_json(doc_dir, doc)
            ner_obj = load_json(ner_dir, doc)
            try:
                merged_obj = merge(sp_obj, doc_obj, ner_obj)
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
    fname = os.path.join(topic_dir, doc)
    try:
        with open(fname) as fh:
            return json.load(fh)
    except FileNotFoundError:
        return {}

def merge(sp_obj, doc_obj, ner_obj):
    """Merge ScienceParse, DocumentParser and NER results into one JSON file
    for loading into ElasticSearch. Uses abstract and metadata from the first,
    the next from the second, and the entities from the third."""
    es_obj = {}
    es_obj['name'] = os.path.splitext(ner_obj['name'])[0]
    es_obj['title'] = get_meta('title', sp_obj)
    es_obj['year'] = get_meta('year', sp_obj)
    es_obj['authors'] = get_meta('authors', sp_obj)
    abstract = doc_obj.get('abstract')
    if abstract is not None:
        abstract = abstract.get('abstract')
    es_obj['abstract'] = abstract
    text = StringIO()
    for section in doc_obj['sections']:
        if section['heading'] is not None:
            text.write(f'{section["heading"].strip()}\n\n')
        text.write(f'{section["text"].strip()}\n\n')
    es_obj['text'] = text.getvalue()[:MAX_SIZE]
    es_obj['entities'] = ner_obj['entities']
    return es_obj

def get_meta(field: str, json_obj: dict):
    return json_obj.get('metadata', {}).get(field) 

def valid_merger(merged_obj: dict):
    for field in ('title', 'year', 'authors'):
        if not merged_obj[field]:
            return False
    return True


if __name__ == '__main__':
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else sys.maxsize
    process_topics(limit)
