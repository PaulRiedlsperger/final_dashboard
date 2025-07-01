import plotly.graph_objects as go
import streamlit as st
from loaddata import read_my_csv_2
import pandas as pd
from itertools import groupby
import unicodedata


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
    return symbol_map.get(status.lower().strip(), "•")

# Einfache Status-Normalisierung
def clean_status(status):
    return str(status).strip().lower()

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


def show_abnormality_analysis_with_datetime(file_path, person_obj):
    # Daten einlesen mit datetime
    df = read_my_csv_2(file_path)

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
    status_icons = {
        "Normal": "✅ Normal",
        "Zu hoch": "❗ Zu hoch",
        "Zu niedrig": "❗ Zu niedrig",
        "Gut": "✅ Gut",
        "Mittelmäßig": "🟡 Mittelmäßig",
        "Schlafqualität gering": "❗ Schlafqualität gering"
    }

    for col in ["RHR_status", "HRV_status", "Temp_status", "Sleep_status"]:
        df[col] = df[col].map(status_icons)

    # Anzeige
    st.markdown("### ⚠️ Abnormalitäten über den Zeitverlauf")
    st.markdown("#### Analyse abgeschlossen ✅ – bereit zur Visualisierung")

    # Tabelle anzeigen
    st.dataframe(df)

    return df  # optional, falls du das später brauchst
