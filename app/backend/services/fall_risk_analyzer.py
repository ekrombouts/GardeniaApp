from datetime import date
from enum import Enum
from typing import Any, Dict, List, Tuple

import pandas as pd
from backend.database.db_connection import Database
from backend.llm.embedding_factory import EmbeddingFactory
from backend.llm.llm_factory import LLMFactory
from pydantic import BaseModel, Field
from sqlalchemy import text


class LLMResponse(BaseModel):
    """Response model voor valrisico-inschattingen."""

    gedachtengang: List[str] = Field(
        description="Overwegingen/gedachtengang van de AI-assistent bij het genereren van het antwoord"
    )
    valincident: bool = Field(
        description="een gedocumenteerd valincident in het dossier"
    )

    datum_laatste_valincident: date = Field(
        description="Datum van het laatste valincident in het dossier"
    )

    class ValrisicoEnum(str, Enum):
        ZEER_HOOG = "Zeer hoog"
        HOOG = "Hoog"
        GEMIDDELD = "Gemiddeld"
        LAAG = "Laag"
        ONBEKEND = "Onbekend"

    valrisico: ValrisicoEnum = Field(
        description="Een inschatting van het valrisico van de cliënt"
    )


class FallRiskAnalyzer:
    def __init__(self, client_id: str, start_date: str, end_date: str, limit: int = 5):
        self.client_id = client_id
        self.start_date = start_date
        self.end_date = end_date
        self.limit = limit
        self.context = pd.DataFrame()

    def _get_query_embedding(self, query: str) -> List[float]:
        embedder = EmbeddingFactory(provider="sentence_transformer")
        return embedder.create_embeddings([query])[0]

    def _get_context(self, query_vector: List[float]) -> pd.DataFrame:
        engine = Database().get_engine()
        vector_str = f"ARRAY{query_vector}::vector"

        sql = text(
            f"""SELECT r.client_id, name, ward, datetime, note as content, nfi_embedding <-> {vector_str} AS distance
            FROM records r
            LEFT JOIN clients c ON r.client_id = c.client_id
            WHERE r.client_id = :client_id
            AND datetime >= :start_date
            AND datetime <= :end_date
            ORDER BY distance
            LIMIT :limit"""
        )

        with engine.connect() as conn:
            df = pd.read_sql(
                sql,
                conn,
                params={
                    "client_id": self.client_id,
                    "start_date": self.start_date,
                    "end_date": self.end_date,
                    "limit": self.limit,
                },
            )

        return df

    def _dataframe_to_json(self, df: pd.DataFrame, columns: List[str]) -> str:
        return df[columns].to_json(orient="records", indent=2)

    def _generate_prompt(self, context: pd.DataFrame) -> List[Dict[str, str]]:
        system_prompt = """Je bent een AI-assistent voor een verpleeghuissysteem dat de zorg ondersteunt in het genereren van zorgplannen. 
Je taak is om een inschatting te maken van het valrisico op basis van relevante rapportages uit het cliëntdossier.

# Richtlijnen:
1. Maak een inschatting van het valrisico op basis van de rapportages. NB Angst en verwardheid op zich zijn niet altijd een indicatie van een verhoogd valrisico.
2. Geef aan of de cliënt een valincident heeft gehad en wanneer dit was. NB een bijna valincident is geen valincident.
3. De context wordt op basis van cosine similarity opgehaald; sommige informatie kan ontbreken of irrelevant zijn. Gebruik uitsluitend de relevante rapportages voor het genereren van je antwoord.
4. Vul geen ontbrekende informatie aan en maak geen aannames."""

        context_str = (
            "[]"
            if context.empty
            else self._dataframe_to_json(
                context, ["content", "datetime", "name", "ward"]
            )
        )

        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"# Rapportages:{context_str}"},
        ]

    def _call_llm(self, messages: List[Dict[str, str]]) -> Tuple[LLMResponse, Any]:
        llm = LLMFactory(provider="azureopenai")
        response_parsed, response_raw = llm.create_completion(LLMResponse, messages)
        return LLMResponse(**response_parsed.model_dump()), response_raw

    def analyze(self) -> LLMResponse:
        query_vector = self._get_query_embedding("valrisico, valincidenten")
        self.context = self._get_context(query_vector)
        messages = self._generate_prompt(self.context)
        result, _ = self._call_llm(messages)
        return result


if __name__ == "__main__":
    # Test the FallRiskAnalyzer class
    client_id = "mag001"
    start_date = "2020-10-01"
    end_date = "2023-01-01"
    limit = 5

    fra = FallRiskAnalyzer(
        client_id=client_id,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
    )
    result = fra.analyze()
    print(result)
