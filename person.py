
import json
from datetime import datetime
import os # Neu importiert für Dateisystemoperationen
import shutil # Neu importiert, falls wir später Dateien kopieren/verschieben müssen (aktuell nur für os.path.join)
from loaddata import read_my_csv

# --- Konfigurationspfade ---
# Pfad zur JSON-Datenbank (Anpassung, falls nötig, aber "data/person_info/person_db.json" ist typisch)
PERSON_DB_PATH = "data/person_info/person_db.json"
# Verzeichnis für hochgeladene Profilbilder
PICTURES_DIR = "data/pictures/"
# Verzeichnis für hochgeladene physiologische CSV-Daten
PHYSIOLOGICAL_CYCLES_DIR = "data/physiological_cycles/"

# Stelle sicher, dass die Verzeichnisse existieren, wenn das Modul importiert wird
# (os.makedirs mit exist_ok=True erstellt sie nur, wenn sie nicht existieren)
os.makedirs(os.path.dirname(PERSON_DB_PATH), exist_ok=True) # Für den Ordner von person_db.json
os.makedirs(PICTURES_DIR, exist_ok=True)
os.makedirs(PHYSIOLOGICAL_CYCLES_DIR, exist_ok=True)


class Person:
    def __init__(self, person_data: dict) -> None:
        # Verwende .get() um auf Schlüssel zuzugreifen, falls sie optional sind oder fehlen könnten
        self.id = person_data.get("id")
        self.date_of_birth = person_data.get("date_of_birth")
        self.firstname = person_data.get("firstname")
        self.lastname = person_data.get("lastname")
        self.gender = person_data.get("gender")
        # picture_path kann None sein, wenn kein Bild hochgeladen wurde
        self.picture_path = person_data.get("picture_path")

        # health_data ist eine Liste von Dictionaries. Prüfe, ob sie existiert und nicht leer ist.
        self.health_data = person_data.get("health_data", [])
        self.healthdata_path = None
        if self.health_data and isinstance(self.health_data, list) and self.health_data[0] and self.health_data[0].get("result_link"):
            self.healthdata_path = self.health_data[0]["result_link"]


    def calculate_age(self):
        # Wir verwenden das aktuelle Jahr, um das Alter zu berechnen.
        # Streamlit-Kontext: Es wurde in main.py bereits mit 2025 angenommen.
        # Hier ist die dynamische Berechnung basierend auf dem aktuellen Datum robuster.
        if self.date_of_birth:
            today = datetime.today()
            return today.year - self.date_of_birth
        return None # Oder raise ValueError("Geburtsjahr nicht gesetzt")


    def max_HR(self):
        age = self.calculate_age()
        if age is not None:
            return 220 - age
        return None # Oder raise ValueError("Alter nicht berechenbar für max_HR")

    @staticmethod
    def load_person_data():
        """
        Lädt die Personendaten aus der JSON-Datenbank.
        Gibt eine Liste von Personen-Dictionaries zurück oder eine leere Liste im Fehlerfall.
        """
        try:
            with open(PERSON_DB_PATH, 'r', encoding='utf-8') as file:
                person_data = json.load(file)
            return person_data
        except FileNotFoundError:
            print(f"WARNUNG: Die Personendatenbank wurde nicht gefunden: {PERSON_DB_PATH}. Erstelle eine neue leere Datenbank.")
            return [] # Gib eine leere Liste zurück, wenn die Datei nicht existiert
        except json.JSONDecodeError:
            print(f"FEHLER: Fehler beim Dekodieren von JSON aus {PERSON_DB_PATH}. Datei könnte leer oder beschädigt sein.")
            return [] # Gib eine leere Liste zurück, wenn JSON fehlerhaft ist


    @staticmethod
    def get_person_list(person_data: list):
        """
        Nimmt eine Liste von Personen-Dictionaries und gibt eine Liste aller Personennamen zurück.
        """
        list_of_names = []
        for eintrag in person_data:
            list_of_names.append(f"{eintrag.get('lastname', 'N.N.')}, {eintrag.get('firstname', 'N.N.')}")
        return list_of_names

    @staticmethod
    def find_person_data_by_id(suchid):
        """
        Sucht eine Person in der Datenbank anhand ihrer ID.
        Gibt das Personen-Dictionary zurück oder None, wenn keine Person gefunden wurde.
        """
        person_data = Person.load_person_data()

        if suchid is None: # Oder suchid == "None", falls der Wert als String kommt
            return None # oder {} je nachdem wie du es behandeln willst

        for eintrag in person_data:
            # Stelle sicher, dass die IDs vergleichbar sind (z.B. int(eintrag["id"]))
            # Hier nehmen wir an, dass IDs in der JSON als Zahlen (int oder float) gespeichert sind.
            if eintrag.get("id") is not None and int(eintrag["id"]) == int(suchid):
                return eintrag
        return None # Wenn keine Person mit der ID gefunden wurde

    def get_health_dataframe(self):
        """
        Lädt die Gesundheitsdaten dieser Person als DataFrame.
        """
        if self.healthdata_path:
            return read_my_csv(self.healthdata_path)
        else:
            return None
