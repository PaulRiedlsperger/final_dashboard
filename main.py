
import streamlit as st
import json
from person import Person
from PIL import Image
from loaddata import read_my_csv
from healthdata import healthData
import os # Importieren für Dateisystemoperationen
import pandas as pd # Für das Speichern der CSV-Datei

# Set page config (optional, aber gut für Layout)
st.set_page_config(layout="wide")

# Initialisiere session_state, falls nicht vorhanden
if 'add_person_mode' not in st.session_state:
    st.session_state.add_person_mode = False

tab1 ,tab2 ,tab3 = st.tabs(["Versuchsperson", "Gesundheitsdaten", "Abnormalitäten"])

with tab1:
    st.header("Versuchsperson")

    # ----- UI für das Hinzufügen einer neuen Person -----
    # Der Button und das Formular werden immer am Anfang des Tabs angezeigt,
    # aber das Formular nur, wenn st.session_state.add_person_mode True ist.
    if st.button("Neue Person hinzufügen", key="add_new_person_btn"):
        # Setze den Modus zum Hinzufügen, wenn der Button geklickt wird
        st.session_state.add_person_mode = True

    if st.session_state.add_person_mode:
        st.subheader("Neue Personendaten eingeben")
        with st.form("new_person_form", clear_on_submit=True):
            new_firstname = st.text_input("Vorname*", key="new_firstname")
            new_lastname = st.text_input("Nachname*", key="new_lastname")
            new_birth_year = st.number_input("Geburtsjahr*", min_value=1900, max_value=2025, value=2000, step=1, key="new_birth_year")
            new_gender = st.selectbox("Geschlecht*", ["male", "female", "other"], key="new_gender")

            st.markdown("---") # Trennlinie

            st.write("### 🖼️ Profilbild hochladen (optional)")
            uploaded_picture = st.file_uploader("Profilbild hochladen (Drag & Drop möglich)", type=["png", "jpg", "jpeg"], key="new_person_picture")

            st.write("### 📈 Physiologische Daten (CSV-Upload)*")
            st.info("Bitte laden Sie eine CSV-Datei hoch, die folgende Spalten enthält: 'time', 'resting heart rate (bpm)', 'heart rate variability (ms)', 'skin temp (celsius)', 'sleep performance %'")
            uploaded_csv = st.file_uploader("Physiologische Daten hochladen (Drag & Drop möglich)", type=["csv"], key="new_person_csv")

            submit_button = st.form_submit_button("Person speichern")

            if submit_button:
                # Prüfen, ob alle Pflichtfelder ausgefüllt sind (CSV ist jetzt Pflicht)
                if new_firstname and new_lastname and new_birth_year and new_gender and uploaded_csv:
                    # Hier wird die neue Logik zum Speichern aufgerufen
                    # Diese Funktionen werden wir in den nächsten Schritten erstellen
                    try:
                        # Zuerst ein potenzielles Bild und die CSV speichern
                        # Dann die Person zur JSON hinzufügen
                        # Wir übergeben uploaded_picture und uploaded_csv direkt

                        # Importiere die neue Funktion aus person.py, die wir noch erstellen müssen
                        from person import add_new_person_to_db, save_uploaded_file

                        # Speichere das Profilbild und erhalte den Pfad (falls hochgeladen)
                        picture_path = None
                        if uploaded_picture is not None:
                            picture_path = save_uploaded_file(uploaded_picture, "pictures") # Speichern in 'data/pictures/'

                        # Speichere die CSV-Datei
                        csv_path = save_uploaded_file(uploaded_csv, "physiological_cycles") # Speichern in 'data/physiological_cycles/'

                        if csv_path:
                            new_person_data = {
                                "date_of_birth": new_birth_year,
                                "firstname": new_firstname,
                                "lastname": new_lastname,
                                "gender": new_gender,
                                "picture_path": picture_path, # Pfad des gespeicherten Bildes
                                "health_data": [
                                    {
                                        "id": 1.1, # Oder eine logische ID für die Gesundheitsdaten (kannst du anpassen)
                                        "date": "1.1.2025", # Beispiel-Datum, idealerweise das Upload-Datum oder Datum aus CSV
                                        "result_link": csv_path # Pfad der gespeicherten CSV
                                    }
                                ]
                            }
                            # Füge die Person zur JSON-Datenbank hinzu
                            add_new_person_to_db(new_person_data)

                            st.success(f"Person '{new_firstname} {new_lastname}' erfolgreich hinzugefügt und Daten gespeichert!")
                            st.session_state.add_person_mode = False # Formular schließen
                            st.rerun() # App neu laden, damit die neue Person in der Auswahl erscheint
                        else:
                            st.error("Fehler beim Speichern der physiologischen Daten.")

                    except Exception as e:
                        st.error(f"Ein Fehler ist aufgetreten: {e}")
                        st.session_state.add_person_mode = True # Formular offen lassen bei Fehler

                else:
                    st.error("Bitte füllen Sie alle mit * markierten Felder aus und laden Sie die CSV-Datei hoch.")
        st.markdown("---") # Trennlinie nach dem Formular
    # ----- Ende UI für das Hinzufügen einer neuen Person -----


    # ----- UI für die Anzeige bestehender Personen -----
    # Dieser Block wird nur ausgeführt, wenn der Add-Person-Modus NICHT aktiv ist,
    # oder nachdem eine Person hinzugefügt und st.rerun() aufgerufen wurde.
    if not st.session_state.add_person_mode:
        person_list = Person.load_person_data() # Lädt alle Personen aus der JSON (inkl. neuer Personen)
        person_ids = [p["id"] for p in person_list]

        if person_ids:
            # Sortiere die IDs, um die höchste ID als Standardwert zu wählen, wenn eine neue Person hinzugefügt wurde
            person_ids.sort()
            default_id = person_ids[-1] if 'newly_added_id' not in st.session_state else st.session_state.newly_added_id
            if default_id not in person_ids: # Fallback falls die ID nicht mehr existiert
                default_id = person_ids[-1]

            selected_id = st.number_input(
                "Versuchsperson-ID auswählen",
                min_value=min(person_ids),
                max_value=max(person_ids),
                value=default_id, # Setze Standardwert auf die höchste ID oder die neu hinzugefügte
                step=1,
                key="selected_person_id"
            )

            selected_person_data = next((p for p in person_list if p["id"] == selected_id), None)

            if selected_person_data:
                # Hier der vorhandene Code zur Anzeige der Personendaten
                st.subheader("Persönliche Daten")
                col_img, col_info = st.columns([1, 2])

                with col_img:
                    image_path = selected_person_data.get("picture_path")
                    if image_path:
                        try:
                            # Streamlit Warnung unterdrücken, da wir use_container_width verwenden
                            # Die Meldung "The use_column_width parameter has been deprecated" kam,
                            # weil Streamlit Änderungen an der Bildanzeige vornimmt.
                            # use_container_width ist der empfohlene Ersatz, aber deine aktuelle Version
                            # verwendet noch use_column_width.
                            # Wenn du eine neuere Streamlit-Version hast, könntest du es ändern.
                            # Für jetzt, lassen wir es wie es ist, da es nur eine Warnung ist.
                            image = Image.open(image_path)
                            st.image(image, caption=f"Bild von {selected_person_data['firstname']}", use_column_width=True)
                        except FileNotFoundError:
                            st.warning(f"Bild nicht gefunden unter: {image_path}")
                            st.image("https://via.placeholder.com/150", caption="Platzhalterbild", use_column_width=True)
                        except Exception as e:
                            st.error(f"Fehler beim Laden des Bildes: {e}")
                            st.image("https://via.placeholder.com/150", caption="Fehler beim Bildladen", use_column_width=True)
                    else:
                        st.image("https://via.placeholder.com/150", caption="Kein Bild verfügbar", use_column_width=True)


                with col_info:
                    # Direkte Verwendung der Person-Klasse hier beibehalten oder wie vorher
                    person_obj = Person(selected_person_data)
                    age = person_obj.calculate_age()

                    st.markdown(f"**🧑 Name:** {person_obj.firstname} {person_obj.lastname}")
                    st.markdown(f"**🎂 Alter:** {age} Jahre")
                    st.markdown(f"**🆔 ID:** {person_obj.id}")
                    st.markdown(f"**🚻 Geschlecht:** {person_obj.gender}")
                    st.markdown(f"**📅 Geburtsjahr:** {person_obj.date_of_birth}")

            else:
                st.warning("Keine Person mit dieser ID gefunden.")
        else:
            st.info("Noch keine Personen vorhanden. Bitte fügen Sie eine neue Person hinzu.")

