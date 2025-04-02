import datetime as dt

import streamlit as st
from backend.database.gardenia_queries import GardeniaClient, GardeniaClients
from dotenv import load_dotenv

load_dotenv()


def main():
    st.set_page_config(page_title="Gardenia App", page_icon=":tulip:")
    st.title("🌷 Gardenia Dashboard- 🌷")

    # Client selection
    with st.spinner("Loading data..."):
        clients_df = GardeniaClients().clients
        st.markdown(
            "[Bekijk de Gardenia-collectie op Hugging Face](https://huggingface.co/collections/ekrombouts/gardenia-66fd983fd8ef894b11f418a1)"
        )

    selected_ward, client_id = select_client(clients_df)
    gardenia_client = GardeniaClient(client_id)

    tab1, tab2, tab3, tab4 = st.tabs(
        [
            "Cliëntprofiel",
            "Scenario",
            "Rapportages",
            "Info",
        ]
    )

    with tab1:
        display_client_profile(gardenia_client)

    with tab2:
        display_scenarios(gardenia_client)

    with tab3:
        display_reports(gardenia_client)

    with tab4:
        st.subheader("ℹ️ Informatie")
        st.markdown(
            f"""
            Deze app toont GardeniaData, een fictieve zorgdatabase van verpleeghuis Gardenia.
De volledig synthetische data bevatten cliëntprofielen, scenario’s en automatisch gegenereerde zorgrapportages. Ze bieden een veilige testomgeving voor AI in de langdurige zorg.

De dataset is onderdeel van mijn leerproces. Verbeteringen en uitbreidingen zijn in de toekomst mogelijk.

gardenia:v1.0 april 2025
            """
        )


def select_client(clients_df):
    col1, col2 = st.columns(2)
    with col1:
        selected_ward = st.selectbox(
            "Selecteer een afdeling:", options=clients_df["ward"].unique()
        )
    with col2:
        client_id = st.selectbox(
            "Selecteer een cliënt:",
            options=clients_df[clients_df["ward"] == selected_ward]["client_id"],
            format_func=lambda x: clients_df[clients_df["client_id"] == x][
                "name"
            ].values[0],
        )
    return selected_ward, client_id


def display_client_profile(gardenia_client):
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
    st.subheader("🎬 Scenario")
    client_scenarios = gardenia_client.get_scenario()
    if not client_scenarios.empty:
        st.table(
            client_scenarios[["week", "scenario"]]
            .rename(columns={"week": "Week", "scenario": "Scenario"})
            .reset_index(drop=True)
        )
    else:
        st.warning("Geen scenario's gevonden voor deze cliënt.")


def display_reports(gardenia_client):
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
            st.info("Geen rapportages gevonden voor de opgegeven periode.")


def select_date_range(client_records):
    selected_start_date = None
    selected_end_date = None

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("##### Van/Tot")
        start_date = st.date_input(
            "Startdatum:",
            value=(
                client_records["datetime"].min().date()
                if not client_records.empty
                else None
            ),
        )
        end_date = st.date_input(
            "Einddatum:",
            value=(
                client_records["datetime"].max().date()
                if not client_records.empty
                else None
            ),
        )
        if st.button("Toon Rapportages", key="manual_range"):
            selected_start_date = start_date
            selected_end_date = end_date

    with col2:
        st.markdown("##### Weeknummer")
        selected_week = st.number_input(
            "Weeknummer:",
            min_value=1,
            value=1,
            step=1,
            help="Kies een weeknummer van het verblijf.",
        )
        if st.button("Pas weeknummer toe", key="select_week"):
            min_date = (
                client_records["datetime"].min().date()
                if not client_records.empty
                else None
            )
            if min_date:
                selected_start_date = min_date + dt.timedelta(weeks=selected_week - 1)
                selected_end_date = selected_start_date + dt.timedelta(weeks=1)

    with col3:
        st.markdown("##### Eerste 6 weken")
        if st.button("Selecteer eerste 6 weken", key="first_six_weeks"):
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


if __name__ == "__main__":
    main()
