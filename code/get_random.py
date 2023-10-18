"""

Select random files from each topic and write three JSON files, one for each topic,
where each line is a summary of a document in JSON format, containing an identifier,
the year, the title, a summary (created from abstract or text) and some entities of
interest (skipping obscure ones like work-of-art).

"""

import os, sys, json, random
import config


# number of random files to pick
DEFAULT_LIMIT = 25

# entity types to include
ENTITY_TYPES = ('PERSON', 'GPE', 'ORG', 'LOC', 'FAC')


def select_random(topic: str, topic_dir: str, limit: int):
	print(topic)
	files = os.listdir(topic_dir)
	random.shuffle(files)
	with open(f'random-{topic}.json', 'w') as fh:
		for fname in files[:limit]:
			#print('   ', fname)
			content = json.loads(open(os.path.join(topic_dir, fname)).read())
			content_summary = {
				'id': content['name'],
				'year': content['year'],
				'title': content['title'],
				'summary': get_summary(content),
				'entities': get_entities(content) }
			fh.write(f'{json.dumps(content_summary)}\n')


def get_summary(content: dict):
	summary = content['abstract'] or content['text']
	return ' '.join(summary.split()[:2000])


def get_entities(content):
	entities = {}
	for entity_type in content['entities'].keys():
		#print(entity_type)
		if entity_type in ENTITY_TYPES:
			entities[entity_type] = list(content['entities'][entity_type].keys())
	return entities


if __name__ == '__main__':

	limit = int(sys.argv[1] if len(sys.argv) > 1 else DEFAULT_LIMIT)
	for topic in config.TOPICS:
		topic_dir = os.path.join(config.TOPICS_DIR, topic, 'processed_mer')
		select_random(topic, topic_dir, limit)