# Der Rest der Tabs bleibt unverändert, da sie von der Auswahl in Tab1 abhängen
# Stellen Sie sicher, dass 'person' (oder 'person_obj') in den folgenden Tabs definiert ist,
# wenn eine Person ausgewählt wurde.

with tab2:
    from healthdata import healthData # Dies importiert die Klasse HealthData (angenommen, deine Klasse heißt so)
    st.header("📊 Gesundheitsdaten")
    if 'selected_person_data' in locals() and selected_person_data: # Prüfen, ob Person ausgewählt ist
        health_data_info = selected_person_data.get("health_data")
        if health_data_info and health_data_info[0].get("result_link"):
            csv_file_path = health_data_info[0]["result_link"]
            try:
                df = read_my_csv(csv_file_path)

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
            except FileNotFoundError:
                st.error(f"Die CSV-Datei für die Gesundheitsdaten wurde nicht gefunden: {csv_file_path}")
            except KeyError as e:
                st.error(f"Fehlende Spalte in der Gesundheitsdaten-CSV: {e}. Bitte überprüfen Sie die Spaltennamen.")
            except Exception as e:
                st.error(f"Fehler beim Laden oder Verarbeiten der Gesundheitsdaten: {e}")
        else:
            st.info("Für diese Person sind keine Gesundheitsdaten verknüpft.")
    else:
        st.info("Bitte wählen Sie zuerst eine Versuchsperson aus dem 'Versuchsperson'-Tab aus.")


