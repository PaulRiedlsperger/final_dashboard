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


# WICHTIG: Importiere die neuen/aktualisierten Funktionen aus person.py
from person import add_new_person_to_db, save_uploaded_file, delete_person_from_db, update_person_in_db # update_person_in_db hinzugefügt

# Set page config (optional, aber gut für Layout)
st.set_page_config(layout="wide")


# Initialisiere session_state, falls nicht vorhanden
if 'add_person_mode' not in st.session_state:
    st.session_state.add_person_mode = False
if 'edit_person_mode' not in st.session_state: # NEU: Zustand für Bearbeitungsmodus
    st.session_state.edit_person_mode = False
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

    # Buttons für Hinzufügen, Bearbeiten, Zurück
    col_add_btn, col_edit_btn, col_back_btn = st.columns([0.2, 0.2, 0.6])

    with col_add_btn:
        if st.button("Neue Person hinzufügen", key="add_new_person_btn"):
            st.session_state.add_person_mode = True
            st.session_state.edit_person_mode = False # Wichtig: Bearbeitungsmodus deaktivieren
            st.session_state.confirm_delete_id = None
            st.session_state.show_recommendations = False
            st.session_state.current_recommendations = []
            st.session_state.analyzed_df = pd.DataFrame()
            st.rerun()

    with col_edit_btn: # NEU: Bearbeiten-Button
        if st.button("Person bearbeiten", key="edit_person_btn"):
            st.session_state.edit_person_mode = True
            st.session_state.add_person_mode = False # Wichtig: Hinzufügemodus deaktivieren
            st.session_state.confirm_delete_id = None
            st.session_state.show_recommendations = False
            st.session_state.current_recommendations = []
            st.session_state.analyzed_df = pd.DataFrame()
            st.rerun()

    with col_back_btn:
        # "Zurück"-Button, sichtbar wenn im Hinzufüge- oder Bearbeitungsmodus
        if st.session_state.add_person_mode or st.session_state.edit_person_mode:
            if st.button("Zurück", key="back_from_add_edit"):
                st.session_state.add_person_mode = False
                st.session_state.edit_person_mode = False
                st.rerun()

    # Logik für das Hinzufügen einer neuen Person
    if st.session_state.add_person_mode:
        st.subheader("Neue Personendaten eingeben")
        with st.form("new_person_form", clear_on_submit=True):
            new_firstname = st.text_input("Vorname*", key="new_firstname")
            new_lastname = st.text_input("Nachname*", key="new_lastname")
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

    # Logik für das Bearbeiten einer bestehenden Person (NEU hinzugefügt)
    elif st.session_state.edit_person_mode:
        st.subheader("Bestehende Person bearbeiten")
        person_list_for_edit = Person.load_person_data()
        person_ids_for_edit = [p["id"] for p in person_list_for_edit]

        if not person_ids_for_edit:
            st.info("Es sind keine Personen zum Bearbeiten vorhanden. Bitte fügen Sie zuerst eine Person hinzu.")
            # Füge einen "Zurück"-Button hinzu, wenn keine Personen vorhanden sind
            if st.button("Zurück", key="back_from_no_edit_person"):
                st.session_state.edit_person_mode = False
                st.rerun()
        else:
            # Stelle sicher, dass immer eine Person ausgewählt ist, wenn der Bearbeitungsmodus aktiv ist
            if 'selected_person_id_edit' not in st.session_state or st.session_state.selected_person_id_edit not in person_ids_for_edit:
                st.session_state.selected_person_id_edit = person_ids_for_edit[0] # Wähle die erste Person aus

            selected_id_edit = st.selectbox(
                "Person zur Bearbeitung auswählen (ID)",
                options=person_ids_for_edit,
                index=person_ids_for_edit.index(st.session_state.selected_person_id_edit),
                key="selected_person_id_edit_selector"
            )
            st.session_state.selected_person_id_edit = selected_id_edit # Aktualisiere den Zustand bei Auswahländerung

            selected_person_data_edit = next((p for p in person_list_for_edit if p["id"] == selected_id_edit), None)

            if selected_person_data_edit:
                with st.form("edit_person_form", clear_on_submit=False):
                    # Vorab ausfüllen mit bestehenden Daten
                    edit_firstname = st.text_input("Vorname*", value=selected_person_data_edit.get("firstname", ""), key="edit_firstname")
                    edit_lastname = st.text_input("Nachname*", value=selected_person_data_edit.get("lastname", ""), key="edit_lastname")
                    edit_birth_year = st.number_input("Geburtsjahr*", min_value=1900, max_value=datetime.now().year, value=selected_person_data_edit.get("date_of_birth", 2000), step=1, key="edit_birth_year")
                    edit_gender = st.selectbox("Geschlecht*", ["male", "female", "other"], index=["male", "female", "other"].index(selected_person_data_edit.get("gender", "male")), key="edit_gender")

                    st.markdown("---")

                    st.write("### 🖼️ Profilbild aktualisieren (optional)")
                    current_picture_path = selected_person_data_edit.get("picture_path")
                    if current_picture_path and os.path.exists(current_picture_path):
                        try:
                            st.image(Image.open(current_picture_path), caption="Aktuelles Profilbild", width=150)
                        except Exception:
                            st.write("Aktuelles Bild konnte nicht angezeigt werden.")
                    else:
                        st.write("Kein aktuelles Profilbild vorhanden.")
                    uploaded_picture_edit = st.file_uploader("Neues Profilbild hochladen (lässt altes Bild ersetzen)", type=["png", "jpg", "jpeg"], key="edit_person_picture")

                    st.write("### 📈 Physiologische Daten aktualisieren (CSV-Upload)*")
                    st.info("Bitte laden Sie eine CSV-Datei hoch, die folgende Spalten enthält: 'time', 'resting heart rate (bpm)', 'heart rate variability (ms)', 'skin temp (celsius)', 'sleep performance %'")
                    
                    # Suche den aktuellen CSV-Pfad aus der health_data Liste
                    current_health_data_list = selected_person_data_edit.get("health_data", [])
                    current_csv_path = current_health_data_list[0].get("result_link") if current_health_data_list else None

                    if current_csv_path and os.path.exists(current_csv_path):
                        st.write(f"Aktuelle CSV-Datei: `{os.path.basename(current_csv_path)}`")
                    else:
                        st.write("Keine aktuelle CSV-Datei für physiologische Daten vorhanden.")

                    uploaded_csv_edit = st.file_uploader("Neue Physiologische Daten hochladen (lässt alte CSV ersetzen)", type=["csv"], key="edit_person_csv")

                    update_button = st.form_submit_button("Änderungen speichern")

                    if update_button:
                        if edit_firstname and edit_lastname and edit_birth_year and edit_gender:
                            try:
                                # Pfad für Profilbild aktualisieren
                                new_picture_path = save_uploaded_file(uploaded_picture_edit, "pictures", existing_path=current_picture_path)
                                
                                # Pfad für CSV aktualisieren
                                new_csv_path = None
                                if uploaded_csv_edit:
                                    new_csv_path = save_uploaded_file(uploaded_csv_edit, "physiological_cycles", existing_path=current_csv_path)
                                else:
                                    # Wenn keine neue CSV hochgeladen wird, behalte den alten Pfad
                                    new_csv_path = current_csv_path


                                updated_data = {
                                    "id": selected_id_edit,
                                    "date_of_birth": edit_birth_year,
                                    "firstname": edit_firstname,
                                    "lastname": edit_lastname,
                                    "gender": edit_gender,
                                    "picture_path": new_picture_path, # save_uploaded_file gibt den korrekten Pfad zurück (neuer oder alter)
                                    "health_data": [
                                        {
                                            "id": 1.1, # Bleibt statisch oder kann dynamisch verwaltet werden
                                            "date": datetime.now().strftime("%d.%m.%Y"),
                                            "result_link": new_csv_path
                                        }
                                    ]
                                }
                                update_person_in_db(updated_data)
                                st.success(f"Daten für Person '{edit_firstname} {edit_lastname}' (ID: {selected_id_edit}) erfolgreich aktualisiert!")
                                st.session_state.edit_person_mode = False # Bearbeitungsmodus verlassen
                                st.rerun()

                            except Exception as e:
                                st.error(f"Fehler beim Aktualisieren der Personendaten: {e}")
                        else:
                            st.error("Bitte füllen Sie alle mit * markierten Felder aus.")
            else:
                st.info("Bitte wählen Sie eine Person zur Bearbeitung aus.")
        st.markdown("---")


    # ----- UI für die Anzeige bestehender Personen (wenn nicht im Add/Edit-Modus) -----
    if not st.session_state.add_person_mode and not st.session_state.edit_person_mode:
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
                    st.session_state.show_recommendations = False
                    st.session_state.current_recommendations = []
                    st.session_state.analyzed_df = pd.DataFrame()
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
                            st.session_state.show_recommendations = False
                            st.session_state.current_recommendations = []
                            st.session_state.analyzed_df = pd.DataFrame()

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
                    elif "datetime" in df.columns: # Falls die Spalte bereits "datetime" heißt
                        df["datetime"] = pd.to_datetime(df["datetime"], errors="coerce")
                        df.dropna(subset=["datetime"], inplace=True)
                    else:
                        st.error("Fehler: Weder 'time' noch 'datetime' Spalte im CSV gefunden. Kann Zeitverlauf nicht analysieren.")
                        df = pd.DataFrame() # Leeres DataFrame, um weitere Fehler zu vermeiden


                    if df is not None and not df.empty:
                        # Die Umbenennung hier ist entscheidend, da `AbnormalityChecker` die Kurznamen erwartet.
                        rename_cols = {
                            "resting heart rate (bpm)": "RHR",
                            "heart rate variability (ms)": "HRV",
                            "skin temp (celsius)": "Temp",
                            "sleep performance %": "Sleep"
                        }
                        # Nur umbenennen, wenn die Spalte existiert
                        df.rename(columns={k: v for k, v in rename_cols.items() if k in df.columns}, inplace=True)

                        expected_columns = ["RHR", "HRV", "Temp", "Sleep", "datetime"] # 'datetime' hinzugefügt
                        missing = [col for col in expected_columns if col not in df.columns]

                        if missing:
                            st.error(f"🚫 Fehlende Spalten in den Gesundheitsdaten für Abnormalitäten: {', '.join(missing)}. Bitte überprüfen Sie die Spaltennamen in der hochgeladenen CSV. Erwartet: 'time', 'resting heart rate (bpm)', 'heart rate variability (ms)', 'skin temp (celsius)', 'sleep performance %'.")
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

                            # Speichern des vorbereiteten DF in session_state
                            st.session_state.analyzed_df = df.copy() 

                            st.subheader("Analyse abgeschlossen ✅ – bereit zur Visualisierung")
                            st.dataframe(df) # Zeigt das DataFrame mit den Statusspalten

                            # Plotting der Abnormalitäten über die Zeit
                            plot_abnormalities_over_time(st.session_state.analyzed_df, age, gender) # Sicherstellen, dass das analysierte DF verwendet wird und age/gender übergeben werden

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
                                    st.session_state.show_recommendations = False 

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