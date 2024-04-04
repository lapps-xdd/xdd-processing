# Collect all elastic files from output/ela, copy them to a common directory
# giving them unique names and compress them for future upload.

TOPICS_DIR=/Users/Shared/data/xdd/topics
OUT_DIR=/Users/Shared/data/xdd/elastic

declare -a domains=(
	biomedical climate-change-modeling cultivars geoarchive
	mars molecular-physics random)

for domain in "${domains[@]}"
do
   echo "Copying $TOPICS_DIR/$domain/output/ela/elastic.json"
   cp $TOPICS_DIR/$domain/output/ela/elastic.json $OUT_DIR/elastic-$domain.json
done

echo "Compressing..."
cd $OUT_DIR
gzip *json
