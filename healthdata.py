import pandas as pd
import plotly.express as px

class healthData:
    @staticmethod
    def get_average_Resting_heart_rate(df):
        return df["Resting heart rate (bpm)"].mean()

    @staticmethod
    def get_average_Heart_rate_variability(df):
        return df["Heart rate variability (ms)"].mean()

    @staticmethod
    def get_average_Skin_temp_celsius(df):
        return df["Skin temp (celsius)"].mean()

    @staticmethod
    def get_average_Sleep_performance_percent(df):
        return df["Sleep performance %"].mean()

    @staticmethod
    def plot_sleep_pie(avg_sleep_score):
        """Zeigt ein Tortendiagramm des Schlafscores."""
        recovered = min(avg_sleep_score, 100)
        missing = 100 - recovered
        fig = px.pie(
            names=["Erholsamer Schlaf", "Fehlender Anteil"],
            values=[recovered, missing],
            color_discrete_sequence=["mediumseagreen", "peachpuff"]
        )
        fig.update_traces(textinfo='label+percent', hole=0.3)
        fig.update_layout(title="🛌 Schlafscore-Verteilung (%)")
        return fig

    @staticmethod
    def plot_all(df):
        df_valid = df.dropna(subset=[
            "Resting heart rate (bpm)",
            "Heart rate variability (ms)",
            "Skin temp (celsius)",
            "Sleep performance %"
        ])
        fig = px.line(
            df_valid,
            x="time",
            y=["Resting heart rate (bpm)", "Heart rate variability (ms)",
               "Skin temp (celsius)", "Sleep performance %"],
            title="📉 Verlauf aller Gesundheitsparameter"
        )
        return fig
