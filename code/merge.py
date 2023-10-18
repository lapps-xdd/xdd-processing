"""Merging document information

Takes the JSON created by the document parser (which itself used the output of ScienceParse),
tranforms it into a more proper format for the AskMe database and adds in the named entities
and the terms.

Usage:

$ python merge [LIMIT]

Use LIMIT to limit the maximum number of files to process for each topic.


TODO:
- Merge in any information from the metadata API

"""

import os, sys, json
from collections import Counter
from io import StringIO
from tqdm import tqdm
from config import TOPICS_DIR, TOPICS, abbreviate_topic, ENTITY_TYPES

# A limit on how much data we want to put in the abstract and text fields for each
# document, now this is set to the same number as for spaCy processing.
MAX_SIZE = 50000

# In addition, we enter a summary, with just the data that will be returned from the
# database. Any processing for ranking will be done using just these data. Setting it
# higher will make ranking better but increase the size of the datastrucutres handed
# from the database.
SUMMARY_MAX_TOKENS = 2000

# Metadata files. Information in these files can also be obtained by pinging the xDD API
# at https://xdd.wisc.edu/api/articles. For example:
# https://xdd.wisc.edu/api/articles?docids=5783bcafcf58f176c768f5cc,5754e291cf58f1b0c7844cd2
METADATA = {
    'biomedical': 'biomedical_docids_10k.bibjson',
    'geoarchive': 'geoarchive.bibjson',
    'molecular_physics': 'molecular_physics_docids_10k.bibjson' }


def process_topics(limit: int):
    for topic in TOPICS:
        process_topic(topic, limit=limit)


def process_topic(topic: str, limit: int):
    sp_dir = os.path.join(TOPICS_DIR, topic, 'scienceparse')
    doc_dir = os.path.join(TOPICS_DIR, topic, 'processed_doc')
    ner_dir = os.path.join(TOPICS_DIR, topic, 'processed_ner')
    trm_dir = os.path.join(TOPICS_DIR, topic, 'processed_trm')
    out_dir = os.path.join(TOPICS_DIR, topic, 'processed_mer')
    meta_file = os.path.join(TOPICS_DIR, topic, METADATA.get(topic))
    os.makedirs(out_dir, exist_ok=True)
    print(f'\nLoading {sp_dir}...')
    print(f'Adding {ner_dir}...')
    print(f'Writing to {out_dir}...\n')
    terms_file = os.path.join(trm_dir, f'frequencies-{abbreviate_topic(topic)}.json')
    terms = json.loads(open(terms_file).read())
    meta = load_metadata(meta_file)
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
            if 'entities' in ner_obj:
                ner_obj['entities'] = sanitize_entities(ner_obj['entities'])
            identifier = os.path.splitext(doc)[0]
            trm_obj = terms.get(identifier, [])
            try:
                merged_obj = merge(doc, sp_obj, doc_obj, ner_obj, trm_obj, meta)
                if valid_merger(merged_obj):
                    with open(os.path.join(out_dir, doc), 'w') as fh:
                        json.dump(merged_obj, fh, indent=2)
                else:
                    log.write(f'{doc} -- object from merger was not complete\n')
                    #with open(os.path.join(out_dir, doc), 'w') as fh:
                    #    json.dump(merged_obj, fh, indent=2)
            except Exception as e:
                log.write(f'{doc} -- {e}\n')


def sanitize_entities(ner_obj: dict):
    """Only keep interesting entity types. This is done at the level of ner.py as well
    but at some point we still included WORK_OF_ART and TIME in the entities, but those
    were close to useless so we now filter them out. This method becomes obsolete when
    we rerun ner.py, because that script has been updated."""
    return {k: v for k, v in ner_obj.items() if k in ENTITY_TYPES}


def load_json(topic_dir: str, doc: str):
    """Return the JSON content of the file, but allow prior processing to not have
    created the desired file and return an empty dictionary in that case."""
    fname = os.path.join(topic_dir, doc)
    try:
        with open(fname) as fh:
            return json.load(fh)
    except FileNotFoundError:
        return {}


def merge(doc: str, sp_obj: dict, doc_obj: dict, ner_obj: dict, trm_obj: dict, meta: dict):
    """Merge ScienceParse, DocumentParser and NER results into one JSON file, collecting
    all data that we want to load into ElasticSearch. Uses abstract and metadata from the
    first, the text from the second, and the entities from the third."""
    merged_obj = {}
    merged_obj['name'] = get_name(doc)
    merged_obj['title'] = get_meta('title', sp_obj)
    merged_obj['year'] = get_meta('year', sp_obj)
    merged_obj['url'] = get_url(merged_obj['name'], meta)
    merged_obj['authors'] = get_meta('authors', sp_obj)
    merged_obj['abstract'] = get_abstract(doc_obj)
    merged_obj['text'] = get_text(doc_obj)
    merged_obj['summary'] = get_summary(merged_obj)
    merged_obj['entities'] = ner_obj.get('entities', {})
    merged_obj['terms'] = trm_obj
    return merged_obj


def load_metadata(fname: str):
    raw_meta = json.loads(open(fname).read())
    meta = {}
    for record in raw_meta:
        identifier = None
        for identifier_pair in record['identifier']:
            if identifier_pair.get('type') == '_xddid':
                identifier = identifier_pair['id']
        if identifier is not None:
            meta[identifier] = record
    return meta

def get_name(doc: str):
    return os.path.splitext(doc)[0]

def get_url(name: str, meta: dict):
    meta_data = meta.get(name)
    if meta_data:
        links = meta_data.get('link', [])
        if links:
            link = links[0]
            if 'url' in link:
                return link['url']
    return None

def get_meta(field: str, json_obj: dict):
    return json_obj.get('metadata', {}).get(field) 

def get_abstract(doc_obj: dict):
    abstract_obj = doc_obj.get('abstract')
    return abstract_obj.get('abstract', '') if abstract_obj is not None else ''

def get_text(doc_obj: dict):
    text = StringIO()
    for section in doc_obj['sections']:
        if section['heading'] is not None:
            text.write(f'{section["heading"].strip()}\n\n')
        text.write(f'{section["text"].strip()}\n\n')
    return text.getvalue()[:MAX_SIZE]

def get_summary(merged_obj: dict):
    """Get a summary by concatenating the abstact and the text while staying within
    the maximum number of tokens allowed."""
    summary = merged_obj['abstract'] + ' ' + merged_obj['text']
    return ' '.join(summary.split()[:SUMMARY_MAX_TOKENS])
    

def valid_merger(merged_obj: dict):
    for field in ('title', 'year', 'authors'):
        if not merged_obj[field]:
            return False
    return True


if __name__ == '__main__':

    limit = int(sys.argv[1]) if len(sys.argv) > 1 else sys.maxsize
    process_topics(limit)
