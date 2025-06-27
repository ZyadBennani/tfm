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
import os
import base64
from PIL import ImageDraw
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.data_loader import DataLoader
from utils.rating_calculator import RatingCalculator

# Importar funciones de navegación
sys.path.append('..')
from utils.navigation import show_home_button, show_page_header, show_navbar_switch_page

# Configuración de la página
st.set_page_config(
    page_title="Plantilla",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="collapsed"
)
st.markdown("""
    <style>
    /* Estilo especial para la métrica de valor de mercado */
    div[data-testid="metric-container"] {
        background-color: #f0f2f6;
        border: 1px solid #e1e5e9;
        padding: 0.5rem;
        border-radius: 0.5rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    
    /* Resaltar la métrica de valor total */
    div[data-testid="metric-container"]:last-child {
        background: linear-gradient(45deg, #004d98, #a50044);
        color: white;
        border: 2px solid #004d98;
    }
    
    div[data-testid="metric-container"]:last-child [data-testid="metric-container"] > div > div {
        color: white !important;
    }
    
    /* Tarjetas de jugadores (copiado de Scouting) */
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
    </style>
""", unsafe_allow_html=True)
show_home_button()
show_page_header("Plantilla")

# Definición completa de la plantilla del Barça organizada por posiciones
barca_full_squad = {
    # Porteros
    "Porteros": [
        "Wojciech Szczesny",
        "Lucas Chevalier",
        "Inaki Pena"
    ],
    
    # Defensas
    "Defensas": [
        "Ronald Araujo",
        "Pau Cubarsi",
        "Inigo Martinez",
        "Andreas Christensen",
        "Jules Kounde",
        "Eric Garcia",
        "Alejandro Balde",
        "Gerard Martin",
        "Hector Fort",
        "Juanlu Sanchez"
    ],
    
    # Centrocampistas
    "Centrocampistas": [
        "Frenkie de Jong",
        "Pedri",
        "Gavi",
        "Dani Olmo",
        "Marc Casado",
        "Fermin Lopez",
        "Pablo Torre"
    ],
    
    # Delanteros
    "Delanteros": [
        "Robert Lewandowski",
        "Raphinha",
        "Lamine Yamal",
        "Ferran Torres",
        "Nico Williams",
        "Ivan Perisic"
    ]
}

