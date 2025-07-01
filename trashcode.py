# Ausgabe
    # RHR
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown(f"**💖 RHR:** {rhr_warning}")
    with col2:
        st.plotly_chart(show_mini_chart(current=latest_rhr, lower=lower_rhr, upper=upper_rhr, unit="bpm"), use_container_width=True)

    # HRV
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown(f"**💕 HRV:** {hrv_warning}")
    with col2:
        st.plotly_chart(show_mini_chart(current=latest_hrv, lower=lower_hrv, upper=upper_hrv, unit="ms"), use_container_width=True)

    # Temperatur
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown(f"**🌡️ Hauttemperatur:** {temp_warning}")
    with col2:
        st.plotly_chart(show_mini_chart(current=latest_temp, lower=lower_temp, upper=upper_temp, unit="°C"), use_container_width=True)

    # Schlafscore
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown(f"**😴 Schlafscore:** {sleep_warning}")
    with col2:
        st.plotly_chart(show_mini_chart(current=latest_sleep, lower=lower_sleep, upper=upper_sleep, unit="%"), use_container_width=True)
            
    result_link = person.healthdata_path
    df = read_my_csv(result_link)
   
'''import json
from datetime import datetime

class Person:
    
    @staticmethod
    def load_person_data():
        """A Function that knows where te person Database is and returns a Dictionary with the Persons"""
        file = open("data/person_info/person_db.json")
        person_data = json.load(file)
        return person_data

    @staticmethod
    def get_person_list(person_data):
        """A Function that takes the persons-dictionary and returns a list auf all person names"""
        list_of_names = []

        for eintrag in person_data:
            list_of_names.append(eintrag["lastname"] + ", " +  eintrag["firstname"])
        return list_of_names
        
    @staticmethod
    def find_person_data_by_id(suchid):
        """ Eine Funktion der Nachname, Vorname als ein String übergeben wird
        und die die Person als Dictionary zurück gibt"""

        person_data = Person.load_person_data()
        #print(suchstring)
        if suchid == "None":
            return {}
    
        
        for eintrag in person_data:
            print(eintrag)
            if eintrag["id"] == suchid:
                print()
                return eintrag
        else:
            raise Exception(f"the id {suchid} was not found in the person database")
        
    def calculate_age(self):
        
        today = datetime.today()
        age = today.year - self.date_of_birth 
        return age
        
    def max_HR(self):

        HR_max = 220 - self.calculate_age()
        return HR_max

    def __init__(self, person_dict) -> None:
        self.date_of_birth = person_dict["date_of_birth"]
        self.firstname = person_dict["firstname"]
        self.lastname = person_dict["lastname"]
        self.picture_path = person_dict["picture_path"]
        self.id = person_dict["id"]
        self.healthdata_path = person_dict["health_data"][0]["result_link"]
        self.gender = person_dict["gender"]





    
    
if __name__ == "__main__":
    #print("This is a module with some functions to read the person data")
    persons = Person.load_person_data()
    person_names = Person.get_person_list(persons)
    #print(person_names)

    Person_dict= Person.find_person_data_by_id(6)
    print(Person_dict)

    person6 = Person(Person_dict)
    Person_age=person6.calculate_age()
    print(Person_age)

    person_max_HR = person6.max_HR()
    print(person_max_HR)'''

'''import json
from datetime import datetime

class Person:
    
    @staticmethod
    def load_person_data():
        """A Function that knows where te person Database is and returns a Dictionary with the Persons"""
        file = open("data/person_info/person_db.json")
        person_data = json.load(file)
        return person_data

    @staticmethod
    def get_person_list(person_data):
        """A Function that takes the persons-dictionary and returns a list auf all person names"""
        list_of_names = []

        for eintrag in person_data:
            list_of_names.append(eintrag["lastname"] + ", " +  eintrag["firstname"])
        return list_of_names
        
    @staticmethod
    def find_person_data_by_id(suchid):
        """ Eine Funktion der Nachname, Vorname als ein String übergeben wird
        und die die Person als Dictionary zurück gibt"""

        person_data = Person.load_person_data()
        #print(suchstring)
        if suchid == "None":
            return {}
    
        
        for eintrag in person_data:
            print(eintrag)
            if eintrag["id"] == suchid:
                print()
                return eintrag
        else:
            raise Exception(f"the id {suchid} was not found in the person database")
        
    def calculate_age(self):
        
        today = datetime.today()
        age = today.year - self.date_of_birth 
        return age
        
    def max_HR(self):

        HR_max = 220 - self.calculate_age()
        return HR_max

    def __init__(self, person_dict) -> None:
        self.date_of_birth = person_dict["date_of_birth"]
        self.firstname = person_dict["firstname"]
        self.lastname = person_dict["lastname"]
        self.picture_path = person_dict["picture_path"]
        self.id = person_dict["id"]
        self.healthdata_path = person_dict["health_data"][0]["result_link"]
        self.gender = person_dict["gender"]





    
    
if __name__ == "__main__":
    #print("This is a module with some functions to read the person data")
    persons = Person.load_person_data()
    person_names = Person.get_person_list(persons)
    #print(person_names)

    Person_dict= Person.find_person_data_by_id(6)
    print(Person_dict)

    person6 = Person(Person_dict)
    Person_age=person6.calculate_age()
    print(Person_age)

    person_max_HR = person6.max_HR()
    print(person_max_HR)'''


