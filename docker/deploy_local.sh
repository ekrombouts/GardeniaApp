#!/bin/bash

# Variabelen instellen
RESOURCE_GROUP="rg-gardenia-app"
KEYVAULT_NAME="kv-gardenia"
IMAGE_NAME="gardenia:v1.0-local"
DB_HOST="gardenia-db-container"
DB_NAME="gardenia"
DB_USER="gardenia"
DB_PORT="5432"
# Wachtwoorden ophalen uit Key Vault
DB_PASSWORD=$(az keyvault secret show --vault-name $KEYVAULT_NAME --name DB-PASS --query value -o tsv)

docker-compose down --remove-orphans
docker system prune -af
export IMAGE_NAME DB_HOST DB_NAME DB_USER DB_PORT DB_PASSWORD
docker-compose build --no-cache
docker-compose up -d

echo "Je Gardenia app is lokaal beschikbaar op:"
echo "http://localhost:8501"