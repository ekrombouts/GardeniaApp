#!/bin/bash

# Variabelen instellen
RESOURCE_GROUP="rg-gardenia-app"
KEYVAULT_NAME="kv-gardenia"
REGISTRY_NAME="gardeniaapp"
CONTAINER_NAME="gardenia-app-container"
IMAGE_NAME="gardeniaapp.azurecr.io/gardenia:v1.0-azure"
DNS_LABEL="gardeniaapp-demo"
DB_HOST="db-gardenia-data.postgres.database.azure.com"
# DB_HOST="gardenia-db-container"
DB_NAME="gardenia"
DB_USER="gardenia"
DB_PORT="5432"
APP_PORT="8501"

# Wachtwoorden ophalen uit Key Vault
DB_PASSWORD=$(az keyvault secret show --vault-name $KEYVAULT_NAME --name DB-PASS --query value -o tsv)
REG_PASSWORD=$(az keyvault secret show --vault-name $KEYVAULT_NAME --name REGISTRY-PASSWORD --query value -o tsv)

# Docker image bouwen en pushen
# Platform linux/amd64 toevoegen voor cross-platform support
# Docker image bouwen en pushen
docker build -f Dockerfile --platform linux/amd64 -t $IMAGE_NAME .

# Pushen naar Azure Container Registry
az acr login --name $REGISTRY_NAME
docker push $IMAGE_NAME
# Bestaande container verwijderen
az container delete --resource-group $RESOURCE_GROUP --name $CONTAINER_NAME --yes

# Nieuwe container aanmaken
az container create \
  --resource-group $RESOURCE_GROUP \
  --name $CONTAINER_NAME \
  --image $IMAGE_NAME \
  --registry-login-server "$REGISTRY_NAME.azurecr.io" \
  --registry-username $REGISTRY_NAME \
  --registry-password "$REG_PASSWORD" \
  --restart-policy OnFailure \
  --dns-name-label $DNS_LABEL \
  --ports 8501 \
  --os-type Linux \
  --cpu 1 \
  --memory 1.5 \
  --environment-variables DB_HOST=$DB_HOST DB_NAME=$DB_NAME DB_USER=$DB_USER DB_PORT=$DB_PORT APP_PORT=$APP_PORT\
  --secure-environment-variables DB_PASSWORD="$DB_PASSWORD"


echo "Je Gardenia app is beschikbaar op:"
APP_URL=$(az container show --resource-group $RESOURCE_GROUP --name $CONTAINER_NAME --query ipAddress.fqdn -o tsv)
echo "http://$APP_URL:8501"