st.header("⚠ Abnormalitäten")
    if 'selected_person_data' in locals() and selected_person_data:
        # Importe hier, um Ladezeit zu optimieren, wenn Tab nicht aktiv ist
        from abnormality import AbnormalityChecker, show_mini_chart

        health_data_info = selected_person_data.get("health_data")
        if health_data_info and health_data_info[0].get("result_link"):
            csv_file_path = health_data_info[0]["result_link"]
            try:
                df = read_my_csv(csv_file_path)
                person_obj = Person(selected_person_data) # Neu initialisieren, um sicherzustellen
                age = person_obj.calculate_age()
                gender = person_obj.gender

                # Letzte Werte extrahieren
                latest_rhr = healthData.get_latest_value(df, "Resting heart rate (bpm)")
                latest_hrv = healthData.get_latest_value(df, "Heart rate variability (ms)")
                latest_temp = healthData.get_latest_value(df, "Skin temp (celsius)")
                latest_sleep = healthData.get_latest_value(df, "Sleep performance %")

                # Dynamische Grenzwerte aus der Klasse holen
                lower_rhr, upper_rhr = AbnormalityChecker.get_rhr_thresholds(age, gender)
                lower_hrv, upper_hrv = AbnormalityChecker.get_hrv_thresholds(age, gender)
                lower_temp, upper_temp = AbnormalityChecker.get_skin_temp_thresholds(gender)
                lower_sleep, upper_sleep = AbnormalityChecker.get_sleep_score_thresholds()

                # Analyse
                rhr_warning = AbnormalityChecker.check_rhr(latest_rhr, age, gender)
                hrv_warning = AbnormalityChecker.check_hrv(latest_hrv, age, gender)
                temp_warning = AbnormalityChecker.check_skin_temp(latest_temp, age, gender)
                sleep_warning = AbnormalityChecker.check_sleep_score(latest_sleep, age, gender) # Achtung: hier war latest_temp statt latest_sleep!

                # Ausgabe
                # RHR
                col1, col2 = st.columns([2, 1])
                with col1:
                    st.markdown(f"**💖 RHR:** {rhr_warning}")
                with col2:
                    st.plotly_chart(show_mini_chart(current=latest_rhr, lower=lower_rhr, upper=upper_rhr, unit="bpm"), use_container_width=True)

                # HRV
                col1, col2 = st.columns([2, 1])
                with col1:
                    st.markdown(f"**💕 HRV:** {hrv_warning}")
                with col2:
                    st.plotly_chart(show_mini_chart(current=latest_hrv, lower=lower_hrv, upper=upper_hrv, unit="ms"), use_container_width=True)

                # Temperatur
                col1, col2 = st.columns([2, 1])
                with col1:
                    st.markdown(f"**🌡️ Hauttemperatur:** {temp_warning}")
                with col2:
                    st.plotly_chart(show_mini_chart(current=latest_temp, lower=lower_temp, upper=upper_temp, unit="°C"), use_container_width=True)

                # Schlafscore
                col1, col2 = st.columns([2, 1])
                with col1:
                    st.markdown(f"**😴 Schlafscore:** {sleep_warning}")
                with col2:
                    st.plotly_chart(show_mini_chart(current=latest_sleep, lower=lower_sleep, upper=upper_sleep, unit="%"), use_container_width=True)

            except FileNotFoundError:
                st.error(f"Die CSV-Datei für die Gesundheitsdaten wurde nicht gefunden: {csv_file_path}")
            except KeyError as e:
                st.error(f"Fehlende Spalte in der Gesundheitsdaten-CSV: {e}. Bitte überprüfen Sie die Spaltennamen.")
            except Exception as e:
                st.error(f"Fehler beim Laden oder Verarbeiten der Abnormalitätsdaten: {e}")
        else:
            st.info("Für diese Person sind keine Gesundheitsdaten verknüpft, um Abnormalitäten zu prüfen.")
    else:
        st.info("Bitte wählen Sie zuerst eine Versuchsperson aus dem 'Versuchsperson'-Tab aus.")


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
