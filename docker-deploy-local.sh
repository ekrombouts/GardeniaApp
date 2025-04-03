# Wachtwoorden ophalen uit Key Vault
DB_PASSWORD=$(az keyvault secret show --vault-name "kv-gardenia" --name DB-PASS --query value -o tsv)

# Stop en verwijder de huidige containers
docker-compose down --remove-orphans 
docker system prune -af

export DB_PASSWORD 
docker-compose build --no-cache
docker-compose up -d