# --- NEUE HILFSFUNKTIONEN ZUM HINZUFÜGEN VON PERSONEN UND SPEICHERN VON DATEIEN ---

def get_next_person_id():
    """
    Generiert die nächste verfügbare, fortlaufende ID für eine neue Person.
    """
    person_list = Person.load_person_data()
    if not person_list:
        return 1 # Start bei ID 1, wenn keine Personen vorhanden sind
    else:
        # Finde die höchste vorhandene ID und inkrementiere sie
        max_id = 0
        for p in person_list:
            # Stellen Sie sicher, dass 'id' vorhanden und eine Zahl ist
            if p.get("id") is not None and isinstance(p["id"], (int, float)):
                max_id = max(max_id, int(p["id"]))
        return max_id + 1

def save_uploaded_file(uploaded_file, target_subdir: str):
    """
    Speichert eine hochgeladene Streamlit-Datei in einem spezifischen Unterverzeichnis unter 'data/'.
    Generiert einen eindeutigen Dateinamen mit Zeitstempel, um Konflikte zu vermeiden.
    Gibt den relativen Pfad zur gespeicherten Datei zurück oder None bei Fehlschlag.
    """
    if uploaded_file is None:
        return None

    # Zielverzeichnis erstellen, falls nicht vorhanden
    target_dir = os.path.join("data", target_subdir)
    os.makedirs(target_dir, exist_ok=True)

    # Erstelle einen eindeutigen Dateinamen: Originalname_Timestamp.Erweiterung
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    # Trenne Dateiname und Erweiterung sauber
    base_filename, file_extension = os.path.splitext(uploaded_file.name)
    # Entferne eventuelle nicht-alphanumerische Zeichen aus dem Basisnamen für einen sauberen Pfad
    safe_base_filename = "".join(c for c in base_filename if c.isalnum() or c in (' ', '.', '_')).strip()
    
    filename = f"{safe_base_filename}_{timestamp}{file_extension}"
    file_path = os.path.join(target_dir, filename)

    try:
        # Schreibe den Inhalt der hochgeladenen Datei
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        # Gib den Pfad zurück, mit forward slashes für JSON/URL-Kompatibilität
        return file_path.replace("\\", "/")
    except Exception as e:
        print(f"FEHLER: Konnte die Datei '{uploaded_file.name}' nicht speichern in '{file_path}'. Fehler: {e}")
        return None

def add_new_person_to_db(new_person_data: dict):
    """
    Fügt eine neue Person (als Dictionary) zur 'person_db.json' hinzu.
    Generiert eine neue ID für die Person, falls nicht bereits vorhanden.
    """
    person_list = Person.load_person_data()
    
    # Generiere eine neue ID nur, wenn die Daten noch keine ID haben
    if "id" not in new_person_data or new_person_data["id"] is None:
        new_person_data["id"] = get_next_person_id()

    # Stelle sicher, dass 'health_data' als Liste initialisiert ist, falls nicht vorhanden
    if "health_data" not in new_person_data or not isinstance(new_person_data["health_data"], list):
        new_person_data["health_data"] = []

    # Füge die neue Person zur Liste hinzu
    person_list.append(new_person_data)

    # Speichere die aktualisierte Liste zurück in die JSON-Datei
    try:
        with open(PERSON_DB_PATH, 'w', encoding='utf-8') as file:
            # indent=4 für bessere Lesbarkeit, ensure_ascii=False für Umlaute etc.
            json.dump(person_list, file, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"FEHLER: Konnte Personendaten nicht in '{PERSON_DB_PATH}' speichern. Fehler: {e}")
        return False

