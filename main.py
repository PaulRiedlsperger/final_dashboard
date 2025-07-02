import streamlit as st
import json
from person import Person # Stelle sicher, dass Person-Klasse importiert ist
from PIL import Image
from loaddata import read_my_csv, read_my_csv_2 # read_my_csv_2 hinzugefügt
from healthdata import healthData
import os # Importieren für Dateisystemoperationen
import pandas as pd # Für das Speichern der CSV-Datei
from abnormality import AbnormalityChecker, plot_abnormalities_over_time # plot_abnormalities_over_time importieren
from datetime import datetime # DIESE ZEILE BLEIBT
import plotly.graph_objects as go


# WICHTIG: Importiere die neue Löschfunktion aus person.py
from person import add_new_person_to_db, save_uploaded_file, delete_person_from_db

# Set page config (optional, aber gut für Layout)
st.set_page_config(layout="wide")


# Initialisiere session_state, falls nicht vorhanden
if 'add_person_mode' not in st.session_state:
    st.session_state.add_person_mode = False
if 'confirm_delete_id' not in st.session_state: # Zustand für Löschbestätigung
    st.session_state.confirm_delete_id = None # Speichert die ID der Person, die zum Löschen ansteht
if 'show_recommendations' not in st.session_state: # Zustand für Empfehlungsanzeige
    st.session_state.show_recommendations = False
if 'current_recommendations' not in st.session_state: # Speichert die generierten Empfehlungen
    st.session_state.current_recommendations = []
if 'analyzed_df' not in st.session_state: # Speichert das analysierte DataFrame für Abnormalitäten
    st.session_state.analyzed_df = pd.DataFrame() # Initialisiere als leeres DataFrame

tab1, tab2, tab3 = st.tabs(["Versuchsperson", "Gesundheitsdaten", "Abnormalitäten"])

