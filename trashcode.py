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
