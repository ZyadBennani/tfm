import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from PIL import Image
from matplotlib.colors import LinearSegmentedColormap
import io

# Cargar datos del CSV
@st.cache_data
def load_player_data():
    return pd.read_csv('Datos/radares_normalizados.csv', sep=';')

# Función para obtener métricas de un jugador
def get_player_metrics(df, player_name, team):
    try:
        player_data = df[(df['Jugador'].str.strip() == player_name) & 
                        (df['Equipo'] == team)]
        
        if len(player_data) == 0:
            st.error(f"No se encontraron datos para {player_name} en {team}")
            return None
            
        player_data = player_data.iloc[0]
        metrics = {}
        for i in range(1, 10):  # 9 métricas posibles
            metric_name = player_data[f'Metrica {i}']
            metric_value = player_data[f'Valor Normalizado {i}']
            if pd.notna(metric_name) and pd.notna(metric_value):
                try:
                    # Convert to float and ensure value is between 0 and 100
                    value = float(str(metric_value).replace(',', '.'))
                    value = max(0, min(100, value))  # Clamp value between 0 and 100
                    metrics[metric_name] = value
                except:
                    continue
        return metrics
    except Exception as e:
        st.error(f"Error al obtener métricas para {player_name}: {str(e)}")
        return None

# Definición de jugadores y posiciones
barca_players = [
    "Wojciech Szczesny",      # GK
    "Inigo Martinez", "Pau Cubarsi",  # CB-L, CB-R
    "Alejandro Balde",            # LB
    "Jules Kounde",               # RB
    "Frenkie De Jong",            # DM
    "Pedri",                      # CM
    "Dani Olmo",                  # AM
    "Raphinha", "Lamine Yamal",   # Wingers
    "Robert Lewandowski"          # ST
]

bayern_players = [
    "Manuel Neuer",               # GK
    "David Alaba", "Jerome Boateng",  # CB-L, CB-R
    "Alphonso Davies",            # LB
    "Benjamin Pavard",            # RB
    "Joshua Kimmich",             # DM
    "Leon Goretzka",              # CM
    "Thomas Muller",              # AM
    "Kingsley Coman", "Serge Gnabry", # Wingers
    "Robert Lewandowski"          # ST
]

positions = [
    "GK", "CB-L", "CB-R", "LB", "RB", "DM", "CM", "AM", "LW", "RW", "ST"
]

# Posiciones de los jugadores
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

bayern_positions = {
    "Manuel Neuer": (4, 32.5),
    "David Alaba": (20, 21),
    "Jerome Boateng": (20, 43),
    "Benjamin Pavard": (35, 5),
    "Alphonso Davies": (35, 60),
    "Joshua Kimmich": (47, 20),
    "Leon Goretzka": (47, 45),
    "Thomas Muller": (66, 32.5),
    "Serge Gnabry": (77, 5),
    "Kingsley Coman": (77, 60),
    "Robert Lewandowski": (85, 32.5),
}

# Función para crear gráfico radar
def create_radar_chart(barca_player: str, bayern_player: str, position: str, chart_id: str = None):
    df = load_player_data()
    
    try:
        # Obtener métricas reales
        metrics_barca = get_player_metrics(df, barca_player, 'Barcelona')
        metrics_bayern = get_player_metrics(df, bayern_player, 'Bayern')
        
        if not metrics_barca or not metrics_bayern:
            st.error(f"No se pudieron obtener métricas para la comparación {barca_player} vs {bayern_player}")
            st.write("Datos disponibles en el CSV:")
            st.write(df[['Jugador', 'Equipo']].to_dict('records'))
            return None
            
        categories = list(metrics_barca.keys())
        
        fig = go.Figure()
        
        # Datos Barcelona
        fig.add_trace(go.Scatterpolar(
            r=list(metrics_barca.values()),
            theta=categories,
            fill='toself',
            name=barca_player,
            line_color='#004D98',  # Azul Barça
            fillcolor='rgba(0, 77, 152, 0.3)'
        ))
        
        # Datos Bayern
        fig.add_trace(go.Scatterpolar(
            r=list(metrics_bayern.values()),
            theta=categories,
            fill='toself',
            name=bayern_player,
            line_color='#DC052D',  # Rojo Bayern
            fillcolor='rgba(220, 5, 45, 0.3)'
        ))
        
        # Actualizar layout
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100]  # Fijamos el rango máximo a 100 para todos los gráficos
                )
            ),
            showlegend=True,
            title=f"{position}: {barca_player} vs {bayern_player}",
            height=400,
            polar_angularaxis_rotation=90  # Rotar las etiquetas para mejor legibilidad
        )
        
        return fig
    except Exception as e:
        st.error(f"Error al crear el gráfico para {barca_player} vs {bayern_player}: {str(e)}")
        return None

