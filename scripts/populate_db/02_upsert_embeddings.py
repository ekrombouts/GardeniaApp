"""
This script populates a specified table in the database with embeddings for text data.
It ensures the necessary embedding column exists and updates rows where embeddings are missing.
The embeddings are generated using a specified provider, such as Sentence Transformer or Azure OpenAI.
"""

import pandas as pd
from backend.database.db_connection import Database
from backend.llm.embedding_factory import EmbeddingFactory
from sqlalchemy import inspect, text
from tqdm import tqdm


def ensure_vector_extension(engine):
    """Ensure the 'vector' extension is enabled in the database."""
    with engine.begin() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))


def get_existing_columns(engine, table_name: str):
    """Retrieve the list of existing columns in a table."""
    inspector = inspect(engine)
    return [col["name"] for col in inspector.get_columns(table_name)]


def add_column(engine, table_name: str, column_name: str, column_type: str):
    """Add a column to a table."""
    with engine.begin() as conn:
        conn.execute(
            text(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type};")
        )


def add_embedding_column_if_not_exists(
    engine, table_name: str, column_name: str, embedding_dimension: int
):
    """Add the embedding column to the specified table if it does not already exist."""
    ensure_vector_extension(engine)
    existing_columns = get_existing_columns(engine, table_name)
    if column_name not in existing_columns:
        add_column(engine, table_name, column_name, f"vector({embedding_dimension})")


def fetch_rows_for_embedding(
    engine, table_name: str, column_name: str, batch_size: int
):
    """Fetch a batch of rows where the embedding column is NULL and the 'note' column is not empty."""
    with engine.connect() as conn:
        result = pd.read_sql(
            text(
                f"SELECT id, note FROM {table_name} WHERE {column_name} IS NULL AND note IS NOT NULL AND note != '' LIMIT :limit"
            ),
            conn,
            params={"limit": batch_size},
        )
    return result


def update_row_embeddings(engine, table_name: str, column_name: str, rows, embeddings):
    """Update the embedding column for a batch of rows."""
    with engine.begin() as conn:
        for i, (_, row) in enumerate(rows.iterrows()):
            conn.execute(
                text(
                    f"UPDATE {table_name} SET {column_name} = :embedding WHERE id = :id"
                ),
                {"embedding": embeddings[i], "id": row["id"]},
            )


def count_null_embeddings(engine, table_name: str, column_name: str):
    """Count the total number of rows where the embedding column is NULL."""
    with engine.connect() as conn:
        return (
            conn.execute(
                text(f"SELECT COUNT(*) FROM {table_name} WHERE {column_name} IS NULL")
            ).scalar()
            or 0
        )


def update_embeddings(
    engine, table_name: str, embed_factory: EmbeddingFactory, batch_size: int = 5
):
    """Update the specified table with embeddings for rows where the embedding column is NULL."""
    column_name = embed_factory.get_embedding_column_name()
    total = count_null_embeddings(engine, table_name, column_name)
    total_batches = (total + batch_size - 1) // batch_size
    pbar = tqdm(total=total_batches, desc="Embedding batches", unit="batch")

    while True:
        rows = fetch_rows_for_embedding(engine, table_name, column_name, batch_size)
        if rows.empty:
            break

        embeddings = embed_factory.create_embeddings(texts=rows["note"].tolist())
        update_row_embeddings(engine, table_name, column_name, rows, embeddings)
        pbar.update(1)

    pbar.close()


def initialize_database_and_factory(provider: str):
    """Initialize the database connection and embedding factory."""
    db = Database()
    engine = db.get_engine()
    embed_factory = EmbeddingFactory(provider=provider)
    return engine, embed_factory


def main(provider: str = "sentence_transformer", table_name: str = "records"):
    """Main function to add the embedding column (if needed) and update embeddings."""
    engine, embed_factory = initialize_database_and_factory(provider)
    add_embedding_column_if_not_exists(
        engine=engine,
        table_name=table_name,
        column_name=embed_factory.get_embedding_column_name(),
        embedding_dimension=embed_factory.get_dimension(),
    )
    update_embeddings(
        engine=engine, table_name=table_name, embed_factory=embed_factory, batch_size=50
    )


if __name__ == "__main__":
    # Uncomment the line below to use Azure OpenAI as the embedding provider
    main(provider="azureopenai", table_name="records")
    # main(
    #     provider="sentence_transformer", table_name="records"
    # )  # Default to using Sentence Transformer
