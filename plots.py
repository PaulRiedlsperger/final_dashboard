from loaddata import read_my_csv
import plotly.express as px
import plotly.io as pio
pio.renderers.default = "browser"

def plot_all(df):

    # Erstellte einen Line Plot, der ersten 2000 Werte mit der Zeit aus der x-Achse
    fig = px.line(df.head(2000), x= "time", y=["Resting heart rate (bpm)", "Heart rate variability (ms)", "Skin temp (celsius)", "Sleep performance %"],
        title="Healthdata over the time")
    
    return fig

def plot_RHR(df):

    # Erstellte einen Line Plot, der ersten 2000 Werte mit der Zeit aus der x-Achse
    fig = px.line(df.head(2000), x= "time", y=["Resting heart rate (bpm)"],
        title="Resting Heart Rate over the time")
    return fig

def plot_HRV(df):

    # Erstellte einen Line Plot, der ersten 2000 Werte mit der Zeit aus der x-Achse
    fig = px.line(df.head(2000), x= "time", y=["Heart rate variability (ms)"],
        title="Heart Rate Variability over the time")
    return fig

def plot_skin_temp(df):

    # Erstellte einen Line Plot, der ersten 2000 Werte mit der Zeit aus der x-Achse
    fig = px.line(df.head(2000), x= "time", y=["skin temp (celsius)"],
        title="Skin temperature over the time")
    return fig

def plot_sleep_performance(df):

    # Erstellte einen Line Plot, der ersten 2000 Werte mit der Zeit aus der x-Achse
    fig = px.line(df.head(2000), x= "time", y=["sleep performance %"],
        title="sleep performance over the time")
    return fig

if __name__ == "__main__":
    df = read_my_csv()   
    fig1 = plot_all(df)
    

    fig1.show()