# Posiciones específicas para el campograma (coordenadas exactas)
barca_positions_campograma = {
    "Lucas Chevalier": (4, 31.5),  # Reemplaza a Ter Stegen
    "Wojciech Szczesny": (4, 19.5),
    "Inaki Pena": (4, 45),
    "Juanlu Sanchez": (35, 5),      # Reemplaza a Hector Fort
    "Nico Williams": (77, 60),     # Reemplaza a Ronald Araujo
    "Pau Cubarsi": (20, 26),
    "Andreas Christensen": (20, 48),
    "Inigo Martinez": (20, 37),
    "Jules Kounde": (48, 5),
    "Eric Garcia": (20, 15),
    "Gerard Martin": (35, 60),
    "Alejandro Balde": (48, 60),
    "Marc Casado": (39, 20),
    "Pedri": (49, 45),
    "Frenkie de Jong": (39, 45),
    "Gavi": (49, 20),
    "Dani Olmo": (90, 25),
    "Fermin Lopez": (70, 43.5),
    "Pablo Torre": (70, 21.5),
    "Lamine Yamal": (77, 5),
    "Ferran Torres": (65, 5),
    "Raphinha": (70, 32.5),
    "Ivan Perisic": (65, 60),  # Nuevo fichaje, extremo izquierdo
    "Robert Lewandowski": (90, 40),
    # Pau Victor eliminado
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
def draw_pitch_barca():
    fig, ax = plt.subplots(figsize=(12, 7))
    
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
            # Usar ruta especial para los nuevos jugadores
            nuevos_jugadores = {
                "Juanlu Sanchez": r"C:/Users/zyadb/Documents/tfm/static/wetransfer_players_2025-06-18_1752/Players/Juanlu Sanchez.png",
                "Nico Williams": r"C:/Users/zyadb/Documents/tfm/static/wetransfer_players_2025-06-18_1752/Players/Nico Williams.png",
                "Lucas Chevalier": r"C:/Users/zyadb/Documents/tfm/static/wetransfer_players_2025-06-18_1752/Players/Lucas Chevalier.png",
                "Ivan Perisic": r"C:/Users/zyadb/Documents/tfm/static/wetransfer_players_2025-06-18_1752/Players/Ivan Perišić.png"
            }
            if player_name in nuevos_jugadores:
                image_path = nuevos_jugadores[player_name]
            elif player_name == "Robert Lewandowski":
                image_path = os.path.join("static", "wetransfer_players_2025-06-18_1752", "Players", "Robert Lewandowski.png")
                if not os.path.exists(image_path):
                    filename = player_name.lower().replace(" ", "_") + ".png"
                    image_path = os.path.join("static", "players", "Barca", filename)
            else:
                filename = player_name.lower().replace(" ", "_") + ".png"
                image_path = os.path.join("static", "players", "Barca", filename)
            if not os.path.exists(image_path):
                return None
            img = Image.open(image_path)
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Definir colores de borde por posición y destacar nuevos fichajes
            nuevos_fichajes = [
                "Nico Williams",
                "Lucas Chevalier",
                "Juanlu Sanchez",
                "Ivan Perisic"
            ]
            position_colors = {
                # GK - Amarillo
                "Lucas Chevalier": "#FFD700",
                "Wojciech Szczesny": "#FFD700", 
                "Inaki Pena": "#FFD700",
                # DC - Azul
                "Nico Williams": "#00FFD0",  # Color especial para destacar
                "Pau Cubarsi": "#0066FF",
                "Andreas Christensen": "#0066FF",
                "Inigo Martinez": "#0066FF",
                "Eric Garcia": "#0066FF",
                # Laterales - Verde
                "Juanlu Sanchez": "#FF00FF",  # Color especial para destacar
                "Jules Kounde": "#00CC66",
                "Gerard Martin": "#00CC66",
                "Alejandro Balde": "#00CC66",
                # CM - Blanco
                "Marc Casado": "#FFFFFF",
                "Pedri": "#FFFFFF",
                "Frenkie de Jong": "#FFFFFF",
                "Gavi": "#FFFFFF",
                # CAM - Naranja
                "Dani Olmo": "#FF6600",
                "Fermin Lopez": "#FF6600",
                "Pablo Torre": "#FF6600",
                # Extremos - Morado
                "Lamine Yamal": "#9966FF",
                "Ferran Torres": "#9966FF",
                "Raphinha": "#9966FF",
                "Ivan Perisic": "#9966FF",
                # ST - Rojo
                "Robert Lewandowski": "#FF3333",
            }
            # Si es nuevo fichaje, usar borde con degradado blaugrana
            if player_name in nuevos_fichajes:
                border_width = 8  # Más grueso
                size = (100, 100)
                border_img = Image.new('RGBA', size, (0, 0, 0, 0))
                draw = ImageDraw.Draw(border_img)
                center = (size[0] // 2, size[1] // 2)
                max_radius = size[0] // 2
                # Borde angular: mitad azul, mitad granate
                for angle in range(360):
                    # De 0 a 179: azul, de 180 a 359: granate
                    if angle < 180:
                        color = (0x13, 0x29, 0x76, 255)  # Azul
                    else:
                        color = (0xae, 0x15, 0x15, 255)  # Granate
                    # Coordenadas polares a cartesianas
                    for r in range(max_radius, max_radius - border_width, -1):
                        x = int(center[0] + r * np.cos(np.deg2rad(angle)))
                        y = int(center[1] + r * np.sin(np.deg2rad(angle)))
                        if 0 <= x < size[0] and 0 <= y < size[1]:
                            border_img.putpixel((x, y), color)
                # Crear máscara circular para la imagen del jugador
                mask = Image.new('L', (size[0] - border_width*2, size[1] - border_width*2), 0)
                draw_mask = ImageDraw.Draw(mask)
                draw_mask.ellipse([0, 0, size[0] - border_width*2, size[1] - border_width*2], fill=255)
                img = img.resize((size[0] - border_width*2, size[1] - border_width*2), Image.Resampling.LANCZOS)
                img.putalpha(mask)
                border_img.paste(img, (border_width, border_width), img)
                output = border_img
            else:
                # Borde blanco para todos los demás jugadores
                border_color = "#FFFFFF"
                border_width = 4
                size = (100, 100)
                img = img.resize((size[0] - border_width*2, size[1] - border_width*2), Image.Resampling.LANCZOS)
                output = Image.new('RGBA', size, (0, 0, 0, 0))
                draw = ImageDraw.Draw(output)
                draw.ellipse([0, 0, size[0], size[1]], fill=border_color)
                mask = Image.new('L', (size[0] - border_width*2, size[1] - border_width*2), 0)
                draw_mask = ImageDraw.Draw(mask)
                draw_mask.ellipse([0, 0, size[0] - border_width*2, size[1] - border_width*2], fill=255)
                img.putalpha(mask)
                output.paste(img, (border_width, border_width), img)
            return output
        except Exception as e:
            return None

    # Añadir jugadores al campo
    for player, (x, y) in barca_positions_campograma.items():
        # Tamaño especial para nuevos fichajes
        nuevos_fichajes = [
            "Nico Williams",
            "Lucas Chevalier",
            "Juanlu Sanchez",
            "Ivan Perisic"
        ]
        if player in nuevos_fichajes:
            zoom = 0.6  # Más grande
        else:
            zoom = 0.4
        player_img = get_player_image_for_field(player)
        if player_img:
            player_img_array = np.array(player_img)
            imagebox = OffsetImage(player_img_array, zoom=zoom)
            ab = AnnotationBbox(imagebox, (x, y + 2), frameon=False, box_alignment=(0.5, 0.5))
            ax.add_artist(ab)
        ax.text(x, y - 3.5, player, fontsize=8, color="white", ha='center', fontweight='bold', bbox=dict(facecolor='black', alpha=0.6, edgecolor='none'))

    return fig, ax

# Función para obtener imagen circular del jugador
def get_circular_player_image(player_name):
    try:
        filename = player_name.lower().replace(" ", "_") + ".png"
        image_path = os.path.join("static", "players", "Barca", filename)
        
        if not os.path.exists(image_path):
            return None
            
        img = Image.open(image_path)
        
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        size = (200, 200)
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


# Datos calculados de la plantilla actual
player_ages = {
    "Wojciech Szczesny": 34, "Inaki Pena": 25, "Lucas Chevalier": 22,
    "Nico Williams": 21, "Pau Cubarsi": 17, "Andreas Christensen": 28, 
    "Inigo Martinez": 33, "Eric Garcia": 24, "Jules Kounde": 26,
    "Gerard Martin": 22, "Alejandro Balde": 21, "Juanlu Sanchez": 20,
    "Marc Casado": 21, "Pedri": 22, "Frenkie de Jong": 27, "Gavi": 20,
    "Dani Olmo": 26, "Fermin Lopez": 21, "Pablo Torre": 21,
    "Lamine Yamal": 17, "Ferran Torres": 24, "Raphinha": 27,
    "Robert Lewandowski": 36, "Ivan Perisic": 35
}

# Valores de mercado actuales de la plantilla (en millones de euros)
player_market_values = {
    "Wojciech Szczesny": 3, "Inaki Pena": 8, "Lucas Chevalier": 25,
    "Nico Williams": 60, "Pau Cubarsi": 25, "Andreas Christensen": 35, 
    "Inigo Martinez": 20, "Eric Garcia": 15, "Jules Kounde": 55,
    "Gerard Martin": 3, "Alejandro Balde": 50, "Juanlu Sanchez": 5,
    "Marc Casado": 10, "Pedri": 80, "Frenkie de Jong": 60, "Gavi": 60,
    "Dani Olmo": 60, "Fermin Lopez": 25, "Pablo Torre": 15,
    "Lamine Yamal": 180, "Ferran Torres": 40, "Raphinha": 55,
    "Robert Lewandowski": 15, "Ivan Perisic": 2
}

# Calcular estadísticas
all_players = list(player_ages.keys())
total_players = len(all_players)
average_age = sum(player_ages.values()) / total_players

# Calcular jugadores internacionales (estimación basada en jugadores conocidos)
international_players = [
    "Wojciech Szczesny", "Andreas Christensen",
    "Inigo Martinez", "Jules Kounde", "Alejandro Balde", "Pedri", "Frenkie de Jong", 
    "Gavi", "Dani Olmo", "Lamine Yamal", "Ferran Torres", "Raphinha",
    "Robert Lewandowski", "Nico Williams", "Ivan Perisic"
]
international_percentage = (len(international_players) / total_players) * 100

# Jugadores de la cantera (estimación)
cantera_players = ["Pau Cubarsi", "Gerard Martin", "Alejandro Balde", 
                   "Marc Casado", "Pedri", "Gavi", "Fermin Lopez", "Pablo Torre", 
                   "Lamine Yamal"]
cantera_percentage = (len(cantera_players) / total_players) * 100

# Jugadores jóvenes (sub-23)
young_players = [name for name, age in player_ages.items() if age < 23]
young_percentage = (len(young_players) / total_players) * 100

# Calcular valor total de mercado
total_market_value = 944  # Valor fijo
market_value_increase = 0  # Sin aumento

# Datos de la temporada pasada (2023-24) para comparación
previous_season_data = {
    "average_age": 24.5,
    "international_percentage": 64,  # porcentaje
    "cantera_percentage": 48,        # porcentaje
    "young_percentage": 44,          # porcentaje
    "market_value": 944              # millones de euros
}

# Calcular diferencias con la temporada pasada
age_difference = average_age - previous_season_data["average_age"]
international_difference = international_percentage - previous_season_data["international_percentage"]
cantera_difference = cantera_percentage - previous_season_data["cantera_percentage"]
young_difference = young_percentage - previous_season_data["young_percentage"]


# Helper para obtener foto del jugador (copiado de scouting)
@st.cache_resource
def get_photo_manager_barca():
    from utils.player_photo_manager import PlayerPhotoManager
    return PlayerPhotoManager()




# Campograma principal
col_legend, col_campo = st.columns([1, 4])

# Mostrar estadísticas alineadas con el campograma
with col_campo:
    # Las métricas van dentro de la misma columna que el campograma
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric(
            label="Edad Media", 
            value=f"{average_age:.1f} años",
            delta=f"{age_difference:+.1f} años"
        )

    with col2:
        st.metric(
            label="Internacionales", 
            value=f"{international_percentage:.0f}%",
            delta=f"{international_difference:+.0f}%"
        )

    with col3:
        st.metric(
            label="Canteranos", 
            value=f"{cantera_percentage:.0f}%",
            delta=f"{cantera_difference:+.0f}%"
        )

    with col4:
        st.metric(
            label="Sub-23", 
            value=f"{young_percentage:.0f}%",
            delta=f"{young_difference:+.0f}%"
        )

    with col5:
        st.metric(
            label="Valor Total", 
            value=f"€{total_market_value}M",
            delta=f"0%",
            delta_color="off"
        )
    
    # Generar el campograma dentro de la misma columna
    fig_barca, ax_barca = draw_pitch_barca()
    
    # Mostrar el campograma
    buf = io.BytesIO()
    fig_barca.savefig(buf, format='png', bbox_inches='tight', transparent=True, dpi=150)
    buf.seek(0)
    st.image(buf, use_container_width=True)
    plt.close(fig_barca)
