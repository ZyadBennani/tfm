import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
from datetime import datetime
import io
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.colors import LinearSegmentedColormap

# Configuración de la página
st.set_page_config(
    page_title="Player Scouting",
    page_icon="🔍",
    layout="wide"
)

# Estilos CSS personalizados
st.markdown("""
    <style>
        /* Estilos generales */
        .main {
            background-color: #f8f9fa;
            color: #1a1a1a;
            padding: 0.5rem;
        }
        
        /* Reducir padding del contenedor principal */
        .block-container {
            padding-top: 1rem !important;
            padding-bottom: 1rem !important;
        }
        
        /* Sidebar mejorada */
        .stSidebar {
            background-color: white;
            padding: 1rem 1rem;
        }
        
        /* Títulos y texto - reducir espacios */
        h1, h2, h3 {
            color: #1a1a1a;
            font-weight: 600;
            margin-bottom: 0.5rem !important;
            margin-top: 0.5rem !important;
        }
        
        /* Reducir espacio del título principal */
        h1 {
            margin-top: 0 !important;
            margin-bottom: 0.3rem !important;
            padding-top: 0 !important;
        }
        
        /* Tabs mejorados - menos padding */
        .stTabs [data-baseweb="tab-list"] {
            gap: 24px;
            padding: 0.5rem;
            border-radius: 1rem;
            background-color: white;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 0.5rem;
        }
        
        .stTabs [data-baseweb="tab"] {
            height: 40px;
            padding: 8px 20px;
            border-radius: 0.5rem;
            background-color: transparent;
            color: #1a1a1a;
            font-weight: 500;
            font-size: 1rem;
            transition: all 0.3s ease;
        }
        
        .stTabs [data-baseweb="tab"]:hover {
            background-color: #f0f0f0;
        }
        
        .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {
            background-color: #004D98;
            color: white;
            transform: scale(1.05);
        }
        
        /* Tarjetas de jugadores mejoradas */
        .player-card {
            background-color: white;
            padding: 1rem;
            border-radius: 1rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            margin: 0.5rem 0;
            border: 1px solid #E5E7EB;
            transition: all 0.3s ease;
        }
        
        .player-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 12px rgba(0, 0, 0, 0.15);
        }
        
        .player-card h3 {
            font-size: 1.3rem;
            margin-bottom: 0.3rem;
            color: #004D98;
        }
        
        .player-card p {
            font-size: 1rem;
            color: #4a5568;
            margin-bottom: 0.5rem;
        }
        
        /* Badges y métricas */
        .metric-badge {
            background-color: #A50044;
            color: white;
            padding: 0.4rem 0.8rem;
            border-radius: 9999px;
            font-size: 0.9rem;
            font-weight: 600;
            display: inline-block;
            margin-top: 0.3rem;
        }
        
        /* Navegación y breadcrumbs - reducir espacio */
        .breadcrumb {
            padding: 0.5rem 0;
            color: #4a5568;
            font-size: 1rem;
            margin-bottom: 0.5rem;
        }
        
        .shortlist-counter {
            background-color: #A50044;
            color: white;
            padding: 0.4rem 0.8rem;
            border-radius: 9999px;
            font-size: 1rem;
            font-weight: 600;
        }
        
        /* Filtros y controles - espacios reducidos */
        .filter-title {
            margin: 0.5rem 0 0.3rem 0;
            font-weight: 600;
            color: #1a1a1a;
            font-size: 1.1rem;
        }
        
        /* Botones mejorados - más compactos */
        .stButton button {
            width: 100%;
            padding: 0.6rem 1.2rem;
            font-size: 1rem;
            font-weight: 600;
            border-radius: 0.5rem;
            transition: all 0.3s ease;
        }
        
        .stButton button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        
        /* Tabla mejorada */
        .stDataFrame {
            font-size: 0.9rem;
        }
        
        .stDataFrame td, .stDataFrame th {
            padding: 0.6rem !important;
        }
        
        /* Selectores y inputs - espacios reducidos */
        .stSelectbox, .stMultiSelect {
            margin-bottom: 0.5rem;
        }
        
        /* Sliders mejorados - menos padding */
        .stSlider {
            padding: 0.5rem 0;
        }
        
        /* Expander mejorado - más compacto */
        .streamlit-expanderHeader {
            font-size: 1rem;
            font-weight: 600;
            color: #1a1a1a;
            background-color: #f8f9fa;
            border-radius: 0.5rem;
            padding: 0.6rem 1rem;
        }
        
        /* Estilos para filtros rápidos - más compactos */
        .quick-filter-btn {
            background: linear-gradient(135deg, #004D98 0%, #A50044 100%);
            color: white;
            border: none;
            padding: 0.6rem 0.8rem;
            border-radius: 0.5rem;
            font-weight: 600;
            transition: all 0.3s ease;
            width: 100%;
            margin-bottom: 0.3rem;
        }
        
        .quick-filter-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,77,152,0.3);
        }
        
        /* Chips de filtros activos */
        .filter-chip {
            background-color: #004D98;
            color: white;
            padding: 0.2rem 0.6rem;
            border-radius: 15px;
            margin: 0.1rem;
            display: inline-block;
            font-size: 0.8rem;
            font-weight: 500;
        }
        
        /* Contador de resultados - más compacto */
        .results-counter {
            background-color: #f8f9fa;
            padding: 0.5rem 0.8rem;
            border-radius: 0.5rem;
            border-left: 4px solid #004D98;
            margin: 0.5rem 0;
        }
        
        /* Reducir espacios entre secciones */
        .stMarkdown {
            margin-bottom: 0.5rem;
        }
        
        /* Expanders más compactos */
        .streamlit-expanderContent {
            padding: 0.5rem 0;
        }
        
        /* Reducir espacio en columnas */
        .element-container {
            margin-bottom: 0.5rem;
        }
    </style>
""", unsafe_allow_html=True)

