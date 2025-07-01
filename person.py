import json
import os
import shutil # Importiere shutil für das Löschen von Verzeichnissen (falls nötig)
from datetime import datetime # Neu hinzugefügt für das aktuelle Datum

# Der Pfad zur JSON-Datei, in der die Personendaten gespeichert sind
PERSON_DB_PATH = "data/person.json"
DATA_DIR = "data" # Hauptdatenverzeichnis

class Person:
    def __init__(self, data):
        self.id = data.get("id")
        self.date_of_birth = data.get("date_of_birth")
        self.firstname = data.get("firstname")
        self.lastname = data.get("lastname")
        self.gender = data.get("gender")
        self.picture_path = data.get("picture_path")
        self.health_data = data.get("health_data", [])

        # Spezieller Getter für den Pfad der Gesundheitsdaten-CSV
        self.healthdata_path = self.get_healthdata_csv_path()

    def get_healthdata_csv_path(self):
        # Annahme: Es gibt immer nur einen Eintrag unter "health_data" oder der erste ist der relevante
        if self.health_data and isinstance(self.health_data, list) and len(self.health_data) > 0:
            return self.health_data[0].get("result_link")
        return None

    @staticmethod
    def load_person_data():
        if not os.path.exists(PERSON_DB_PATH):
            return []
        try:
            with open(PERSON_DB_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            # Handle empty or malformed JSON file
            print(f"Warning: {PERSON_DB_PATH} is empty or malformed. Returning empty list.")
            return []
        except Exception as e:
            print(f"Error loading person data from {PERSON_DB_PATH}: {e}")
            return []


    @staticmethod
    def save_person_data(data):
        # Erstelle den 'data'-Ordner, falls er nicht existiert
        os.makedirs(os.path.dirname(PERSON_DB_PATH), exist_ok=True)
        with open(PERSON_DB_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    def calculate_age(self):
        current_year = datetime.now().year
        return current_year - self.date_of_birth

def generate_new_person_id(person_list):
    if not person_list:
        return 1
    return max(p["id"] for p in person_list) + 1

def save_uploaded_file(uploaded_file, subfolder):
    """
    Speichert eine hochgeladene Datei in einem Unterordner innerhalb von 'data/'.
    Gibt den Pfad der gespeicherten Datei zurück.
    """
    if uploaded_file is None:
        return None

    upload_dir = os.path.join(DATA_DIR, subfolder)
    os.makedirs(upload_dir, exist_ok=True)

    file_path = os.path.join(upload_dir, uploaded_file.name)
    # Sicherstellen, dass der Dateiname eindeutig ist, um Überschreiben zu vermeiden
    # Optional: Eine eindeutige ID oder Zeitstempel hinzufügen
    base, ext = os.path.splitext(uploaded_file.name)
    counter = 1
    original_file_path = file_path
    while os.path.exists(file_path):
        file_path = os.path.join(upload_dir, f"{base}_{counter}{ext}")
        counter += 1


    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return file_path

def add_new_person_to_db(new_person_data):
    """
    Fügt eine neue Person zur JSON-Datenbank hinzu.
    """
    person_list = Person.load_person_data()
    new_id = generate_new_person_id(person_list)
    new_person_data["id"] = new_id
    person_list.append(new_person_data)
    Person.save_person_data(person_list)


def delete_person_from_db(person_id_to_delete):
    """
    Löscht eine Person aus der JSON-Datenbank und die zugehörigen Dateien (Bild, CSV).
    """
    person_list = Person.load_person_data()
    # Finde die Person, die gelöscht werden soll
    person_to_delete = next((p for p in person_list if p["id"] == person_id_to_delete), None)

    if person_to_delete:
        # Lösche die zugehörigen Dateien
        if person_to_delete.get("picture_path") and os.path.exists(person_to_delete["picture_path"]):
            try:
                os.remove(person_to_delete["picture_path"])
                print(f"DEBUG: Bild gelöscht: {person_to_delete['picture_path']}")
            except OSError as e:
                print(f"ERROR: Konnte Bild nicht löschen {person_to_delete['picture_path']}: {e}")

        # Annahme: Gesundheitsdaten sind eine Liste, und der Pfad ist in "result_link"
        for health_entry in person_to_delete.get("health_data", []):
            csv_path = health_entry.get("result_link")
            if csv_path and os.path.exists(csv_path):
                try:
                    os.remove(csv_path)
                    print(f"DEBUG: CSV gelöscht: {csv_path}")
                except OSError as e:
                    print(f"ERROR: Konnte CSV nicht löschen {csv_path}: {e}")

        # Entferne die Person aus der Liste
        person_list = [p for p in person_list if p["id"] != person_id_to_delete]
        Person.save_person_data(person_list)
    else:
        raise ValueError(f"Person mit ID {person_id_to_delete} nicht gefunden.")