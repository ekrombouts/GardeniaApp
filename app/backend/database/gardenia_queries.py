from typing import Any, Dict, Optional

import pandas as pd

# from database.db_connection import Database
from backend.database.db_connection import Database
from sqlalchemy import create_engine, text


class GardeniaData:
    """Database loader for Gardenia data."""

    # Create a database engine using the Database class
    _engine = Database().get_engine()

    @classmethod
    def _get_connection(cls):
        # Get a connection from the database engine
        return cls._engine.connect()

    @classmethod
    def run_query(
        cls, query: str, params: Optional[Dict[str, Any]] = None
    ) -> pd.DataFrame:
        """
        Execute a SQL query and return the result as a pandas DataFrame.
        If an error occurs, return an empty DataFrame.
        """
        try:
            with cls._get_connection() as conn:
                return pd.read_sql(text(query), conn, params=params or {})
        except Exception:
            return pd.DataFrame()

    @classmethod
    def load_table(cls, table_name: str) -> pd.DataFrame:
        """
        Load all rows from a specific table in the database.
        """
        return cls.run_query(f"SELECT * FROM {table_name}")

    @classmethod
    def load_clients(cls) -> pd.DataFrame:
        """
        Load all rows from the 'clients' table.
        """
        return cls.load_table("clients")

    @classmethod
    def load_scenarios(cls) -> pd.DataFrame:
        """
        Load all rows from the 'scenarios' table.
        """
        return cls.load_table("scenarios")

    @classmethod
    def load_records(cls) -> pd.DataFrame:
        """
        Load all rows from the 'records' table.
        """
        return cls.load_table("records")


class GardeniaClients:
    """
    Class to manage and retrieve client data.
    """

    def __init__(self) -> None:
        # Load all clients into a DataFrame
        self.clients = GardeniaData.load_clients()

    def get_client(self, client_id: str) -> "GardeniaClient":
        """
        Retrieve a specific client by their client_id.
        Returns a GardeniaClient object or None if the client is not found.
        """
        row = self.clients[self.clients["client_id"] == client_id]
        if row.empty:
            return None
        return GardeniaClient(client_id, row.iloc[0].to_dict())

    def get_random_client(self) -> "GardeniaClient":
        """
        Retrieve a random client from the loaded clients.
        Returns a GardeniaClient object.
        """
        row = self.clients.sample().iloc[0]
        return GardeniaClient(row["client_id"], row.to_dict())


class GardeniaClient:
    """
    Class to represent a single client and their associated data.
    """

    # Use the same database engine as GardeniaData
    _engine = GardeniaData._engine

    def __init__(
        self, client_id: str, client_details: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Initialize a GardeniaClient object with client_id and optional client details.
        If client details are not provided, fetch them from the database.
        """
        self.client_id = client_id
        self.client_details = client_details or self._fetch_client_details()

        # Basic client information
        self.ward = self.client_details.get("ward") if self.client_details else None
        self.name = self.client_details.get("name") if self.client_details else None
        self.dementia_type = (
            self.client_details.get("dementia_type") if self.client_details else None
        )
        self.physical = (
            self.client_details.get("physical") if self.client_details else None
        )
        self.adl = self.client_details.get("adl") if self.client_details else None
        self.mobility = (
            self.client_details.get("mobility") if self.client_details else None
        )
        self.behavior = (
            self.client_details.get("behavior") if self.client_details else None
        )

    def __str__(self) -> str:
        """
        String representation of the client.
        """
        return f"{self.name} ({self.client_id})"

    def _fetch_client_details(self) -> Optional[Dict[str, Any]]:
        """
        Fetch client details from the database using the client_id.
        Returns a dictionary of client details or None if not found.
        """
        query = "SELECT * FROM clients WHERE client_id = :client_id"
        with self._engine.connect() as conn:
            df = pd.read_sql(text(query), conn, params={"client_id": self.client_id})
        return df.iloc[0].to_dict() if not df.empty else None

    def get_notes(
        self, start_date: Optional[str] = None, end_date: Optional[str] = None
    ) -> Optional[pd.DataFrame]:
        """
        Retrieve notes (records) for the client within an optional date range.
        Returns a pandas DataFrame or None if no client details are available.
        """
        if not self.client_details:
            return None

        query = """
        SELECT * FROM records
        WHERE client_id = :client_id
        """
        params: Dict[str, Any] = {"client_id": self.client_id}

        # Add date filters to the query if provided
        if start_date and end_date:
            query += " AND datetime BETWEEN :start_date AND :end_date"
            params.update({"start_date": start_date, "end_date": end_date})
        elif start_date:
            query += " AND datetime >= :start_date"
            params.update({"start_date": start_date})
        elif end_date:
            query += " AND datetime <= :end_date"
            params.update({"end_date": end_date})

        query += " ORDER BY datetime ASC"

        with self._engine.connect() as conn:
            return pd.read_sql(text(query), conn, params=params)

    def get_scenario(self) -> Optional[pd.DataFrame]:
        """
        Retrieve the scenario associated with the client.
        Returns a pandas DataFrame or None if no client details are available.
        """
        if not self.client_details:
            return None

        query = "SELECT * FROM scenarios WHERE client_id = :client_id"
        with self._engine.connect() as conn:
            return pd.read_sql(text(query), conn, params={"client_id": self.client_id})
