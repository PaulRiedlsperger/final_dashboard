import plotly.graph_objects as go
import streamlit as st


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




import plotly.graph_objects as go

def show_mini_chart(current, lower, upper, unit):
    fig = go.Figure()

    fig.add_trace(go.Bar(
    x=["Wert"],
    y=[upper - lower],
    base=lower,
    width=0.4,
    name="Normalbereich",
    marker_color='lightgreen',
    orientation='v',
    showlegend=True
))

    fig.add_trace(go.Scatter(
        x=["Wert"],  # NICHT x=[""]
        y=[current],
        mode='markers',
        marker=dict(
            color='blue',
            size=12,
            line=dict(color='black', width=1)
        ),
        name="Aktueller Wert",
        showlegend=True
    ))

    fig.update_layout(
        height=120,
        margin=dict(l=0, r=0, t=0, b=0),
        yaxis=dict(
            title=unit,
            range=[lower - 10, upper + 10]  # Puffer für Punktanzeige
        ),
    )

    return fig


def analyze_abnormalities(df, person):
    age = person.calculate_age()
    gender = person.gender

    results = {}

    parameters = {
        "RHR": {
            "column": "Resting heart rate (bpm)",
            "check_func": AbnormalityChecker.check_rhr,
            "threshold_func": AbnormalityChecker.get_rhr_thresholds,
            "unit": "bpm"
        },
        "HRV": {
            "column": "Heart rate variability (ms)",
            "check_func": AbnormalityChecker.check_hrv,
            "threshold_func": AbnormalityChecker.get_hrv_thresholds,
            "unit": "ms"
        },
        "Hauttemperatur": {
            "column": "Skin temp (celsius)",
            "check_func": AbnormalityChecker.check_temp,
            "threshold_func": AbnormalityChecker.get_temp_thresholds,
            "unit": "°C"
        },
        "Schlafscore": {
            "column": "Sleep performance %",
            "check_func": AbnormalityChecker.check_sleep,
            "threshold_func": AbnormalityChecker.get_sleep_thresholds,
            "unit": "%"
        }
    }

    for param_name, param in parameters.items():
        values = df[param["column"]]
        lower, upper = param["threshold_func"](age, gender)
        abnormalities = ((values < lower) | (values > upper))

        # Visualisierung
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df["time"], y=values, mode="lines", name="Wert"))
        fig.add_trace(go.Scatter(x=df["time"][abnormalities], y=values[abnormalities],
                                 mode="markers", name="Abnormalität", marker=dict(color="red", size=8)))
        fig.add_hrect(y0=lower, y1=upper, fillcolor="green", opacity=0.2, line_width=0)
        fig.update_layout(title=f"{param_name} über Zeit", yaxis_title=param["unit"])
        st.plotly_chart(fig)

        # Ergebnis zusammenfassen
        n_abnormal = abnormalities.sum()
        if n_abnormal == 0:
            summary = "✅ Keine Abnormalitäten"
        else:
            summary = f"❗ {n_abnormal} Abnormalitäten erkannt"

        results[param_name] = summary

    # Farbcodierte Gesamtübersicht
    for name, res in results.items():
        st.markdown(f"**{name}:** {res}")
