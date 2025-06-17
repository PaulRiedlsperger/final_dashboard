import streamlit as st
import json
from person import Person

tab1 ,tab2 ,tab3 = st.tabs(["Versuchsperson", "Gesundheitsdaten", "Abnormalitäten"])

with tab1:
 # Session State wird leer angelegt, solange er noch nicht existiert
    if 'current_user' not in st.session_state:
        st.session_state.current_user = 'None'

    # Legen Sie eine neue Liste mit den Personennamen an indem Sie ihre 
    # Funktionen aufrufen
    person_dict = read_my_csv.load_person_data()
    person_names = read_my_csv.get_person_list(person_dict)
    # bzw: wenn Sie nicht zwei separate Funktionen haben
    # person_names = read_data.get_person_list()

    # Eine Überschrift der ersten Ebene
    st.write("# Health-Alert APP")

    # Eine Überschrift der zweiten Ebene
    st.write("## Versuchsperson auswählen")

    # Eine Auswahlbox, das Ergebnis wird in current_user gespeichert
    st.session_state.current_user = st.selectbox(
        'Versuchsperson',
        options = person_names, key="sbVersperson_namesuchsperson")

    # Anlegen des Session State. Bild, wenn es kein Bild gibt
    if 'picture_path' not in st.session_state:
        st.session_state.picture_path = 'data/pictures/none.jpg'

    st.session_state.picture_path = read_data.find_person_data_by_name(st.session_state.current_user)["picture_path"]

    image = Image.open(st.session_state.picture_path)
    st.image(image, caption=st.session_state.current_user)
        

    

    