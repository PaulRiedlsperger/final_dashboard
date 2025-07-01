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

    selected_id = st.number_input(
        "Versuchsperson-ID auswählen", 
        min_value=min(person_ids), 
        max_value=max(person_ids), 
        step=1
    )

    person_data = Person.find_person_data_by_id(suchid=selected_id)
    person = Person(person_data)
    age = person.calculate_age()

    st.header("👤 Persönliche Daten")

    col1, col2 = st.columns([1, 2])

    with col1:
        st.image(person.picture_path, width=180)

    with col2:
        st.markdown(f"**🧑 Name:** {person.firstname} {person.lastname}")
        st.markdown(f"**🎂 Alter:** {age} Jahre")
        st.markdown(f"**🆔 ID:** {person.id}")
        st.markdown(f"**🚻 Geschlecht:** {person.gender}")
        st.markdown(f"**📅 Geburtsjahr:** {person.date_of_birth}")

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
    from abnormality import AbnormalityChecker
    from loaddata import read_my_csv
    from abnormality import AbnormalityChecker, show_mini_chart

    # CSV laden
    df = read_my_csv(person.healthdata_path)
    age = person.calculate_age()
    gender = person.gender

    # Letzte Werte extrahieren
    latest_rhr = healthData.get_latest_value(df, "Resting heart rate (bpm)")
    latest_hrv = healthData.get_latest_value(df, "Heart rate variability (ms)")
    latest_temp = healthData.get_latest_value(df, "Skin temp (celsius)")
    latest_sleep = healthData.get_latest_value(df, "Sleep performance %")

    # Dynamische Grenzwerte aus der Klasse holen
    lower_rhr, upper_rhr = AbnormalityChecker.get_rhr_thresholds(age,gender)
    lower_hrv, upper_hrv = AbnormalityChecker.get_hrv_thresholds(age, gender)
    lower_temp, upper_temp = AbnormalityChecker.get_skin_temp_thresholds(gender)
    lower_sleep, upper_sleep = AbnormalityChecker.get_sleep_score_thresholds()

    # Analyse
    rhr_warning = AbnormalityChecker.check_rhr(latest_rhr,person.calculate_age(), person.gender)
    hrv_warning = AbnormalityChecker.check_hrv(latest_hrv, person.calculate_age(), person.gender)
    temp_warning = AbnormalityChecker.check_skin_temp(latest_temp, person.calculate_age(), person.gender)
    sleep_warning = AbnormalityChecker.check_sleep_score(latest_temp, person.calculate_age(), person.gender)

    # Ausgabe
    # RHR
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown(f"**💖 RHR:** {rhr_warning}")
    with col2:
        st.plotly_chart(show_mini_chart(current=latest_rhr, lower=lower_rhr, upper=upper_rhr, unit="bpm"), use_container_width=True)

    # HRV
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown(f"**💕 HRV:** {hrv_warning}")
    with col2:
        st.plotly_chart(show_mini_chart(current=latest_hrv, lower=lower_hrv, upper=upper_hrv, unit="ms"), use_container_width=True)

    # Temperatur
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown(f"**🌡️ Hauttemperatur:** {temp_warning}")
    with col2:
        st.plotly_chart(show_mini_chart(current=latest_temp, lower=lower_temp, upper=upper_temp, unit="°C"), use_container_width=True)

    # Schlafscore
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown(f"**😴 Schlafscore:** {sleep_warning}")
    with col2:
        st.plotly_chart(show_mini_chart(current=latest_sleep, lower=lower_sleep, upper=upper_sleep, unit="%"), use_container_width=True)
            
    result_link = person.healthdata_path
    df = read_my_csv(result_link)
   

        