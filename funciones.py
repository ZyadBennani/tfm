import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.colors import LinearSegmentedColormap

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
    "Inigo Martinez", "Pau Cubarsi",  # CBL, CBR
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
    "David Alaba", "Jerome Boateng",  # CBL, CBR
    "Alphonso Davies",            # LB
    "Benjamin Pavard",            # RB
    "Joshua Kimmich",             # DM
    "Leon Goretzka",              # CM
    "Thomas Muller",              # AM
    "Kingsley Coman", "Serge Gnabry", # Wingers
    "Robert Lewandowski"          # ST
]

positions = [
    "GK", "CBL", "CBR", "LB", "RB", "DM", "CM", "AM", "LW", "RW", "ST"
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