# Título principal y descripción
st.markdown("""
    <div style='background-color: white; padding: 1rem; border-radius: 0.5rem; margin-bottom: 1rem; box-shadow: 0 2px 4px rgba(0,0,0,0.1);'>
        <h1 style='margin: 0; color: #1a1a1a; font-size: 2rem; font-weight: 600; display: flex; align-items: center; gap: 0.5rem;'>
            <span style='font-size: 2.2rem;'>⚽</span>
            <span>Player Scouting</span>
        </h1>
    </div>
""", unsafe_allow_html=True)

# Filtros rápidos
st.markdown('<h3 style="margin-top: 0.5rem !important; margin-bottom: 0.3rem !important;">⚡ Filtros Rápidos</h3>', unsafe_allow_html=True)
col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("🌟 Jóvenes Promesas", use_container_width=True):
        # RESETEAR TODOS LOS FILTROS A NEUTROS (RANGOS COMPLETOS)
        st.session_state.position_select = "All"
        st.session_state.profile_select = "All Profiles"
        st.session_state.foot = "Both"
        st.session_state.nationality = "Todos los países"
        st.session_state.contract_year = "Todos"
        st.session_state.market_value = (0, 200)  # RANGO COMPLETO
        st.session_state.max_salary_k = 100000    # SALARIO MÁXIMO
        st.session_state.height_range = (140, 210)  # RANGO COMPLETO
        st.session_state.has_clause = "Ambos"
        st.session_state.metrics_90 = []
        st.session_state.contract_years = None
        
        # APLICAR FILTROS ESPECÍFICOS DE JÓVENES PROMESAS
        st.session_state.age_range = (16, 22)  # Edad específica
        st.session_state.rating_min = 70       # Rating específico

with col2:
    if st.button("🆓 Mercado Libre", use_container_width=True):
        # RESETEAR TODOS LOS FILTROS A NEUTROS (RANGOS COMPLETOS)
        st.session_state.position_select = "All"
        st.session_state.profile_select = "All Profiles"
        st.session_state.age_range = (15, 40)     # RANGO COMPLETO
        st.session_state.rating_min = 40          # RATING MÍNIMO
        st.session_state.foot = "Both"
        st.session_state.nationality = "Todos los países"
        st.session_state.market_value = (0, 200)  # RANGO COMPLETO
        st.session_state.max_salary_k = 100000    # SALARIO MÁXIMO
        st.session_state.height_range = (140, 210)  # RANGO COMPLETO
        st.session_state.has_clause = "Ambos"
        st.session_state.metrics_90 = []
        st.session_state.contract_year = "Todos"
        
        # APLICAR FILTRO ESPECÍFICO DE MERCADO LIBRE
        st.session_state.contract_years = [2025]  # Solo contratos 2025

with col3:
    if st.button("⭐ Elite", use_container_width=True):
        # RESETEAR TODOS LOS FILTROS A NEUTROS (RANGOS COMPLETOS)
        st.session_state.position_select = "All"
        st.session_state.profile_select = "All Profiles"
        st.session_state.foot = "Both"
        st.session_state.nationality = "Todos los países"
        st.session_state.contract_year = "Todos"
        st.session_state.market_value = (0, 200)  # RANGO COMPLETO
        st.session_state.max_salary_k = 100000    # SALARIO MÁXIMO
        st.session_state.height_range = (140, 210)  # RANGO COMPLETO
        st.session_state.has_clause = "Ambos"
        st.session_state.metrics_90 = []
        st.session_state.contract_years = None
        
        # APLICAR FILTROS ESPECÍFICOS DE ELITE
        st.session_state.age_range = (22, 30)  # Edad específica
        st.session_state.rating_min = 83       # Rating específico

