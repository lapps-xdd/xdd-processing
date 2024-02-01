"""Extracting named entities and noun groups from xDD data

Runs spaCy over the output of ScienceParse.

Requirements:

$ pip install spacy==3.5.1
$ python -m spacy download en_core_web_sm

Usage:

$ python usage: ner.py [-h] [--doc DOC] [--pos POS] [--ner NER] [--limit LIMIT]

Without LIMIT all files in the DOC directory are processed.

Only the first N characters of the data will be processed, the exact size is set
by the MAX_SIZE variable.

"""

import os, sys, json, time, argparse
from collections import Counter
import spacy
from tqdm import tqdm
import frequencies, utils
from config import ENTITY_TYPES

nlp = spacy.load("en_core_web_sm")


# a limit on how much data we want to process for each file
MAX_SIZE = 30000

# load the 500 most frequent English words
FREQUENT_ENGLISH_WORDS = set(
    [line.split()[1] for line in frequencies.FREQUENCIES.split('\n') if line])


def process_directory(doc_dir: str, pos_dir: str, ner_dir: str, limit: int):
    """Run NER over all documents in doc_dir and write part-of-speech output to
    pos_dir and named entities to ner_dir."""
    os.makedirs(pos_dir, exist_ok=True)
    os.makedirs(ner_dir, exist_ok=True)
    print(f'\nProcessing {doc_dir}...')
    print(f'Writing to {pos_dir}...')
    print(f'Writing to {ner_dir}...\n')
    docs = os.listdir(doc_dir)
    with open('log-preprocessing-ner.txt', 'w') as log:
        n = 1
        for doc in tqdm(list(sorted(docs))[:limit]):
            n += 1
            try:
                t0 = time.time()
                entities, paragraphs = process_doc(doc_dir, doc, n + 1)
                write_entities(ner_dir, doc, entities)
                write_tokens(pos_dir, doc, paragraphs)
                elapsed = time.time() - t0
                log.write(f'{doc}\t{elapsed:.2f}\n')
            except Exception as e:
                log.write(f'{doc}\t{e}\n')


def process_doc(doc_dir: str, doc: str, n: int):
    fname = os.path.join(doc_dir, doc)
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


def parse_args():
    parser = argparse.ArgumentParser(description='Run NER over xDD files')
    parser.add_argument('--doc', help="directory with document structure parses")
    parser.add_argument('--pos', help="output directory for POS data")
    parser.add_argument('--ner', help="output directory for NER data")
    parser.add_argument('--limit', help="Maximum number of documents to process",
                        type=int, default=sys.maxsize)
    return parser.parse_args()



if __name__ == '__main__':

    args = parse_args()
    process_directory(args.doc, args.pos, args.ner, args.limit)
