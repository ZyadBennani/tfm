import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from matplotlib.colors import LinearSegmentedColormap
import io
import os
from PIL import Image, ImageDraw
from datetime import datetime, timedelta

# Configuración de la página
st.set_page_config(
    page_title="Análisis Propio",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Estilos CSS modernos
st.markdown("""
    <style>
        /* Variables globales */
        :root {
            --primary-color: #004D98;
            --secondary-color: #A50044;
            --background-light: #f8f9fa;
            --text-color: #2C3E50;
            --card-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }

        /* Estilos generales */
        .main {
            background-color: var(--background-light);
            color: var(--text-color);
        }

        /* Tarjetas modernas */
        .modern-card {
            background-color: white;
            padding: 1.5rem;
            border-radius: 15px;
            box-shadow: var(--card-shadow);
            margin: 1rem 0;
            transition: transform 0.2s ease;
        }

        .modern-card:hover {
            transform: translateY(-5px);
        }

        /* Tabs personalizados */
        .stTabs [data-baseweb="tab-list"] {
            gap: 24px;
            background-color: white;
            padding: 1.5rem;
            border-radius: 10px;
            box-shadow: var(--card-shadow);
            margin-bottom: 2rem;
        }

        .stTabs [data-baseweb="tab"] {
            height: 60px;
            padding: 15px 30px;
            background-color: #f8f9fa;
            border: none;
            color: var(--text-color);
            font-weight: 600;
            font-size: 1.1rem;
            transition: all 0.3s ease;
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
        }

        .stTabs [data-baseweb="tab"]:hover {
            background-color: #e9ecef;
            transform: translateY(-2px);
        }

        .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {
            background-color: var(--primary-color);
            color: white;
            border-radius: 8px;
            transform: translateY(-2px);
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }

        /* Subtabs para análisis táctico */
        .subtabs {
            margin-top: 1rem;
            padding: 1rem;
            background-color: white;
            border-radius: 10px;
            box-shadow: var(--card-shadow);
        }

        .subtab-button {
            padding: 10px 20px;
            margin: 5px;
            border: none;
            border-radius: 5px;
            background-color: #f8f9fa;
            color: var(--text-color);
            cursor: pointer;
            transition: all 0.2s ease;
        }

        .subtab-button:hover {
            background-color: #e9ecef;
        }

        .subtab-button.active {
            background-color: var(--primary-color);
            color: white;
        }

        /* Métricas y KPIs */
        .metric-container {
            background: white;
            padding: 1rem;
            border-radius: 10px;
            box-shadow: var(--card-shadow);
        }

        .metric-value {
            font-size: 2rem;
            font-weight: bold;
            color: var(--primary-color);
        }

        .metric-label {
            color: var(--text-color);
            font-size: 1rem;
        }

        /* Gráficos y visualizaciones */
        .chart-container {
            background: white;
            padding: 1rem;
            border-radius: 10px;
            box-shadow: var(--card-shadow);
            margin: 1rem 0;
        }

        /* Animaciones */
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .animate-fade-in {
            animation: fadeIn 0.5s ease forwards;
        }
    </style>
""", unsafe_allow_html=True)

# Ocultar menú y footer
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# Definir la ruta base de assets
ASSETS_BASE_PATH = r"C:\Users\zyadb\MASTER\REORGANIZACION\assets"

# Posiciones de los jugadores del Barcelona
barca_positions = {
    "Wojciech Szczesny": (4, 32.5),
    "Pau Cubarsi": (20, 21),
    "Inigo Martinez": (20, 43),
    "Jules Kounde": (35, 5),
    "Alejandro Balde": (35, 60),
    "Frenkie De Jong": (47, 20),
    "Pedri": (47, 45),
    "Dani Olmo": (66, 32.5),
    "Lamine Yamal": (77, 5),
    "Raphinha": (77, 60),
    "Robert Lewandowski": (85, 32.5),
}

# Función para crear un degradado blaugrana
def create_blaugrana_gradient(ax):
    colors = ['#132976', '#ae1515']
    n_bins = 100
    cm = LinearSegmentedColormap.from_list('blaugrana', colors, N=n_bins)
    gradient = np.linspace(10, 256).reshape(1, -1)
    gradient = np.vstack((gradient, gradient))
    ax.imshow(gradient, aspect='auto', cmap=cm, extent=[-5, 105, -5, 70], alpha=0.8)

# Función para dibujar el campo
def draw_pitch():
    # Reducir el tamaño del campo
    fig, ax = plt.subplots(figsize=(8, 5))
    
    create_blaugrana_gradient(ax)
    
    # Límites del campo
    ax.plot([0, 100, 100, 0, 0], [0, 0, 65, 65, 0], color="white", linewidth=2)
    ax.plot([50, 50], [0, 65], color="white", linewidth=2)

    # Círculo central
    centre_circle = patches.Circle((50, 32.5), 9.15, color="white", fill=False, linewidth=2)
    ax.add_patch(centre_circle)

    # Áreas de penalti
    ax.plot([0, 16.5, 16.5, 0], [20, 20, 45, 45], color="white", linewidth=2)
    ax.plot([100, 83.5, 83.5, 100], [20, 20, 45, 45], color="white", linewidth=2)

    # Áreas pequeñas
    ax.plot([0, 5.5, 5.5, 0], [27, 27, 38, 38], color="white", linewidth=2)
    ax.plot([100, 94.5, 94.5, 100], [27, 27, 38, 38], color="white", linewidth=2)

    # Puntos de penalti
    ax.scatter([11, 89], [32.5, 32.5], color="white", s=30)

    # Arcos de área
    ax.add_patch(patches.Arc((11, 32.5), 20, 20, angle=0, theta1=300, theta2=60, color="white", linewidth=2))
    ax.add_patch(patches.Arc((89, 32.5), 20, 20, angle=0, theta1=120, theta2=240, color="white", linewidth=2))

    # Ajustes visuales
    ax.set_xlim(-5, 105)
    ax.set_ylim(-5, 70)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_frame_on(False)

    # Función para cargar y procesar imagen circular para el campo
    def get_player_image_for_field(player_name):
        try:
            filename = player_name.lower().replace(" ", "_") + ".jpg"
            image_path = os.path.join(ASSETS_BASE_PATH, "imagenes_jugadores_barca", filename)
            
            if not os.path.exists(image_path):
                return None
                
            img = Image.open(image_path)
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Crear imagen circular
            size = (80, 80)
            img = img.resize(size, Image.Resampling.LANCZOS)
            
            mask = Image.new('L', size, 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse((0, 0, size[0], size[1]), fill=255)
            
            output = Image.new('RGB', size, (0, 0, 0))
            output.paste(img, (0, 0))
            output.putalpha(mask)
            
            return output
        except Exception as e:
            return None

    # Añadir jugadores al campo
    for player, (x, y) in barca_positions.items():
        # Cargar imagen del jugador
        player_img = get_player_image_for_field(player)
        
        if player_img:
            # Convertir la imagen de PIL a un formato que matplotlib pueda usar
            player_img_array = np.array(player_img)
            
            # Aumentar significativamente el tamaño de las imágenes
            imagebox = OffsetImage(player_img_array, zoom=0.4)
            ab = AnnotationBbox(imagebox, (x, y + 2),
                              frameon=False,
                              box_alignment=(0.5, 0.5))
            ax.add_artist(ab)
        
        # Solo añadir el nombre del jugador, sin punto
        ax.text(x, y - 5, player, fontsize=8, color="white", ha='center', 
                     fontweight='bold', bbox=dict(facecolor='black', alpha=0.5, edgecolor='none'))
    
    return fig, ax

# Título principal con diseño moderno
st.markdown("""
    <div class="modern-card animate-fade-in">
        <h1 style="color: var(--primary-color); margin-bottom: 0.5rem;">Análisis Propio: FC Barcelona</h1>
        <p style="color: var(--text-color); font-size: 1.2rem;">
            Análisis detallado del estilo de juego y rendimiento del equipo
        </p>
    </div>
""", unsafe_allow_html=True)

# Crear pestañas principales con iconos más grandes
tabs = st.tabs([
    "📊  Panel General  ",
    "⚔️  Análisis Táctico  ",
    "👥  Rendimiento Individual  ",
    "📈  Estadísticas del Equipo  ",
    "🎯  Análisis de Rivales  "
])

# 1. Panel General
with tabs[0]:
    st.markdown("""
        <div class="modern-card">
            <h2>Resumen de Rendimiento</h2>
        </div>
    """, unsafe_allow_html=True)
    
    # Métricas clave
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown("""
            <div class="metric-container">
                <div class="metric-value">65%</div>
                <div class="metric-label">Posesión Media</div>
            </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
            <div class="metric-container">
                <div class="metric-value">88%</div>
                <div class="metric-label">Precisión de Pases</div>
            </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
            <div class="metric-container">
                <div class="metric-value">2.8</div>
                <div class="metric-label">Goles por Partido</div>
            </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown("""
            <div class="metric-container">
                <div class="metric-value">58%</div>
                <div class="metric-label">Duelos Ganados</div>
            </div>
        """, unsafe_allow_html=True)

    # Gráfico de forma reciente
    st.markdown("""
        <div class="chart-container">
            <h3>Forma Reciente</h3>
        </div>
    """, unsafe_allow_html=True)
    
    # Crear datos de ejemplo para la forma reciente
    fechas = pd.date_range(end=datetime.now(), periods=10, freq='D')
    rendimiento = np.random.normal(75, 15, 10)
    rendimiento = np.clip(rendimiento, 0, 100)
    
    fig_forma = go.Figure()
    fig_forma.add_trace(go.Scatter(
        x=fechas,
        y=rendimiento,
        mode='lines+markers',
        name='Rendimiento',
        line=dict(color='#004D98', width=3),
        marker=dict(size=8, color='#A50044')
    ))
    
    fig_forma.update_layout(
        title='Evolución del Rendimiento',
        xaxis_title='Fecha',
        yaxis_title='Índice de Rendimiento',
        template='plotly_white',
        height=400
    )
    
    st.plotly_chart(fig_forma, use_container_width=True)

# 2. Análisis Táctico
with tabs[1]:
    st.markdown("""
        <div class="modern-card">
            <h2>Análisis Táctico del Equipo</h2>
        </div>
    """, unsafe_allow_html=True)
    
    # Subtabs para las fases del juego
    fase_seleccionada = st.radio(
        "Selecciona la fase de juego",
        ["Fase Ofensiva", "Fase Defensiva", "Balón Parado", "Transición Defensiva", "Transición Ofensiva"],
        horizontal=True
    )
    
    if fase_seleccionada == "Fase Ofensiva":
        st.markdown("""
            <div class="chart-container">
                <h3>Métricas Ofensivas</h3>
            </div>
        """, unsafe_allow_html=True)
        
        # Métricas ofensivas
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Posesión", "65%", "+5%")
        with col2:
            st.metric("xG/90", "2.1", "+0.3")
        with col3:
            st.metric("Tiros/90", "15.3", "+2.1")
        with col4:
            st.metric("Pases Completados", "89%", "+3%")
        
        # Gráfico radar ofensivo
        metrics_offensive = ['Posesión', 'xG/90', 'Tiros/90', 'Pases %', 'Centros/90', 'Toques área/90', 'Duelos Of. %', 'Regates/90']
        valores = np.random.uniform(60, 90, len(metrics_offensive))
        
        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(
            r=valores,
            theta=metrics_offensive,
            fill='toself',
            name='Métricas Ofensivas',
            line_color='#004D98'
        ))
        
        fig_radar.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
            showlegend=False,
            height=400
        )
        
        st.plotly_chart(fig_radar, use_container_width=True)
        
    elif fase_seleccionada == "Fase Defensiva":
        st.markdown("""
            <div class="chart-container">
                <h3>Métricas Defensivas</h3>
            </div>
        """, unsafe_allow_html=True)
        
        # Métricas defensivas
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Tiros Concedidos/90", "8.2", "-1.3")
        with col2:
            st.metric("xG Concedido/90", "0.8", "-0.2")
        with col3:
            st.metric("Duelos Def. Ganados", "72%", "+4%")
        with col4:
            st.metric("Intercepciones/90", "12.5", "+1.8")
        
        # Gráfico radar defensivo
        metrics_defensive = ['Tiros Conc./90', 'xG Conc./90', 'Duelos Def. %', 'Interc./90', 'Despejes/90', 'Entradas %', 'Presión %', 'Duelos Aéreos %']
        valores = np.random.uniform(60, 90, len(metrics_defensive))
        
        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(
            r=valores,
            theta=metrics_defensive,
            fill='toself',
            name='Métricas Defensivas',
            line_color='#A50044'
        ))
        
        fig_radar.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
            showlegend=False,
            height=400
        )
        
        st.plotly_chart(fig_radar, use_container_width=True)
        
    elif fase_seleccionada == "Balón Parado":
        st.markdown("""
            <div class="chart-container">
                <h3>Métricas de Balón Parado</h3>
            </div>
        """, unsafe_allow_html=True)
        
        # Métricas de balón parado
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("xG Córners", "0.35", "+0.05")
        with col2:
            st.metric("Goles Córner/90", "0.22", "+0.08")
        with col3:
            st.metric("Eficiencia Penaltis", "85%", "+5%")
        with col4:
            st.metric("Córners Ganados/90", "6.5", "+0.8")
        
        # Gráfico radar balón parado
        metrics_set_pieces = ['xG Córners', 'Goles Córner/90', 'xG Tiros Libres', 'Eficiencia Penaltis', 'Córners Ganados/90']
        valores = np.random.uniform(60, 90, len(metrics_set_pieces))
        
        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(
            r=valores,
            theta=metrics_set_pieces,
            fill='toself',
            name='Balón Parado',
            line_color='#004D98'
        ))
        
        fig_radar.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
            showlegend=False,
            height=400
        )
        
        st.plotly_chart(fig_radar, use_container_width=True)
        
    elif fase_seleccionada == "Transición Defensiva":
        st.markdown("""
            <div class="chart-container">
                <h3>Métricas de Transición Defensiva</h3>
            </div>
        """, unsafe_allow_html=True)
        
        # Métricas de transición defensiva
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Recuperaciones ≤10s", "8.5", "+1.2")
        with col2:
            st.metric("PPDA", "7.8", "-0.5")
        with col3:
            st.metric("Contras Concedidas/90", "2.3", "-0.8")
        with col4:
            st.metric("Tiempo Reacción (s)", "2.8", "-0.3")
        
        # Gráfico radar transición defensiva
        metrics_def_transition = ['Recuperaciones ≤10s', 'Duelos Def. Trans.', 'PPDA', 'Contras Concedidas', 'Tiempo Reacción']
        valores = np.random.uniform(60, 90, len(metrics_def_transition))
        
        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(
            r=valores,
            theta=metrics_def_transition,
            fill='toself',
            name='Transición Defensiva',
            line_color='#A50044'
        ))
        
        fig_radar.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
            showlegend=False,
            height=400
        )
        
        st.plotly_chart(fig_radar, use_container_width=True)
        
    else:  # Transición Ofensiva
        st.markdown("""
            <div class="chart-container">
                <h3>Métricas de Transición Ofensiva</h3>
            </div>
        """, unsafe_allow_html=True)
    
        # Métricas de transición ofensiva
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Contraataques/90", "4.5", "+0.8")
        with col2:
            st.metric("xG Contras", "0.45", "+0.12")
        with col3:
            st.metric("Pases/Contra", "3.2", "+0.3")
        with col4:
            st.metric("Vel. Progresión", "4.2 m/s", "+0.5")
        
        # Gráfico radar transición ofensiva
        metrics_off_transition = ['Contraataques/90', 'xG Contras', 'Pases/Contra', 'Vel. Progresión', 'Eficiencia']
        valores = np.random.uniform(60, 90, len(metrics_off_transition))
        
        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(
            r=valores,
            theta=metrics_off_transition,
            fill='toself',
            name='Transición Ofensiva',
            line_color='#004D98'
        ))
        
        fig_radar.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
            showlegend=False,
            height=400
        )
        
        st.plotly_chart(fig_radar, use_container_width=True)

# 3. Rendimiento Individual
with tabs[2]:
    st.markdown("""
        <div class="modern-card">
            <h2>Análisis de Jugadores</h2>
        </div>
    """, unsafe_allow_html=True)
    
    # Selector de jugadores
    jugadores = list(barca_positions.keys())
    jugador_seleccionado = st.selectbox('Seleccionar Jugador', jugadores)
    
    # Estadísticas del jugador
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
            <div class="chart-container">
                <h3>Estadísticas Clave</h3>
            </div>
        """, unsafe_allow_html=True)
        
        # Gráfico radar de ejemplo
        categorias = ['Pases', 'Tiros', 'Regates', 'Tackles', 'Intercepciones']
        valores = np.random.uniform(60, 90, len(categorias))
        
        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(
            r=valores,
            theta=categorias,
            fill='toself',
            name=jugador_seleccionado
        ))
        
        fig_radar.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
            showlegend=False
        )
        
        st.plotly_chart(fig_radar, use_container_width=True)
    
    with col2:
        st.markdown("""
            <div class="chart-container">
                <h3>Evolución de Rendimiento</h3>
            </div>
        """, unsafe_allow_html=True)
        
        # Gráfico de evolución
        fechas = pd.date_range(end=datetime.now(), periods=10, freq='D')
        rendimiento = np.random.normal(75, 10, 10)
        
        fig_evolucion = go.Figure()
        fig_evolucion.add_trace(go.Scatter(
            x=fechas,
            y=rendimiento,
            mode='lines+markers',
            name='Rendimiento'
        ))
        
        fig_evolucion.update_layout(
            xaxis_title='Fecha',
            yaxis_title='Rendimiento',
            height=300
        )
        
        st.plotly_chart(fig_evolucion, use_container_width=True)

