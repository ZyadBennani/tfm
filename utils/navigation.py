import streamlit as st

def show_home_button():
    st.button("Inicio")

def show_page_header(title, subtitle=None, icon=None):
    st.markdown(f"# {title}")
    if subtitle:
        st.markdown(f"## {subtitle}")

def show_navbar_switch_page():
    st.sidebar.title("Navegación")
    st.sidebar.button("Ir a otra página") 