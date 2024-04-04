# Convenience script to run some processing on a directory.
#
# Requires jq to be installed
#
# Assumes that this is run from the code directory (one level up from this script)
# and that the xdd-docprocessing and xdd-terms repositories are sisters of this
# repository.
#
# Usage:
#
# $ bash run.sh -d DIRECTORY -m MODE -t TAGS
#
# The -d option is the directory to run this on, it should have a file name
# metadata.json as well as subdirectories scienceparse and text. The -m option
# indicates the mode and the -t option is a comma-separated list of tags, which
# are only used for the merging mode.
#
# There are five modes:
#
#    doc -- runs document processing
#    ner -- runs spaCy NER
#    trm -- runs term extraction
#    cla -- runs the classifier (not implemented yet)
#    mer -- runs the merger code and creates EalsticSearch input
#
# For all modes, output is written to subdirectories of DIRECTORY/output.


while getopts "d:m:t:" option; do
    case "${option}" in
        d) data=${OPTARG} ;;
        m) mode=${OPTARG} ;;
        t) tags=${OPTARG} ;;
        *) echo "Usage: bash merge.sh -d DIRECTORY -m MODE -t TAGS -c N"; exit ;;
    esac
done

echo "DATA: $data"
echo "MODE: $mode"
echo "TAGS: $tags"

if [ "$mode" == "doc" ]; then

	echo 'Document structure parsing'
	cd ../../xdd-docstructure/code
	python parse.py --scpa $data/scienceparse --text $data/text --out $data/output/doc

elif [ $mode == 'ner' ]; then

	echo "Running spaCy"
	python ner.py --doc $data/output/doc --pos $data/output/pos --ner $data/output/ner

elif [ $mode == 'trm' ]; then

	echo "Running term extraction"
	cd ../../xdd-terms/code
	python pos2phr.py --pos $data/output/pos --out /$data/output/trm
	python accumulate.py --terms $data/output/trm

elif [ $mode == 'cla' ]; then

	echo "Running classifier, NOT"

elif [ $mode == 'mer' ]; then

	echo "Running merging code and creating ElasticSearch input"
	python merge.py --scpa $data/scienceparse --doc $data/output/doc --ner $data/output/ner --trm $data/output/trm --meta $data/metadata.json --out $data/output/mer
	python prepare_elastic.py -i $data/output/mer -o $data/output/ela --tags $tags
	head -2 $data/output/ela/elastic.json | tail -1 | jq > $data/output/ela/example.json

fi

