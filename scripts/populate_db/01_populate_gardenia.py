"""
This script populates the GardeniaApp database with data from Hugging Face datasets.
It checks if the required tables already exist and allows the user to replace, append, or cancel the operation.
"""

import pandas as pd
from backend.database.db_connection import Database
from datasets import load_dataset
from sqlalchemy import inspect, text


def add_id_column(engine, table_name):
    """
    Adds an 'id' column as a SERIAL PRIMARY KEY to the specified table if it doesn't already exist.
    """
    inspector = inspect(engine)
    if "id" not in [col["name"] for col in inspector.get_columns(table_name)]:
        query = f"""ALTER TABLE {table_name}
        ADD COLUMN "id" SERIAL PRIMARY KEY;"""
        with engine.begin() as conn:
            conn.execute(text(query))
        print(f"Added 'id' column to {table_name}")


def load_and_write_dataset(dataset_name, table_name, engine):
    """
    Loads a dataset from Hugging Face, converts it to a pandas DataFrame, and writes it to the database.
    Handles cases where the table already exists by allowing the user to replace, append, or cancel the operation.
    """
    # Load the dataset and convert it to a pandas DataFrame
    df = load_dataset(path=dataset_name, split="train").to_pandas()

    # Check if the table already exists in the database
    inspector = inspect(engine)
    if inspector.has_table(table_name):
        # Prompt the user for action if the table exists
        action = (
            input(
                f"Table '{table_name}' already exists. Do you want to (r)eplace, (a)ppend, or (c)ancel? "
            )
            .strip()
            .lower()
        )
        if action == "r":
            # Replace the existing table with the new data
            df.to_sql(name=table_name, con=engine, if_exists="replace", index=True)
            print(f"DataFrame for {table_name} successfully replaced in the database!")
        elif action == "a":
            # Append the new data to the existing table
            df.to_sql(name=table_name, con=engine, if_exists="append", index=True)
            print(f"DataFrame for {table_name} successfully appended to the database!")
        elif action == "c":
            # Cancel the operation
            print(f"Operation for {table_name} cancelled.")
        else:
            # Handle invalid input
            print(f"Invalid action. Operation for {table_name} cancelled.")
    else:
        # If the table does not exist, create it and write the data
        df.to_sql(name=table_name, con=engine, if_exists="replace", index=True)
        print(f"DataFrame for {table_name} successfully written to the database!")

    # Add an 'id' column to the table if it doesn't already exist
    add_id_column(engine, table_name)


def main():
    """
    Main function to initialize the database connection and populate it with data from Hugging Face datasets.
    """
    db = Database()
    engine = db.get_engine()

    # List of Hugging Face datasets to be loaded and written to the database
    hf_datasets = [
        "ekrombouts/Gardenia_notes",
        "ekrombouts/Gardenia_clients",
        "ekrombouts/Gardenia_scenarios",
        "ekrombouts/Gardenia_records",
    ]

    # Check if all tables corresponding to the datasets already exist in the database
    inspector = inspect(engine)
    all_tables_exist = all(
        inspector.has_table(dataset.split("/")[-1].split("_")[-1])
        for dataset in hf_datasets
    )

    if all_tables_exist:
        # If all tables exist, print a message indicating the database is already populated
        print("The database is running and contains data.")
    else:
        # Loop through each dataset, derive the table name, and write the data to the database
        for dataset in hf_datasets:
            table_name = dataset.split("/")[-1].split("_")[-1]
            load_and_write_dataset(dataset, table_name, engine)


if __name__ == "__main__":
    main()
