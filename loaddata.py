import pandas as pd
import numpy as np
import plotly.express as px
import plotly.io as pio
pio.renderers.default = "browser"

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


def make_plot(df):

    # Erstellte einen Line Plot, der ersten 2000 Werte mit der Zeit aus der x-Achse
    fig = px.line(df.head(2000), x= "time", y=["Resting heart rate (bpm)"],
        title="Resting Heart Rate über die Zeit")
    
    return fig


if __name__ == "__main__":
    df = read_my_csv()   
    fig = make_plot(df)

    fig.show()


#print(read_my_csv())

#df = pd.read_csv("data/physiological_cycles.csv")
#print(df.columns.tolist())
   