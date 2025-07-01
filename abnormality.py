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


import streamlit as st
import plotly.graph_objects as go

def plot_abnormalities_over_time(df):
    """
    Plottet die vier Gesundheitsparameter (RHR, HRV, Temp, Sleep) über die Zeit mit Statusanzeige.
    """
    color_map = {
        "Normal": "green",
        "Zu hoch": "red",
        "Zu niedrig": "orange",
        "Gut": "blue",
        "Schlafqualität gering": "darkred",
        "Mittelmäßig": "gold"
    }

    st.subheader("📈 Verlauf der Gesundheitsparameter mit Statusanzeige")

    for param in ["RHR", "HRV", "Temp", "Sleep"]:
        status_col = param + "_status"
        if param in df.columns and status_col in df.columns:
            st.markdown(f"**{param} über die Zeit**")
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df["time"],
                y=df[param],
                mode="lines+markers",
                marker=dict(color=[color_map.get(status, "grey") for status in df[status_col]]),
                text=df[status_col],
                name=param
            ))
            fig.update_layout(
                xaxis_title="Zeit",
                yaxis_title=param,
                height=300
            )
            st.plotly_chart(fig, use_container_width=True)


