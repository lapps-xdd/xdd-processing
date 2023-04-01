"""spacy.py

Run spaCy over the output of ScienceParse.

Requirements:

$ pip install spacy==3.5.1
$ python -m spacy download en_core_web_sm

Usage:

$ python ner.py [LIMIT]

Without LIMIT all files in each topic direrctory are processed. 

"""

import os, sys, json, time
from collections import Counter
import spacy


nlp = spacy.load("en_core_web_sm")

topics_dir = '/Users/Shared/data/xdd/doc2vec/topic_doc2vecs'
topics = ('biomedical',  'geoarchive', 'molecular_physics')


def process_topics(limit=sys.maxsize):
	for topic in topics:
		process_topic(topic, limit=limit)

def process_topic(topic: str, limit: int):
	in_dir = os.path.join(topics_dir, topic, 'scienceparse')
	out_dir = os.path.join(topics_dir, topic, 'processed_ner')
	os.makedirs(out_dir, exist_ok=True)
	print(f'\nProcessing {in_dir}...')
	print(f'Writing to {out_dir}...\n')
	docs = os.listdir(in_dir)
	with open(f'log-{topic}.txt', 'w') as log:
		for n, doc in enumerate(sorted(docs)):
			if n >= limit:
				break
			try:
				t0 = time.time()
				entities = process_doc(in_dir, doc, n + 1)
				answer = { 'name': doc, 'entities': entities }
				with open(os.path.join(out_dir, doc), 'w') as fh:
					json.dump(answer, fh, indent=2)
				elapsed = time.time() - t0
				log.write(f'{doc}\t{elapsed:.2f}\n')
			except Exception as e:
				log.write(f'{doc}\t{e}\n')

def process_doc(topic_dir: str, doc: str, n: int):
	fname = os.path.join(topic_dir, doc)
	with open(fname) as fh:
		json_obj = json.load(fh)
		name = json_obj['name']
		size = os.path.getsize(fname)
		print(f'{n:06d} {name} {size}')
		if size > 200000:
			return {}
		sections = json_obj['metadata']['sections']
		entities = {}
		if sections is not None:
			for section in json_obj['metadata']['sections']:
				text = section['text']
				doc = nlp(text)
				for entity in doc.ents:
					entities.setdefault(entity.label_, Counter())
					entities[entity.label_][entity.text] += 1
	return entities


if __name__ == '__main__':

	limit = int(sys.argv[1]) if len(sys.argv) > 1 else sys.maxsize
	process_topics(limit)
