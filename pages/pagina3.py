import streamlit as st
boton = st.button("Volver a la página principal")

if boton:
    st.switch_page("inicio.py")
