import pandas as pd
import numpy as np


def read_my_csv():
    # Einlesen eines Dataframes
    ## "\t" steht für das Trennzeichen in der txt-Datei (Tabulator anstelle von Beistrich)
    ## header = None: es gibt keine Überschriften in der txt-Datei
    df = pd.read_csv("data/physiological_cycles.csv")

    t_end= len(df)
    time = np.arange(0, t_end)
    df["time"] = time
    
    cols = ["time", "Resting heart rate (bpm)", "Heart rate variability (ms)", "Skin temp (celsius)", "Sleep performance %"]
    df = df[cols]

    return df 




   