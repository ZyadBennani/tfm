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
import sys
import os

# Agregar el directorio utils al path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Importaciones con manejo de errores
try:
    from utils.scouting_data_manager import ScoutingDataManager
    from utils.player_photo_manager import get_photo_manager
    from utils.rating_calculator import RatingCalculator
    print("✅ Módulos utils importados correctamente")
except ImportError as e:
    print(f"⚠️ Error importando módulos utils: {e}")
    # Crear clases de fallback
    class RatingCalculator:
        def __init__(self):
            self.profiles_data = {}
        def bulk_calculate_ratings(self, df):
            df = df.copy()
            df['Display_Rating'] = df.get('Rating', 65)
            return df
        def gauss_scale(self, df, **kwargs):
            return df
except SyntaxError as e:
    print(f"⚠️ Error de sintaxis en rating_calculator: {e}")
    # Crear clases de fallback
    class RatingCalculator:
        def __init__(self):
            self.profiles_data = {}
        def bulk_calculate_ratings(self, df):
            df = df.copy()
            df['Display_Rating'] = df.get('Rating', 65)
            return df
        def gauss_scale(self, df, **kwargs):
            return df

# Configuración de la página
st.set_page_config(
    page_title="Player Scouting",
    page_icon="🔍",
    layout="wide"
)

# Inicializar el gestor de datos
@st.cache_resource
def get_data_manager():
    return ScoutingDataManager()

# Inicializar el gestor de fotos
@st.cache_resource
def get_photo_manager_cached():
    return get_photo_manager()

# Inicializar el calculador de rating - SIN CACHE para nuevos cambios
def get_rating_calculator():
    return RatingCalculator()

