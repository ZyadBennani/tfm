import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np

# Configuración de la página
st.set_page_config(
    page_title="Análisis Propio",
    page_icon="📊",
    layout="wide"
)

# Estilos CSS personalizados
st.markdown("""
    <style>
        .main {
            background-color: #f5f5f5;
        }
        .stTabs [data-baseweb="tab-list"] {
            gap: 24px;
        }
        .stTabs [data-baseweb="tab"] {
            height: 50px;
            padding-top: 10px;
            padding-bottom: 10px;
            white-space: pre-wrap;
            background-color: white;
            border-radius: 5px;
            color: #0E1117;
            font-weight: 500;
        }
        .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {
            background-color: #0E1117;
            color: white;
        }
        div[data-testid="stSidebarNav"] li div a {
            margin-left: 1rem;
            padding: 1rem;
            width: 300px;
            border-radius: 0.5rem;
        }
        div[data-testid="stSidebarNav"] li div::focus-visible {
            background-color: rgba(151, 166, 195, 0.15);
        }
        .metric-card {
            background-color: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
            margin: 10px 0;
        }
        h1 {
            color: #0E1117;
            padding: 1rem 0;
        }
        h2 {
            color: #0E1117;
            padding: 0.5rem 0;
        }
    </style>
""", unsafe_allow_html=True)

# Ocultar menú de hamburguesa y pie de página
hide_menu_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
"""
st.markdown(hide_menu_style, unsafe_allow_html=True)

# Título y descripción
st.title("Análisis Propio: Estilo y Modelo de Juego")
st.markdown("""
    <div style='background-color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px;'>
        <h4 style='color: #0E1117; margin-bottom: 10px;'>Análisis detallado del estilo de juego basado en datos agregados de Wyscout</h4>
        <p style='color: #666666;'>Visualización de KPIs clave en las 5 fases principales del juego, permitiendo un análisis profundo del modelo de juego.</p>
    </div>
""", unsafe_allow_html=True)

# Funciones helper (placeholders)
def create_sample_radar_chart(title, metrics):
    """Crea un gráfico radar de ejemplo con datos aleatorios"""
    values = np.random.uniform(40, 90, len(metrics))
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=metrics,
        fill='toself',
        name='Equipo',
        line_color='#1f77b4'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )
        ),
        showlegend=False,
        title=title,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    return fig

def create_sample_bar_chart(title, metrics):
    """Crea un gráfico de barras de ejemplo con datos aleatorios"""
    values = np.random.uniform(40, 90, len(metrics))
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=metrics,
        y=values,
        marker_color='#1f77b4'
    ))
    
    fig.update_layout(
        title=title,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=400
    )
    return fig

# Sidebar con filtros
with st.sidebar:
    st.markdown("""
        <div style='background-color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px;'>
            <h3 style='color: #0E1117; margin-bottom: 15px;'>Filtros de Análisis</h3>
        </div>
    """, unsafe_allow_html=True)
    
    season = st.selectbox(
        "Temporada",
        ["2023/24"],
        key="season_filter"
    )
    
    competition = st.selectbox(
        "Competición",
        ["LaLiga", "Champions League"],
        key="competition_filter"
    )
    
    opponent = st.selectbox(
        "Rival",
        ["Todos", "Real Madrid", "Atlético Madrid"],
        key="opponent_filter"
    )

# Crear tabs para las diferentes fases
tabs = st.tabs([
    "Fase Ofensiva", 
    "Fase Defensiva", 
    "Balón Parado",
    "Transición Defensiva",
    "Transición Ofensiva"
])

# 1. Fase Ofensiva
with tabs[0]:
    st.subheader("Fase Ofensiva")
    
    # KPIs en cards
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown("""
            <div class='metric-card'>
                <h3 style='margin:0;color:#0E1117;'>65%</h3>
                <p style='margin:0;color:#666666;'>Posesión</p>
            </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
            <div class='metric-card'>
                <h3 style='margin:0;color:#0E1117;'>2.1</h3>
                <p style='margin:0;color:#666666;'>xG por 90</p>
            </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
            <div class='metric-card'>
                <h3 style='margin:0;color:#0E1117;'>15.3</h3>
                <p style='margin:0;color:#666666;'>Tiros por 90</p>
            </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown("""
            <div class='metric-card'>
                <h3 style='margin:0;color:#0E1117;'>89%</h3>
                <p style='margin:0;color:#666666;'>Pases Completados</p>
            </div>
        """, unsafe_allow_html=True)
    
    # Gráficos
    col1, col2 = st.columns(2)
    with col1:
        metrics_offensive = ['Posesión', 'xG/90', 'Tiros/90', 'Pases %', 'Centros/90', 'Toques área/90', 'Duelos Of. %', 'Regates/90']
        fig_radar = create_sample_radar_chart("Métricas Ofensivas", metrics_offensive)
        st.plotly_chart(fig_radar, use_container_width=True, key="offensive_radar")
    
    with col2:
        fig_bar = create_sample_bar_chart("Distribución de Acciones Ofensivas", ['Pases', 'Centros', 'Regates', 'Tiros'])
        st.plotly_chart(fig_bar, use_container_width=True, key="offensive_bar")