with col4:
    # Espacio vacío para mantener el diseño
    st.write("")

# Reducir espacio del divisor
st.markdown('<hr style="margin: 0.5rem 0;">', unsafe_allow_html=True)

# Breadcrumb y contador de shortlist con mejor diseño
col1, col2 = st.columns([6,1])
# Inicializar shortlist si no existe
if 'shortlist' not in st.session_state:
    st.session_state.shortlist = []

shortlist_count = len(st.session_state.shortlist)
with col2:
    st.markdown(f"""
        <div style='text-align: right; background-color: white; padding: 0.5rem; border-radius: 0.5rem; margin-bottom: 0.5rem;'>
            <span style='font-size: 1.2rem;'>📋</span> 
            <span class="shortlist-counter">{shortlist_count}</span>
        </div>
    """, unsafe_allow_html=True)

# Diccionario de perfiles por posición
position_profiles = {
    "GK": ["Sweeper", "Line Keeper", "Traditional"],
    "CB": ["Ball Playing", "Stopper", "Sweeper"],
    "RB": ["Defensive", "Progressive", "Offensive"],
    "LB": ["Defensive", "Progressive", "Offensive"],
    "CM-CDM": ["Deep Lying", "Box-to-Box", "Holding"],
    "CAM": ["Advanced Playmaker", "Shadow Striker", "Dribbling Creator"],
    "RW": ["Wide Playmaker", "Direct Winger", "Hybrid"],
    "LW": ["Wide Playmaker", "Direct Winger", "Hybrid"],
    "ST": ["Target Man", "Poacher", "Playmaker"],
    "All": ["All Profiles"]  # Opción por defecto
}

