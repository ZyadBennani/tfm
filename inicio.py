import streamlit as st
import os
from PIL import Image
import base64
import pandas as pd
import plotly.express as px
import numpy as np

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
        margin-top: 10px;
        padding: 15px;
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

# Contenedor principal
st.markdown('<div class="main-content">', unsafe_allow_html=True)

# Inicializar variables de estado
if 'pagina_actual' not in st.session_state:
    st.session_state.pagina_actual = 'inicio'
if 'liga_seleccionada' not in st.session_state:
    st.session_state.liga_seleccionada = None
if 'equipo_seleccionado' not in st.session_state:
    st.session_state.equipo_seleccionado = None

# Sección principal con título FCBLAB
st.markdown("""
    <div style="
        display: flex;
        justify-content: center;
        align-items: center;
        margin: 0 auto;
        margin-bottom: 15px;
        max-width: 600px;
    ">
        <div style="
            width: 100%;
            margin: 0;
            background: linear-gradient(135deg, #004D98, #A50044);
            border-radius: 20px;
            box-shadow: 0 8px 25px rgba(0, 77, 152, 0.3);
            padding: 20px;
            text-align: center;
            position: relative;
            overflow: hidden;
        ">
            <div style="
                position: absolute;
                top: -50%;
                left: -50%;
                width: 200%;
                height: 200%;
                background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
                animation: pulse 4s ease-in-out infinite;
            "></div>
                         <h1 style="
                 font-size: 1.8em;
                 font-weight: 900;
                 color: white;
                 margin: 0;
                 letter-spacing: 2px;
                 text-shadow: 2px 4px 8px rgba(0,0,0,0.3);
                 font-family: 'Arial Black', Arial, sans-serif;
                 position: relative;
                 z-index: 2;
             ">FCBLAB</h1>
             <p style="
                 font-size: 0.9em;
                 color: rgba(255,255,255,0.9);
                 margin: 10px 0 15px 0;
                 font-weight: 300;
                 letter-spacing: 1px;
                 position: relative;
                 z-index: 2;
                          ">Laboratorio de Análisis del FC Barcelona</p>
         </div>
     </div>
""", unsafe_allow_html=True)

# Logo del Barça centrado debajo del título
st.markdown("""
    <div style="
        display: flex;
        justify-content: center;
        align-items: center;
        margin: -10px auto 20px auto;
        max-width: 400px;
    ">
        <div style="
            background: white;
            border-radius: 50%;
            padding: 18px;
            box-shadow: 0 8px 25px rgba(0, 77, 152, 0.2);
            border: 3px solid rgba(255,255,255,0.9);
        ">
""", unsafe_allow_html=True)

barca_logo = get_team_logo_path("Barcelona")
if os.path.exists(barca_logo):
    st.markdown(f"""
        <img 
            src="data:image/png;base64,{get_image_base64(barca_logo)}" 
            alt="FC Barcelona"
            style="
                width: 120px;
                height: auto;
                display: block;
                margin: 0 auto;
            "
        />
    """, unsafe_allow_html=True)
else:
    st.markdown("""
        <div style="
            width: 120px;
            height: 120px;
            background: #f0f0f0;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #666;
            font-weight: bold;
        ">Logo FC Barcelona</div>
    """, unsafe_allow_html=True)

st.markdown("""
        </div>
     </div>
    
    <style>
    @keyframes pulse {
        0% { transform: rotate(0deg) scale(1); opacity: 0.3; }
        50% { transform: rotate(180deg) scale(1.1); opacity: 0.1; }
        100% { transform: rotate(360deg) scale(1); opacity: 0.3; }
    }
    </style>
""", unsafe_allow_html=True)

# Botones principales con espaciado reducido
st.markdown('<div style="margin-top: 10px; margin-bottom: 10px;">', unsafe_allow_html=True)
col1, col2, col3, col4 = st.columns([1,2,2,1])
with col2:
    if st.button("Analisis Propio", key="barca_analysis", use_container_width=True):
        st.switch_page("pages/Analisis Propio.py")
with col3:
    if st.button("Barça VS Bayern", key="barca_bayern", use_container_width=True):
        st.switch_page("pages/Barça VS Bayern.py")
st.markdown('</div>', unsafe_allow_html=True)

# Separador visual
st.markdown("<hr style='margin: 20px 0; opacity: 0.2;'>", unsafe_allow_html=True)

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

