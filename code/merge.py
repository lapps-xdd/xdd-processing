"""Merging document information

Takes the output of ScienceParse, the matadata file and various outputs of prior processing,
and tranforms it into a more proper format for the AskMe database.

To get help on running the script:

$ python merge.py -h

Example use:

$ export DIR=/Users/Shared/data/xdd/doc2vec/topic_doc2vecs/topic_samples/mars
$ python merge.py \
      --scpa $DIR/scienceparse --doc $DIR/output/doc --ner $DIR/output/ner \
      --trm $DIR/output/trm --meta $DIR/metadata.json --out $DIR/output/mer

"""

import os, sys, json, argparse
from collections import Counter
from io import StringIO
from tqdm import tqdm
from utils import timestamp
from config import TOPICS_DIR, TOPICS, abbreviate_topic, ENTITY_TYPES

# A limit on how much data we want to put in the abstract and text fields for each
# document, now this is set to the same number as for spaCy processing.
MAX_SIZE = 25000

# In addition, we enter a summary, with just the data that will be returned from the
# database. Any processing for ranking will be done using just these data. Setting it
# higher will make ranking better but increase the size of the datastrucutres handed
# from the database.
SUMMARY_MAX_TOKENS = 2000


def merge_directory(
        scpa_dir: str, meta_file: str, doc_dir: str, ner_dir: str, trm_dir: str,
        sum_dir: str, out_dir: str, limit: int):
    os.makedirs(out_dir, exist_ok=True)
    terms_file = os.path.join(trm_dir, 'frequencies.json')
    terms = json.loads(open(terms_file).read())
    meta = load_metadata(meta_file)
    docs = os.listdir(doc_dir)
    with open(f'logs/merger-{timestamp()}.log', 'w') as log:
        for doc in tqdm(sorted(docs)[:limit]):
            # scienceparse file format:  54b4324ee138239d8684aeb2_input.pdf.json
            # processed_doc file format: 54b4324ee138239d8684aeb2.json
            # processed_ner file format: 54b4324ee138239d8684aeb2.json
            scp_obj = load_json(scpa_dir, doc[:-5] + '_input.pdf.json')
            doc_obj = load_json(doc_dir, doc)
            ner_obj = load_json(ner_dir, doc)
            summary = get_summary(sum_dir, doc)
            if 'entities' in ner_obj:
                ner_obj['entities'] = sanitize_entities(ner_obj['entities'])
            identifier = os.path.splitext(doc)[0]
            trm_obj = terms.get(identifier, [])
            try:
                merged_obj = merge(doc, scp_obj, doc_obj, ner_obj, trm_obj, summary, meta)
                if valid_merger(merged_obj):
                    with open(os.path.join(out_dir, doc), 'w') as fh:
                        json.dump(merged_obj, fh, indent=2)
                else:
                    log.write(f'{doc} -- object from merger was not complete\n')
                    #with open(os.path.join(out_dir, doc), 'w') as fh:
                    #    json.dump(merged_obj, fh, indent=2)
            except Exception as e:
                exception_type = type(e).__name__
                log.write(f'{doc} -- {exception_type} - {e}\n')


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


def get_summary(directory: str, docname: str):
    with open(os.path.join(directory, docname[:-4] + 'txt')) as fh:
        summary = fh.read()
    return summary


def merge(doc: str, sp_obj: dict, doc_obj: dict, ner_obj: dict, trm_obj: dict, summary: str, meta: dict):
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
    merged_obj['content'] = get_text(doc_obj)
    merged_obj['summary'] = summary
    #merged_obj['summary'] = get_summary(merged_obj)
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

def valid_merger(merged_obj: dict):
    for field in ('title', 'year', 'authors'):
        if not merged_obj[field]:
            return False
    return True


def parse_args():
    parser = argparse.ArgumentParser(description='Merging processing layers and metadata')
    parser.add_argument('--scpa', help="directory with ScienceParse results")
    parser.add_argument('--meta', help="file with meta data")
    parser.add_argument('--doc', help="directory with document structure parses")
    parser.add_argument('--ner', help="directory with NER data")
    parser.add_argument('--trm', help="directory with term data")
    parser.add_argument('--sum', help="directory with summary data")
    parser.add_argument('--out', help="output directory")
    parser.add_argument('--limit', help="Maximum number of documents to process",
                        type=int, default=sys.maxsize)
    return parser.parse_args()



if __name__ == '__main__':

    args = parse_args()
    merge_directory(args.scpa, args.meta, args.doc, args.ner, args.trm, args.sum, args.out, args.limit)
