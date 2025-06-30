from loaddata import read_my_csv
import pandas as pd 
from loaddata import read_my_csv
import plotly.express as px
import plotly.io as pio
pio.renderers.default = "browser"

class healthData:
    @staticmethod
    def get_average_Resting_heart_rate(df):
        """ Berechnet den Durchschnitt der Ruheherzfrequenz """
        return df["Resting heart rate (bpm)"].mean()

    @staticmethod
    def get_average_Heart_rate_variability(df):
        """ Berechnet den Durchschnitt der Herzfrequenzvariabilität """
        return df["Heart rate variability (ms)"].mean()

    @staticmethod
    def get_average_Skin_temp_celsius(df):
        """ Berechnet den Durchschnitt der Hauttemperatur in Celsius """
        return df["Skin temp (celsius)"].mean()

    @staticmethod
    def get_average_Sleep_performance_percent(df):
        """ Berechnet den Durchschnitt der Schlafleistung in Prozent """
        return df["Sleep performance %"].mean()

    @staticmethod
    def plot_all(df):

        
        fig = px.line(df.head(2000), x= "time", y=["Resting heart rate (bpm)", "Heart rate variability (ms)", "Skin temp (celsius)", "Sleep performance %"],
            title="Healthdata over the time")

        return fig

    @staticmethod
    def plot_RHR(df):

        df_valid = df[["time", "Resting heart rate (bpm)"]].dropna()
        fig = px.line(df_valid, x= "time", y="Resting heart rate (bpm)",
            title="Resting Heart Rate over the time")
        return fig

    @staticmethod
    def plot_HRV(df):
        df_valid = df[["time", "Heart rate variability (ms)"]].dropna()
        fig = px.line(df_valid, x= "time", y="Heart rate variability (ms)",
            title="Heart Rate Variability over the time")
        return fig

    
    @staticmethod
    def plot_skin_temp(df):
        df_valid = df[["time", "Skin temp (celsius)"]].dropna()
        fig = px.line(df_valid, x="time", y="Skin temp (celsius)",
                  title="Skin temperature over the time")
        return fig

    @staticmethod
    def plot_sleep_performance(df):

        df_valid = df[["time", "Sleep performance %"]].dropna()
        fig = px.line(df_valid, x= "time", y="Sleep performance %",
            title="sleep performance over the time")
        return fig
    
    @staticmethod
    def get_latest_value(df, column):
        df["time"] = pd.to_datetime(df["time"], errors='coerce')
        latest_row = df.sort_values(by="time", ascending=False).iloc[0]
        return latest_row[column]

if __name__ == "__main__":
    df = read_my_csv()
    print("Durchschnittliche Ruheherzfrequenz:", healthData.get_average_Resting_heart_rate(df))
    print("Durchschnittliche Herzfrequenzvariabilität:", healthData.get_average_Heart_rate_variability(df))
    print("Durchschnittliche Hauttemperatur in Celsius:", healthData.get_average_Skin_temp_celsius(df))
    print("Durchschnittliche Schlafleistung in Prozent:", healthData.get_average_Sleep_performance_percent(df))
    fig1 = healthData.plot_all(df)
    fig1.show() 