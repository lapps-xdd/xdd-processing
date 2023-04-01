"""Create document for ES database

Takes the JSON created by the ScienceParser, tranforms it into the proper format
for the AskMe database and then adds in the named entities.

"""

import os, sys, json
from collections import Counter

topics_dir = '/Users/Shared/data/xdd/doc2vec/topic_doc2vecs'
topics = ('biomedical',  'geoarchive', 'molecular_physics')


def process_topics(limit=sys.maxsize):
	for topic in topics:
		process_topic(topic, limit=limit)

def process_topic(topic: str, limit: int):
	sp_dir = os.path.join(topics_dir, topic, 'scienceparse')
	ner_dir = os.path.join(topics_dir, topic, 'processed_ner')
	out_dir = os.path.join(topics_dir, topic, 'processed_merged')
	os.makedirs(out_dir, exist_ok=True)
	print(f'\nLoading {sp_dir}...')
	print(f'Adding {ner_dir}...')
	print(f'Writing to {out_dir}...\n')
	docs = os.listdir(sp_dir)
	for n, doc in enumerate(sorted(docs)):
		if n >= limit:
			break
		print(f'{n:06}\t{doc}')
		sp_obj = load_json(sp_dir, doc)
		ner_obj = load_json(ner_dir, doc)
		merged_obj = merge(sp_obj, ner_obj)
		with open(os.path.join(out_dir, doc), 'w') as fh:
			json.dump(merged_obj, fh, indent=2)

def load_json(topic_dir: str, doc: str):
	fname = os.path.join(topic_dir, doc)
	with open(fname) as fh:
		return json.load(fh)

def merge(sp_obj, ner_obj):
	es_obj = {}

	return es_obj


if __name__ == '__main__':
	limit = int(sys.argv[1]) if len(sys.argv) > 1 else sys.maxsize
	process_topics(limit)