# Sidebar con filtros
with st.sidebar:

    
    # Valores por defecto
    default_filters = {
        "position_select": "All",
        "profile_select": "All Profiles",
        "age_range": (15, 40),  # RANGO COMPLETO
        "rating_min": 40,  # Rating mínimo
        "contract_years": None,  # Años de contrato específicos
        "contract_year": "Todos",  # Año de contrato del sidebar
        "foot": "Both",
        "nationality": "Todos los países",
        "market_value": (0, 200),  # RANGO COMPLETO
        "max_salary_k": 100000,  # SALARIO MÁXIMO
        "metrics_90": [],
        "percentile": False,
        "height_range": (140, 210),  # RANGO COMPLETO
        "has_clause": "Ambos",
    }

    # --- SOLUCIÓN RESET ---
    if st.session_state.get("reset_filters", False):
        for k, v in default_filters.items():
            st.session_state[k] = v
        st.session_state["reset_filters"] = False
        # Resetear también el filtro específico de mercado libre
        if 'contract_years' in st.session_state:
            st.session_state.contract_years = None

    # Inicializar filtros si no existen
    for k, v in default_filters.items():
        if k not in st.session_state:
            st.session_state[k] = v
    
    # 📍 SECCIÓN 1: CARACTERÍSTICAS BÁSICAS
    with st.expander("📍 **Características Básicas**", expanded=True):
        st.markdown("##### Posición y Rol")
    # Posición
        position_options = ["All", "GK", "CB", "RB", "LB", "CM-CDM", "CAM", "RW", "LW", "ST"]
        position_index = position_options.index(st.session_state.position_select) if st.session_state.position_select in position_options else 0
    position = st.selectbox(
            "Puesto",
            options=position_options,
            index=position_index,
            key="position_select"
    )
    
    # Perfil/Rol
    available_profiles = position_profiles.get(position, ["All Profiles"])
    profile_index = available_profiles.index(st.session_state.profile_select) if st.session_state.profile_select in available_profiles else 0
    roles = st.selectbox(
        "Perfil de Juego",
        options=available_profiles,
        index=profile_index,
        key="profile_select"
    )
    
    st.markdown("---")
    st.markdown("##### Edad y Físico")
    # Edad
    age_range = st.slider("Edad", 15, 40, st.session_state.age_range, key="age_range")
    
    # Rating mínimo
    default_rating = st.session_state.get('rating_min', 40)
    if not isinstance(default_rating, int):
        default_rating = int(default_rating)
    rating_min = st.slider("Rating Mínimo", min_value=40, max_value=99, value=default_rating, key="rating_min")
    
    # Altura
    height_range = st.slider("Altura (cm)", 140, 210, st.session_state.height_range, key="height_range")
    
    # Pie dominante
    foot_options = ["Both", "Left", "Right"]
    foot_index = foot_options.index(st.session_state.foot) if st.session_state.foot in foot_options else 0
    foot = st.radio("Pie Dominante", foot_options, index=foot_index, key="foot")
    
    # País
    nationality_options = [
        "Todos los países",
        "Albania – ALB",
        "Algeria – ALG",
        "Angola – ANG",
        "Argentina – ARG",
        "Armenia – ARM",
        "Australia – AUS",
        "Austria – AUT",
        "Belgium – BEL",
        "Benin – BEN",
        "Bosnia and Herzegovina – BIH",
        "Brazil – BRA",
        "Bulgaria – BUL",
        "Burkina Faso – BFA",
        "Cameroon – CMR",
        "Canada – CAN",
        "Cape Verde – CPV",
        "Chile – CHI",
        "China – CHN",
        "Colombia – COL",
        "Comoros – COM",
        "Congo – COG",
        "DR Congo – COD",
        "Côte d'Ivoire – CIV",
        "Croatia – CRO",
        "Curaçao – CUW",
        "Cyprus – CYP",
        "Czech Republic – CZE",
        "Denmark – DEN",
        "Dominican Republic – DOM",
        "Ecuador – ECU",
        "Egypt – EGY",
        "England – ENG",
        "Equatorial Guinea – GNQ",
        "Finland – FIN",
        "France – FRA",
        "Gabon – GAB",
        "Gambia – GAM",
        "Georgia – GEO",
        "Germany – GER",
        "Ghana – GHA",
        "Greece – GRE",
        "Guinea – GIN",
        "Guinea-Bissau – GNB",
        "Haiti – HAI",
        "Hungary – HUN",
        "Iceland – ISL",
        "Iran – IRN",
        "Ireland – IRL",
        "Israel – ISR",
        "Italy – ITA",
        "Jamaica – JAM",
        "Japan – JPN",
        "Kosovo – KOS",
        "Lithuania – LTU",
        "Luxembourg – LUX",
        "Mali – MLI",
        "Mexico – MEX",
        "Montenegro – MNE",
        "Morocco – MAR",
        "Netherlands – NED",
        "New Zealand – NZL",
        "Nigeria – NGA",
        "North Macedonia – MKD",
        "Northern Ireland – NIR",
        "Norway – NOR",
        "Paraguay – PAR",
        "Peru – PER",
        "Poland – POL",
        "Portugal – POR",
        "Romania – ROU",
        "Russia – RUS",
        "Saudi Arabia – KSA",
        "Scotland – SCO",
        "Senegal – SEN",
        "Serbia – SRB",
        "Slovakia – SVK",
        "Slovenia – SVN",
        "South Africa – RSA",
        "South Korea – KOR",
        "Spain – ESP",
        "Suriname – SUR",
        "Sweden – SWE",
        "Switzerland – SUI",
        "Tunisia – TUN",
        "Turkey – TUR",
        "Ukraine – UKR",
        "United States – USA",
        "Uruguay – URU",
        "Uzbekistan – UZB",
        "Venezuela – VEN",
        "Wales – WAL",
        "Zambia – ZAM",
        "Zimbabwe – ZIM"
    ]
    
    nationality_index = nationality_options.index(st.session_state.nationality) if st.session_state.nationality in nationality_options else 0
    nationality = st.selectbox(
        "Nacionalidad",
        options=nationality_options,
        index=nationality_index,
        key="nationality"
    )
    
    # 💰 SECCIÓN 2: ASPECTOS ECONÓMICOS
    with st.expander("💰 **Aspectos Económicos**", expanded=True):
        st.markdown("##### Valor y Salario")
        # Valor de mercado
        market_value = st.slider("Valor de Mercado (M€)", 0, 200, st.session_state.market_value, key="market_value")
        
        # Salario
        def format_salary(val):
            if val < 1_000_000:
                return f"{val//1000}K€"
            else:
                if val % 1_000_000 == 0:
                    return f"{val//1_000_000}M€"
                else:
                    return f"{val/1_000_000:.1f}M€".replace('.0','')
        
        max_salary_k = st.slider(
            f"Salario Máximo: {format_salary(1000*st.session_state.get('max_salary_k', 5000))}",
            min_value=100,
            max_value=100_000,
            value=5_000,
            step=50,
            format="%dK€",
            key="max_salary_k"
        )
        max_salary = max_salary_k * 1000
        
        st.markdown("---")
        st.markdown("##### Situación Contractual")
        # Contrato
        contract_options = ["Todos", 2024, 2025, 2026, 2027, 2028, 2029, 2030]
        contract_index = contract_options.index(st.session_state.contract_year) if st.session_state.contract_year in contract_options else 0
        contract_year = st.selectbox(
            "Fin de Contrato",
            options=contract_options,
            index=contract_index,
            key="contract_year"
        )
        
        # Filtro de cláusula
        clause_options = ["Ambos", "Sí", "No"]
        clause_index = clause_options.index(st.session_state.has_clause) if st.session_state.has_clause in clause_options else 0
        has_clause = st.radio(
            "¿Tiene Cláusula de Rescisión?",
            clause_options,
            index=clause_index,
            key="has_clause"
        )
    
    # 🎯 SECCIÓN 3: FILTROS AVANZADOS
    with st.expander("🎯 **Análisis Avanzado**", expanded=False):
        metrics_90 = st.multiselect(
            "Métricas de Rendimiento/90",
            ["xG", "xA", "Passes Completed", "Tackles", "Interceptions", "Distance Covered"],
            default=st.session_state.metrics_90,
            key="metrics_90",
            help="Selecciona métricas para encontrar jugadores destacados"
        )
        
        if metrics_90:
            st.info(f"🔍 Buscaré jugadores en el TOP 10 de: {', '.join(metrics_90)}")

    # 🔄 BOTONES DE ACCIÓN
  
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔍 Aplicar Filtros", type="primary", use_container_width=True):
            st.success("✅ Filtros aplicados")
    with col2:
        if st.button("🗑️ Limpiar Todo", use_container_width=True):
            st.session_state["reset_filters"] = True
            st.rerun()