# --- Testbereich (wird nur ausgeführt, wenn person.py direkt gestartet wird) ---
if __name__ == "__main__":
    print(f"Personendatenbank-Pfad: {PERSON_DB_PATH}")
    print(f"Bilder-Verzeichnis: {PICTURES_DIR}")
    print(f"Physiologische Daten-Verzeichnis: {PHYSIOLOGICAL_CYCLES_DIR}")

    print("\n--- Test: load_person_data ---")
    persons = Person.load_person_data()
    print(f"Geladene Personen: {len(persons)}")
    if persons:
        print(persons[0])

    print("\n--- Test: get_next_person_id ---")
    next_id = get_next_person_id()
    print(f"Nächste verfügbare ID: {next_id}")

    # Beispiel einer neuen Person (ohne tatsächlichen Dateiupload)
    # Dies würde normalerweise von Streamlit kommen
    test_new_person_data = {
        "date_of_birth": 1995,
        "firstname": "Max",
        "lastname": "Mustermann",
        "gender": "male",
        "picture_path": "data/pictures/Max_Mustermann_Test.jpg", # Beispielpfad
        "health_data": [
            {
                "id": 1.1,
                "date": "2025-07-01",
                "result_link": "data/physiological_cycles/Max_Mustermann_physio.csv" # Beispielpfad
            }
        ]
    }

    # print("\n--- Test: add_new_person_to_db (Kommentiert, um keine echten Daten hinzuzufügen) ---")
    # if add_new_person_to_db(test_new_person_data):
    #     print(f"Testperson mit ID {test_new_person_data['id']} erfolgreich hinzugefügt.")
    # else:
    #     print("Fehler beim Hinzufügen der Testperson.")

    print("\n--- Test: find_person_data_by_id ---")
    # Wenn Sie eine Person mit ID 1 haben
    found_person = Person.find_person_data_by_id(1)
    if found_person:
        print(f"Person mit ID 1 gefunden: {found_person['firstname']}")
        person_obj_test = Person(found_person)
        print(f"Alter von Person 1: {person_obj_test.calculate_age()} Jahre")
        print(f"Max HR von Person 1: {person_obj_test.max_HR()}")
    else:
        print("Person mit ID 1 nicht gefunden.")

    print("\n--- Test: Person ohne Gesundheitsdaten (sollte keinen Fehler werfen) ---")
    person_without_health = {"id": 99, "firstname": "Test", "lastname": "OhneDaten"}
    obj_without_health = Person(person_without_health)
    print(f"Person ohne Gesundheitsdaten Healthdata-Pfad: {obj_without_health.healthdata_path}")
    
    # Beispiel für eine fehlerhafte JSON-Datei
    # Versuche, eine leere oder kaputte JSON-Datei zu simulieren, um die Fehlerbehandlung zu testen
    # try:
    #     with open(PERSON_DB_PATH, 'w') as f:
    #         f.write("invalid json {")
    #     persons_broken = Person.load_person_data()
    #     print(f"Geladene Personen (fehlerhafte Datei): {len(persons_broken)}")
    # except Exception as e:
    #     print(f"Erwarteter Fehler beim Laden einer fehlerhaften JSON-Datei: {e}")
    # finally:
    #     # Originaldatei wiederherstellen (falls vorhanden)
    #     # shutil.copyfile("data/person_info/person_db.json.bak", PERSON_DB_PATH) 
    #     pass # Hier ist es wichtig, die Originaldatei wiederherzustellen, wenn man das wirklich testet