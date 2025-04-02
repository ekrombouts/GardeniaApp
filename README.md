This project is under construction

Draai:
source docker/deploy_local.sh

Je database is nu nog leeg. 

pip install -r requirements-dev.txt

# Populate de database met testdata
python scripts/populate_db/01_populate_gardenia.py
python scripts/populate_db/02_upsert_embeddings.py
