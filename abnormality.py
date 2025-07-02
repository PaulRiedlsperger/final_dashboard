import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import streamlit as st
from itertools import groupby
import unicodedata # Bleibt, da es in dem von dir gegebenen Code war


class AbnormalityChecker:

    @staticmethod
    def check_rhr(value, age, gender):
        # Annahme: trainierte Männer können niedrigeren RHR haben
        lower = 45 if gender == 'male' else 50
        upper = 90 if age > 50 else 85
        if value < lower:
            return "❗Zu niedrig"
        elif value > upper:
            return "❗Zu hoch"
        else:
            return "✅ Normal"

    @staticmethod
    def get_rhr_thresholds(age, gender):
        lower = 45 if gender == 'male' else 50
        upper = 90 if age > 50 else 85
        return lower, upper

    @staticmethod
    def check_hrv(value, age, gender):
        lower = 20 if age > 50 else 30
        if gender == 'male':
            lower -= 5  # Männer oft geringere HRV
        if value < lower:
            return "❗Zu niedrig"
        else:
            return "✅ Normal"
        
    @staticmethod
    def get_hrv_thresholds(age, gender):
        lower = 20 if age > 50 else 30
        if gender == 'male':
            lower -= 5
        upper = 100  # optional fix setzen
        return lower, upper


    @staticmethod
    def check_skin_temp(value, age, gender):
        # Frauen haben oft höhere Hauttemperatur
        normal_range = (32.5, 34.5) if gender == 'female' else (32.0, 34.0)
        if value < normal_range[0]:
            return "❗Zu niedrig"
        elif value > normal_range[1]:
            return "❗Zu hoch"
        else:
            return "✅ Normal"
        
    @staticmethod
    def get_skin_temp_thresholds(gender):
        return (32.5, 34.5) if gender == 'female' else (32.0, 34.0)

    @staticmethod
    def check_sleep_score(value, age, gender):
        if value < 70:
            return "❗Schlafqualität gering"
        elif value < 85:
            return "🟡 Mittelmäßig"
        else:
            return "✅ Gut"
        
    @staticmethod
    def get_sleep_score_thresholds():
        return 70, 85

    # NEU: Angepasste Funktion zur Analyse und Empfehlungsgenerierung mit Emojis
    @staticmethod
    def analyze_and_recommend(df, days_lookback=30):
        recommendations = []
        df['datetime'] = pd.to_datetime(df['datetime']) # Stelle sicher, dass 'datetime' ein datetime-Objekt ist

        if not df.empty:
            latest_date = df['datetime'].max()
            df_recent = df[df['datetime'] >= (latest_date - timedelta(days=days_lookback))]
        else:
            return [("ℹ️", "Keine ausreichenden Daten für eine Analyse im angegebenen Zeitraum.")]

        # --- Allgemeine Gesundheitsübersicht ---
        # Zähle Vorkommen von problematischen Status
        problem_rhr_count = df_recent[df_recent['RHR_status'].str.contains('❗')].shape[0]
        problem_hrv_count = df_recent[df_recent['HRV_status'].str.contains('❗')].shape[0]
        problem_temp_count = df_recent[df_recent['Temp_status'].str.contains('❗')].shape[0]
        problem_sleep_count = df_recent[df_recent['Sleep_status'].str.contains('❗')].shape[0]

        total_problem_days = sum([problem_rhr_count, problem_hrv_count, problem_temp_count, problem_sleep_count])
        
        # Empfehlung für den Gesamtstatus
        if total_problem_days == 0:
            recommendations.append(("✅", "Alle gemessenen Parameter sind in den letzten 30 Tagen im normalen Bereich. Hervorragend! Behalten Sie Ihre Routinen bei."))
        elif total_problem_days < len(df_recent) * 0.2: # Weniger als 20% der Tage mit Problemen
            recommendations.append(("👍", "Ihre Daten zeigen größtenteils gute Werte mit nur wenigen kleineren Abweichungen. Weiter so!"))
        elif total_problem_days > len(df_recent) * 0.5: # Mehr als 50% der Tage mit Problemen
             recommendations.append(("🚨", "**Achtung: Erhebliche Abweichungen in Ihren Gesundheitsdaten.**\n"
                                     "Ihre Daten der letzten 30 Tage zeigen wiederholt signifikante Abweichungen in mehreren Bereichen. "
                                     "Es ist ratsam, einen Arzt zu konsultieren oder Ihre Lebensweise (Ernährung, Schlaf, Stress) genau zu überprüfen. "
                                     "Ihr Körper sendet deutliche Warnsignale."))
        else:
            recommendations.append(("⚠️", "**Beachten Sie einige Abweichungen in Ihren Gesundheitsdaten.**\n"
                                     "In den letzten 30 Tagen wurden einige Werte außerhalb des Optimalbereichs registriert. "
                                     "Lesen Sie die spezifischen Empfehlungen unten, um gezielt darauf einzugehen und Ihr Wohlbefinden zu verbessern."))


        # --- Spezifische Empfehlungen basierend auf häufigen oder kritischen Abweichungen ---

        # Hohe Ruheherzfrequenz
        if df_recent['RHR_status'].str.contains('❗Zu hoch').any():
            recommendations.append(
                ("❤️‍🩹", "**Hohe Ruheherzfrequenz (RHR) erkannt.**\n"
                 "Eine wiederholt erhöhte RHR kann auf Stress, mangelnde Erholung oder eine beginnende Erkältung hinweisen. "
                 "Versuchen Sie, Entspannungstechniken zu integrieren (Meditation, tiefe Atmung) und achten Sie auf ausreichend Schlaf und Hydration. "
                 "Vermeiden Sie übermäßigen Koffein- oder Alkoholkonsum am Abend.")
            )
        # Niedrige Ruheherzfrequenz
        if df_recent['RHR_status'].str.contains('❗Zu niedrig').any():
            recommendations.append(
                ("🐌", "**Niedrige Ruheherzfrequenz (RHR) erkannt.**\n"
                 "Eine ungewöhnlich niedrige RHR kann bei sehr gut trainierten Personen normal sein, aber auch auf Übertraining oder Unterernährung hinweisen. "
                 "Achten Sie auf ausreichende Kalorienzufuhr und geben Sie Ihrem Körper genügend Erholungszeit nach intensiven Trainingseinheiten.")
            )

        # Niedrige Herzfrequenz-Variabilität (HRV)
        if df_recent['HRV_status'].str.contains('❗Zu niedrig').any():
            recommendations.append(
                ("🧘‍♀️", "**Niedrige Herzfrequenz-Variabilität (HRV) erkannt.**\n"
                 "Eine niedrige HRV ist ein starker Indikator für physischen oder mentalen Stress und unzureichende Erholung. "
                 "Fokussieren Sie sich auf Stressmanagement, ausreichend Schlaf (7-9 Stunden), moderate Bewegung und eine ausgewogene Ernährung. "
                 "Vermeiden Sie intensive Trainingseinheiten, wenn Ihre HRV niedrig ist.")
            )

        # Abweichende Hauttemperatur
        if df_recent['Temp_status'].str.contains('❗').any():
            recommendations.append(
                ("🌡️", "**Abweichende Hauttemperatur festgestellt.**\n"
                 "Ob zu hoch oder zu niedrig, eine Abweichung der Hauttemperatur kann auf eine beginnende Krankheit, hormonelle Schwankungen oder Umwelteinflüsse hindeuten. "
                 "Beobachten Sie weitere Symptome. Bei anhaltenden oder ungewöhnlichen Abweichungen konsultieren Sie einen Arzt.")
            )

        # Schlechte Schlafqualität
        if df_recent['Sleep_status'].str.contains('❗Schlafqualität gering').any():
            recommendations.append(
                ("😴", "**Geringe Schlafqualität.**\n"
                 "Regelmäßig schlechter Schlaf beeinträchtigt die Erholung und Leistungsfähigkeit. "
                 "Verbessern Sie Ihre Schlafhygiene: Feste Schlafzeiten, kühles, dunkles Zimmer, Vermeidung von Bildschirmen vor dem Schlafengehen. "
                 "Ein kurzes Nickerchen am Nachmittag (max. 20-30 Min.) kann helfen, sollte aber den Nachtschlaf nicht beeinträchtigen.")
            )
        
        # Mittelmäßige Schlafqualität
        if df_recent['Sleep_status'].str.contains('🟡 Mittelmäßig').any() and not df_recent['Sleep_status'].str.contains('❗Schlafqualität gering').any():
            recommendations.append(
                ("💡", "**Mittelmäßige Schlafqualität.**\n"
                 "Ihre Schlafqualität ist akzeptabel, aber es gibt Raum für Verbesserungen. "
                 "Experimentieren Sie mit kleinen Anpassungen wie einem entspannenden Ritual vor dem Schlafengehen oder einer Tasse Kräutertee. "
                 "Auch eine Optimierung der Matratze oder des Kissens kann Wunder wirken.")
            )

        if not recommendations:
            recommendations.append(("ℹ️", "Keine spezifischen Empfehlungen basierend auf den aktuellen Anomalien erforderlich."))

        return recommendations

