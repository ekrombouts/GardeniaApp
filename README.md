# Gardenia App

## Gardenia Docker Setup

This setup runs a PostgreSQL database and two versions of the Gardenia app (prod and test) in separate containers, connected via a shared network.

### 1. Preparation

Create the shared network (one-time setup):

```bash
docker network create gardenia-net
```

### 2. Set Secret Parameters

Before populating the database, ensure you set the required secret parameters. 

```bash
export DB_PASSWORD=your_password_here

export OPENAI_API_KEY=your_key_here
export AZURE_OPENAI_API_KEY=your_key_here
export AZURE_OPENAI_ENDPOINT=your_endpoint_here
export ANTHROPIC_API_KEY=
```

Replace `your_password_here` with the actual database password.  
Fill in either OPENAI_API_KEY, ANTHROPIC_API_KEY or AZURE_OPENAI_API_KEY + AZURE_OPENAI_ENDPOINT.

### 3. Start the Database

Start the database container:

```bash
docker-compose -f docker-compose.db.yml -p gardenia-db up -d
```

This ensures:  
    • Container: gardenia-db-container  
    • Volume: gardenia-db_gardenia_data  
    • Network: gardenia-net (external)  

### 4. Start Production and Test Apps

Start the production and/or test app containers:

```bash
docker-compose -f docker-compose.prod.yml -p gardenia-prod up -d --build
docker-compose -f docker-compose.test.yml -p gardenia-test up -d --build
```  

    • Port: 8501 for production, 8502 for test  
    • Network: gardenia-net  

### 5. Install Dependencies

Install the required dependencies for development:

```bash
pip install -r requirements-dev.txt
```

### 6. Populate the Database

Populate the database with test data by running the following scripts:

```bash
python scripts/populate_db/01_populate_gardenia.py
python scripts/populate_db/02_upsert_embeddings.py
```

Your database should now be populated and ready for use.

### 6. Check llm-Settings

Change app/backend/config/llm_config.py as desired.
