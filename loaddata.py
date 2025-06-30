import pandas as pd
import numpy as np


def read_my_csv(filepath):
    """
    Liest eine CSV-Datei mit physiologischen Daten ein und gibt einen bereinigten DataFrame zurück.
    
    Parameter:
    filepath (str): Pfad zur CSV-Datei
    
    Rückgabe:
    pd.DataFrame: DataFrame mit ausgewählten Spalten
    """
    df = pd.read_csv(filepath)

    t_end = len(df)
    time = np.arange(0, t_end)
    df["time"] = time

    cols = ["time", "Resting heart rate (bpm)", 
            "Heart rate variability (ms)", 
            "Skin temp (celsius)", 
            "Sleep performance %"]

    df = df[cols]  # nur relevante Spalten behalten
    return df




   