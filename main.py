import streamlit as st
import json
from person import Person
from PIL import Image
from loaddata import read_my_csv
from healthdata import healthData

tab1 ,tab2 ,tab3 = st.tabs(["Versuchsperson", "Gesundheitsdaten", "Abnormalitäten"])

with tab1:

    person_dict = Person.load_person_data()
    person_names = Person.get_person_list(person_dict)
    person_data = Person.find_person_data_by_id(suchid=1)
    person = Person(**person_data)  
    age = person.calculate_age()
    
    st.header("Persönliche Daten")
    st.image(person["picture_path"], width=200)
    st.markdown(f"**Name:** {person['firstname']}")
    st.markdown(f"**Alter:** {age} Jahre") 
    st.markdown(f"**ID:** {person['id']}")

with tab2:
    pass

with tab3:
    pass


        

   

    

    