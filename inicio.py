import streamlit as st
import os
from PIL import Image
import base64

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

# Función para cargar imágenes
def load_image(image_path):
    try:
        return Image.open(image_path)
    except:
        return None

# Función para obtener la ruta de la imagen del equipo
def get_team_logo_path(team_name):
    # Normalizar el nombre del equipo para el nombre del archivo
    filename = team_name.lower().replace(" ", "_") + ".png"
    return os.path.join("static", "logos", filename)

# Función para obtener la ruta del logo de la liga
def get_league_logo_path(league_name):
    # Normalizar el nombre de la liga para el nombre del archivo
    filename = league_name.lower().replace(" ", "_") + ".png"
    return os.path.join("static", "leagues", filename)

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
                    st.markdown('<div class="team-card">', unsafe_allow_html=True)
                    logo_path = get_team_logo_path(equipo)
                    if os.path.exists(logo_path):
                        st.markdown(f'<img src="data:image/png;base64,{get_image_base64(logo_path)}" class="team-logo" alt="{equipo}"/>', unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                            <div class="placeholder-image">Logo {equipo}</div>
                        """, unsafe_allow_html=True)
                    st.markdown(f'<div class="team-name">{equipo}</div>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                    if st.button(f"Ver {equipo}", key=f"btn_{equipo}"):
                        st.session_state.equipo_seleccionado = equipo
                        st.rerun()

# Función para convertir imagen a base64
def get_image_base64(image_path):
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode()
    except Exception as e:
        print(f"Error loading image {image_path}: {str(e)}")
        return ""

# Estilos CSS personalizados
st.markdown("""
    <style>
    /* Variables de color para tema consistente */
    :root {
        --background-dark: #1E1E1E;
        --text-light: #FFFFFF;
        --text-dark: #333333;
        --card-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        --transition-speed: 0.3s;
        --barca-primary: #004D98;
        --barca-secondary: #A50044;
    }

    /* Estilos generales y animaciones */
    * {
        transition: all var(--transition-speed) ease;
    }

    .main-content {
        margin-top: 80px;
        padding: 20px;
        animation: fadeIn 0.5s ease;
    }

    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }

    /* Tarjetas mejoradas */
    .liga-card {
        border: none;
        border-radius: 15px;
        padding: 25px;
        text-align: center;
        background: white;
        margin: 15px;
        cursor: pointer;
        transition: all var(--transition-speed) ease;
        box-shadow: var(--card-shadow);
    }

    .liga-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 12px rgba(0, 0, 0, 0.15);
    }

    .team-card {
        border: none;
        border-radius: 15px;
        padding: 20px;
        text-align: center;
        background: white;
        margin: 15px;
        transition: all var(--transition-speed) ease;
        box-shadow: var(--card-shadow);
    }

    .team-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 12px rgba(0, 0, 0, 0.15);
    }

    .team-logo {
        width: 120px;
        height: auto;
        margin-bottom: 10px;
    }

    .team-name {
        font-size: 1.2em;
        font-weight: bold;
        color: var(--text-dark);
        margin-top: 10px;
    }

    .centered-header {
        text-align: center;
        padding: 30px;
        background: linear-gradient(135deg, var(--barca-primary), var(--barca-secondary));
        color: var(--text-light);
        border-radius: 15px;
        margin-bottom: 30px;
        box-shadow: var(--card-shadow);
    }

    .centered-header h1 {
        font-size: 2.5em;
        margin-bottom: 10px;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.2);
    }

    .centered-header p {
        font-size: 1.2em;
        opacity: 0.9;
    }

    /* Botones mejorados */
    .stButton button {
        background: linear-gradient(135deg, var(--barca-primary), var(--barca-secondary));
        color: white;
        border: none;
        border-radius: 25px;
        padding: 10px 20px;
        font-weight: 500;
        transition: all var(--transition-speed) ease;
    }

    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    }

    /* Navbar mejorada */
    .navbar {
        background: linear-gradient(90deg, #1e3c72, #2a5298);
        backdrop-filter: blur(10px);
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    }

    .nav-link {
        position: relative;
        overflow: hidden;
    }

    .nav-link::after {
        content: '';
        position: absolute;
        bottom: 0;
        left: 0;
        width: 100%;
        height: 2px;
        background-color: white;
        transform: translateX(-100%);
        transition: transform var(--transition-speed) ease;
    }

    .nav-link:hover::after {
        transform: translateX(0);
    }
    </style>
""", unsafe_allow_html=True)

# Barra de navegación
st.markdown("""
    <div class="navbar">
        <a href="#" class="navbar-logo">⚽ ScoutVision</a>
        <div class="navbar-links">
            <a href="#" class="nav-link active">Inicio</a>
            <a href="#" class="nav-link">Análisis</a>
            <a href="#" class="nav-link">Comparación</a>
        </div>
    </div>
""", unsafe_allow_html=True)

# Contenedor principal
st.markdown('<div class="main-content">', unsafe_allow_html=True)

# Inicializar variables de estado
if 'pagina_actual' not in st.session_state:
    st.session_state.pagina_actual = 'inicio'
if 'liga_seleccionada' not in st.session_state:
    st.session_state.liga_seleccionada = None
if 'equipo_seleccionado' not in st.session_state:
    st.session_state.equipo_seleccionado = None

# Título principal
st.markdown('<div class="centered-header"><h1>⚽ ScoutVision</h1><p>Análisis y Comparación de Equipos y Jugadores</p></div>', unsafe_allow_html=True)

# Sección del Barça (centrada)
st.markdown("""
    <div style="
        display: flex;
        justify-content: center;
        align-items: center;
        margin: 0 auto;
        margin-bottom: 40px;
        max-width: 400px;
    ">
        <div class="team-card" style="
            width: 100%;
            margin: 0;
            background: white;
            border-radius: 15px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            padding: 30px;
            text-align: center;
        ">
""", unsafe_allow_html=True)

barca_logo = get_team_logo_path("Barcelona")
if os.path.exists(barca_logo):
    st.markdown(f"""
        <img 
            src="data:image/png;base64,{get_image_base64(barca_logo)}" 
            alt="FC Barcelona"
            style="
                width: 180px;
                height: auto;
                margin: 0 auto;
                display: block;
            "
        />
    """, unsafe_allow_html=True)
else:
    st.markdown("""
        <div class="placeholder-image">Logo FC Barcelona</div>
    """, unsafe_allow_html=True)

st.markdown("""
            <div style="
                font-size: 1.4em;
                font-weight: bold;
                color: #333;
                margin: 15px 0;
                text-align: center;
            ">FC Barcelona</div>
        </div>
    </div>
""", unsafe_allow_html=True)

# Botón centrado
col1, col2, col3, col4 = st.columns([1,2,2,1])
with col2:
    if st.button("Analisis Propio", key="barca_analysis", use_container_width=True):
        st.switch_page("pages/Analisis Propio.py")
with col3:
    if st.button("Barça VS Bayern", key="barca_bayern", use_container_width=True):
        st.switch_page("pages/Barça VS Bayern.py")

# Separador visual
st.markdown("<hr style='margin: 30px 0; opacity: 0.2;'>", unsafe_allow_html=True)

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
                    st.markdown('<div class="liga-card">', unsafe_allow_html=True)
                    logo_path = get_league_logo_path(liga_nombre)
                    if os.path.exists(logo_path):
                        st.markdown(f'<img src="data:image/png;base64,{get_image_base64(logo_path)}" class="team-logo" alt="{liga_nombre}"/>', unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                            <div class="placeholder-image">Logo {liga_nombre}</div>
                        """, unsafe_allow_html=True)
                    st.markdown(f'<div class="liga-title">{liga_nombre}</div>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                    if st.button(f"Ver {liga_nombre}", key=f"btn_{liga_nombre}"):
                        st.session_state.liga_seleccionada = liga_nombre
                        st.rerun()

    # Si hay una liga seleccionada, mostrar sus equipos
    if st.session_state.liga_seleccionada:
        mostrar_equipos(st.session_state.liga_seleccionada)

    # Si hay un equipo seleccionado, mostrar su información
    if st.session_state.equipo_seleccionado:
        st.markdown(f"<h2>Información de {st.session_state.equipo_seleccionado}</h2>", unsafe_allow_html=True)

# Cerrar el contenedor principal
st.markdown('</div>', unsafe_allow_html=True)
