import ast
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from backend.database.db_connection import Database
from backend.llm.embedding_visualizer import create_interactive_plot
from sqlalchemy import text
from sqlalchemy.engine import Engine
from umap import UMAP

engine: Engine = Database().get_engine()

root = Path(__file__).resolve().parents[2]
model_folder = root / "app" / "backend" / "models"
plot_folder = root / "output"


def get_embedding_data(
    table_name: str = "notes",
    embedding_column: str = "nfi_embedding",
    text_column: str = "note",
    category_column: str = "client_id",
) -> pd.DataFrame:
    query: str = f"""
    SELECT id, {category_column} as category, {text_column} as text, {embedding_column} as embedding
    FROM {table_name};
    """
    with engine.connect() as conn:
        df: pd.DataFrame = pd.read_sql(text(query), conn)
    return df


def main() -> None:
    table_name = "notes"
    embedding_column = "nfi_embedding"
    text_column = "note"
    category_column = "category"

    df: pd.DataFrame = get_embedding_data(
        table_name=table_name,
        embedding_column=embedding_column,
        text_column=text_column,
        category_column=category_column,
    )
    df.dropna(inplace=True)

    n_components = 2
    random_state = 6
    n_neighbors = 15  # Default: 15. Lower values give more spread out embeddings, higher values give more clustered embeddings
    min_dist = 0.02  # Default: 0.1. Lower values give more clustered embeddings, higher values give more spread out embeddings

    reducer = UMAP(
        n_components=n_components,
        random_state=random_state,
        n_neighbors=n_neighbors,
        min_dist=min_dist,
        n_jobs=1,  # Prevents UMAP from using multiple threads that can cause crashes in Docker
    )

    df["embedding"] = df["embedding"].apply(ast.literal_eval)
    embeddings: np.ndarray = np.vstack(df["embedding"])
    reduced_embeddings = reducer.fit_transform(embeddings)

    joblib.dump(
        value=reducer,
        filename=model_folder / f"{table_name}_umap_2d.pkl",
    )

    df["reduced_embeddings"] = list(reduced_embeddings)

    title = f"2D Visualization of Reduced Embeddings using UMAP"
    caption = f"Parameters: n_neighbors={n_neighbors}, min_dist={min_dist}, random_state={random_state}"
    fig = create_interactive_plot(
        data=df,
        embedding_column="reduced_embeddings",
        color_column=category_column,
        hover_column="text",
        title=title,
        caption=caption,
    )

    fig.write_html(plot_folder / f"notes_UMAP_2d_plot.html")


if __name__ == "__main__":
    main()