# Emojis für Tooltips
def status_to_symbol(status):
    symbol_map = {
        "normal": "✅",
        "zu hoch": "❗",
        "zu niedrig": "⚠️",
        "gut": "✅",
        "schlafqualität gering": "❗",
        "mittelmäßig": "🟡"
    }
    # Normalize status string to remove non-ASCII and extra spaces
    normalized_status = unicodedata.normalize('NFKD', status).encode('ascii', 'ignore').decode('utf-8').lower().strip()
    return symbol_map.get(normalized_status, "•")

# Einfache Status-Normalisierung
def clean_status(status):
    return unicodedata.normalize('NFKD', str(status)).encode('ascii', 'ignore').decode('utf-8').strip().lower()


# Gruppiere zusammenhängende gleiche Status in Intervalle
def get_status_intervals(dates, statuses):
    intervals = []
    cleaned = [clean_status(s) for s in statuses]
    for status, group in groupby(zip(dates, cleaned), key=lambda x: x[1]):
        group = list(group)
        start = group[0][0]
        end = group[-1][0] + pd.Timedelta(hours=12)  # etwas verlängert
        intervals.append((start, end, status))
    return intervals

# Hauptfunktion zum Plotten
def plot_abnormalities_over_time(df):
    st.subheader("📈 Verlauf der Gesundheitsparameter mit Statusanzeige")

    color_map = {
        "normal": "green",
        "zu hoch": "red",
        "zu niedrig": "orange",
        "gut": "blue",
        "schlafqualität gering": "darkred",
        "mittelmäßig": "gold"
    }

    for param in ["RHR", "HRV", "Temp", "Sleep"]:
        status_col = param + "_status"
        if param in df.columns and status_col in df.columns:

            st.markdown(f"**{param} über die Zeit**")

            # Statusspalte vereinheitlichen
            df[status_col] = df[status_col].apply(clean_status)

            # Optionale Debug-Anzeige
            if st.checkbox(f"🛠️ Zeige Status-Werte für {param}", key=param):
                st.write(df[status_col].unique())

            # Tooltip & Markerfarben vorbereiten
            hover_text = [
                f"{status_to_symbol(status)} {status.title()}<br>Wert: {value}"
                for status, value in zip(df[status_col], df[param])
            ]
            marker_colors = [color_map.get(status, "grey") for status in df[status_col]]

            # Plot erstellen
            fig = go.Figure()

            # Hintergrundfarben anhand zusammenhängender Status
            intervals = get_status_intervals(df["datetime"], df[status_col])
            shapes = []
            for start, end, status in intervals:
                color = color_map.get(status, "lightgrey")
                shapes.append(dict(
                    type="rect",
                    xref="x",
                    yref="paper",
                    x0=start,
                    x1=end,
                    y0=0,
                    y1=1,
                    fillcolor=color,
                    opacity=0.2,  # gut sichtbar
                    layer="below",
                    line=dict(width=0)
                ))

            # Linie
            fig.add_trace(go.Scatter(
                x=df["datetime"],
                y=df[param],
                mode="lines",
                line=dict(color="blue", width=2),
                name=f"{param} Verlauf"
            ))

            # Punkte
            fig.add_trace(go.Scatter(
                x=df["datetime"],
                y=df[param],
                mode="markers",
                marker=dict(size=10, color=marker_colors),
                text=hover_text,
                hoverinfo="text",
                name=f"{param} Status"
            ))

            fig.update_layout(
                xaxis_title="Datum",
                yaxis_title=param,
                height=300,
                shapes=shapes,
                margin=dict(t=20, b=40)
            )

            st.plotly_chart(fig, use_container_width=True)


