from gedcom.parser import Parser
import streamlit as st
import pickle

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


def main():
    st.title('Legrövidebb út két ember között a Hollai/Görög családfában')
    st.write('Add meg a két személy nevét, majd kattints a gombra. Név-töredék is megadható, viszont kisbetű-nagybetű érzékeny. Az évszám nem kötelező, de segíthet szűkíteni. 1800')

    col1, col2, col3, col4 = st.columns(4)
    p1_1 = col1.text_input('1. személy vezetéknév:', value="Görög")
    p1_2 = col2.text_input('1. személy keresztnév:', value="Márton Jenő")
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
        try:
            gedcom_parser
        except NameError:
            st.write('Családfa betöltése (~30 másodperc)...')
            with open('gedcom_parser.bin', 'rb') as handle:
                gedcom_parser = pickle.load(handle)

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

        st.write('Kirajzolás...')
        img = drawJumps(gedcom_parser, p2, jumps)

        st.image(img.render())
    

if check_password():
    main()