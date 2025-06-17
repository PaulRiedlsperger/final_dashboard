from loaddata import read_my_csv
import pandas as pd 



def get_average_Resting_heart_rate(df):
    """ Berechnet den Durchschnitt der Ruheherzfrequenz """
    return df["Resting heart rate (bpm)"].mean()


def get_average_Heart_rate_variability(df):
    """ Berechnet den Durchschnitt der Herzfrequenzvariabilität """
    return df["Heart rate variability (ms)"].mean()

def get_average_Skin_temp_celsius(df):
    """ Berechnet den Durchschnitt der Hauttemperatur in Celsius """
    return df["Skin temp (celsius)"].mean()

def get_average_Sleep_performance_percent(df):
    """ Berechnet den Durchschnitt der Schlafleistung in Prozent """
    return df["Sleep performance %"].mean() 


if __name__ == "__main__":
    df=read_my_csv()
    print("Durchschnittliche Ruheherzfrequenz:", get_average_Resting_heart_rate(df))
    print("Durchschnittliche Herzfrequenzvariabilität:", get_average_Heart_rate_variability(df))
    print("Durchschnittliche Hauttemperatur in Celsius:", get_average_Skin_temp_celsius(df))
    print("Durchschnittliche Schlafleistung in Prozent:", get_average_Sleep_performance_percent(df))