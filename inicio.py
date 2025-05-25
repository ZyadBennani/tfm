import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import funciones_data as fd
import funciones_graficas as fg

@st.cache_data
def leer_data():
    pases = fd.cargar_datos()
    return pases

pases = leer_data()
st.set_page_config(
    page_title="Análisis Comparativo: Flick's Barcelona vs Bayern",
    page_icon="⚽",
    layout="wide"
)

# Estilos CSS personalizados
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 20px;
        margin-bottom: 30px;
    }
    .team-section {
        background: linear-gradient(45deg, rgba(0,0,0,0.1), rgba(0,0,0,0.2));
        border-radius: 10px;
        padding: 20px;
        margin: 10px;
    }
    .barca-gradient {
        background: linear-gradient(45deg, #004D98, #A50044);
        padding: 2px;
        border-radius: 10px;
        color: white;
    }
    .bayern-gradient {
        background: linear-gradient(45deg, #DC052D, #8B0000);
        padding: 2px;
        border-radius: 10px;
        color: white;
    }
    .feature-card {
        background: rgba(255,255,255,0.1);
        padding: 20px;
        border-radius: 10px;
        margin: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Encabezado principal
st.markdown("""
<div class="main-header">
    <h1>🏆 Análisis Comparativo del Fútbol de Elite 🏆</h1>
    <h2>Flick's Barcelona vs Flick's Bayern</h2>
</div>
""", unsafe_allow_html=True)

# Introducción
st.markdown("""
Este análisis profundo examina las similitudes y diferencias entre dos equipos históricos bajo la dirección 
de Hansi Flick: el FC Barcelona actual y el Bayern Munich de su época dorada.
""")

# Secciones principales
col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div class="barca-gradient">
        <h2 style="text-align: center; padding: 10px;">FC Barcelona</h2>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="team-section">
        <h3>Características Principales</h3>
        <ul>
            <li>Posesión dominante</li>
            <li>Presión alta</li>
            <li>Juego posicional</li>
            <li>Talento joven</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="bayern-gradient">
        <h2 style="text-align: center; padding: 10px;">Bayern Munich</h2>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="team-section">
        <h3>Características Principales</h3>
        <ul>
            <li>Intensidad física</li>
            <li>Transiciones rápidas</li>
            <li>Presión agresiva</li>
            <li>Eficiencia goleadora</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# Sección de análisis disponibles
st.markdown("### 📊 Análisis Disponibles")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="feature-card">
        <h4>🎮 Tácticas y Formaciones</h4>
        <p>Análisis detallado de las formaciones y tácticas empleadas por ambos equipos.</p>
        <ul>
            <li>Mapas de calor</li>
            <li>Redes de pases</li>
            <li>Posiciones medias</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="feature-card">
        <h4>👥 Comparación de Jugadores</h4>
        <p>Análisis comparativo jugador por jugador entre ambos equipos.</p>
        <ul>
            <li>Estadísticas individuales</li>
            <li>Gráficos radar</li>
            <li>Métricas avanzadas</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="feature-card">
        <h4>📈 Estadísticas del Equipo</h4>
        <p>Métricas y estadísticas comparativas a nivel de equipo.</p>
        <ul>
            <li>Posesión</li>
            <li>Efectividad</li>
            <li>Presión</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# Botón para ir a la comparación detallada
st.markdown("<br>", unsafe_allow_html=True)
col1, col2, col3 = st.columns([1,2,1])
with col2:
    if st.button("🔍 Ver Análisis Detallado", use_container_width=True):
        st.switch_page("pages/PAGINA2.py")

# Pie de página
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: grey;'>
    Desarrollado con ❤️ por Zyad Bayasi | Datos actualizados: 2024
</div>
""", unsafe_allow_html=True)