# 4. Estadísticas del Equipo
with tabs[3]:
    st.markdown("""
        <div class="modern-card">
            <h2>Estadísticas Detalladas del Equipo</h2>
        </div>
    """, unsafe_allow_html=True)
    
    # Métricas avanzadas
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
            <div class="metric-container">
                <h3>Ataque</h3>
                <div class="metric-value">2.8</div>
                <div class="metric-label">Goles por partido</div>
                <div class="metric-value">16.5</div>
                <div class="metric-label">Tiros por partido</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
            <div class="metric-container">
                <h3>Posesión</h3>
                <div class="metric-value">65%</div>
                <div class="metric-label">Posesión media</div>
                <div class="metric-value">88%</div>
                <div class="metric-label">Precisión de pases</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
            <div class="metric-container">
                <h3>Defensa</h3>
                <div class="metric-value">0.8</div>
                <div class="metric-label">Goles recibidos por partido</div>
                <div class="metric-value">85%</div>
                <div class="metric-label">Duelos aéreos ganados</div>
            </div>
        """, unsafe_allow_html=True)

    # Gráfico de distribución de goles
    st.markdown("""
        <div class="chart-container">
            <h3>Distribución de Goles</h3>
        </div>
    """, unsafe_allow_html=True)
    
    # Datos de ejemplo para la distribución de goles
    minutos = list(range(0, 91, 15))
    goles = np.random.poisson(lam=2, size=len(minutos)-1)
    
    fig_goles = go.Figure()
    fig_goles.add_trace(go.Bar(
        x=[f"{m}-{m+14}" for m in minutos[:-1]],
        y=goles,
        marker_color='#004D98'
    ))
    
    fig_goles.update_layout(
        xaxis_title='Minutos',
        yaxis_title='Número de Goles',
        height=400
    )
    
    st.plotly_chart(fig_goles, use_container_width=True)

# 5. Análisis de Rivales
with tabs[4]:
    st.markdown("""
        <div class="modern-card">
            <h2>Análisis Comparativo con Rivales</h2>
        </div>
    """, unsafe_allow_html=True)
    
    # Selector de rival
    rivales = ["Real Madrid", "Atlético Madrid", "Bayern Munich", "Manchester City"]
    rival_seleccionado = st.selectbox('Seleccionar Rival', rivales)
    
    # Comparativa de estadísticas
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
            <div class="chart-container">
                <h3>Comparativa de Estadísticas</h3>
            </div>
        """, unsafe_allow_html=True)
    
        # Gráfico de comparación
        metricas = ['Posesión', 'Pases', 'Tiros', 'Presión', 'Duelos']
        barca_stats = np.random.uniform(60, 90, len(metricas))
        rival_stats = np.random.uniform(50, 85, len(metricas))
        
        fig_comp = go.Figure()
        fig_comp.add_trace(go.Bar(
            name='Barcelona',
            x=metricas,
            y=barca_stats,
            marker_color='#004D98'
        ))
        fig_comp.add_trace(go.Bar(
            name=rival_seleccionado,
            x=metricas,
            y=rival_stats,
            marker_color='#DC052D'
        ))
        
        fig_comp.update_layout(
            barmode='group',
            height=400
        )
        
        st.plotly_chart(fig_comp, use_container_width=True)
    
    with col2:
        st.markdown("""
            <div class="chart-container">
                <h3>Historial de Enfrentamientos</h3>
            </div>
        """, unsafe_allow_html=True)

        # Datos de ejemplo para el historial
        fechas = pd.date_range(end=datetime.now(), periods=5, freq='M')
        resultados_barca = np.random.randint(0, 4, 5)
        resultados_rival = np.random.randint(0, 3, 5)
        
        # Crear tabla de resultados
        resultados_df = pd.DataFrame({
            'Fecha': fechas.strftime('%d/%m/%Y'),
            'Barcelona': resultados_barca,
            rival_seleccionado: resultados_rival
        })
        
        st.table(resultados_df)