with tab1:
    st.header("Versuchsperson")

    # ----- UI für das Hinzufügen einer neuen Person -----
    col_add_btn, col_back_btn = st.columns([0.2, 0.8])

    with col_add_btn:
        if st.button("Neue Person hinzufügen", key="add_new_person_btn"):
            st.session_state.add_person_mode = True
            st.session_state.confirm_delete_id = None # Löschbestätigung zurücksetzen
            st.session_state.show_recommendations = False # Empfehlungen zurücksetzen
            st.session_state.current_recommendations = [] # Empfehlungen zurücksetzen
            st.session_state.analyzed_df = pd.DataFrame() # Analysierte Daten zurücksetzen
            st.rerun() # Wichtig, um den Zustand sofort zu aktual

    with col_back_btn:
        if st.session_state.add_person_mode:
            if st.button("Zurück", key="back_from_add_person"):
                st.session_state.add_person_mode = False
                st.rerun()

    if st.session_state.add_person_mode:
        st.subheader("Neue Personendaten eingeben")
        with st.form("new_person_form", clear_on_submit=True):
            new_firstname = st.text_input("Vorname*", key="new_firstname")
            new_lastname = st.text_input("Nachname*", key="new_lastname")
            # Max-Wert auf aktuelles Jahr setzen
            new_birth_year = st.number_input("Geburtsjahr*", min_value=1900, max_value=datetime.now().year, value=2000, step=1, key="new_birth_year")
            new_gender = st.selectbox("Geschlecht*", ["male", "female", "other"], key="new_gender")

            st.markdown("---")

            st.write("### 🖼️ Profilbild hochladen (optional)")
            uploaded_picture = st.file_uploader("Profilbild hochladen (Drag & Drop möglich)", type=["png", "jpg", "jpeg"], key="new_person_picture")

            st.write("### 📈 Physiologische Daten (CSV-Upload)*")
            st.info("Bitte laden Sie eine CSV-Datei hoch, die folgende Spalten enthält: 'time', 'resting heart rate (bpm)', 'heart rate variability (ms)', 'skin temp (celsius)', 'sleep performance %'")
            uploaded_csv = st.file_uploader("Physiologische Daten hochladen (Drag & Drop möglich)", type=["csv"], key="new_person_csv")

            submit_button = st.form_submit_button("Person speichern")

            if submit_button:
                if new_firstname and new_lastname and new_birth_year and new_gender and uploaded_csv:
                    try:
                        picture_path = None
                        if uploaded_picture is not None:
                            picture_path = save_uploaded_file(uploaded_picture, "pictures")

                        csv_path = save_uploaded_file(uploaded_csv, "physiological_cycles")

                        if csv_path:
                            new_person_data = {
                                "date_of_birth": new_birth_year,
                                "firstname": new_firstname,
                                "lastname": new_lastname,
                                "gender": new_gender,
                                "picture_path": picture_path,
                                "health_data": [
                                    {
                                        "id": 1.1, # Diese ID ist statisch, sollte aber dynamisch sein (z.B. Zeitstempel oder Zähler)
                                        "date": datetime.now().strftime("%d.%m.%Y"), # Verwende aktuelles Datum
                                        "result_link": csv_path
                                    }
                                ]
                            }
                            add_new_person_to_db(new_person_data)

                            st.success(f"Person '{new_firstname} {new_lastname}' erfolgreich hinzugefügt und Daten gespeichert!")
                            st.session_state.add_person_mode = False
                            st.rerun()
                        else:
                            st.error("Fehler beim Speichern der physiologischen Daten.")

                    except Exception as e:
                        st.error(f"Ein Fehler ist aufgetreten: {e}")
                        st.session_state.add_person_mode = True

                else:
                    st.error("Bitte füllen Sie alle mit * markierten Felder aus und laden Sie die CSV-Datei hoch.")
        st.markdown("---")


    # ----- UI für die Anzeige bestehender Personen -----
    if not st.session_state.add_person_mode:
        person_list = Person.load_person_data()
        person_ids = [p["id"] for p in person_list]

        if person_ids:
            person_ids.sort()
            if 'selected_person_id' not in st.session_state or st.session_state.selected_person_id not in person_ids:
                st.session_state.selected_person_id = person_ids[-1]

            col_select_id, col_delete_btn = st.columns([0.7, 0.3])

            with col_select_id:
                selected_id_input = st.number_input(
                    "Versuchsperson-ID auswählen",
                    min_value=min(person_ids),
                    max_value=max(person_ids),
                    value=st.session_state.selected_person_id,
                    step=1,
                    key="selected_person_id_selector"
                )
                if selected_id_input != st.session_state.selected_person_id:
                    st.session_state.selected_person_id = selected_id_input
                    st.session_state.confirm_delete_id = None
                    st.session_state.show_recommendations = False # Empfehlungen zurücksetzen
                    st.session_state.current_recommendations = [] # Empfehlungen zurücksetzen
                    st.session_state.analyzed_df = pd.DataFrame() # Analysierte Daten zurücksetzen
                    st.rerun()

            with col_delete_btn:
                st.write("")
                st.write("")
                if st.button("Person löschen", key="trigger_delete_btn", help="Löscht die aktuell ausgewählte Person und ihre Daten."):
                    st.session_state.confirm_delete_id = st.session_state.selected_person_id
                    st.rerun()

            # Löschbestätigungslogik
            if st.session_state.confirm_delete_id is not None and st.session_state.confirm_delete_id == st.session_state.selected_person_id:
                st.warning(f"Möchten Sie Person mit ID {st.session_state.confirm_delete_id} wirklich löschen? Diese Aktion kann nicht rückgängig gemacht werden.")
                col_confirm_yes, col_confirm_no = st.columns(2)
                with col_confirm_yes:
                    if st.button("Ja, Person löschen", key="confirm_delete_yes"):
                        try:
                            delete_person_from_db(st.session_state.confirm_delete_id)
                            st.success(f"Person mit ID {st.session_state.confirm_delete_id} wurde erfolgreich gelöscht.")
                            st.session_state.confirm_delete_id = None
                            st.session_state.show_recommendations = False # Empfehlungen zurücksetzen
                            st.session_state.current_recommendations = [] # Empfehlungen zurücksetzen
                            st.session_state.analyzed_df = pd.DataFrame() # Analysierte Daten zurücksetzen

                            person_list_after_delete = Person.load_person_data()
                            if person_list_after_delete:
                                st.session_state.selected_person_id = person_list_after_delete[0]["id"]
                            else:
                                if 'selected_person_id' in st.session_state:
                                    del st.session_state.selected_person_id
                            st.rerun()

                        except ValueError as ve:
                            st.error(f"Fehler: {ve}")
                            st.session_state.confirm_delete_id = None
                        except Exception as e:
                            st.error(f"Ein unerwarteter Fehler ist aufgetreten: {e}")
                            st.session_state.confirm_delete_id = None

                with col_confirm_no:
                    if st.button("Abbrechen", key="confirm_delete_no"):
                        st.session_state.confirm_delete_id = None
                        st.info("Löschvorgang abgebrochen.")
                        st.rerun()


            selected_person_data = next((p for p in person_list if p["id"] == st.session_state.selected_person_id), None)

            if selected_person_data:
                st.subheader("Persönliche Daten")
                col_img, col_info = st.columns([1, 2])

                with col_img:
                    image_path = selected_person_data.get("picture_path")
                    if image_path:
                        try:
                            image = Image.open(image_path)
                            st.image(image, caption=f"Bild von {selected_person_data['firstname']}", use_container_width=True)
                        except FileNotFoundError:
                            st.warning(f"Bild nicht gefunden unter: {image_path}")
                            st.image("https://via.placeholder.com/150", caption="Platzhalterbild", use_container_width=True)
                        except Exception as e:
                            st.error(f"Fehler beim Laden des Bildes: {e}")
                            st.image("https://via.placeholder.com/150", caption="Fehler beim Bildladen", use_container_width=True)
                    else:
                        st.image("https://via.placeholder.com/150", caption="Kein Bild verfügbar", use_container_width=True)

                with col_info:
                    person_obj = Person(selected_person_data)
                    age = person_obj.calculate_age()

                    st.markdown(f"**🧑 Name:** {person_obj.firstname} {person_obj.lastname}")
                    st.markdown(f"**🎂 Alter:** {age} Jahre")
                    st.markdown(f"**🆔 ID:** {person_obj.id}")
                    st.markdown(f"**🚻 Geschlecht:** {person_obj.gender}")
                    st.markdown(f"**📅 Geburtsjahr:** {person_obj.date_of_birth}")

            else:
                st.info("Keine Person ausgewählt oder keine Personen verfügbar. Bitte fügen Sie eine neue Person hinzu.")
        else:
            st.info("Noch keine Personen vorhanden. Bitte fügen Sie eine neue Person hinzu.")

