"""Extracting named entities and noun groups from xDD data

Runs spaCy over the output of ScienceParse.

Requirements:

$ pip install spacy==3.5.1
$ python -m spacy download en_core_web_sm

Usage:

$ python ner.py [LIMIT]

Without LIMIT all files in each topic directory are processed. 

Only the first N characters of the data will be processed, the exact size is set
by the MAX_SIZE valiable

Uses a hard-code directory path in config.

"""

import os, sys, json, time
from collections import Counter
import spacy
from tqdm import tqdm
import frequencies, utils
from config import TOPICS_DIR, data_directory

nlp = spacy.load("en_core_web_sm")


# a limit on how much data we want to process for each file
MAX_SIZE = 30000

FREQUENT_ENGLISH_WORDS = set(
    [line.split()[1] for line in frequencies.FREQUENCIES.split('\n') if line])

# Interesting entity types, not included are for example 'CARDINAL', 'DATE',
# 'LANGUAGE', 'LAW', 'ORDINAL', 'PERCENT', 'QUANTITY' and 'TIME'
ENTITY_TYPES = set(['FAC', 'GPE', 'LOC', 'NORP',  'ORG',  'PERSON',
                    'PRODUCT', 'WORK_OF_ART'])


DOC_SUBDIR = 'processed_doc'
POS_SUBDIR = 'processed_pos'
NER_SUBDIR = 'processed_ner'


def process_topics(limit=sys.maxsize):
    for topic in TOPICS:
        process_topic(topic, limit=limit)
    print()

def process_topic(topic: str, limit: int):
    # TODO: those directories should not be hard-coded, they are also in the 
    # config file as a list.
    in_dir = data_directory(topic, DOC_SUBDIR)
    pos_dir = data_directory(topic, POS_SUBDIR)
    ner_dir = data_directory(topic, NER_SUBDIR)
    os.makedirs(pos_dir, exist_ok=True)
    os.makedirs(ner_dir, exist_ok=True)
    print(f'\nProcessing {in_dir}...')
    print(f'Writing to {pos_dir}...')
    print(f'Writing to {ner_dir}...\n')
    docs = os.listdir(in_dir)
    with open(f'log-{topic}.txt', 'w') as log:
        n = 1
        for doc in tqdm(list(sorted(docs))[:limit]):
            n += 1
            try:
                t0 = time.time()
                # if not '54b4324ee138239d8684aeb2' in doc:
                #     continue
                entities, paragraphs = process_doc(in_dir, doc, n + 1)
                write_entities(ner_dir, doc, entities)
                write_tokens(pos_dir, doc, paragraphs)
                elapsed = time.time() - t0
                log.write(f'{doc}\t{elapsed:.2f}\n')
            except Exception as e:
                log.write(f'{doc}\t{e}\n')

def process_doc(topic_dir: str, doc: str, n: int):
    fname = os.path.join(topic_dir, doc)
    entities = {}
    paragraphs = []
    with open(fname) as fh:
        json_obj = json.load(fh)
        size = os.path.getsize(fname)
        sections = json_obj['sections']
        total_size = 0
        # TODO: should also run over the abstract and the title!!!
        if sections is not None:
            for section in sections:
                text = section['text']
                total_size += len(text)
                if total_size > MAX_SIZE:
                    break
                run_spacy(text, entities, paragraphs)
    return entities, paragraphs


def run_spacy(text, entities, paragraphs):
    text = text.replace('-\n', '')
    doc = nlp(text)
    paragraph = []
    for sent in doc.sents:
        if accept_sentence(sent):
            for entity in sent.ents:
                if entity.label_ in ENTITY_TYPES:
                    entities.setdefault(entity.label_, Counter())
                    entities[entity.label_][entity.text] += 1
            # t.i, t.text, t.lemma_, t.pos_, t.tag_, t.shape_, t.ent_type_) for th]
            tokens = [t for t in doc]
            # nc.start, nc.end, nc
            noun_chunks = [nc for nc in doc.noun_chunks]
            paragraphs.append((sent, tokens, noun_chunks))


def accept_sentence(sent):
    """Specifies some minimal requirements for a sentence to be accepted."""
    tokens = [t.text for t in sent]
    tokens_counter = Counter(tokens)
    average_token_length = utils.average_token_length(len(tokens), tokens_counter)
    singletons_per_token = utils.singletons_per_token(tokens)
    language_score = utils.language_score(tokens_counter, FREQUENT_ENGLISH_WORDS)
    return (average_token_length > 4
            and singletons_per_token < 2
            and language_score > 0.2)


def write_entities(ner_dir, doc, entities):
    answer = { 'name': doc, 'entities': entities }
    with open(os.path.join(ner_dir, doc), 'w') as fh:
        json.dump(answer, fh, indent=2)

             
def write_tokens(pos_dir, doc, paragraphs):
    txt_doc = os.path.splitext(doc)[0] + '.txt'
    with open(os.path.join(pos_dir, txt_doc), 'w') as fh:
        fh.write('<p>\n\n')
        for paragraph in paragraphs:
            s = paragraph[0]
            fh.write(f'\n<s>\n\n{str(s)}\n\n')
            for t in s:
                write_token(fh, t)
            fh.write('\n')
            for nc in s.noun_chunks:
                text = nc.text
                text = text.replace('\n', '')
                text = ' '.join(text.split())
                fh.write(f'{nc.start}\t{nc.end}\t{text}\n')


def write_token(fh, t):
    text = t.text.strip()
    lemma = t.lemma_.strip()
    ent_type = t.ent_type_ if t.ent_type_ in ENTITY_TYPES else ''
    elements = [t.i, text, lemma, t.pos_, t.tag_, ent_type]
    elements = [str(e) for e in elements]
    line = "\t".join(elements)
    fh.write(f'{line}\n')


def write_token2(t):
    text = t.text.strip()
    lemma = t.lemma_.strip()
    ent_type = t.ent_type_ if t.ent_type_ in ENTITY_TYPES else ''
    elements = [t.i, text, lemma, t.pos_, t.tag_, ent_type]
    elements = [str(e) for e in elements]
    line = "\t".join(elements)
    print(f'{line}')


if __name__ == '__main__':

    limit = int(sys.argv[1]) if len(sys.argv) > 1 else sys.maxsize
    process_topics(limit)