# 2. Fase Defensiva
with tabs[1]:
    st.subheader("Fase Defensiva")
    
    # KPIs en cards
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown("""
            <div class='metric-card'>
                <h3 style='margin:0;color:#0E1117;'>8.2</h3>
                <p style='margin:0;color:#666666;'>Tiros Concedidos/90</p>
            </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
            <div class='metric-card'>
                <h3 style='margin:0;color:#0E1117;'>0.8</h3>
                <p style='margin:0;color:#666666;'>xG Concedido/90</p>
            </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
            <div class='metric-card'>
                <h3 style='margin:0;color:#0E1117;'>72%</h3>
                <p style='margin:0;color:#666666;'>Duelos Def. Ganados</p>
            </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown("""
            <div class='metric-card'>
                <h3 style='margin:0;color:#0E1117;'>12.5</h3>
                <p style='margin:0;color:#666666;'>Intercepciones/90</p>
            </div>
        """, unsafe_allow_html=True)
    
    # Gráficos
    col1, col2 = st.columns(2)
    with col1:
        metrics_defensive = ['Tiros Conc./90', 'xG Conc./90', 'Duelos Def. %', 'Interc./90', 'Despejes/90', 'Entradas %', 'Presión %', 'Duelos Aéreos %']
        fig_radar = create_sample_radar_chart("Métricas Defensivas", metrics_defensive)
        st.plotly_chart(fig_radar, use_container_width=True, key="defensive_radar")
    
    with col2:
        fig_bar = create_sample_bar_chart("Distribución de Acciones Defensivas", ['Intercepciones', 'Despejes', 'Entradas', 'Duelos Aéreos'])
        st.plotly_chart(fig_bar, use_container_width=True, key="defensive_bar")

# 3. Balón Parado
with tabs[2]:
    st.subheader("Balón Parado")
    metrics_set_pieces = ['xG Córners', 'Goles Córner/90', 'xG Tiros Libres', 'Eficiencia Penaltis', 'Córners Ganados/90']
    fig_set_pieces = create_sample_radar_chart("Métricas de Balón Parado", metrics_set_pieces)
    st.plotly_chart(fig_set_pieces, use_container_width=True, key="set_pieces_radar")

# 4. Transición Defensiva
with tabs[3]:
    st.subheader("Transición Defensiva")
    metrics_def_transition = ['Recuperaciones ≤10s', 'Duelos Def. Trans.', 'PPDA', 'Contras Concedidas', 'Tiempo Reacción']
    fig_def_transition = create_sample_radar_chart("Métricas de Transición Defensiva", metrics_def_transition)
    st.plotly_chart(fig_def_transition, use_container_width=True, key="def_transition_radar")

# 5. Transición Ofensiva
with tabs[4]:
    st.subheader("Transición Ofensiva")
    metrics_off_transition = ['Contraataques/90', 'xG Contras', 'Pases/Contra', 'Vel. Progresión', 'Eficiencia']
    fig_off_transition = create_sample_radar_chart("Métricas de Transición Ofensiva", metrics_off_transition)
    st.plotly_chart(fig_off_transition, use_container_width=True, key="off_transition_radar")