# show_abnormality_analysis_with_datetime muss nun das df zurückgeben, da es in main.py für die Analyse benötigt wird
def show_abnormality_analysis_with_datetime(file_path, person_obj):
    # Daten einlesen mit datetime
    df = read_my_csv_2(file_path) # Gehe davon aus, dass read_my_csv_2 jetzt korrekt importiert ist

    # Alter & Geschlecht berechnen
    age = person_obj.calculate_age()
    gender = person_obj.gender

    # Abweichungen prüfen & Statusspalten hinzufügen
    for param, check_func in {
        "RHR": AbnormalityChecker.check_rhr,
        "HRV": AbnormalityChecker.check_hrv,
        "Temp": AbnormalityChecker.check_skin_temp,
        "Sleep": AbnormalityChecker.check_sleep_score,
    }.items():
        df[param + "_status"] = df[param].apply(lambda v: check_func(v, age, gender))

    # Farbige Icons
    # Beachte, dass die Icons hier nochmals hinzugefügt werden, um die Spalten für die Anzeige zu bereinigen.
    # Die analyze_and_recommend Funktion sollte die "sauberen" Statusstrings verwenden, ohne Icons.
    # Daher ist es wichtig, die Statusübergabe in analyze_and_recommend nicht direkt aus diesen angezeigten Spalten zu nehmen,
    # sondern aus den ursprünglichen Check-Funktionen oder einer separaten Verarbeitung.
    # Für analyze_and_recommend habe ich die strings.contains logic verwendet, die robust gegen die Emojis ist.
    status_icons_display = { # Benenne dies um, um Verwechslungen zu vermeiden
        "Normal": "✅ Normal",
        "Zu hoch": "❗ Zu hoch",
        "Zu niedrig": "❗ Zu niedrig",
        "Gut": "✅ Gut",
        "Mittelmäßig": "🟡 Mittelmäßig",
        "Schlafqualität gering": "❗ Schlafqualität gering"
    }

    # Nur für die Anzeige im Dataframe die Spalten ändern
    for col in ["RHR_status", "HRV_status", "Temp_status", "Sleep_status"]:
        # Erstelle eine temporäre Spalte, die die sauberen Statusstrings enthält, um sie für die Empfehlungen zu nutzen
        # Hier ist es wichtig, dass analyze_and_recommend auf die ursprünglichen Status ohne Emojis zugreift
        # oder robust damit umgeht. Meine analyze_and_recommend ist robust, da sie auf "❗", "🟡" etc. prüft.
        # df[col] = df[col].map(status_icons_display) # Nur anwenden, wenn es wirklich nur für die Anzeige ist

        # Bessere Handhabung: Wenn die Status schon Emojis haben, müssen sie nicht nochmal gemappt werden
        # Wir wollen nur die Status, wie sie von den Check-Funktionen zurückkommen.
        # Die check_rhr, check_hrv etc. Funktionen geben bereits die Emojis zurück.
        # Daher ist diese Zeile, die die Emojis nochmal hinzufügt, überflüssig und würde die Strings doppelt ändern,
        # wenn sie bereits Emojis enthalten.
        pass


    # Anzeige
    st.markdown("### ⚠️ Abnormalitäten über den Zeitverlauf")
    st.markdown("#### Analyse abgeschlossen ✅ – bereit zur Visualisierung")

    # Tabelle anzeigen
    st.dataframe(df)

    return df # Rückgabe des DataFrame ist entscheidend für main.py