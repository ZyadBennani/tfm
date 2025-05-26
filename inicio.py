import streamlit as st
import os

# Configuración de la página
st.set_page_config(
    page_title="ScoutVision",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Diccionario con nombres de ligas y sus equipos
ligas_y_equipos = {
    "La Liga": [
        "Real Madrid", "Barcelona", "Atletico Madrid", "Real Sociedad", 
        "Athletic Club", "Real Betis", "Valencia", "Villarreal",
        "Osasuna", "Sevilla", "Rayo Vallecano", "Celta de Vigo",
        "Mallorca", "Girona", "Almería", "Cádiz",
        "Granada", "Getafe", "Alavés", "Las Palmas"
    ],
    "Premier League": [
        "Manchester City", "Arsenal", "Manchester United", "Liverpool",
        "Newcastle", "Brighton", "Aston Villa", "Tottenham",
        "Brentford", "Chelsea", "Crystal Palace", "Wolves",
        "West Ham", "Bournemouth", "Nottingham Forest", "Fulham",
        "Everton", "Luton Town", "Burnley", "Sheffield United"
    ],
    "Serie A": [
        "Napoli", "Juventus", "Inter", "Milan", 
        "Lazio", "Roma", "Atalanta", "Fiorentina",
        "Bologna", "Torino", "Monza", "Udinese",
        "Sassuolo", "Empoli", "Salernitana", "Lecce",
        "Hellas Verona", "Spezia", "Cremonese", "Sampdoria"
    ],
    "Bundesliga": [
        "Bayern Munich", "Borussia Dortmund", "RB Leipzig", "Union Berlin",
        "Freiburg", "Bayer Leverkusen", "Eintracht Frankfurt", "Wolfsburg",
        "Mainz 05", "Borussia Mönchengladbach", "Köln", "Hoffenheim",
        "Werder Bremen", "Bochum", "Augsburg", "Stuttgart",
        "Schalke 04", "Hertha BSC", "Darmstadt", "Heidenheim"
    ],
    "Ligue 1": [
        "PSG", "Lens", "Marseille", "Monaco",
        "Lille", "Rennes", "Lyon", "Nice",
        "Reims", "Lorient", "Montpellier", "Toulouse",
        "Nantes", "Strasbourg", "Clermont", "Brest",
        "Auxerre", "Troyes", "Ajaccio", "Angers"
    ]
}

# Función para mostrar equipos de una liga
def mostrar_equipos(liga):
    st.markdown(f"<h2 style='text-align: center; color: #1e3c72;'>Equipos de {liga}</h2>", unsafe_allow_html=True)
    
    # Botón para volver a la selección de ligas
    if st.button("← Volver a selección de ligas"):
        st.session_state.liga_seleccionada = None
        st.session_state.equipo_seleccionado = None
        st.rerun()
    
    # Crear filas de 5 equipos cada una
    equipos = ligas_y_equipos[liga]
    for i in range(0, len(equipos), 5):
        cols = st.columns(5)
        for j, col in enumerate(cols):
            if i + j < len(equipos):
                equipo = equipos[i + j]
                with col:
                    st.markdown(f"""
                        <div class="equipo-card">
                            <div class="placeholder-image">Logo {equipo}</div>
                            <h3 style='margin-top: 10px; font-size: 1.2em;'>{equipo}</h3>
                        </div>
                    """, unsafe_allow_html=True)
                    if st.button(f"Ver {equipo}", key=f"btn_{equipo}"):
                        st.session_state.equipo_seleccionado = equipo
                        st.rerun()

# Estilos CSS personalizados
st.markdown("""
    <style>
    .liga-card {
        border: 1px solid #ddd;
        border-radius: 10px;
        padding: 20px;
        text-align: center;
        background-color: white;
        margin: 10px;
        cursor: pointer;
    }
    .liga-card:hover {
        transform: scale(1.02);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .liga-title {
        font-size: 1.5em;
        margin-top: 10px;
        font-weight: bold;
        color: #1e3c72;
    }
    .centered-header {
        text-align: center;
        padding: 20px;
        background: linear-gradient(45deg, #1e3c72, #2a5298);
        color: white;
        border-radius: 10px;
        margin-bottom: 30px;
    }
    .barca-section {
        text-align: center;
        margin: 20px 0;
        padding: 20px;
        cursor: pointer;
    }
    .barca-section img {
        max-width: 150px;
        transition: transform 0.3s ease;
    }
    .barca-section:hover img {
        transform: scale(1.05);
    }
    .analysis-card {
        border: 1px solid #ddd;
        border-radius: 10px;
        padding: 30px;
        text-align: center;
        background: white;
        margin: 10px;
        cursor: pointer;
        transition: transform 0.3s ease;
    }
    .analysis-card:hover {
        transform: scale(1.02);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .analysis-title {
        font-size: 1.3em;
        font-weight: bold;
        margin-bottom: 10px;
        color: #1e3c72;
    }
    .analysis-description {
        color: #666;
        font-size: 0.9em;
    }
    .equipo-card {
        border: 1px solid #ddd;
        border-radius: 5px;
        padding: 15px;
        text-align: center;
        margin: 5px;
        background-color: white;
    }
    .placeholder-image {
        width: 150px;
        height: 150px;
        background-color: #f0f0f0;
        border-radius: 10px;
        margin: 0 auto;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #666;
    }
    .stButton button {
        width: 100%;
        background-color: #1e3c72;
        color: white;
    }
    .stButton button:hover {
        background-color: #2a5298;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

# Inicializar variables de estado
if 'pagina_actual' not in st.session_state:
    st.session_state.pagina_actual = 'inicio'
if 'liga_seleccionada' not in st.session_state:
    st.session_state.liga_seleccionada = None
if 'equipo_seleccionado' not in st.session_state:
    st.session_state.equipo_seleccionado = None

# Título principal
st.markdown('<div class="centered-header"><h1>⚽ ScoutVision</h1><p>Análisis y Comparación de Equipos y Jugadores</p></div>', unsafe_allow_html=True)

# Sección del Barça
col1, col2, col3 = st.columns([1,2,1])
with col2:
    st.markdown("""
        <div class="barca-section">
            <div class="placeholder-image" style="width: 150px; height: 150px; margin: 0 auto;">
                Logo FC Barcelona
            </div>
            <h3 style="margin-top: 10px; color: #1e3c72;">FC Barcelona</h3>
        </div>
    """, unsafe_allow_html=True)
    if st.button("Análisis Detallado del FC Barcelona"):
        st.session_state.pagina_actual = 'barca'
        st.rerun()

# Página de análisis del Barça
if st.session_state.pagina_actual == 'barca':
    st.markdown("<h2 style='text-align: center; color: #1e3c72;'>Análisis FC Barcelona</h2>", unsafe_allow_html=True)
    
    # Botón para volver
    if st.button("← Volver al inicio"):
        st.session_state.pagina_actual = 'inicio'
        st.rerun()
    
    # Mostrar las diferentes opciones de análisis
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
            <div class="analysis-card">
                <div class="analysis-title">Comparación Flick's Barça vs Flick's Bayern</div>
                <div class="analysis-description">
                    Análisis comparativo detallado entre los sistemas tácticos y rendimiento de ambos equipos
                </div>
            </div>
        """, unsafe_allow_html=True)
        if st.button("Ver Comparación", key="btn_comparacion"):
            st.switch_page("pages/PAGINA2.py")
    
    with col2:
        st.markdown("""
            <div class="analysis-card">
                <div class="analysis-title">Análisis Propio</div>
                <div class="analysis-description">
                    Estudio detallado del sistema de juego y estadísticas del FC Barcelona
                </div>
            </div>
        """, unsafe_allow_html=True)
        if st.button("Ver Análisis", key="btn_analisis"):
            st.switch_page("pages/pagina3.py")

    col3, col4 = st.columns(2)
    
    with col3:
        st.markdown("""
            <div class="analysis-card">
                <div class="analysis-title">Evolución Táctica</div>
                <div class="analysis-description">
                    Análisis de la evolución del sistema de juego y adaptaciones tácticas
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
            <div class="analysis-card">
                <div class="analysis-title">Análisis por Posiciones</div>
                <div class="analysis-description">
                    Estudio detallado del rendimiento por posiciones y roles tácticos
                </div>
            </div>
        """, unsafe_allow_html=True)

# Si estamos en la página de inicio, mostrar el contenido normal
if st.session_state.pagina_actual == 'inicio':
    st.markdown("## 🌍 Selecciona una Liga", unsafe_allow_html=True)
    
    # Mostrar las ligas en una cuadrícula
    for i in range(0, len(ligas_y_equipos), 5):
        cols = st.columns(5)
        for j, col in enumerate(cols):
            if i + j < len(ligas_y_equipos):
                liga_nombre = list(ligas_y_equipos.keys())[i + j]
                with col:
                    st.markdown(f"""
                        <div class="liga-card">
                            <div class="placeholder-image">Logo {liga_nombre}</div>
                            <div class="liga-title">{liga_nombre}</div>
                        </div>
                    """, unsafe_allow_html=True)
                    if st.button(f"Ver {liga_nombre}", key=f"btn_{liga_nombre}"):
                        st.session_state.liga_seleccionada = liga_nombre
                        st.rerun()

    # Si hay una liga seleccionada, mostrar sus equipos
    if st.session_state.liga_seleccionada:
        mostrar_equipos(st.session_state.liga_seleccionada)

    # Si hay un equipo seleccionado, mostrar su información
    if st.session_state.equipo_seleccionado:
        st.markdown(f"<h2>Información de {st.session_state.equipo_seleccionado}</h2>", unsafe_allow_html=True)
