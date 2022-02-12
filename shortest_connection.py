from pkgutil import get_data
from gedcom.parser import Parser
import streamlit as st
import pickle
import datetime

from utils import *
import gm_secrets

st.set_page_config(layout="wide")


def check_password():
    """Returns `True` if the user had the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["password"] == gm_secrets.password:
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # don't store password
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # First run, show input for password.
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        return False
    elif not st.session_state["password_correct"]:
        # Password not correct, show input + error.
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        st.error("😕 Password incorrect")
        return False
    else:
        # Password correct.
        return True

gedcom_parser = None

@st.experimental_singleton
def get_database_session():
    global gedcom_parser
    if gedcom_parser is None:
        st.write('Családfa betöltése (~30 másodperc)...')
        with open('gedcom_parser.bin', 'rb') as handle:
            gedcom_parser = pickle.load(handle)
    return gedcom_parser

def main():
    funkcio_selectbox = st.sidebar.selectbox("Funkció választás", ("Legrövidebb út, név alapján", "Legrövidebb út, ID alapján", "Név lista keresése a családfában"))

    if funkcio_selectbox == "Legrövidebb út, név alapján":
        st.title('Legrövidebb út két ember között a Hollai/Görög családfában')
        st.write('Add meg a két személy nevét, majd kattints a gombra. Név-töredék is megadható, viszont kisbetű-nagybetű érzékeny. Az évszám nem kötelező, de segíthet szűkíteni.')

        col1, col2, col3, col4 = st.columns(4)
        p1_1 = col1.text_input('1. személy vezetéknév:', value="Görög")
        p1_2 = col2.text_input('1. személy keresztnév:', value="Márton")
        p1_filter_birth = col3.checkbox('Szűrés születési évre', key='p1_filter_birth')
        if p1_filter_birth:
            p1_birth = col4.number_input('1. személy születési év:', min_value=1300, max_value=2023, format='%d')
        col1, col2, col3, col4 = st.columns(4)
        p2_1 = col1.text_input('2. személy vezetéknév:', value="Andrássy")
        p2_2 = col2.text_input('2. személy keresztnév:', value="Ilona")
        p2_filter_birth = col3.checkbox('Szűrés születési évre', key='p2_filter_birth')
        if p2_filter_birth:
            p2_birth = col4.number_input('2. személy születési év:', min_value=1300, max_value=2023, format='%d')

        if st.button('Keress'):
            gedcom_parser = get_database_session()

            root_child_elements = gedcom_parser.get_root_child_elements()

            p1 = find(root_child_elements, p1_1, p1_2, p1_birth if p1_filter_birth else None)
            if p1 is None:
                st.error(p1_1 + ' ' + p1_2 + ' nem található')
                return
            p2 = find(root_child_elements, p2_1, p2_2, p2_birth if p2_filter_birth else None)
            if p2 is None:
                st.error(p2_1 + ' ' + p2_2 + ' nem található')
                return

            st.write('Kapcsolat keresése...')
            jumps = findConnection(gedcom_parser, p1, p2)
            print(datetime.datetime.now(), toString(p1) , toString(p2))

            st.write('Kirajzolás...')
            img = drawJumps(gedcom_parser, p2, jumps)

            st.image(img.render())

    if funkcio_selectbox == "Legrövidebb út, ID alapján":
        st.title('Legrövidebb út két ember között a Hollai/Görög családfában')
        st.write('Add meg a két személy ID-ját, majd kattints a gombra.')

        col1, col2, col3, col4 = st.columns(4)
        p1_id = col1.text_input('1. személy ID:', value="605084")
        
        col1, col2, col3, col4 = st.columns(4)
        p2_id = col1.text_input('2. személy ID:', value="I533566")
        
        if st.button('Keress'):
            gedcom_parser = get_database_session()

            root_child_elements = gedcom_parser.get_root_child_elements()

            p1 = findPersonByID(gedcom_parser, p1_id)
            if p1 is None:
                st.error(p1_id + ' nem található')
                return
            st.write(f'{p1_id} = {toString(p1)}')
            p2 = findPersonByID(gedcom_parser, p2_id)
            if p2 is None:
                st.error(p2_id + ' nem található')
                return
            st.write(f'{p2_id} = {toString(p2)}')

            st.write('Kapcsolat keresése...')
            jumps = findConnection(gedcom_parser, p1, p2)
            print(datetime.datetime.now(), toString(p1) , toString(p2))

            st.write('Kirajzolás...')
            img = drawJumps(gedcom_parser, p2, jumps)

            st.image(img.render())

    if funkcio_selectbox == "Név lista keresése a családfában":
        st.title('Nevek ellenőrzése a családfában')
        st.write('Adj meg egy név-listát, amit a program összevet a családfán szereplő nevekkel, és az egyezéseket listázza')
        st.write('Soronként egy embert szerepeltess. Vezetéknév keresztnév sorrendben. Az első szóközig tételezi fel a vezetéknevet, utána jön a keresztnév. Lehet név-töredék is, de pont nélkül és kisbetű-nagybetű helyesen (pl. Habs Károly )')
        
        col0, col1, col2 = st.columns(3)
        lines = col0.text_area('Név lista', value='Görög Demeter\r\nGipsz Jakab\r\nHabsburg Károly', height=400).replace('\r', '\n').replace('\n\n', '\n').split('\n')
        print('Tömeges név-ellenőrzés ennyi névvel: ' + str(len(lines)))
        show_only_fresh = col0.checkbox('Csak 1900 után születetteket, vagy ismeretlen születési évűeket mutasson')
        col1.write('')
        col2.write('')

        if st.button('Keress'):
            gedcom_parser = get_database_session()

            root_child_elements = gedcom_parser.get_root_child_elements()

            st.write('Találatok:')

            for line in lines:
                parts = line.split(' ')
                if len(parts) < 2:
                    st.write(line + ' kihagyva, mert nincs keresztneve')
                    continue
                for element in root_child_elements:
                    if isinstance(element, IndividualElement):
                        if show_only_fresh and element.get_birth_year() != -1 and element.get_birth_year() < 1900:
                            continue
                        (first, last) = element.get_name()
                        if parts[0] in last and parts[1] in first:
                                st.write(toString(element))
                        if parts[1] in last and parts[0] in first:
                                st.write(toString(element))
            st.write('-kész-')
        

if check_password():
    main()