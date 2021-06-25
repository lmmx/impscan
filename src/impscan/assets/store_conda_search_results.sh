FILEPATH=$(dirname $(readlink -f $0))
CONDA_LISTINGS_JSON="$FILEPATH/conda_listings.json"
conda search -c anaconda -c conda-forge --info --json > $CONDA_LISTINGS_JSON
echo "Wrote $CONDA_LISTINGS_JSON"
