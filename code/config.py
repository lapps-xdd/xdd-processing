import os

# location of all the topics
TOPICS_DIR = '/Users/Shared/data/xdd/doc2vec/topic_doc2vecs'

# list of topics
TOPICS = ('biomedical',  'geoarchive', 'molecular_physics')

# data directories of source data and processing layers
DATA_DIRS = ('text', 'scienceparse', 'processed_doc', 'processed_ner', 'processed_pos')


def data_directory(topic: str, data_dir: str):
    return os.path.join(TOPICS_DIR, topic, data_dir)