# Función para crear un degradado blaugrana
def create_blaugrana_gradient(ax):
    colors = ['#132976', '#ae1515']
    n_bins = 100
    cm = LinearSegmentedColormap.from_list('blaugrana', colors, N=n_bins)
    gradient = np.linspace(10, 256).reshape(1, -1)
    gradient = np.vstack((gradient, gradient))
    ax.imshow(gradient, aspect='auto', cmap=cm, extent=[-5, 105, -5, 70], alpha=0.8)

# Función para crear un degradado del Bayern
def create_bayern_gradient(ax):
    colors = ['#DC052D', '#8B0000']  # Rojo Bayern
    n_bins = 100
    cm = LinearSegmentedColormap.from_list('bayern', colors, N=n_bins)
    gradient = np.linspace(10, 256).reshape(1, -1)
    gradient = np.vstack((gradient, gradient))
    ax.imshow(gradient, aspect='auto', cmap=cm, extent=[-5, 105, -5, 70], alpha=0.8)

# Función para dibujar el campo
def draw_pitch(team="barcelona"):
    # Reducir el tamaño del campo
    fig, ax = plt.subplots(figsize=(8, 5))
    
    if team == "barcelona":
        create_blaugrana_gradient(ax)
    else:
        create_bayern_gradient(ax)
    
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

    return fig, ax

# Configuración de la página
st.set_page_config(page_title="Análisis del FC Barcelona", page_icon="⚽", layout="wide")

# Título
st.title("Análisis Comparativo: FC Barcelona vs Bayern Munich")

# Métricas generales en una fila
with st.container():
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="Posesión Media", value="65%", delta="5%")
    with col2:
        st.metric(label="Precisión de Pases", value="88%", delta="3%")
    with col3:
        st.metric(label="Duelos Ganados", value="58%", delta="-2%")

# Campogramas y estadísticas
st.markdown("### Alineaciones y Formaciones")
col1_campo, col2_stats, col3_campo = st.columns([2, 1, 2])

with col1_campo:
    # Campograma Barça
    fig_barca, ax_barca = draw_pitch("barcelona")
    for player, (x, y) in barca_positions.items():
        ax_barca.text(x, y, "●", fontsize=20, color="white", ha='center', va='center')
        ax_barca.text(x, y - 5, player, fontsize=8, color="white", ha='center', 
                     fontweight='bold', bbox=dict(facecolor='black', alpha=0.5, edgecolor='none'))
    
    buf = io.BytesIO()
    fig_barca.savefig(buf, format='png', bbox_inches='tight', transparent=True)
    buf.seek(0)
    st.image(buf, use_container_width=True)
    plt.close(fig_barca)

with col2_stats:
    st.markdown("### Formación")
    formation = st.selectbox("Seleccionar formación", ["4-2-3-1", "4-3-3", "3-5-2"])
    st.markdown("### Estadísticas del Equipo")
    st.metric("Goles marcados", "45", "+5")
    st.metric("Goles recibidos", "15", "-3")
    st.metric("Victorias", "18", "+2")

with col3_campo:
    # Campograma Bayern
    fig_bayern, ax_bayern = draw_pitch("bayern")
    for player, (x, y) in bayern_positions.items():
        ax_bayern.text(x, y, "●", fontsize=20, color="white", ha='center', va='center')
        ax_bayern.text(x, y - 5, player, fontsize=8, color="white", ha='center', 
                      fontweight='bold', bbox=dict(facecolor='black', alpha=0.5, edgecolor='none'))
    
    buf = io.BytesIO()
    fig_bayern.savefig(buf, format='png', bbox_inches='tight', transparent=True)
    buf.seek(0)
    st.image(buf, use_container_width=True)
    plt.close(fig_bayern)

# Definición de las comparaciones
comparisons = [
    ("GK", "Wojciech Szczesny", "Manuel Neuer"),
    ("CB-L", "Inigo Martinez", "David Alaba"),
    ("CB-R", "Pau Cubarsi", "Jerome Boateng"),
    ("LB", "Alejandro Balde", "Alphonso Davies"),
    ("RB", "Jules Kounde", "Benjamin Pavard"),
    ("CDM", "Frenkie De Jong", "Joshua Kimmich"),
    ("CM", "Pedri", "Leon Goretzka"),
    ("CAM", "Dani Olmo", "Thomas Muller"),
    ("LW", "Raphinha", "Kingsley Coman"),
    ("RW", "Lamine Yamal", "Serge Gnabry"),
    ("ST", "Robert Lewandowski", "Robert Lewandowski"),
]

# Comparaciones Individuales
st.markdown("### Comparaciones Individuales")

# Iterar sobre las comparaciones definidas
for pos, barca_player, bayern_player in comparisons:
    # Crear columnas para cada comparación
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        st.markdown(f"### {barca_player}")
        st.markdown("🔵🔴 FC Barcelona")
        
    with col2:
        try:
            fig = create_radar_chart(barca_player, bayern_player, pos)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Error al crear el gráfico radar: {str(e)}")
        
    with col3:
        st.markdown(f"### {bayern_player}")
        st.markdown("🔴⚪ Bayern Munich")
    
    st.divider()
