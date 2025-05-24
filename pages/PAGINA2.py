import streamlit as st
import pandas as pd
import funciones_data as fd
import funciones_graficas as fg

st.set_page_config(page_title="Análisis Detallado", page_icon="📊")

st.title("Análisis Detallado - FC Barcelona 2024/25")

# Cargar datos
pases = fd.cargar_datos()

# Añadir contenido específico para esta página
st.write("Bienvenido al análisis detallado de los pases")

# Selector de jugador
jugador_seleccionado = st.selectbox("Selecciona un jugador para análisis detallado", 
                                   ["EL 10", "EL 9", "EL 8", "EL 7", "EL 6", "EL 5", "EL 4", "EL 3", "EL 2", "EL 1"])

if jugador_seleccionado:
    fg.crear_grafico_radar(jugador_seleccionado, pases)