# Panel principal
tab1, tab2, tab3 = st.tabs(["Table View", "Card View", "Heatmap View"])

with tab1:
    st.markdown("""
        <div style='background-color: white; padding: 1rem; border-radius: 1rem; margin-bottom: 0.5rem;'>
            <h3 style='margin-bottom: 0.5rem;'>Resultados de la Búsqueda</h3>
        </div>
    """, unsafe_allow_html=True)
    
    # Tabla de resultados mejorada con nuevo sistema de rating 40-99
    df = pd.DataFrame({
        'Name': ['Player 1', 'Player 2', 'Player 3', 'Player 4', 'Player 5', 'Player 6', 'Player 7', 'Player 8', 'Player 9', 'Player 10', 'Player 11', 'Player 12'],
        'Age': [23, 25, 21, 28, 24, 27, 22, 29, 26, 20, 30, 19],
        'Position': ['CM', 'ST', 'CB', 'RW', 'LW', 'GK', 'CB', 'CM', 'ST', 'LB', 'RB', 'CAM'],
        'Profile': ['Box-to-Box', 'Poacher', 'Stopper', 'Direct Winger', 'Wide Playmaker', 'Sweeper', 'Ball Playing', 'Deep Lying', 'Target Man', 'Defensive', 'Progressive', 'Advanced Playmaker'],
        'Value (M€)': [15, 45, 8, 22, 18, 5, 12, 30, 25, 10, 9, 16],
        'Rating': [78, 89, 65, 84, 80, 72, 77, 91, 76, 73, 74, 85],  # Nuevo sistema 40-99
        'xG': [0.25, 0.45, 0.10, 0.30, 0.28, 0.05, 0.12, 0.33, 0.40, 0.08, 0.09, 0.29],
        'xA': [0.18, 0.22, 0.05, 0.27, 0.19, 0.03, 0.07, 0.25, 0.21, 0.06, 0.08, 0.24],
        'Passes Completed': [65, 40, 55, 70, 68, 30, 60, 75, 50, 45, 48, 72],
        'Tackles': [2, 1, 4, 3, 2, 0, 5, 2, 1, 6, 7, 2],
        'Interceptions': [1, 0, 3, 2, 1, 0, 4, 1, 0, 5, 6, 1],
        'Distance Covered': [10.2, 9.8, 10.5, 11.0, 10.7, 9.0, 10.1, 11.2, 10.3, 9.5, 9.7, 11.1],
        'Nationality': ['🇪🇸 ESP', '🇫🇷 FRA', '🇩🇪 GER', '🇮🇹 ITA', '🇧🇷 BRA', '🇵🇹 POR', '🇳🇱 NED', '🇦🇷 ARG', '🇧🇪 BEL', '🇬🇧 ENG', '🇺🇾 URU', '🇭🇷 CRO'],
        'Club': ['Barcelona', 'PSG', 'Bayern Munich', 'Juventus', 'Real Madrid', 'Chelsea', 'Liverpool', 'Atletico', 'Sevilla', 'Valencia', 'Betis', 'Milan'],
        'Contract End': [2026, 2025, 2027, 2024, 2026, 2025, 2027, 2024, 2026, 2025, 2027, 2024],
        'Market Value': [15, 45, 8, 22, 18, 5, 12, 30, 25, 10, 9, 16],
        'Salary': [2_000_000, 8_000_000, 1_200_000, 3_500_000, 2_800_000, 900_000, 1_500_000, 4_000_000, 2_200_000, 1_000_000, 1_100_000, 2_600_000],
        'Height': [180, 185, 190, 175, 178, 192, 188, 181, 183, 177, 179, 176],
        'Foot': ['Right', 'Left', 'Right', 'Right', 'Left', 'Right', 'Left', 'Right', 'Right', 'Left', 'Right', 'Left'],
        'Has Clause': ['Sí', 'No', 'Sí', 'No', 'Sí', 'No', 'Sí', 'No', 'Sí', 'No', 'Sí', 'No'],
    })

    # --- FILTRADO POR TODOS LOS FILTROS ---
    filtered_df = df.copy()
    
    # Posición
    if position != "All":
        filtered_df = filtered_df[filtered_df["Position"] == position]
    
    # Perfil
    if roles != "All Profiles":
        filtered_df = filtered_df[filtered_df["Profile"] == roles]
    
    # Edad
    filtered_df = filtered_df[(filtered_df["Age"] >= age_range[0]) & (filtered_df["Age"] <= age_range[1])]
    
    # Rating mínimo (NUEVO)
    if 'rating_min' in st.session_state and st.session_state.rating_min > 40:
        filtered_df = filtered_df[filtered_df["Rating"] >= st.session_state.rating_min]
    
    # Altura
    filtered_df = filtered_df[(filtered_df["Height"] >= height_range[0]) & (filtered_df["Height"] <= height_range[1])]
    
    # Pie dominante
    if foot != "Both":
        filtered_df = filtered_df[filtered_df["Foot"] == foot]
    
    # Nacionalidad
    if nationality != "Todos los países":
        # Extraer el código del país (últimas 3 letras después del guión)
        country_code = nationality.split(" – ")[-1]
        filtered_df = filtered_df[filtered_df["Nationality"].str.contains(country_code, case=False)]
    
    # Contrato (NUEVO - Simplificado)
    # Mercado Libre: filtro específico para contratos específicos
    if 'contract_years' in st.session_state and st.session_state.contract_years is not None:
        filtered_df = filtered_df[filtered_df["Contract End"].isin(st.session_state.contract_years)]
    elif contract_year != "Todos":
        # Filtro del sidebar por año específico
        filtered_df = filtered_df[filtered_df["Contract End"] == contract_year]
    
    # Valor de mercado
    # Siempre aplicar el filtro
    filtered_df = filtered_df[(filtered_df["Market Value"] >= market_value[0]) & (filtered_df["Market Value"] <= market_value[1])]
    
    # Salario
    filtered_df = filtered_df[filtered_df["Salary"] <= max_salary]
    
    # Cláusula
    if has_clause == "Sí":
        filtered_df = filtered_df[filtered_df["Has Clause"] == "Sí"]
    elif has_clause == "No":
        filtered_df = filtered_df[filtered_df["Has Clause"] == "No"]
    
    # Contador de resultados y paginación
    total_results = len(filtered_df)
    
    # Reset de página si no hay resultados en la página actual
    players_per_page = 10
    total_pages = max(1, (total_results + players_per_page - 1) // players_per_page)
    
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 1
    
    # Resetear página si está fuera de rango
    if st.session_state.current_page > total_pages:
        st.session_state.current_page = 1
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"<div class='results-counter'>📊 **{total_results} jugadores encontrados**</div>", unsafe_allow_html=True)
    
    # Paginación
    with col2:
        if total_pages > 1:
            col_prev, col_page, col_next = st.columns([1, 2, 1])
            with col_prev:
                if st.button("◀", disabled=st.session_state.current_page <= 1):
                    st.session_state.current_page -= 1
            with col_page:
                st.markdown(f"<div style='text-align: center; padding: 0.5rem;'>Página {st.session_state.current_page} de {total_pages}</div>", unsafe_allow_html=True)
            with col_next:
                if st.button("▶", disabled=st.session_state.current_page >= total_pages):
                    st.session_state.current_page += 1

    # --- LÓGICA DE FILTRO POR MÉTRICAS (mantener al final) ---
    if metrics_90:
        top_sets = []
        for metric in metrics_90:
            if metric in filtered_df.columns:
                top_players = filtered_df.nlargest(10, metric)["Name"].tolist()
                top_sets.append(set(top_players))
        if top_sets:
            top_intersection = set.intersection(*top_sets)
            if top_intersection:
                st.markdown(f"#### Top jugadores en {' & '.join(metrics_90)} (en el top 10 de todas)")
                cols_to_show = ["Name", "Club"] + metrics_90
                filtered_top = filtered_df[filtered_df["Name"].isin(top_intersection)][cols_to_show]
                
                # Paginación para métricas también
                start_idx = (st.session_state.current_page - 1) * players_per_page
                end_idx = start_idx + players_per_page
                paginated_top = filtered_top.iloc[start_idx:end_idx]
                
                st.dataframe(paginated_top.sort_values(by=metrics_90[0], ascending=False), hide_index=True, use_container_width=True)
            else:
                st.info("No hay jugadores que estén en el top 10 de todas las métricas seleccionadas. Prueba con otras combinaciones o menos métricas.")
        else:
            st.info("No hay métricas válidas seleccionadas.")
    else:
        # Aplicar paginación
        start_idx = (st.session_state.current_page - 1) * players_per_page
        end_idx = start_idx + players_per_page
        paginated_df = filtered_df.iloc[start_idx:end_idx].copy()
        
        # Añadir columna de shortlist
        paginated_df['Shortlist'] = paginated_df['Name'].apply(
            lambda x: x in st.session_state.shortlist
        )
        
        # Configuración de columnas
        st.dataframe(
            paginated_df,
            column_config={
                "Shortlist": st.column_config.CheckboxColumn(
                    "📋",
                    width="small",
                    help="Añadir/quitar de shortlist"
                ),
                "Name": st.column_config.TextColumn(
                    "Player Name",
                    width="medium",
                    help="Full name of the player"
                ),
                "Rating": st.column_config.ProgressColumn(
                    "Rating",
                    format="%d",
                    min_value=40,
                    max_value=99,
                ),
                "Value (M€)": st.column_config.NumberColumn(
                    "Market Value",
                    format="€%.1fM",
                ),
            },
            hide_index=True,
            use_container_width=True,
            on_select="rerun",
            selection_mode="multi-row"
        )
        
        # Botones de acción para shortlist
        st.markdown("---")
        col1, col2, col3 = st.columns([2, 2, 4])
        
        with col1:
            if st.button("➕ Añadir seleccionados a shortlist"):
                # Esta funcionalidad se implementará cuando tengamos eventos
                st.info("Selecciona jugadores en la tabla y usa este botón para añadirlos")
        
        with col2:
            if st.button("🗑️ Limpiar shortlist"):
                st.session_state.shortlist = []
        
        with col3:
            if st.session_state.shortlist:
                shortlist_names = ", ".join(st.session_state.shortlist[:3])
                if len(st.session_state.shortlist) > 3:
                    shortlist_names += f" y {len(st.session_state.shortlist) - 3} más..."
                st.info(f"📋 Shortlist: {shortlist_names}")

    # Sección de gestión manual de shortlist
    st.markdown("---")
    with st.expander("📋 Gestión de Shortlist", expanded=len(st.session_state.shortlist) > 0):
        if st.session_state.shortlist:
            st.markdown("**Jugadores en tu shortlist:**")
            for i, player_name in enumerate(st.session_state.shortlist):
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.markdown(f"• {player_name}")
                with col2:
                    if st.button("🗑️", key=f"remove_{i}", help="Quitar de shortlist"):
                        st.session_state.shortlist.remove(player_name)
        else:
            st.info("Tu shortlist está vacía. Usa la tabla de arriba para añadir jugadores.")
        
        # Función para añadir jugadores manualmente
        st.markdown("**Añadir jugador manualmente:**")
        available_players = [name for name in df['Name'].tolist() if name not in st.session_state.shortlist]
        if available_players:
            player_to_add = st.selectbox("Selecciona un jugador:", [""] + available_players)
            if st.button("➕ Añadir a shortlist") and player_to_add:
                if player_to_add not in st.session_state.shortlist:
                    st.session_state.shortlist.append(player_to_add)
                    st.success(f"✅ {player_to_add} añadido a la shortlist")

