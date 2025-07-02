# 📊 Gesundheits-Dashboard (Streamlit App)

Diese Streamlit-Anwendung dient zur Visualisierung, Analyse und Bewertung physiologischer Gesundheitsdaten einzelner Versuchspersonen.

## 🔍 Funktionen

- 👤 **Personenverwaltung**: Auswahl und Anzeige von persönlichen Daten (Name, Alter, Geschlecht, Bild).
- 📈 **Gesundheitsdaten**: Darstellung aktueller Werte zu:
  - Ruheherzfrequenz (RHR)
  - Herzfrequenzvariabilität (HRV)
  - Hauttemperatur
  - Schlafscore
- 📊 **Zeitreihenverlauf**: Visualisierung der Gesundheitswerte über die Zeit.
- ⚠️ **Abnormalitäten**: Automatische Bewertung der Parameter im Vergleich zu alters- und geschlechtsspezifischen Normwerten mit farblicher Ampel-Logik (Normal / Auffällig).
- 🧠 **Datenbasis**: Gesundheitsdaten werden individuell pro Person aus CSV-Dateien geladen.


## Zuküntige Verbesserungs Punkte

-gepublishte Seite optimieren! (https://finaldashboard-fsd4t3us5dfmwbkvqgxftn.streamlit.app/)
  -aktuelle Fehler mit den Fotos und csv Datein die lokal gespeichert sind. 
-Abnormalitäten per Mail an die jenineg Person schicken
-Grafische verbesserungen




## ▶️ Starten der App

```bash
streamlit run main.py


