import pandas as pd
from backend.database.db_connection import Database
from backend.llm.embedding_factory import EmbeddingFactory
from sqlalchemy import inspect, text
from tqdm import tqdm


# Voeg kolom toe als die nog niet bestaat
def add_column_if_not_exists(engine, column_name: str, embedding_dimension: int):

    inspector = inspect(engine)

    existing_columns = [col["name"] for col in inspector.get_columns("records")]
    if column_name not in existing_columns:
        with engine.begin() as conn:
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
            conn.execute(
                text(
                    f"ALTER TABLE records ADD COLUMN {column_name} vector({embedding_dimension});"
                )
            )


# Update records met embeddings
def update_embeddings(engine, embed_factory: EmbeddingFactory, batch_size: int = 5):
    with engine.connect() as conn:
        column_name = embed_factory.get_embedding_column_name()
        total = (
            conn.execute(
                text(f"SELECT COUNT(*) FROM records WHERE {column_name} IS NULL")
            ).scalar()
            or 0  # prevent NoneType error
        )

    total_batches = (total + batch_size - 1) // batch_size
    pbar = tqdm(total=total_batches, desc="Embedding records")

    while True:
        with engine.connect() as conn:
            result = pd.read_sql(
                text(
                    f"SELECT id, note FROM records WHERE {column_name} IS NULL AND note IS NOT NULL AND note != '' LIMIT :limit"
                ),
                conn,
                params={"limit": batch_size},
            )
        if result.empty:
            break

        with engine.begin() as conn:
            embeddings = embed_factory.create_embeddings(texts=result["note"].tolist())
            for i, (_, row) in enumerate(result.iterrows()):
                conn.execute(
                    text(
                        f"UPDATE records SET {column_name} = :embedding WHERE id = :id"
                    ),
                    {"embedding": embeddings[i], "id": row["id"]},
                )

        pbar.update(1)

    pbar.close()


# Main
def main(provider: str = "sentence_transformer"):
    db = Database()
    engine = db.get_engine()

    embed_factory = EmbeddingFactory(provider=provider)
    add_column_if_not_exists(
        engine=engine,
        column_name=embed_factory.get_embedding_column_name(),
        embedding_dimension=embed_factory.get_dimension(),
    )
    update_embeddings(engine=engine, embed_factory=embed_factory, batch_size=5)


if __name__ == "__main__":
    # main(provider="azureopenai")
    main(provider="sentence_transformer")