with tab2:
    from healthdata import healthData
    st.header("📊 Gesundheitsdaten")
    
    if "selected_person_id" in st.session_state:
        person_list_tab2 = Person.load_person_data()
        selected_person_data_tab2 = next(
            (p for p in person_list_tab2 if p["id"] == st.session_state.selected_person_id), None
        )

        if selected_person_data_tab2:
            health_data_info = selected_person_data_tab2.get("health_data")
            if health_data_info and health_data_info[0].get("result_link"):
                csv_file_path = health_data_info[0]["result_link"]
                try:
                    df = read_my_csv(csv_file_path)
                    df.rename(columns={
                        "resting heart rate (bpm)": "Resting heart rate (bpm)",
                        "heart rate variability (ms)": "Heart rate variability (ms)",
                        "skin temp (celsius)": "Skin temp (celsius)",
                        "sleep performance %": "Sleep performance %"
                    }, inplace=True)

                    avg_rhr = healthData.get_average_Resting_heart_rate(df)
                    avg_hrv = healthData.get_average_Heart_rate_variability(df)
                    avg_temp = healthData.get_average_Skin_temp_celsius(df)
                    avg_sleep = healthData.get_average_Sleep_performance_percent(df)

                    st.subheader("📈 Durchschnittliche Gesundheitswerte")
                    col1, col2 = st.columns([2, 2])
                    with col1:
                        st.metric("🫀 Ruheherzfrequenz (bpm)", f"{avg_rhr:.1f}")
                        st.metric("💓 Herzfrequenz-Variabilität (ms)", f"{avg_hrv:.1f}")
                        st.metric("🌡️ Hauttemperatur (°C)", f"{avg_temp:.1f}")
                    with col2:
                        pie_fig = healthData.plot_sleep_pie(avg_sleep)
                        st.plotly_chart(pie_fig, use_container_width=True)

                    st.divider()
                    st.subheader("📉 Verlauf aller Gesundheitsparameter")
                    st.plotly_chart(healthData.plot_all(df), use_container_width=True)

                except FileNotFoundError:
                    st.error(f"Die CSV-Datei wurde nicht gefunden: {csv_file_path}")
                except KeyError as e:
                    st.error(f"Fehlende Spalte in der CSV: {e}")
                except Exception as e:
                    st.error(f"Fehler beim Verarbeiten der Daten: {e}")
            else:
                st.info("Für diese Person sind keine Gesundheitsdaten verknüpft.")
        else:
            st.info("Keine gültige Person gefunden.")
    else:
        st.info("Bitte wähle zuerst eine Versuchsperson im ersten Tab aus.")



