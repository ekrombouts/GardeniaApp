from sqlalchemy import text


def get_nearest_neighbors(
    query_text: str,
    table: str,
    text_column: str,
    embedding_factory,
    engine,
    limit: int = 5,
    distance_op: str = "<->",
    filters: dict = None,
):
    embedding = embedding_factory.create_embeddings(texts=[query_text])[0]
    embedding_column = embedding_factory.get_embedding_column_name()

    where_clauses = []
    params = {"embedding": embedding, "limit": limit}

    if filters:
        for i, (key, value) in enumerate(filters.items()):
            if isinstance(value, list):
                for j, (op, val) in enumerate(value):
                    param_key = f"filter_{i}_{j}"
                    where_clauses.append(f"{key} {op} :{param_key}")
                    params[param_key] = val
            else:
                param_key = f"filter_{i}"
                where_clauses.append(f"{key} = :{param_key}")
                params[param_key] = value

    where_sql = " AND " + " AND ".join(where_clauses) if where_clauses else ""

    sql = f"""
        SELECT id, {text_column}, ({embedding_column}) {distance_op} (:embedding)::vector AS similarity
        FROM {table}
        WHERE 1=1
        {where_sql}
        ORDER BY similarity ASC
        LIMIT :limit;
    """

    with engine.connect() as conn:
        result = conn.execute(text(sql), params)
        return result.fetchall()
