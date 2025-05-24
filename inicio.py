import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import funciones_data as fd
import funciones_graficas as fg

pases = fd.cargar_datos()
st.set_page_config(page_title="Análisis de Fútbol", page_icon="⚽", layout="wide")

st.title("Análisis de Pases - FC Barcelona 2024/25")

fg.crear_grafico_radar("Pedri", pases)

st.write(pases.head(20))

x = st.button("Mostrar mensaje")
if x:
    st.write("¡Bienvenido al análisis!")

st.metric(label="Estadísticas", value="Pases", delta="+10%")


st.data_input("Nombre del jugador", key="nombre_jugador")