# Función para limpiar cache del rating calculator
def clear_rating_cache():
    """Limpiar cache del rating calculator"""
    if 'get_rating_calculator' in st.session_state:
        del st.session_state['get_rating_calculator']
    # get_rating_calculator.clear()  # Ya no hay cache

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
        
        /* Selectbox con borde siempre visible */
        .stSelectbox > div > div {
            border: 2px solid #004D98 !important;
            border-radius: 0.5rem !important;
            background-color: white !important;
        }
        
        .stSelectbox > div > div:hover {
            border-color: #0066CC !important;
            box-shadow: 0 0 0 1px #0066CC !important;
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

# Inicializar shortlist si no existe
if 'shortlist' not in st.session_state:
    st.session_state.shortlist = []

shortlist_count = len(st.session_state.shortlist)

# Título principal con contador de shortlist integrado
st.markdown(f"""
    <div style='background-color: white; padding: 1rem; border-radius: 0.5rem; margin-bottom: 1rem; box-shadow: 0 2px 4px rgba(0,0,0,0.1); display: flex; justify-content: space-between; align-items: center;'>
        <div style='display: flex; align-items: center; gap: 0.5rem;'>
            <span style='font-size: 2.2rem;'>⚽</span>
            <span style='font-size: 2rem; font-weight: 600; color: #1a1a1a;'>Player Scouting</span>
            <span style='font-size: 1.2rem; background: linear-gradient(135deg, #004D98 0%, #A50044 100%); color: white; padding: 0.2rem 0.5rem; border-radius: 15px; margin-left: 1rem;'>⚡ Rating System</span>
        </div>
        <div style='display: flex; align-items: center; gap: 0.5rem;'>
            <span style='font-size: 1.2rem;'>📋</span> 
            <span style='background-color: #A50044; color: white; padding: 0.4rem 0.8rem; border-radius: 50%; font-size: 1rem; font-weight: 600; min-width: 2rem; text-align: center;'>{shortlist_count}</span>
        </div>
    </div>
""", unsafe_allow_html=True)

# Diccionario de perfiles por posición - ACTUALIZADO CON TODOS LOS PERFILES
position_profiles = {
    "GK": ["Sweeper", "Line Keeper", "Traditional"],
    "CB": ["Ball Playing", "Stopper", "Sweeper"],
    "RB": ["Defensive", "Progressive", "Offensive"],
    "LB": ["Defensive", "Progressive", "Offensive"],
    "CDM": ["Deep Lying", "Holding", "Box-to-Box Destroyer"],
    "CM": ["Box-to-Box", "Playmaker", "Defensive"],
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
        "league": "Todas las ligas",  # Liga por defecto
        "club": "Todos los clubes",  # Club por defecto
        "nationality": "Todos los países",
        "market_value": (0, 200),  # RANGO COMPLETO
        "max_salary_k": 100000,  # SALARIO MÁXIMO (100M€)
        "metrics_90": [],
        "percentile": False,
        "height_range": (140, 210),  # RANGO COMPLETO
        "has_clause": "Todos",  # Mostrar todos por defecto
        "current_page": 1,  # Resetear también la página
    }

    # Inicializar filtros si no existen
    for k, v in default_filters.items():
        if k not in st.session_state:
            st.session_state[k] = v
    
    # 📍 SECCIÓN 1: CARACTERÍSTICAS BÁSICAS
    with st.expander("📍 **Características Básicas**", expanded=False):
        # Posición
        position_options = ["All", "GK", "CB", "RB", "LB", "CDM", "CM", "CAM", "RW", "LW", "ST"]
        position_index = position_options.index(st.session_state.get('position_select', 'All')) if st.session_state.get('position_select', 'All') in position_options else 0
        position = st.selectbox(
            "Puesto",
            options=position_options,
            index=position_index,
            key="position_select"
        )
        
        # Perfil/Rol
        available_profiles = position_profiles.get(position, ["All Profiles"])
        profile_index = available_profiles.index(st.session_state.get('profile_select', 'All Profiles')) if st.session_state.get('profile_select', 'All Profiles') in available_profiles else 0
        roles = st.selectbox(
            "Perfil de Juego",
            options=available_profiles,
            index=profile_index,
            key="profile_select"
        )
        
        # Edad - ajustar según filtros especiales
        default_age = (15, 40)
        if st.session_state.get('young_prospects_filter', False):
            default_age = (16, 22)
        elif st.session_state.get('elite_filter', False):
            default_age = (22, 30)
        
        age_range = st.slider("Edad", 15, 40, st.session_state.get('age_range', default_age), key="age_range")
        
        # Rating mínimo - ajustar según filtros especiales
        default_rating = 40
        if st.session_state.get('young_prospects_filter', False):
            default_rating = 70
        elif st.session_state.get('elite_filter', False):
            default_rating = 83
        
        current_rating = st.session_state.get('rating_min', default_rating)
        if not isinstance(current_rating, int):
            current_rating = int(current_rating)
        rating_min = st.slider("Rating Mínimo", min_value=40, max_value=99, value=current_rating, key="rating_min")
        
        # Altura
        height_range = st.slider("Altura (cm)", 140, 210, st.session_state.get('height_range', (140, 210)), key="height_range")
        
        # Pie dominante
        foot_options = ["Both", "Left", "Right"]
        foot_index = foot_options.index(st.session_state.get('foot', 'Both')) if st.session_state.get('foot', 'Both') in foot_options else 0
        foot = st.radio("Pie Dominante", foot_options, index=foot_index, key="foot")
        
        # Liga - obtener ligas dinámicamente de los datos
        data_manager = get_data_manager()
        temp_df = data_manager.get_player_data(use_real_data=True)
        available_leagues = data_manager.get_available_leagues(temp_df)
        
        league_options = ["Todas las ligas"] + available_leagues
        league_index = league_options.index(st.session_state.get('league', 'Todas las ligas')) if st.session_state.get('league', 'Todas las ligas') in league_options else 0
        league = st.selectbox(
            "Liga",
            options=league_options,
            index=league_index,
            key="league"
        )
        
        # Club - obtener clubes dinámicamente de los datos (filtrados por liga si está seleccionada)
        if league != "Todas las ligas":
            available_clubs = data_manager.get_available_clubs(temp_df, league)
        else:
            available_clubs = data_manager.get_available_clubs(temp_df)
        
        club_options = ["Todos los clubes"] + available_clubs
        club_index = club_options.index(st.session_state.get('club', 'Todos los clubes')) if st.session_state.get('club', 'Todos los clubes') in club_options else 0
        club = st.selectbox(
            "Club",
            options=club_options,
            index=club_index,
            key="club"
        )
        
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
        
        nationality_index = nationality_options.index(st.session_state.get('nationality', 'Todos los países')) if st.session_state.get('nationality', 'Todos los países') in nationality_options else 0
        nationality = st.selectbox(
            "Nacionalidad",
            options=nationality_options,
            index=nationality_index,
            key="nationality"
        )
    
    # 💰 SECCIÓN 2: ASPECTOS ECONÓMICOS
    with st.expander("💰 **Aspectos Económicos**", expanded=False):
        st.markdown("##### Valor y Salario")
        # Valor de mercado
        market_value = st.slider("Valor de Mercado (M€)", 0, 200, st.session_state.get('market_value', (0, 200)), key="market_value")
        
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
            f"Salario Máximo: {format_salary(1000*st.session_state.get('max_salary_k', 100000))}",
            min_value=100,
            max_value=100_000,
            value=st.session_state.get('max_salary_k', 100000),
            step=50,
            format="%dK€",
            key="max_salary_k"
        )
        max_salary = max_salary_k * 1000
        
       
        st.markdown("##### Situación Contractual")
        # Contrato - ajustar según filtros especiales
        contract_options = ["Todos", 2024, 2025, 2026, 2027, 2028, 2029, 2030]
        default_contract = 'Todos'
        if st.session_state.get('free_market_filter', False):
            default_contract = 2025
        
        contract_index = contract_options.index(st.session_state.get('contract_year', default_contract)) if st.session_state.get('contract_year', default_contract) in contract_options else 0
        contract_year = st.selectbox(
            "Fin de Contrato",
            options=contract_options,
            index=contract_index,
            key="contract_year"
        )
        
        # Filtro de cláusula
        clause_options = ["Todos", "No", "Sí"]
        
        # Limpiar valor inválido del session_state si existe
        if 'has_clause' in st.session_state and st.session_state['has_clause'] not in clause_options:
            st.session_state['has_clause'] = 'Todos'
        
        clause_index = clause_options.index(st.session_state.get('has_clause', 'Todos')) if st.session_state.get('has_clause', 'Todos') in clause_options else 0
        has_clause = st.radio(
            "¿Tiene Cláusula de Rescisión?",
            clause_options,
            index=clause_index,
            key="has_clause"
        )
    
    # 🎯 SECCIÓN 3: FILTROS AVANZADOS
    with st.expander("🎯 **Análisis Avanzado**", expanded=False):
        col1, col2 = st.columns([2, 1])
        
        with col1:
            metrics_90 = st.multiselect(
                "Métricas de Rendimiento/90",
                ["xG", "xA", "Passes Completed", "Tackles", "Interceptions", "Distance Covered"],
                default=st.session_state.get('metrics_90', []),
                key="metrics_90",
                help="Selecciona métricas para encontrar jugadores destacados"
            )
        
        with col2:
            min_minutes = st.selectbox(
                "Mínimo de Minutos",
                options=[1000, 2000, 3000, 4000, 5000, 6000],
                index=0,
                key="min_minutes_filter",
                help="Filtro de minutos jugados para el Top 10"
            )
        
        if metrics_90:
            st.info(f"TOP 10 jugadores con mejor {', '.join(metrics_90)} (mínimo {min_minutes} minutos jugados)")

    # ⚡ SECCIÓN 4: FILTROS RÁPIDOS
    with st.expander("⚡ **Filtros Rápidos**", expanded=False):
        
        
        if st.button("🌟 Jóvenes Promesas", use_container_width=True, help="Jugadores de 16-22 años con rating 70+"):
            # LIMPIAR FILTROS PRIMERO
            keys_to_reset = [
                'position_select', 'profile_select', 'foot', 'nationality',
                'contract_year', 'market_value', 'max_salary_k', 'height_range',
                'has_clause', 'metrics_90', 'contract_years', 'age_range', 'rating_min',
                'free_market_filter', 'elite_filter'
            ]
            for key in keys_to_reset:
                if key in st.session_state:
                    del st.session_state[key]
            
            # APLICAR FILTROS ESPECÍFICOS DE JÓVENES PROMESAS
            st.session_state['young_prospects_filter'] = True
            st.session_state.current_page = 1
            st.success("✅ Filtro aplicado: Jóvenes Promesas")
        
        if st.button("🆓 Libres", use_container_width=True, help="Jugadores con contrato terminando en 2025"):
            # LIMPIAR FILTROS PRIMERO
            keys_to_reset = [
                'position_select', 'profile_select', 'age_range', 'rating_min',
                'foot', 'nationality', 'market_value', 'max_salary_k', 
                'height_range', 'has_clause', 'metrics_90', 'contract_year',
                'young_prospects_filter', 'elite_filter'
            ]
            for key in keys_to_reset:
                if key in st.session_state:
                    del st.session_state[key]
            
            # APLICAR FILTRO ESPECÍFICO DE MERCADO LIBRE
            st.session_state['free_market_filter'] = True
            st.session_state.current_page = 1
            st.success("✅ Filtro aplicado: Mercado Libre")
        
        if st.button("⭐ Elite", use_container_width=True, help="Jugadores de 22-30 años con rating 83+"):
            # LIMPIAR FILTROS PRIMERO
            keys_to_reset = [
                'position_select', 'profile_select', 'foot', 'nationality',
                'contract_year', 'market_value', 'max_salary_k', 'height_range',
                'has_clause', 'metrics_90', 'contract_years', 'age_range', 'rating_min',
                'young_prospects_filter', 'free_market_filter'
            ]
            for key in keys_to_reset:
                if key in st.session_state:
                    del st.session_state[key]
            
            # APLICAR FILTROS ESPECÍFICOS DE ELITE
            st.session_state['elite_filter'] = True
            st.session_state.current_page = 1
            st.success("✅ Filtro aplicado: Elite")

    # 🔄 BOTÓN DE ACCIÓN
    if st.button("🗑️ Limpiar Todo", use_container_width=True):
        # LIMPIAR TODOS LOS FILTROS - eliminar las claves para que se reinicialicen
        keys_to_reset = [
            'position_select', 'profile_select', 'age_range', 'rating_min',
            'height_range', 'foot', 'league', 'club', 'nationality', 'market_value', 
            'max_salary_k', 'contract_year', 'has_clause', 'metrics_90',
            'contract_years', 'current_page', 'young_prospects_filter',
            'free_market_filter', 'elite_filter'
        ]
        
        for key in keys_to_reset:
            if key in st.session_state:
                del st.session_state[key]
        
        st.rerun()

    # 💾 GESTIÓN DE CACHÉ - OCULTO AL USUARIO PERO FUNCIONAL
    # Nota: El caché sigue funcionando en segundo plano para mantener el rendimiento
    # Solo se oculta la interfaz de gestión ya que no es útil para el usuario final
    
    # with st.expander("💾 **Gestión de Caché**", expanded=False):
    #     st.markdown("**Gestión del caché de datos:**")
    #     
    #     data_manager = get_data_manager()
    #     
    #     # Verificar si el método existe (compatibilidad)
    #     if hasattr(data_manager.loader, 'get_cache_info'):
    #         try:
    #             cache_info = data_manager.loader.get_cache_info()
    #             
    #             for cache_type, info in cache_info.items():
    #                 if info['exists']:
    #                     status_icon = "✅" if info['is_valid'] else "⚠️"
    #                     st.markdown(f"{status_icon} **{cache_type.title()}**: {info['size_mb']} MB - Modificado: {info['last_modified']}")
    #                     if not info['is_valid']:
    #                         st.markdown(f"   ⏰ Caché expirado (hace {abs(info['expires_in_days'])} días)")
    #                 else:
    #                     st.markdown(f"❌ **{cache_type.title()}**: No existe")
    #         except Exception as e:
    #             st.markdown("⚠️ No se pudo obtener información del caché")
    #     
    #     st.markdown("---")
    #     
    #     col1, col2 = st.columns(2)
    #     with col1:
    #         if st.button("🔄 Limpiar Caché Completo", help="Elimina todos los archivos de caché. Los datos se recargarán la próxima vez."):
    #             if hasattr(data_manager.loader, 'clear_cache'):
    #                 data_manager.loader.clear_cache('all')
    #                 st.info("🔄 Reinicia la aplicación para recargar los datos")
    #             else:
    #                 st.warning("⚠️ Función de limpieza no disponible")
    #     
    #     with col2:
    #         if st.button("🗑️ Solo Datos Consolidados", help="Limpia solo el caché de datos consolidados"):
    #             if hasattr(data_manager.loader, 'clear_cache'):
    #                 data_manager.loader.clear_cache('consolidated')
    #                 st.info("🔄 Los datos se reconsolidarán automáticamente")
    #             else:
    #                 st.warning("⚠️ Función de limpieza no disponible")

