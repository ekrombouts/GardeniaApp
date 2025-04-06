import datetime as dt

import streamlit as st
import streamlit.components.v1 as components
from backend.database.gardenia_queries import GardeniaClient, GardeniaClients
from backend.services.generate_client_embedding_plot import create_client_embedding_plot
from dotenv import load_dotenv

load_dotenv()


def main():
    # Page configuration affects the layout of the app
    st.set_page_config(
        page_title="Gardenia App",
        page_icon=":tulip:",
        layout="centered",
        initial_sidebar_state="auto",
    )
    st.title("🌷 Gardenia Dashboard-dev 🌷")

    # Display a loading spinner while fetching data
    with st.spinner("Loading data..."):
        clients_df = GardeniaClients().clients
        st.markdown(
            "[Bekijk de Gardenia-collectie op Hugging Face](https://huggingface.co/collections/ekrombouts/gardenia-66fd983fd8ef894b11f418a1)"
        )

    # Allow the user to select a ward and client
    selected_ward, client_id = select_client(clients_df)
    gardenia_client = GardeniaClient(client_id)

    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        [
            "Cliëntprofiel",  # Client profile
            "Scenario",  # Scenarios
            "Rapportages",  # Reports
            "Visualisatie",  # Visualization
            "Info",  # Information
        ]
    )

    # Display content for each tab
    with tab1:
        display_client_profile(gardenia_client)

    with tab2:
        display_scenarios(gardenia_client)

    with tab3:
        display_reports(gardenia_client)

    with tab4:
        # Display the client embedding plot
        display_client_embedding_plot(client_id)

    with tab5:
        # Display information about the app
        st.subheader("ℹ️ Informatie")
        st.markdown(
            f"""
            Deze app toont GardeniaData, een fictieve zorgdatabase van verpleeghuis Gardenia.
De volledig synthetische data bevatten cliëntprofielen, scenario’s en automatisch gegenereerde zorgrapportages. Ze bieden een veilige testomgeving voor AI in de langdurige zorg.

De dataset is onderdeel van mijn leerproces. Verbeteringen en uitbreidingen zijn in de toekomst mogelijk.

gardenia:v1.2-test April 2025: Added visualization tab with embedding plot.

https://github.com/ekrombouts/GardeniaApp
            """
        )


def select_client(clients_df):
    # Allow the user to select a ward and client from dropdowns
    col1, col2 = st.columns(2)
    with col1:
        selected_ward = st.selectbox(
            "Selecteer een afdeling:",  # Select a ward
            options=clients_df["ward"].unique(),
        )
    with col2:
        client_id = st.selectbox(
            "Selecteer een cliënt:",  # Select a client
            options=clients_df[clients_df["ward"] == selected_ward]["client_id"],
            format_func=lambda x: clients_df[clients_df["client_id"] == x][
                "name"
            ].values[0],
        )
    return selected_ward, client_id


def display_client_profile(gardenia_client):
    # Display the profile of the selected client
    st.subheader(f"🪪 Profiel van {gardenia_client.name}")
    st.markdown(
        f"""
        | **Kenmerk**         | **Beschrijving**                      |
        |---------------------|---------------------------------|
        | **Afdeling**        | {gardenia_client.ward}       |
        | **Diagnose**        | {gardenia_client.dementia_type} |
        | **Somatiek**        | {gardenia_client.physical}   |
        | **ADL**             | {gardenia_client.adl}        |
        | **Mobiliteit**      | {gardenia_client.mobility}   |
        | **Gedrag**          | {gardenia_client.behavior}   |
        """,
        unsafe_allow_html=True,
    )


def display_scenarios(gardenia_client):
    # Display scenarios for the selected client
    st.subheader("🎬 Scenario")
    client_scenarios = gardenia_client.get_scenario()
    if not client_scenarios.empty:
        st.table(
            client_scenarios[["week", "scenario"]]
            .rename(columns={"week": "Week", "scenario": "Scenario"})
            .reset_index(drop=True)
        )
    else:
        st.warning("Geen scenario's gevonden voor deze cliënt.")  # No scenarios found


def display_reports(gardenia_client):
    # Display reports for the selected client
    client_records = gardenia_client.get_notes()
    st.subheader("📋 Rapportages")
    selected_start_date, selected_end_date = select_date_range(client_records)
    if selected_start_date and selected_end_date:
        st.markdown("#### Rapportages")
        client_notes = gardenia_client.get_notes(
            start_date=selected_start_date, end_date=selected_end_date
        )
        if not client_notes.empty:
            for _, row in client_notes.iterrows():
                st.markdown(f"- **{row['datetime']}**: {row['note']}")
        else:
            st.info(
                "Geen rapportages gevonden voor de opgegeven periode."
            )  # No reports found


def select_date_range(client_records):
    # Allow the user to select a date range for reports
    selected_start_date = None
    selected_end_date = None

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("##### Van/Tot")  # From/To
        start_date = st.date_input(
            "Startdatum:",  # Start date
            value=(
                client_records["datetime"].min().date()
                if not client_records.empty
                else None
            ),
        )
        end_date = st.date_input(
            "Einddatum:",  # End date
            value=(
                client_records["datetime"].max().date()
                if not client_records.empty
                else None
            ),
        )
        if st.button("Toon Rapportages", key="manual_range"):  # Show reports
            selected_start_date = start_date
            selected_end_date = end_date

    with col2:
        st.markdown("##### Weeknummer")  # Week number
        selected_week = st.number_input(
            "Weeknummer:",  # Week number
            min_value=1,
            value=1,
            step=1,
            help="Kies een weeknummer van het verblijf.",  # Choose a week number
        )
        if st.button("Toon week", key="select_week"):  # Show week
            min_date = (
                client_records["datetime"].min().date()
                if not client_records.empty
                else None
            )
            if min_date:
                selected_start_date = min_date + dt.timedelta(weeks=selected_week - 1)
                selected_end_date = selected_start_date + dt.timedelta(weeks=1)

    with col3:
        st.markdown("##### Eerste 6 weken")  # First 6 weeks
        if st.button("Toon weken", key="first_six_weeks"):  # Show weeks
            min_date = (
                client_records["datetime"].min().date()
                if not client_records.empty
                else None
            )
            if min_date:
                selected_start_date = min_date
                selected_end_date = min_date + dt.timedelta(weeks=6)

    if selected_start_date and selected_end_date:
        st.session_state["selected_start_date"] = selected_start_date
        st.session_state["selected_end_date"] = selected_end_date

    return selected_start_date, selected_end_date


def display_client_embedding_plot(client_id):
    st.subheader("📊 Embedding Plot")
    if st.button("Toon Embedding Plot"):
        with st.spinner("Genereren van de embedding plot..."):
            html_path = create_client_embedding_plot(client_id)

            # **Laad en toon HTML in Streamlit**
            with open(html_path, "r", encoding="utf-8") as f:
                html_content = f.read()

            components.html(html_content, height=600, width=700, scrolling=True)


if __name__ == "__main__":
    main()
