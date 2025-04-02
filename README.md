# Gardenia App

Welcome to the Gardenia App! This project is currently under construction.

## Getting Started

Follow the steps below to set up and populate the database with test data.

### 1. Deploy Locally

Run the following script to deploy the application locally:

```bash
source docker/deploy_local.sh
```

### 2. Install Dependencies

Install the required dependencies for development:

```bash
pip install -r requirements-dev.txt
```

### 3. Populate the Database

Populate the database with test data by running the following scripts:

```bash
python scripts/populate_db/01_populate_gardenia.py
python scripts/populate_db/02_upsert_embeddings.py
```

Your database should now be populated and ready for use.

---

Thank you for contributing to the Gardenia App!