# Distribución gaussiana estricta activa en segundo plano (sin mostrar mensaje al usuario)

# Panel principal
tab1, tab2, tab3 = st.tabs(["Table View", "Card View", "Heatmap View"])

with tab1:
    # Cargar datos reales de jugadores
    data_manager = get_data_manager()
    
    # Cargar datos reales directamente
    df = data_manager.get_player_data(use_real_data=True)
    
    # Validar calidad de datos silenciosamente
    data_quality = data_manager.validate_data_quality(df)
    
    if data_quality['status'] == 'error':
        st.error(data_quality['message'])
        st.stop()
    
    # Ajustar nombres de columnas para compatibilidad
    if 'Market_Value' in df.columns:
        df['Market Value'] = df['Market_Value']
    if 'Salary_Annual' in df.columns:
        df['Salary'] = df['Salary_Annual']
    if 'Contract_End' in df.columns:
        df['Contract End'] = df['Contract_End']
    if 'xG_90' in df.columns:
        df['xG'] = df['xG_90']
    if 'xA_90' in df.columns:
        df['xA'] = df['xA_90']
    if 'Passes_Completed_90' in df.columns:
        df['Passes Completed'] = df['Passes_Completed_90']
    if 'Tackles_90' in df.columns:
        df['Tackles'] = df['Tackles_90']
    if 'Interceptions_90' in df.columns:
        df['Interceptions'] = df['Interceptions_90']
    if 'Distance_Covered_90' in df.columns:
        df['Distance Covered'] = df['Distance_Covered_90']

    # --- FILTRADO USANDO EL SISTEMA DE GESTIÓN DE DATOS ---
    
    # Aplicar filtros especiales si están activos
    if st.session_state.get('young_prospects_filter', False):
        # Jóvenes promesas: 16-22 años, rating 70+
        age_range = (16, 22)
        rating_min = 70
        contract_years = [2025, 2026, 2027]  # Contratos que terminan pronto
    elif st.session_state.get('free_market_filter', False):
        # Mercado libre: contratos que terminan en 2025
        contract_years = [2025]
        contract_year = 2025
    elif st.session_state.get('elite_filter', False):
        # Elite: 22-30 años, rating 83+
        age_range = (22, 30)
        rating_min = 83
        contract_years = None
    else:
        # Sin filtros especiales, usar valores normales
        contract_years = None
    
    filters = {
        'position': position,
        'profile': roles,
        'age_range': age_range,
        'rating_min': rating_min,
        'height_range': height_range,
        'foot': foot,
        'league': league,
        'club': club,
        'nationality': nationality,
        'contract_year': contract_year,
        'contract_years': contract_years,
        'market_value': market_value,
        'max_salary': max_salary * 1000,  # Convertir a formato anual
        'has_clause': has_clause
    }
    
    filtered_df = data_manager.apply_filters(df, filters)
    
    # 🔥 CALCULAR RATINGS CON DISTRIBUCIÓN GAUSSIANA ESTRICTA (SIEMPRE ACTIVA)
    if not df.empty:
        try:
            # Crear calculador con distribución gaussiana estricta (SIEMPRE)
            rating_calculator = RatingCalculator()
            
            # Aplicar distribución gaussiana estricta automáticamente
            df_with_ratings = rating_calculator.bulk_calculate_ratings(df)
            
            # Usar rating calculado si está disponible
            df_with_ratings['Display_Rating'] = df_with_ratings.get('Display_Rating', 
                                               df_with_ratings.get('Calculated_Rating', 
                                               df_with_ratings.get('Rating', 65)))
            
        except Exception as e:
            st.error(f"❌ Error en sistema de rating: {str(e)}")
            st.info("Usando ratings originales como fallback")
            df_with_ratings = df.copy()
            df_with_ratings['Display_Rating'] = df_with_ratings.get('Rating', 65)
    else:
        df_with_ratings = df.copy()
        df_with_ratings['Display_Rating'] = 65

    # APLICAR FILTROS CON RATINGS YA CALCULADOS  
    filtered_df = data_manager.apply_filters(df_with_ratings, filters)
    
    # Mostrar estadísticas de ratings calculados DESPUÉS del filtrado
    if not filtered_df.empty and 'Display_Rating' in filtered_df.columns:
        max_calc = filtered_df['Display_Rating'].max()
        min_calc = filtered_df['Display_Rating'].min()
        avg_calc = filtered_df['Display_Rating'].mean()
        over_80 = len(filtered_df[filtered_df['Display_Rating'] > 80])
        over_70 = len(filtered_df[filtered_df['Display_Rating'] > 70])
        
        if over_70 > 0 or max_calc > 75:  # Solo mostrar si hay ratings interesantes
            over_90 = len(filtered_df[filtered_df['Display_Rating'] > 90])
            over_95 = len(filtered_df[filtered_df['Display_Rating'] > 95])
            # Información del sistema gaussiano calculada pero no mostrada
    
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
    
    # Mostrar métricas dinámicas de los jugadores filtrados
    if not filtered_df.empty:
        # Calcular estadísticas de los datos filtrados
        # Determinar columna de liga
        league_col = 'Liga' if 'Liga' in filtered_df.columns else ('League' if 'League' in filtered_df.columns else None)
        
        filtered_stats = {
            'total_players': len(filtered_df),
            'total_leagues': filtered_df[league_col].nunique() if league_col and league_col in filtered_df.columns else 0,
            'total_clubs': filtered_df['Club'].nunique() if 'Club' in filtered_df.columns else 0,
            'avg_rating': filtered_df['Rating'].mean() if 'Rating' in filtered_df.columns else 0
        }
        
        # Obtener estadísticas del gestor de fotos
        photo_manager = get_photo_manager_cached()
        photo_stats = photo_manager.get_stats()
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Jugadores Encontrados", filtered_stats['total_players'])
        with col2:
            st.metric("Ligas", filtered_stats['total_leagues'])
        with col3:
            st.metric("Clubes", filtered_stats['total_clubs'])
        with col4:
            st.metric("Rating Promedio", f"{filtered_stats['avg_rating']:.1f}")
    else:
        st.info("No se encontraron jugadores con los filtros aplicados.")
    
    # Paginación
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
        # Obtener el valor de minutos mínimos del selectbox
        min_minutes = st.session_state.get('min_minutes_filter', 1000)
        
        top_sets = []
        for metric in metrics_90:
            if metric in filtered_df.columns:
                # Filtrar jugadores con más del mínimo de minutos seleccionado
                minutes_columns = ['Minutes', 'Min', 'Minutos', 'Playing_Time', 'MP']
                minutes_col = None
                
                # Buscar la columna de minutos
                for col in minutes_columns:
                    if col in filtered_df.columns:
                        minutes_col = col
                        break
                
                # Si hay columna de minutos, filtrar por más del mínimo seleccionado
                if minutes_col:
                    qualified_df = filtered_df[filtered_df[minutes_col] > min_minutes]
                else:
                    # Si no hay datos de minutos, usar todos los jugadores
                    qualified_df = filtered_df
                
                if not qualified_df.empty:
                    # Obtener top 10 de jugadores cualificados
                    top_df = qualified_df.nlargest(min(10, len(qualified_df)), metric)
                    top_players = []
                    
                    for name in top_df["Name"].tolist():
                        # Verificar que no sea un nombre de equipo
                        team_indicators = [
                            'fc ', 'cf ', 'cd ', 'ud ', 'ca ', 'rcd ', 'real ', 'atletico', 'barcelona', 
                            'madrid', 'sevilla', 'valencia', 'betis', 'celta', 'villarreal', 'girona',
                            'getafe', 'osasuna', 'mallorca', 'espanyol', 'las palmas', 'leganes',
                            'alaves', 'rayo', 'vallecano', 'athletic', 'sociedad', 'valladolid'
                        ]
                        is_team_name = any(indicator in str(name).lower() for indicator in team_indicators)
                        
                        if not is_team_name and name != 'Unknown':
                            top_players.append(name)
                    
                    if top_players:  # Solo añadir si hay jugadores válidos
                        top_sets.append(set(top_players))
        if top_sets:
            top_intersection = set.intersection(*top_sets)
            if top_intersection:
                st.markdown(f"#### Top jugadores en {' & '.join(metrics_90)} (en el top 10 de todas)")
                
                # Buscar columna de minutos para incluir en la tabla
                minutes_columns = ['Minutes', 'Min', 'Minutos', 'Playing_Time', 'MP']
                minutes_col = None
                
                for col in minutes_columns:
                    if col in filtered_df.columns:
                        minutes_col = col
                        break
                
                # Definir columnas a mostrar incluyendo minutos si está disponible
                cols_to_show = ["Name", "Club"]
                if minutes_col:
                    cols_to_show.append(minutes_col)
                cols_to_show.extend(metrics_90)
                
                filtered_top = filtered_df[filtered_df["Name"].isin(top_intersection)][cols_to_show]
                
                # Paginación para métricas también
                start_idx = (st.session_state.current_page - 1) * players_per_page
                end_idx = start_idx + players_per_page
                paginated_top = filtered_top.iloc[start_idx:end_idx]
                
                # Configurar formato de columnas
                column_config = {}
                if minutes_col:
                    column_config[minutes_col] = st.column_config.NumberColumn(
                        "Minutos",
                        format="%d min",
                        help="Minutos jugados en la temporada"
                    )
                
                st.dataframe(
                    paginated_top.sort_values(by=metrics_90[0], ascending=False), 
                    hide_index=True, 
                    use_container_width=True,
                    column_config=column_config
                )
            else:
                st.info("No hay jugadores que estén en el top 10 de todas las métricas seleccionadas. Prueba con otras combinaciones o menos métricas.")
        else:
            st.info("No hay métricas válidas seleccionadas.")
    else:
        # Inicializar datos sin ordenación inicial
        sorted_df = filtered_df.copy()
        
        # Aplicar ordenación solo si ya está definida (para mostrar el estado actual)
        if hasattr(st.session_state, 'sort_column') and st.session_state.sort_column:
            try:
                if st.session_state.sort_column == 'Foot':
                    # Ordenación especial para pie: Zurdos primero, luego derechos
                    foot_order = {'Left': 0, 'Right': 1}
                    sorted_df['foot_sort'] = sorted_df['Foot'].map(foot_order).fillna(2)
                    sorted_df = sorted_df.sort_values('foot_sort', ascending=st.session_state.sort_ascending)
                    sorted_df = sorted_df.drop('foot_sort', axis=1)
                elif st.session_state.sort_column == 'Profile':
                    # Ordenación especial para perfil
                    profile_order = {'Completo': 0, 'Ofensivo': 1, 'Defensivo': 2, 'Técnico': 3, 'Físico': 4, 'TBD': 5}
                    sorted_df['profile_sort'] = sorted_df.get('Profile', 'TBD').map(profile_order).fillna(5)
                    sorted_df = sorted_df.sort_values('profile_sort', ascending=st.session_state.sort_ascending)
                    sorted_df = sorted_df.drop('profile_sort', axis=1)
                elif st.session_state.sort_column in ['Salary_Annual', 'Market_Value']:
                    # Manejar valores nulos/cero en salarios y valores de mercado
                    col_name = st.session_state.sort_column
                    if col_name == 'Salary_Annual':
                        # Usar Salary si Salary_Annual no existe
                        if col_name not in sorted_df.columns and 'Salary' in sorted_df.columns:
                            col_name = 'Salary'
                    elif col_name == 'Market_Value':
                        # Usar 'Market Value' si 'Market_Value' no existe
                        if col_name not in sorted_df.columns and 'Market Value' in sorted_df.columns:
                            col_name = 'Market Value'
                    
                    if col_name in sorted_df.columns:
                        sorted_df = sorted_df.sort_values(col_name, ascending=st.session_state.sort_ascending, na_position='last')
                else:
                    # Ordenación normal para otras columnas
                    if st.session_state.sort_column in sorted_df.columns:
                        sorted_df = sorted_df.sort_values(st.session_state.sort_column, ascending=st.session_state.sort_ascending, na_position='last')
            except Exception as e:
                st.warning(f"Error al ordenar por {st.session_state.sort_column}: {str(e)}")
        
        # Calcular paginación inicial
        total_pages = max(1, (len(sorted_df) + players_per_page - 1) // players_per_page)
        start_idx = (st.session_state.current_page - 1) * players_per_page
        end_idx = start_idx + players_per_page
        paginated_df = sorted_df.iloc[start_idx:end_idx].copy()
        
        # Mostrar jugadores con fotos en formato de columnas
        if not paginated_df.empty:
            
            
            # Obtener gestor de fotos
            photo_manager = get_photo_manager_cached()
            
            # Función para formatear salario
            def format_salary(val):
                if pd.isna(val) or val == 0:
                    return "N/A"
                if val >= 1000000:
                    return f"€{val/1000000:.1f}M"
                elif val >= 1000:
                    return f"€{val/1000:.0f}K"
                else:
                    return f"€{val:.0f}"
            
            # Función para formatear valor de mercado
            def format_market_value(val):
                if pd.isna(val) or val == 0:
                    return "N/A"
                return f"€{val:.1f}M"
            
            # Función para color del rating
            def get_rating_color(rating):
                if rating >= 85:
                    return "#22c55e"  # Verde
                elif rating >= 75:
                    return "#f59e0b"  # Amarillo
                elif rating >= 65:
                    return "#ef4444"  # Rojo
                else:
                    return "#6b7280"  # Gris
            
            # Inicializar estado de ordenación si no existe
            if 'sort_column' not in st.session_state:
                st.session_state.sort_column = None
            if 'sort_ascending' not in st.session_state:
                st.session_state.sort_ascending = True
            
            # Crear encabezados de columnas como botones clicables (ajustar anchos)
            cols = st.columns([0.6, 1.8, 1.7, 1.2, 1.0, 1.3, 1.8, 1.2, 1.2, 1.5])
            headers = ["", "Jugador", "Posición", "Perfil", "Pie", "Edad", "Club", "Sal", "Valor", "Rating"]
            sort_columns = ["", "Name", "Position", "Profile", "Foot", "Age", "Club", "Salary_Annual", "Market_Value", "Display_Rating"]
            
            for i, header in enumerate(headers):
                with cols[i]:
                    if header:  # No mostrar header para la columna de fotos
                        # Agregar flecha indicadora de ordenación
                        sort_indicator = ""
                        if st.session_state.sort_column == sort_columns[i]:
                            sort_indicator = " ↑" if st.session_state.sort_ascending else " ↓"
                        
                        # Estilo especial para botones de header
                        button_style = """
                            <style>
                            div[data-testid="column"] button[kind="secondary"] {
                                background-color: #f8f9fa !important;
                                border: 1px solid #004D98 !important;
                                color: #004D98 !important;
                                font-weight: 600 !important;
                                padding: 0.3rem 0.2rem !important;
                                font-size: 0.65rem !important;
                                white-space: nowrap !important;
                                overflow: visible !important;
                                text-overflow: clip !important;
                                min-height: 2.5rem !important;
                            }
                            div[data-testid="column"] button[kind="secondary"]:hover {
                                background-color: #004D98 !important;
                                color: white !important;
                            }
                            </style>
                        """
                        st.markdown(button_style, unsafe_allow_html=True)
                        
                        if st.button(f"{header}{sort_indicator}", key=f"sort_{i}", use_container_width=True):
                            # Si se clica en la misma columna, cambiar dirección
                            if st.session_state.sort_column == sort_columns[i]:
                                st.session_state.sort_ascending = not st.session_state.sort_ascending
                            else:
                                st.session_state.sort_column = sort_columns[i]
                                # Configurar ordenación por defecto según el tipo de columna
                                if sort_columns[i] in ['Age', 'Salary_Annual', 'Market_Value', 'Display_Rating']:
                                    st.session_state.sort_ascending = False  # Descendente para números
                                elif sort_columns[i] == 'Foot':
                                    st.session_state.sort_ascending = False  # Zurdos primero
                                else:
                                    st.session_state.sort_ascending = True   # Ascendente para texto
                            
                            # Resetear a la primera página cuando se cambia el ordenamiento
                            st.session_state.current_page = 1
                            
                            # Aplicar ordenamiento inmediatamente
                            if st.session_state.sort_column:
                                try:
                                    if st.session_state.sort_column == 'Foot':
                                        # Ordenación especial para pie: Zurdos primero, luego derechos
                                        foot_order = {'Left': 0, 'Right': 1}
                                        sorted_df['foot_sort'] = sorted_df['Foot'].map(foot_order).fillna(2)
                                        sorted_df = sorted_df.sort_values('foot_sort', ascending=st.session_state.sort_ascending)
                                        sorted_df = sorted_df.drop('foot_sort', axis=1)
                                    elif st.session_state.sort_column == 'Profile':
                                        # Ordenación especial para perfil
                                        profile_order = {'Completo': 0, 'Ofensivo': 1, 'Defensivo': 2, 'Técnico': 3, 'Físico': 4, 'TBD': 5}
                                        sorted_df['profile_sort'] = sorted_df.get('Profile', 'TBD').map(profile_order).fillna(5)
                                        sorted_df = sorted_df.sort_values('profile_sort', ascending=st.session_state.sort_ascending)
                                        sorted_df = sorted_df.drop('profile_sort', axis=1)
                                    elif st.session_state.sort_column in ['Salary_Annual', 'Market_Value']:
                                        # Manejar valores nulos/cero en salarios y valores de mercado
                                        col_name = st.session_state.sort_column
                                        if col_name == 'Salary_Annual':
                                            # Usar Salary si Salary_Annual no existe
                                            if col_name not in sorted_df.columns and 'Salary' in sorted_df.columns:
                                                col_name = 'Salary'
                                        elif col_name == 'Market_Value':
                                            # Usar 'Market Value' si 'Market_Value' no existe
                                            if col_name not in sorted_df.columns and 'Market Value' in sorted_df.columns:
                                                col_name = 'Market Value'
                                        
                                        if col_name in sorted_df.columns:
                                            sorted_df = sorted_df.sort_values(col_name, ascending=st.session_state.sort_ascending, na_position='last')
                                    else:
                                        # Ordenación normal para otras columnas
                                        if st.session_state.sort_column in sorted_df.columns:
                                            sorted_df = sorted_df.sort_values(st.session_state.sort_column, ascending=st.session_state.sort_ascending, na_position='last')
                                except Exception as e:
                                    st.warning(f"Error al ordenar por {st.session_state.sort_column}: {str(e)}")
            
            st.markdown("---")
            
            # Actualizar paginación después del ordenamiento inmediato
            total_pages = max(1, (len(sorted_df) + players_per_page - 1) // players_per_page)
            start_idx = (st.session_state.current_page - 1) * players_per_page
            end_idx = start_idx + players_per_page
            paginated_df = sorted_df.iloc[start_idx:end_idx].copy()
            
            # Mostrar cada jugador
            for idx, (_, player) in enumerate(paginated_df.iterrows()):
                cols = st.columns([0.6, 1.8, 1.7, 1.2, 1.0, 1.3, 1.8, 1.2, 1.2, 1.5])
                
                # Columna 1: Foto (50x50px - más grande)
                with cols[0]:
                    photo_base64 = photo_manager.get_player_photo_base64(player['Name'], size=(50, 50))
                    st.markdown(f"""
                        <div style="display: flex; justify-content: center; align-items: center; height: 50px;">
                            <img src="data:image/png;base64,{photo_base64}" 
                                 style="width: 50px; height: 50px; border-radius: 50%; object-fit: cover;">
                        </div>
                    """, unsafe_allow_html=True)
                
                # Columna 2: Nombre del jugador
                with cols[1]:
                    is_in_shortlist = player['Name'] in st.session_state.shortlist
                    shortlist_icon = "⭐" if is_in_shortlist else ""
                    st.markdown(f"**{player['Name']}** {shortlist_icon}")
                
                # Columna 3: Posición
                with cols[2]:
                    position_emoji = {
                        'GK': '🟡', 'CB': '🔵', 'RB': '🟢', 'LB': '🟢',
                        'CM': '⚪', 'CDM': '⚪', 'CAM': '🟠',
                        'RW': '🟣', 'LW': '🟣', 'ST': '🔴'
                    }.get(player['Position'], '⚫')
                    st.markdown(f"{position_emoji} {player['Position']}")
                
                # Columna 4: Perfil
                with cols[3]:
                    st.markdown(player.get('Profile', 'TBD'))
                
                # Columna 5: Pie dominante
                with cols[4]:
                    foot_emoji = "" if player.get('Foot') == 'Right' else "" if player.get('Foot') == 'Left' else "⚽"
                    st.markdown(f"{foot_emoji} {player.get('Foot', 'N/A')}")
                
                # Columna 6: Edad
                with cols[5]:
                    st.markdown(f" {int(player['Age'])}")
                
                # Columna 7: Club
                with cols[6]:
                    st.markdown(f" {player['Club']}")
                
                # Columna 8: Salario
                with cols[7]:
                    salary = player.get('Salary_Annual', player.get('Salary', 0))
                    st.markdown(f" {format_salary(salary)}")
                
                # Columna 9: Valor de mercado
                with cols[8]:
                    market_val = player.get('Market_Value', player.get('Market Value', 0))
                    st.markdown(f" {format_market_value(market_val)}")
                
                # Columna 10: Rating con color (usar rating calculado)
                with cols[9]:
                    display_rating = player.get('Display_Rating', player.get('Calculated_Rating', player.get('Rating', 65)))
                    display_rating = int(display_rating)  # Forzar a entero
                    rating_color = get_rating_color(display_rating)
                    
                    # Mostrar rating original vs calculado si son diferentes
                    original_rating = int(player.get('Rating', 65))  # También forzar a entero
                    if abs(display_rating - original_rating) > 1:
                        tooltip = f"Original: {original_rating} → Calculado: {display_rating}"
                        rating_display = f"{display_rating} ⚡"
                    else:
                        rating_display = f"{display_rating}"
                        tooltip = f"Rating: {display_rating}"
                    
                    st.markdown(f"""
                        <div title="{tooltip}" style="background-color: {rating_color}; color: white; padding: 0.2rem 0.5rem; 
                                    border-radius: 12px; text-align: center; font-weight: bold; font-size: 0.9rem;">
                            {rating_display}
                        </div>
                    """, unsafe_allow_html=True)
                
                # Separador entre filas
                if idx < len(paginated_df) - 1:
                    st.markdown("<div style='margin: 0.5rem 0; border-bottom: 1px solid #e5e7eb;'></div>", unsafe_allow_html=True)
        
        else:
            st.info("No se encontraron jugadores con los filtros aplicados.")
        
        # Botones de acción para shortlist
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
                        'GK': '🟡', 'CB': '🔵', 'RB': '🟢', 'LB': '🟢',
                        'CM': '⚪', 'CDM': '⚪', 'CAM': '🟠',
                        'RW': '🟣', 'LW': '🟣', 'ST': '🔴'
                    }.get(player['Position'], '⚫')
                    
                    # Color del badge según rating calculado (nuevo sistema 40-99)
                    display_rating = player.get('Display_Rating', player.get('Calculated_Rating', player.get('Rating', 65)))
                    display_rating = int(display_rating)  # Forzar a entero
                    if display_rating >= 85:
                        badge_color = "#22c55e"  # Verde (Excelente)
                    elif display_rating >= 75:
                        badge_color = "#f59e0b"  # Amarillo (Bueno)
                    elif display_rating >= 65:
                        badge_color = "#ef4444"  # Rojo (Regular)
                    else:
                        badge_color = "#6b7280"  # Gris (Bajo)
                    
                    shortlist_button_style = "background-color: #dc2626;" if is_in_shortlist else "background-color: #004D98;"
                    shortlist_text = "❌ Quitar" if is_in_shortlist else "➕ Añadir"
                    
                    with col:
                        # Obtener foto del jugador
                        photo_manager = get_photo_manager_cached()
                        photo_base64 = photo_manager.get_player_photo_base64(player['Name'], size=(80, 80))
                        
                        st.markdown(f"""
                            <div class="player-card">
                                <div style="display: flex; justify-content: center; margin-bottom: 1rem;">
                                    <img src="data:image/png;base64,{photo_base64}" 
                                         style="width: 80px; height: 80px; border-radius: 50%; object-fit: cover; 
                                                border: 3px solid #004D98; box-shadow: 0 4px 8px rgba(0,0,0,0.2);">
                                </div>
                                <h3 style="text-align: center; margin-bottom: 0.5rem;">{player['Name']}</h3>
                                <p style="text-align: center;">{position_emoji} {player['Position']} | 👤 {int(player['Age'])} años</p>
                                <p style="text-align: center;">{player['Nationality']} |  {player['Club']}</p>
                                <p style="text-align: center;">€{player.get('Market_Value', 0):.1f}M | {player['Height']}cm</p>
                                <div style="display: flex; justify-content: center; margin-top: 0.5rem;">
                                    <div style="background-color: {badge_color}; color: white; padding: 0.5rem 1rem; border-radius: 9999px; font-size: 1rem; font-weight: 600;">
                                    Rating: {display_rating} ⚡
                                    </div>
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

# ⭐ PANEL DE INFORMACIÓN DEL CACHE (en sidebar)
with st.sidebar:
    st.markdown("---")
    with st.expander("🚀 Estado del Cache", expanded=False):
        data_manager = get_data_manager()
        cache_info = data_manager.loader.get_cache_info()
        
        st.markdown(f"**Tamaño Total:** {cache_info.get('total_size_mb', 0)} MB")
        
        for cache_type, info in cache_info.items():
            if isinstance(info, dict) and 'exists' in info:
                status_icon = "✅" if info['exists'] else "⏳"
                st.markdown(f"**{cache_type.title()}:** {status_icon}")
                if info['exists']:
                    st.markdown(f"  - Tamaño: {info.get('size_mb', 0)} MB")
                    st.markdown(f"  - Modificado: {info.get('modified', 'N/A')}")
        
        st.markdown("---")
        st.markdown("**⚠️ Gestión del Cache:**")
        
        if st.button("🗑️ Limpiar Cache", help="Solo usar si hay problemas"):
            data_manager.loader.clear_cache('all')
            st.success("Cache limpiado - refresca la página manualmente")
        
        if st.button("🔄 Regenerar Cache", help="Fuerza la regeneración completa"):
            data_manager.loader.force_rebuild_cache()
            st.success("Cache regenerado - refresca la página manualmente")
        
        if st.button("⚡ Limpiar Cache Rating", help="Recalcula todos los ratings con el nuevo sistema"):
            clear_rating_cache()
            st.success("Sistema de rating actualizado - los nuevos cálculos se aplicarán automáticamente")
        
        st.markdown("---")
        st.markdown("🎯 **Sistema Gaussiano Manual:**")
        
        if st.button("🚀 Aplicar Reescalado Gaussiano", help="Fuerza el reescalado gaussiano a todos los jugadores para alcanzar ratings 90-99"):
            # Aplicar reescalado gaussiano manual
            data_manager = get_data_manager()
            df_temp = data_manager.get_player_data(use_real_data=True)
            
            if not df_temp.empty:
                try:
                    rating_calculator = get_rating_calculator()
                    
                    # Aplicar reescalado gaussiano directo a los ratings existentes
                    st.info("🔄 Aplicando transformación gaussiana...")
                    
                    # Usar el rating existente como base
                    rating_col = 'Rating'
                    if 'Display_Rating' in df_temp.columns:
                        rating_col = 'Display_Rating'
                    elif 'Calculated_Rating' in df_temp.columns:
                        rating_col = 'Calculated_Rating'
                    
                    # Aplicar la función gauss_scale MÁS AGRESIVA
                    df_transformed = rating_calculator.gauss_scale(
                        df_temp,
                        col=rating_col,
                        pos_col='Position',
                        by_position=False,
                        mu=80,    # Media MUY alta (era 75, ahora 80)
                        sigma=22  # MÁS dispersión (era 18, ahora 22)
                    )
                    
                    # Actualizar el cache con los nuevos ratings
                    if 'rating_40_99' in df_transformed.columns:
                        # Mostrar estadísticas del resultado
                        max_rating = df_transformed['rating_40_99'].max()
                        min_rating = df_transformed['rating_40_99'].min()
                        avg_rating = df_transformed['rating_40_99'].mean()
                        over_90 = (df_transformed['rating_40_99'] > 90).sum()
                        over_85 = (df_transformed['rating_40_99'] > 85).sum()
                        over_80 = (df_transformed['rating_40_99'] > 80).sum()
                        
                        # Top 10 jugadores
                        if 'Name' in df_transformed.columns:
                            top_10 = df_transformed.nlargest(10, 'rating_40_99')
                            top_names = ", ".join(top_10['Name'].head(5).tolist())
                            
                            st.success(f"""
✅ **Reescalado Gaussiano Completado!**

📊 **Distribución Final:**
- Rango: {min_rating}-{max_rating}
- Media: {avg_rating:.1f}
- >90 rating: {over_90} jugadores
- >85 rating: {over_85} jugadores  
- >80 rating: {over_80} jugadores

🌟 **Top 5:** {top_names}

💡 **Refresca la página** para ver los nuevos ratings en la tabla principal.
                            """)
                        else:
                            st.success(f"✅ Transformación aplicada: {min_rating}-{max_rating} (media: {avg_rating:.1f})")
                    else:
                        st.error("❌ Error en la transformación gaussiana")
                        
                except Exception as e:
                    st.error(f"❌ Error aplicando reescalado: {str(e)}")
            else:
                st.error("❌ No se pudieron cargar los datos")
        