def get_laliga_teams_data():
    equipos = [
        ("FC Barcelona", "FCB"), ("Real Madrid", "RMA"), ("Atletico Madrid", "ATM"), ("Sevilla", "SEV"),
        ("Real Sociedad", "RSO"), ("Athletic Club", "ATH"), ("Real Betis", "BET"), ("Valencia", "VAL"),
        ("Villarreal", "VIL"), ("Osasuna", "OSA"), ("Rayo Vallecano", "RAY"), ("Celta de Vigo", "CEL"),
        ("Mallorca", "MLL"), ("Girona", "GIR"), ("Almería", "ALM"), ("Cádiz", "CAD"),
        ("Granada", "GRA"), ("Getafe", "GET"), ("Alavés", "ALA"), ("Las Palmas", "LPA")
    ]
    # Datos fijos (puedes ajustar los valores para que sean realistas)
    np.random.seed(42)
    data = {
        "Equipo": [e[0] for e in equipos],
        "Acr": [e[1] for e in equipos],
        "PPDA": np.random.uniform(7, 18, 20),
        "Counterattacks_with_shots_per90": np.random.uniform(0.5, 2.5, 20),
        "CounterPress_success": np.random.uniform(0.2, 0.7, 20),
        "Shots_against_on_target_per90": np.random.uniform(2, 6, 20),
        "Deep_completed_pass_per90": np.random.uniform(5, 18, 20),
        "PSxGA_per90": np.random.uniform(0.7, 2.2, 20),
        "Progressive_pass_accurate_per90": np.random.uniform(7, 18, 20),
        "xG_per90": np.random.uniform(0.7, 2.5, 20),
    }
    return pd.DataFrame(data)

def show_league_dashboard():
    df = get_laliga_teams_data()
    st.markdown("<h2 style='text-align:center;'>Liga – Radar de fases de juego</h2>", unsafe_allow_html=True)
    # Definir configuraciones de los 4 gráficos
    plots = [
        {
            "title": "Transición ofensiva",
            "x": "PPDA",
            "y": "Counterattacks_with_shots_per90",
            "xlabel": "PPDA (menos es mejor)",
            "ylabel": "Counterattacks with shots per 90",
            "invert_x": True,
            "legend": "Press & Punish"
        },
        {
            "title": "Transición defensiva",
            "x": "CounterPress_success",
            "y": "Shots_against_on_target_per90",
            "xlabel": "CounterPress Success Rate",
            "ylabel": "Shots against on target per 90",
            "invert_x": False,
            "legend": "Recover & Resist"
        },
        {
            "title": "Fase defensiva posicional",
            "x": "Deep_completed_pass_per90",
            "y": "PSxGA_per90",
            "xlabel": "Deep completed passes per 90 (menos es mejor)",
            "ylabel": "PSxGA per 90",
            "invert_x": True,
            "legend": "Block & Save"
        },
        {
            "title": "Fase ofensiva posicional",
            "x": "Progressive_pass_accurate_per90",
            "y": "xG_per90",
            "xlabel": "Progressive pass accurate per 90",
            "ylabel": "xG per 90",
            "invert_x": False,
            "legend": "Create & Threaten"
        }
    ]
    # Crear grid 2x2
    cols = st.columns(2)
    for i, plot in enumerate(plots):
        col = cols[i % 2]
        with col:
            x = plot["x"]
            y = plot["y"]
            fig = px.scatter(
                df, x=x, y=y, text="Acr",
                title=plot["title"],
                color_discrete_sequence=["#636EFA"],
                height=400
            )
            # Líneas de la mediana
            x_median = df[x].median()
            y_median = df[y].median()
            fig.add_vline(x=x_median, line_dash="dash", line_color="gray")
            fig.add_hline(y=y_median, line_dash="dash", line_color="gray")
            # Etiquetas de puntos
            fig.update_traces(textposition="top center", marker=dict(size=14, line=dict(width=1, color='DarkSlateGrey')))
            # Leyenda de cuadrantes
            fig.add_annotation(
                xref="paper", yref="paper", x=0.01, y=0.99, showarrow=False,
                text=f"<b>{plot['legend']}</b>", font=dict(size=13, color="#444"), align="left", bgcolor="#f7f7f7"
            )
            # Ejes
            fig.update_xaxes(title=plot["xlabel"], autorange="reversed" if plot["invert_x"] else True)
            fig.update_yaxes(title=plot["ylabel"])
            st.plotly_chart(fig, use_container_width=True)

# Para pruebas: descomenta la siguiente línea para ver los gráficos directamente
# show_league_dashboard()
