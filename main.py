import streamlit as st
import json
from person import Person
from PIL import Image
from loaddata import read_my_csv
from healthdata import healthData

tab1 ,tab2 ,tab3 = st.tabs(["Versuchsperson", "Gesundheitsdaten", "Abnormalitäten"])

with tab1:
    person_list = Person.load_person_data()
    person_ids = [p["id"] for p in person_list]

    selected_id = st.number_input("Versuchsperson-ID auswählen", min_value=min(person_ids), max_value=max(person_ids), step=1)

    person_data = Person.find_person_data_by_id(suchid=selected_id)
    person = Person(person_data)
    age = person.calculate_age()

    st.header("Persönliche Daten")
    st.image(person.picture_path, width=200)
    st.markdown(f"**Name:** {person.firstname}")
    st.markdown(f"**Alter:** {age} Jahre")
    st.markdown(f"**ID:** {person.id}")

with tab2:
    st.header("📊 Gesundheitsdaten")

    filepath = person.healthdata_path
    df = read_my_csv(filepath)


    # Durchschnittswerte berechnen
    avg_rhr = healthData.get_average_Resting_heart_rate(df)
    avg_hrv = healthData.get_average_Heart_rate_variability(df)
    avg_temp = healthData.get_average_Skin_temp_celsius(df)
    avg_sleep = healthData.get_average_Sleep_performance_percent(df)

    # Darstellung in 2 Spalten
    col1, col2 = st.columns(2)
    with col1:
        st.metric("🫀 Ruheherzfrequenz (bpm)", f"{avg_rhr:.1f}")
        st.metric("🌡️ Hauttemperatur (°C)", f"{avg_temp:.1f}")
    with col2:
        st.metric("💓 Herzfrequenz-Variabilität (ms)", f"{avg_hrv:.1f}")
        st.metric("😴 Schlafscore (%)", f"{avg_sleep:.1f}")

    st.divider()
    st.subheader("📈 Verlauf der Gesundheitswerte")

    # Mehrere Plots anzeigen
    st.plotly_chart(healthData.plot_RHR(df), use_container_width=True)
    st.plotly_chart(healthData.plot_HRV(df), use_container_width=True)
    st.plotly_chart(healthData.plot_skin_temp(df), use_container_width=True)
    st.plotly_chart(healthData.plot_sleep_performance(df), use_container_width=True)

with tab3:
    pass


        

   

    

    