with tab2:
    st.markdown("<h3 style='margin-bottom: 1.5rem;'>Player Cards</h3>", unsafe_allow_html=True)
    
    # Mostrar contador y filtros activos también en card view
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"**{total_results} jugadores encontrados**")
    
    with col2:
        if total_pages > 1:
            col_prev, col_page, col_next = st.columns([1, 2, 1])
            with col_prev:
                if st.button("◀", key="card_prev", disabled=st.session_state.current_page <= 1):
                    st.session_state.current_page -= 1
            with col_page:
                st.markdown(f"<div style='text-align: center; padding: 0.5rem;'>Página {st.session_state.current_page} de {total_pages}</div>", unsafe_allow_html=True)
            with col_next:
                if st.button("▶", key="card_next", disabled=st.session_state.current_page >= total_pages):
                    st.session_state.current_page += 1
    
    # Aplicar paginación para cards
    start_idx = (st.session_state.current_page - 1) * players_per_page
    end_idx = start_idx + players_per_page
    paginated_df = filtered_df.iloc[start_idx:end_idx]
    
    # Mostrar cards en grid de 3 columnas
    if len(paginated_df) > 0:
        for i in range(0, len(paginated_df), 3):
            cols = st.columns(3)
            for j, col in enumerate(cols):
                if i + j < len(paginated_df):
                    player = paginated_df.iloc[i + j]
                    is_in_shortlist = player['Name'] in st.session_state.shortlist
                    
                    # Determinar emoji de posición
                    position_emoji = {
                        'GK': '🥅', 'CB': '🛡️', 'RB': '⚡', 'LB': '⚡',
                        'CM': '🎯', 'CDM': '🛡️', 'CAM': '🎨', 
                        'RW': '⚡', 'LW': '⚡', 'ST': '⚔️'
                    }.get(player['Position'], '⚽')
                    
                    # Color del badge según rating (nuevo sistema 40-99)
                    if player['Rating'] >= 85:
                        badge_color = "#22c55e"  # Verde (Excelente)
                    elif player['Rating'] >= 75:
                        badge_color = "#f59e0b"  # Amarillo (Bueno)
                    elif player['Rating'] >= 65:
                        badge_color = "#ef4444"  # Rojo (Regular)
                    else:
                        badge_color = "#6b7280"  # Gris (Bajo)
                    
                    shortlist_button_style = "background-color: #dc2626;" if is_in_shortlist else "background-color: #004D98;"
                    shortlist_text = "❌ Quitar" if is_in_shortlist else "➕ Añadir"
                    
                    with col:
                        st.markdown(f"""
            <div class="player-card">
                                <img src="https://via.placeholder.com/150" style="width: 100%; border-radius: 0.5rem; margin-bottom: 1rem;">
                                <h3>{player['Name']}</h3>
                                <p>{position_emoji} {player['Position']} | 👤 {player['Age']} años</p>
                                <p>{player['Nationality']} | ⚽ {player['Club']}</p>
                                <p>💰 €{player['Value (M€)']}M | 📏 {player['Height']}cm</p>
                                <div style="background-color: {badge_color}; color: white; padding: 0.5rem 1rem; border-radius: 9999px; font-size: 1rem; font-weight: 600; display: inline-block; margin-top: 0.5rem;">
                                    Rating: {player['Rating']}
                                </div>
                                <div style="margin-top: 1rem;">
                                    <button onclick="alert('Funcionalidad de shortlist')" style="{shortlist_button_style} color: white; border: none; padding: 0.5rem 1rem; border-radius: 0.5rem; width: 100%; cursor: pointer; margin-bottom: 0.5rem;">
                                        {shortlist_text}
                                    </button>
                                    <button onclick="alert('Ver perfil completo')" style="background-color: #6b7280; color: white; border: none; padding: 0.5rem 1rem; border-radius: 0.5rem; width: 100%; cursor: pointer;">
                                        Ver Perfil
                                    </button>
                                </div>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.info("No se encontraron jugadores con los filtros aplicados. Prueba ajustando los criterios de búsqueda.")

with tab3:
    # Vista de mapa de calor (placeholder)
    st.markdown("### Player Heatmap")
    st.info("Select a player to view their heatmap")

# Función helper para crear el campo de fútbol (se usará para heatmaps)
def create_football_pitch():
    fig, ax = plt.subplots(figsize=(10, 7))
    
    # Configuración del campo
    ax.set_facecolor('#1E293B')
    fig.patch.set_facecolor('#0F172A')
    
    # Dibujar las líneas del campo
    ax.plot([0, 0, 100, 100, 0], [0, 100, 100, 0, 0], color='white', lw=2)
    ax.plot([50, 50], [0, 100], color='white', lw=2)
    
    # Círculo central
    circle = plt.Circle((50, 50), 9.15, fill=False, color='white', lw=2)
    ax.add_patch(circle)
    
    # Áreas
    ax.plot([0, 16.5, 16.5, 0], [20, 20, 80, 80], color='white', lw=2)
    ax.plot([100, 83.5, 83.5, 100], [20, 20, 80, 80], color='white', lw=2)
    
    ax.set_xlim(-5, 105)
    ax.set_ylim(-5, 105)
    ax.axis('off')
    
    return fig, ax

# Placeholder para el comparador de jugadores
if st.button("Compare Selected Players"):
    st.markdown("### Player Comparison")
    col1, col2 = st.columns(2)
    
    with col1:
        # Radar chart placeholder
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(
            r=[80, 70, 85, 75, 90],
            theta=['Pace', 'Shooting', 'Passing', 'Dribbling', 'Physical'],
            fill='toself',
            name='Player 1'
        ))
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100]
                )
            ),
            showlegend=True,
            paper_bgcolor='#1E293B',
            plot_bgcolor='#1E293B',
            font=dict(color='#E2E8F0')
        )
        st.plotly_chart(fig)
    
    with col2:
        # Tabla comparativa placeholder
        st.dataframe(pd.DataFrame({
            'Metric': ['Goals', 'Assists', 'Pass %', 'Tackles'],
            'Player 1': [15, 8, 87, 45],
            'Player 2': [12, 12, 92, 32]
        }))

# Botón de exportar informe
st.download_button(
    label="Export Report (PDF)",
    data=b"Placeholder PDF data",
    file_name="scouting_report.pdf",
    mime="application/pdf"
) 