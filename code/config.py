import os

# location of all the topics
TOPICS_DIR = '/Users/Shared/data/xdd/doc2vec/topic_doc2vecs'

# list of topics
TOPICS = ('biomedical',  'geoarchive', 'molecular_physics')
ABBREVIATIONS = {t: t[:3] for t in TOPICS}

# data directories of source data and processing layers
DATA_DIRS = ('text', 'scienceparse', 'processed_doc', 'processed_ner', 'processed_pos')

# Interesting entity types, not included are for example 'CARDINAL', 'DATE',
# 'LANGUAGE', 'LAW', 'ORDINAL', 'PERCENT', 'QUANTITY', 'PRODUCT' and 'WORK_OF_ART'
ENTITY_TYPES = set(['FAC', 'GPE', 'LOC', 'NORP',  'ORG',  'PERSON'])


def data_directory(topic: str, data_dir: str):
    return os.path.join(TOPICS_DIR, topic, data_dir)

def abbreviate_topic(topic: str):
    return ABBREVIATIONS.get(topic)


# New datastructure, eventually to replace some of the above
TOPIC_IDX = {
    'bio': ('biomedical', os.path.join(TOPICS_DIR, 'biomedical')),
    'geo': ('geoarchive', os.path.join(TOPICS_DIR, 'geoarchive')),
    'mol': ('molecular_physics', os.path.join(TOPICS_DIR, 'molecular_physics')),
}