with tab3:
    st.header("⚠️ Abnormalitäten über den Zeitverlauf")

    if "selected_person_id" in st.session_state:
        person_list_tab3 = Person.load_person_data()
        selected_person_data_tab3 = next(
            (p for p in person_list_tab3 if p["id"] == st.session_state.selected_person_id), None
        )

        if selected_person_data_tab3:
            person_obj = Person(selected_person_data_tab3)
            age = person_obj.calculate_age() # Alter berechnen
            gender = person_obj.gender     # Geschlecht erhalten

            if hasattr(person_obj, 'healthdata_path') and person_obj.healthdata_path:
                try:
                    # Lade das DataFrame mit read_my_csv_2
                    df = read_my_csv_2(person_obj.healthdata_path)

                    # Überprüfen und Konvertieren der 'datetime'-Spalte
                    if "time" in df.columns and "datetime" not in df.columns:
                        df["datetime"] = pd.to_datetime(df["time"], errors="coerce")
                        df.dropna(subset=["datetime"], inplace=True)
                    elif "datetime" in df.columns:
                        df["datetime"] = pd.to_datetime(df["datetime"], errors="coerce")
                        df.dropna(subset=["datetime"], inplace=True)
                    else:
                        st.error("Fehler: Weder 'time' noch 'datetime' Spalte im CSV gefunden. Kann Zeitverlauf nicht analysieren.")
                        df = pd.DataFrame() # Leeres DataFrame, um weitere Fehler zu vermeiden


                    if df is not None and not df.empty:
                        rename_cols = {
                            "resting heart rate (bpm)": "RHR",
                            "heart rate variability (ms)": "HRV",
                            "skin temp (celsius)": "Temp",
                            "sleep performance %": "Sleep"
                        }

                        df.rename(columns={k: v for k, v in rename_cols.items() if k in df.columns}, inplace=True)

                        expected_columns = ["RHR", "HRV", "Temp", "Sleep"]
                        missing = [col for col in expected_columns if col not in df.columns]

                        if missing:
                            st.error(f"🚫 Fehlende Spalten in den Gesundheitsdaten für Abnormalitäten: {', '.join(missing)}. Bitte überprüfen Sie die Spaltennamen in der hochgeladenen CSV.")
                            st.session_state.analyzed_df = pd.DataFrame() # Leeres DataFrame setzen
                        else:
                            # Füge Statusspalten hinzu
                            for param, check_func in {
                                "RHR": AbnormalityChecker.check_rhr,
                                "HRV": AbnormalityChecker.check_hrv,
                                "Temp": AbnormalityChecker.check_skin_temp,
                                "Sleep": AbnormalityChecker.check_sleep_score
                            }.items():
                                df[param + "_status"] = df[param].apply(lambda v: check_func(v, age, gender))

                            # Speichern des vorbereiteten DF in session_state, bevor es für Empfehlungen verwendet wird
                            st.session_state.analyzed_df = df.copy() # HIER WICHTIGE ÄNDERUNG

                            st.subheader("Analyse abgeschlossen ✅ – bereit zur Visualisierung")
                            st.dataframe(df) # Zeigt das DataFrame mit den Statusspalten

                            # Plotting der Abnormalitäten über die Zeit
                            plot_abnormalities_over_time(df, age, gender) # <<< HIER WICHTIGE ÄNDERUNG: age und gender übergeben

                            st.markdown("---")
                            st.subheader("💡 Deine personalisierten Empfehlungen")

                            # Der Button sollte immer sichtbar sein, aber die Logik dahinter muss das analyzed_df überprüfen
                            if st.button("Empfehlungen anzeigen", key="show_recommendations_btn"):
                                if not st.session_state.analyzed_df.empty:
                                    with st.spinner("Analysiere Daten und generiere Empfehlungen..."):
                                        st.session_state.current_recommendations = AbnormalityChecker.analyze_and_recommend(
                                                st.session_state.analyzed_df,
                                                age,
                                                gender
                                            )
                                        st.session_state.show_recommendations = True
                                else:
                                    st.warning("Keine Daten zum Analysieren für Empfehlungen vorhanden. Bitte stellen Sie sicher, dass die Gesundheitsdaten korrekt geladen wurden.")
                                    st.session_state.show_recommendations = False # Setze auf False, da keine Empfehlungen generiert werden konnten

                            if st.session_state.show_recommendations:
                                with st.expander("Klicken Sie hier, um Ihre Empfehlungen zu sehen", expanded=True):
                                    if st.session_state.current_recommendations:
                                        for emoji, rec_text in st.session_state.current_recommendations:
                                            st.markdown(f"**{emoji} {rec_text}**")
                                    else:
                                        st.info("Es konnten keine spezifischen Empfehlungen generiert werden.")
                    else:
                        st.warning("Die geladenen Gesundheitsdaten sind leer oder konnten nicht verarbeitet werden.")
                        st.session_state.analyzed_df = pd.DataFrame() # Sicherstellen, dass es ein leeres DF ist
                except FileNotFoundError:
                    st.error(f"Die CSV-Datei für die Gesundheitsdaten wurde nicht gefunden: {person_obj.healthdata_path}")
                    st.session_state.analyzed_df = pd.DataFrame() # Sicherstellen, dass es ein leeres DF ist
                except KeyError as e:
                    st.error(f"Fehlende Spalte oder ungültiges Format in den Gesundheitsdaten-CSV: {e}. Bitte überprüfen Sie die Spaltennamen und das Format.")
                    st.session_state.analyzed_df = pd.DataFrame() # Sicherstellen, dass es ein leeres DF ist
                except Exception as e:
                    st.error(f"Fehler beim Laden oder Verarbeiten der Gesundheitsdaten für Abnormalitäten: {e}")
                    st.session_state.analyzed_df = pd.DataFrame() # Sicherstellen, dass es ein leeres DF ist
            else:
                st.info("Für diese Person sind keine Gesundheitsdaten verknüpft.")
                st.session_state.analyzed_df = pd.DataFrame() # Sicherstellen, dass es ein leeres DF ist
        else:
            st.warning("Keine gültige Person mit dieser ID gefunden.")
            st.session_state.analyzed_df = pd.DataFrame() # Sicherstellen, dass es ein leeres DF ist
    else:
        st.info("Bitte wählen Sie zuerst eine Versuchsperson in Tab 1 aus.")
        st.session_state.analyzed_df = pd.DataFrame() # Sicherstellen, dass es ein leeres DF ist