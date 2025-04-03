# Gardenia App

## Gardenia Docker Setup

This setup runs a PostgreSQL database and two versions of the Gardenia app (prod and test) in separate containers, connected via a shared network.

### 1. Preparation

Create the shared network (one-time setup):

```bash
docker network create gardenia-net
```

### 2. Start the Database

Start the database container:

```bash
docker-compose -f docker-compose.db.yml -p gardenia-db up -d
```

This ensures:  
    • Container: gardenia-db-container  
    • Volume: gardenia-db_gardenia_data  
    • Network: gardenia-net (external)  

### 3. Start Production and Test Apps

Start the production and test app containers:

```bash
docker-compose -f docker-compose.prod.yml -p gardenia-prod up -d --build
docker-compose -f docker-compose.test.yml -p gardenia-test up -d --build
```  

    • Port: 8501 for production, 8502 for test  
    • Network: gardenia-net  

### 4. Install Dependencies

Install the required dependencies for development:

```bash
pip install -r requirements-dev.txt
```

### 5. Populate the Database

Populate the database with test data by running the following scripts:

```bash
python scripts/populate_db/01_populate_gardenia.py
python scripts/populate_db/02_upsert_embeddings.py
```

Your database should now be populated and ready for use.