with tab3:
    st.header("⚠ Abnormalitäten")
    if 'selected_person_data' in locals() and selected_person_data:
        # Importe hier, um Ladezeit zu optimieren, wenn Tab nicht aktiv ist
        from abnormality import AbnormalityChecker, show_mini_chart

        health_data_info = selected_person_data.get("health_data")
        if health_data_info and health_data_info[0].get("result_link"):
            csv_file_path = health_data_info[0]["result_link"]
            try:
                df = read_my_csv(csv_file_path)
                person_obj = Person(selected_person_data) # Neu initialisieren, um sicherzustellen
                age = person_obj.calculate_age()
                gender = person_obj.gender

                # Letzte Werte extrahieren
                latest_rhr = healthData.get_latest_value(df, "Resting heart rate (bpm)")
                latest_hrv = healthData.get_latest_value(df, "Heart rate variability (ms)")
                latest_temp = healthData.get_latest_value(df, "Skin temp (celsius)")
                latest_sleep = healthData.get_latest_value(df, "Sleep performance %")

                # Dynamische Grenzwerte aus der Klasse holen
                lower_rhr, upper_rhr = AbnormalityChecker.get_rhr_thresholds(age, gender)
                lower_hrv, upper_hrv = AbnormalityChecker.get_hrv_thresholds(age, gender)
                lower_temp, upper_temp = AbnormalityChecker.get_skin_temp_thresholds(gender)
                lower_sleep, upper_sleep = AbnormalityChecker.get_sleep_score_thresholds()

                # Analyse
                rhr_warning = AbnormalityChecker.check_rhr(latest_rhr, age, gender)
                hrv_warning = AbnormalityChecker.check_hrv(latest_hrv, age, gender)
                temp_warning = AbnormalityChecker.check_skin_temp(latest_temp, age, gender)
                sleep_warning = AbnormalityChecker.check_sleep_score(latest_sleep, age, gender) # Achtung: hier war latest_temp statt latest_sleep!

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

            except FileNotFoundError:
                st.error(f"Die CSV-Datei für die Gesundheitsdaten wurde nicht gefunden: {csv_file_path}")
            except KeyError as e:
                st.error(f"Fehlende Spalte in der Gesundheitsdaten-CSV: {e}. Bitte überprüfen Sie die Spaltennamen.")
            except Exception as e:
                st.error(f"Fehler beim Laden oder Verarbeiten der Abnormalitätsdaten: {e}")
        else:
            st.info("Für diese Person sind keine Gesundheitsdaten verknüpft, um Abnormalitäten zu prüfen.")
    else:
        st.info("Bitte wählen Sie zuerst eine Versuchsperson aus dem 'Versuchsperson'-Tab aus.")