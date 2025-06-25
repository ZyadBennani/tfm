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
st.set_page_config(page_title="Campograma FC Barcelona", page_icon="🔵🔴", layout="wide")

# Mostrar botón de volver al inicio
show_home_button()

# Mostrar header de la página
show_page_header("Plantilla FC Barcelona 2024-2025")

# ... existing code ...

show_navbar_switch_page()

# CSS personalizado para las métricas y player cards
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


# Definición completa de la plantilla del Barça organizada por posiciones
barca_full_squad = {
    # Porteros
    "Porteros": [
        "Marc Andre ter Stegen",
        "Wojciech Szczesny", 
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
        "Hector Fort"
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
        "Ansu Fati",
        "Ferran Torres",
        "Pau Victor"
    ]
}

# Posiciones específicas para el campograma (coordenadas exactas)
barca_positions_campograma = {
    "Marc Andre ter Stegen": (4, 32.5),
    "Wojciech Szczesny": (4, 21.5),
    "Inaki Pena": (4, 43),
    "Ronald Araujo": (20, 21),
    "Pau Cubarsi": (20, 32),
    "Andreas Christensen": (20, 43),
    "Inigo Martinez": (20, 54),
    "Jules Kounde": (48, 5),
    "Eric Garcia": (20, 10),
    "Hector Fort": (35, 5),
    "Gerard Martin": (35, 60), 
    "Alejandro Balde": (48, 60),
    "Marc Casado": (39, 20),
    "Pedri": (49, 45),
    "Frenkie de Jong": (39, 45),
    "Gavi": (49, 20),
    "Dani Olmo": (70, 43.5),
    "Fermin Lopez": (70, 32.5),
    "Pablo Torre": (70, 21.5),
    "Lamine Yamal": (77, 5),
    "Ferran Torres": (65, 5),
    "Raphinha": (77, 60),
    "Ansu Fati": (65, 60),
    "Robert Lewandowski": (95, 40),
    "Pau Victor": (95, 25),
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
            if player_name == "Robert Lewandowski":
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
            
            # Definir colores de borde por posición
            position_colors = {
                # GK - Amarillo
                "Marc Andre ter Stegen": "#FFD700",
                "Wojciech Szczesny": "#FFD700", 
                "Inaki Pena": "#FFD700",
                
                # DC - Azul
                "Ronald Araujo": "#0066FF",
                "Pau Cubarsi": "#0066FF",
                "Andreas Christensen": "#0066FF",
                "Inigo Martinez": "#0066FF",
                "Eric Garcia": "#0066FF",
                
                # Laterales - Verde
                "Jules Kounde": "#00CC66",
                "Hector Fort": "#00CC66",
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
                "Ansu Fati": "#9966FF",
                
                # ST - Rojo
                "Robert Lewandowski": "#FF3333",
                "Pau Victor": "#FF3333",
            }
            
            # Crear imagen circular con borde de color
            size = (100, 100)
            border_width = 4
            
            # Redimensionar imagen
            img = img.resize((size[0] - border_width*2, size[1] - border_width*2), Image.Resampling.LANCZOS)
            
            # Crear imagen final con borde
            output = Image.new('RGBA', size, (0, 0, 0, 0))
            draw = ImageDraw.Draw(output)
            
            # Dibujar borde de color
            border_color = position_colors.get(player_name, "#FFFFFF")
            draw.ellipse([0, 0, size[0], size[1]], fill=border_color)
            
            # Crear máscara circular para la imagen del jugador
            mask = Image.new('L', (size[0] - border_width*2, size[1] - border_width*2), 0)
            draw_mask = ImageDraw.Draw(mask)
            draw_mask.ellipse([0, 0, size[0] - border_width*2, size[1] - border_width*2], fill=255)
            
            # Aplicar máscara a la imagen del jugador
            img.putalpha(mask)
            
            # Pegar la imagen del jugador en el centro (con el borde)
            output.paste(img, (border_width, border_width), img)
            
            return output
        except Exception as e:
            return None

    # Añadir jugadores al campo
    for player, (x, y) in barca_positions_campograma.items():
        # Cargar imagen del jugador
        player_img = get_player_image_for_field(player)
        
        if player_img:
            # Convertir la imagen de PIL a un formato que matplotlib pueda usar
            player_img_array = np.array(player_img)
            
            # Tamaño uniforme para todos los jugadores
            zoom = 0.4  # Mismo tamaño para todos
                
            imagebox = OffsetImage(player_img_array, zoom=zoom)
            ab = AnnotationBbox(imagebox, (x, y + 2),
                              frameon=False,
                              box_alignment=(0.5, 0.5))
            ax.add_artist(ab)
        
        # Añadir nombre del jugador
        ax.text(x, y - 3.5, player, fontsize=8, color="white", ha='center', 
                fontweight='bold', bbox=dict(facecolor='black', alpha=0.6, edgecolor='none'))

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
    "Marc Andre ter Stegen": 32, "Wojciech Szczesny": 34, "Inaki Pena": 25,
    "Ronald Araujo": 25, "Pau Cubarsi": 17, "Andreas Christensen": 28, 
    "Inigo Martinez": 33, "Eric Garcia": 24, "Jules Kounde": 26,
    "Hector Fort": 18, "Gerard Martin": 22, "Alejandro Balde": 21,
    "Marc Casado": 21, "Pedri": 22, "Frenkie de Jong": 27, "Gavi": 20,
    "Dani Olmo": 26, "Fermin Lopez": 21, "Pablo Torre": 21,
    "Lamine Yamal": 17, "Ferran Torres": 24, "Raphinha": 27, "Ansu Fati": 22,
    "Robert Lewandowski": 36, "Pau Victor": 23
}

# Valores de mercado actuales de la plantilla (en millones de euros)
player_market_values = {
    "Marc Andre ter Stegen": 25, "Wojciech Szczesny": 3, "Inaki Pena": 8,
    "Ronald Araujo": 70, "Pau Cubarsi": 25, "Andreas Christensen": 35, 
    "Inigo Martinez": 20, "Eric Garcia": 15, "Jules Kounde": 55,
    "Hector Fort": 5, "Gerard Martin": 3, "Alejandro Balde": 50,
    "Marc Casado": 10, "Pedri": 80, "Frenkie de Jong": 60, "Gavi": 60,
    "Dani Olmo": 60, "Fermin Lopez": 25, "Pablo Torre": 15,
    "Lamine Yamal": 180, "Ferran Torres": 40, "Raphinha": 55, "Ansu Fati": 25,
    "Robert Lewandowski": 15, "Pau Victor": 5
}

# Calcular estadísticas
all_players = list(player_ages.keys())
total_players = len(all_players)
average_age = sum(player_ages.values()) / total_players

# Calcular jugadores internacionales (estimación basada en jugadores conocidos)
international_players = [
    "Marc Andre ter Stegen", "Wojciech Szczesny", "Ronald Araujo", "Andreas Christensen",
    "Inigo Martinez", "Jules Kounde", "Alejandro Balde", "Pedri", "Frenkie de Jong", 
    "Gavi", "Dani Olmo", "Lamine Yamal", "Ferran Torres", "Raphinha", "Ansu Fati",
    "Robert Lewandowski"
]
international_percentage = (len(international_players) / total_players) * 100

# Jugadores de la cantera (estimación)
cantera_players = ["Pau Cubarsi", "Hector Fort", "Gerard Martin", "Alejandro Balde", 
                   "Marc Casado", "Pedri", "Gavi", "Fermin Lopez", "Pablo Torre", 
                   "Lamine Yamal", "Ansu Fati", "Pau Victor"]
cantera_percentage = (len(cantera_players) / total_players) * 100

# Jugadores jóvenes (sub-23)
young_players = [name for name, age in player_ages.items() if age < 23]
young_percentage = (len(young_players) / total_players) * 100

# Calcular valor total de mercado
total_market_value = sum(player_market_values.values())
market_value_increase = 190  # Millones de euros de aumento

# Datos de la temporada pasada (2023-24) para comparación
previous_season_data = {
    "average_age": 25.2,
    "international_percentage": 58,  # 15 de 26 jugadores
    "cantera_percentage": 26,  # 7 de 27 según la foto oficial
    "young_percentage": 27  # 7 de 26 jugadores ≤ 23 años
}

# Calcular diferencias con la temporada pasada
age_difference = average_age - previous_season_data["average_age"]
international_difference = international_percentage - previous_season_data["international_percentage"]
cantera_difference = cantera_percentage - previous_season_data["cantera_percentage"]
young_difference = young_percentage - previous_season_data["young_percentage"]

# Función para color del rating (igual que en scouting)
def get_rating_color(rating):
    if rating >= 85:
        return "#22c55e"  # Verde
    elif rating >= 75:
        return "#f59e0b"  # Amarillo
    elif rating >= 65:
        return "#ef4444"  # Rojo
    else:
        return "#6b7280"  # Gris

# Cargar datos y calcular ratings de los jugadores del Barça
@st.cache_data
def get_barca_player_ratings():
    try:
        # Cargar datos
        data_loader = DataLoader()
        all_players_df = data_loader.load_all_data()
        
        # Calcular ratings
        rating_calculator = RatingCalculator()
        all_players_df = rating_calculator.bulk_calculate_ratings(all_players_df)
        
        # Filtrar jugadores del Barça
        barca_players = all_players_df[all_players_df['Club'] == 'Barcelona'].copy()
        
        # Crear diccionario de ratings
        player_ratings = {}
        for _, player in barca_players.iterrows():
            name = player['Name']
            rating = player.get('Display_Rating', player.get('Calculated_Rating', player.get('Rating', 75)))
            player_ratings[name] = int(rating)
        
        return player_ratings
    except Exception as e:
        # Ratings por defecto si hay error
        return {
            "Marc Andre ter Stegen": 85, "Wojciech Szczesny": 82, "Inaki Pena": 75,
            "Ronald Araujo": 84, "Pau Cubarsi": 78, "Andreas Christensen": 83, 
            "Inigo Martinez": 80, "Eric Garcia": 76, "Jules Kounde": 85,
            "Hector Fort": 72, "Gerard Martin": 70, "Alejandro Balde": 81,
            "Marc Casado": 76, "Pedri": 89, "Frenkie de Jong": 86, "Gavi": 85,
            "Dani Olmo": 87, "Fermin Lopez": 79, "Pablo Torre": 75,
            "Lamine Yamal": 88, "Ferran Torres": 82, "Raphinha": 84, "Ansu Fati": 80,
            "Robert Lewandowski": 88, "Pau Victor": 74
        }

# Obtener ratings de los jugadores
player_ratings = get_barca_player_ratings()

# Helper para obtener foto del jugador (copiado de scouting)
@st.cache_resource
def get_photo_manager_barca():
    from utils.player_photo_manager import PlayerPhotoManager
    return PlayerPhotoManager()

# Diccionario de perfiles español → inglés
perfiles_es_en = {
    # GK
    "Portero líbero": "SWEEPER",
    "Portero de línea": "LINE KEEPER",
    "Portero tradicional": "TRADITIONAL",
    # Fullbacks (LB-RB)
    "Defensivo": "DEFENSIVE",
    "Progresivo": "PROGRESSIVE",
    "Ofensivo": "OFFENSIVE",
    # CB
    "Salida de balón": "BALL PLAYING",
    "Marcador": "STOPPER",
    "Líbero": "SWEEPER",
    # CDM
    "Pivote organizador": "DEEP LYING",
    "Box to box destructor": "BOX TO BOX DESTROYER",
    "Pivote defensivo": "HOLDING",
    # CM
    "Box to box": "BOX TO BOX",
    "Organizador": "PLAYMAKER",
    "Centrocampista defensivo": "DEFENSIVE",
    # CAM
    "Mediapunta creativo": "ADVANCED PLAYMAKER",
    "Segundo delantero": "SHADOW STRIKER",
    "Creador de regate": "DRIBBLING CREATOR",
    # LW/RW
    "Extremo creador": "WIDE PLAYMAKER",
    "Extremo directo": "DIRECT WINGER",
    "Híbrido": "HYBRID",
    # ST
    "Hombre objetivo": "TARGET MAN",
    "Cazagoles": "POACHER",
    "Delantero organizador": "PLAYMAKER"
}

# Diccionario de perfiles de los jugadores (ejemplo, debes completarlo con los reales)
player_profiles = {
    "Marc Andre ter Stegen": "Portero líbero",
    "Wojciech Szczesny": "Portero de línea",
    "Inaki Pena": "Portero tradicional",
    "Ronald Araujo": "Marcador",
    "Pau Cubarsi": "Salida de balón",
    "Andreas Christensen": "Líbero",
    "Inigo Martinez": "Marcador",
    "Eric Garcia": "Salida de balón",
    "Jules Kounde": "Defensivo",
    "Hector Fort": "Progresivo",
    "Gerard Martin": "Ofensivo",
    "Alejandro Balde": "Ofensivo",
    "Marc Casado": "Pivote defensivo",
    "Pedri": "Organizador",
    "Frenkie de Jong": "Box to box",
    "Gavi": "Centrocampista defensivo",
    "Dani Olmo": "Mediapunta creativo",
    "Fermin Lopez": "Segundo delantero",
    "Pablo Torre": "Creador de regate",
    "Lamine Yamal": "Extremo creador",
    "Ferran Torres": "Extremo directo",
    "Raphinha": "Híbrido",
    "Ansu Fati": "Extremo directo",
    "Robert Lewandowski": "Hombre objetivo",
    "Pau Victor": "Cazagoles"
}

# Función helper para crear player cards (usando las mismas imágenes del campograma)
def create_player_card(player, position_emoji, position_name):
    rating = player_ratings.get(player, 75)
    additional_data = player_additional_data.get(player, {})
    
    # Color del badge según rating
    if rating >= 85:
        badge_color = "#22c55e"  # Verde
    elif rating >= 75:
        badge_color = "#f59e0b"  # Amarillo
    elif rating >= 65:
        badge_color = "#ef4444"  # Rojo
    else:
        badge_color = "#6b7280"  # Gris
    
    # Obtener foto del jugador usando la misma función del campograma
    def get_player_photo_base64_barca(player_name):
        try:
            if player_name == "Robert Lewandowski":
                image_path = os.path.join("static", "wetransfer_players_2025-06-18_1752", "Players", "Robert Lewandowski.png")
                if not os.path.exists(image_path):
                    filename = player_name.lower().replace(" ", "_") + ".png"
                    image_path = os.path.join("static", "players", "Barca", filename)
            else:
                filename = player_name.lower().replace(" ", "_") + ".png"
                image_path = os.path.join("static", "players", "Barca", filename)
            if not os.path.exists(image_path):
                return ""
            img = Image.open(image_path)
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Redimensionar para cards (80x80)
            img = img.resize((80, 80), Image.Resampling.LANCZOS)
            
            # Convertir a base64
            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            img_str = base64.b64encode(buffer.getvalue()).decode()
            return img_str
        except Exception as e:
            return ""
    
    photo_base64 = get_player_photo_base64_barca(player)
    
    # Obtener dorsal del jugador
    dorsal = player_dorsals.get(player, 0)
    
    # En la cardview de cada jugador:
    perfil_es = player_profiles.get(player, "Perfil no disponible.")
    perfil = perfiles_es_en.get(perfil_es, perfil_es)
    
    return f"""
        <div class="player-card">
            <div style="display: flex; flex-direction: column; align-items: center; margin-bottom: 1rem;">
                <img src="data:image/png;base64,{photo_base64}" 
                     style="width: 80px; height: 80px; border-radius: 50%; object-fit: cover; 
                            border: 3px solid #004D98; box-shadow: 0 4px 8px rgba(0,0,0,0.2);">
                <div style="background-color: #004D98; color: white; border-radius: 50%; 
                            width: 35px; height: 35px; display: flex; align-items: center; 
                            justify-content: center; font-weight: bold; font-size: 1.2rem; 
                            border: 2px solid white; margin-top: 0.5rem;">
                    {dorsal}
                </div>
            </div>
            <h3 style="text-align: center; margin-bottom: 0.5rem;">{player}</h3>
            <p style="text-align: center;">{position_name} | {player_ages.get(player, 25)} años</p>
            <p style="text-align: center;">{additional_data.get('nationality', 'España')} | Barcelona</p>
            <p style="text-align: center;">€{additional_data.get('market_value', 0):.1f}M | {additional_data.get('height', '180cm')}</p>
            <div style="display: flex; justify-content: center; margin-top: 0.5rem;">
                <div style="background-color: {badge_color}; color: white; padding: 0.5rem 1rem; border-radius: 9999px; font-size: 1rem; font-weight: 600;">
                    Rating: {rating}
                </div>
            </div>
            <p style="text-align: center; color:#555; font-size:1.05em; margin-top:18px; margin-bottom:8px;">{perfil}</p>
        </div>
    """

# Números de dorsal de cada jugador
player_dorsals = {
    "Marc Andre ter Stegen": 1,
    "Wojciech Szczesny": 25,
    "Inaki Pena": 13,
    "Ronald Araujo": 4,
    "Pau Cubarsi": 2,
    "Alejandro Balde": 3,
    "Inigo Martinez": 5,
    "Andreas Christensen": 15,
    "Jules Kounde": 23,
    "Eric Garcia": 24,
    "Hector Fort": 32,
    "Gerard Martin": 35,
    "Gavi": 6,
    "Fermin Lopez": 16,
    "Marc Casado": 17,
    "Pedri": 8,
    "Dani Olmo": 20,
    "Frenkie de Jong": 21,
    "Pablo Torre": 14,
    "Robert Lewandowski": 9,
    "Ansu Fati": 10,
    "Raphinha": 11,
    "Ferran Torres": 7,
    "Pau Victor": 18,
    "Lamine Yamal": 19
}

# Datos adicionales de los jugadores para las cards
player_additional_data = {
    "Marc Andre ter Stegen": {"nationality": "Alemania", "height": "187cm", "market_value": 25},
    "Wojciech Szczesny": {"nationality": "Polonia", "height": "196cm", "market_value": 3},
    "Inaki Pena": {"nationality": "España", "height": "184cm", "market_value": 8},
    "Ronald Araujo": {"nationality": "Uruguay", "height": "188cm", "market_value": 70},
    "Pau Cubarsi": {"nationality": "España", "height": "182cm", "market_value": 25},
    "Andreas Christensen": {"nationality": "Dinamarca", "height": "187cm", "market_value": 35},
    "Inigo Martinez": {"nationality": "España", "height": "182cm", "market_value": 20},
    "Eric Garcia": {"nationality": "España", "height": "182cm", "market_value": 15},
    "Jules Kounde": {"nationality": "Francia", "height": "178cm", "market_value": 55},
    "Hector Fort": {"nationality": "España", "height": "184cm", "market_value": 5},
    "Gerard Martin": {"nationality": "España", "height": "180cm", "market_value": 3},
    "Alejandro Balde": {"nationality": "España", "height": "175cm", "market_value": 50},
    "Marc Casado": {"nationality": "España", "height": "182cm", "market_value": 10},
    "Pedri": {"nationality": "España", "height": "174cm", "market_value": 80},
    "Frenkie de Jong": {"nationality": "Países Bajos", "height": "180cm", "market_value": 60},
    "Gavi": {"nationality": "España", "height": "173cm", "market_value": 60},
    "Dani Olmo": {"nationality": "España", "height": "179cm", "market_value": 60},
    "Fermin Lopez": {"nationality": "España", "height": "174cm", "market_value": 25},
    "Pablo Torre": {"nationality": "España", "height": "173cm", "market_value": 15},
    "Lamine Yamal": {"nationality": "España", "height": "180cm", "market_value": 180},
    "Ferran Torres": {"nationality": "España", "height": "184cm", "market_value": 40},
    "Raphinha": {"nationality": "Brasil", "height": "176cm", "market_value": 55},
    "Ansu Fati": {"nationality": "España", "height": "178cm", "market_value": 25},
    "Robert Lewandowski": {"nationality": "Polonia", "height": "185cm", "market_value": 15},
    "Pau Victor": {"nationality": "España", "height": "181cm", "market_value": 5}
}

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
            delta=f"+€{market_value_increase}M"
        )
    
    # Generar el campograma dentro de la misma columna
    fig_barca, ax_barca = draw_pitch_barca()
    
    # Mostrar el campograma
    buf = io.BytesIO()
    fig_barca.savefig(buf, format='png', bbox_inches='tight', transparent=True, dpi=150)
    buf.seek(0)
    st.image(buf, use_container_width=True)
    plt.close(fig_barca)

with col_legend:
    st.markdown("### **Leyenda:**")
    st.markdown("#### 🟡 **GK** (3)")
    st.markdown("#### 🔵 **CB** (5)")
    st.markdown("#### 🟢 **LB-RB** (4)")
    st.markdown("#### ⚪ **CM-CDM** (4)")
    st.markdown("#### 🟠 **CAM** (3)")
    st.markdown("#### 🟣 **LW-RW** (4)")
    st.markdown("#### 🔴 **ST** (2)")

# Mostrar plantilla por posiciones
st.markdown("### Plantilla por Posiciones")

# Crear tabs para cada posición
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(["🟡 GK", "🔵 CB", "🟢 LB-RB", "⚪ CM-CDM", "🟠 CAM", "🟣 LW-RW", "🔴 ST"])

# Organizar jugadores por posición específica
position_groups = {
    "GK": ["Marc Andre ter Stegen", "Wojciech Szczesny", "Inaki Pena"],
    "CB": ["Ronald Araujo", "Pau Cubarsi", "Andreas Christensen", "Inigo Martinez", "Eric Garcia"],
    "LB-RB": ["Jules Kounde", "Hector Fort", "Gerard Martin", "Alejandro Balde"],
    "CM-CDM": ["Marc Casado", "Pedri", "Frenkie de Jong", "Gavi"],
    "CAM": ["Dani Olmo", "Fermin Lopez", "Pablo Torre"],
    "LW-RW": ["Lamine Yamal", "Ferran Torres", "Raphinha", "Ansu Fati"],
    "ST": ["Robert Lewandowski", "Pau Victor"]
}

with tab1:
    st.markdown("<h3 style='margin-bottom: 1.5rem; text-align: center;'>🟡 Porteros</h3>", unsafe_allow_html=True)
    
    # Mostrar cards en grid de 3 columnas
    cols = st.columns(3)
    for i, player in enumerate(position_groups["GK"]):
        with cols[i]:
            st.markdown(create_player_card(player, "🟡", "GK"), unsafe_allow_html=True)

with tab2:
    st.markdown("<h3 style='margin-bottom: 1.5rem; text-align: center;'>🔵 Centrales</h3>", unsafe_allow_html=True)
    
    # Mostrar cards en grid de 5 columnas para centrales
    cols = st.columns(5)
    for i, player in enumerate(position_groups["CB"]):
        with cols[i]:
            st.markdown(create_player_card(player, "🔵", "CB"), unsafe_allow_html=True)

with tab3:
    st.markdown("<h3 style='margin-bottom: 1.5rem; text-align: center;'>🟢 Laterales</h3>", unsafe_allow_html=True)
    
    # Mostrar cards en grid de 4 columnas para laterales
    cols = st.columns(4)
    for i, player in enumerate(position_groups["LB-RB"]):
        with cols[i]:
            st.markdown(create_player_card(player, "🟢", "LB-RB"), unsafe_allow_html=True)

with tab4:
    st.markdown("<h3 style='margin-bottom: 1.5rem; text-align: center;'>⚪ Centrocampistas</h3>", unsafe_allow_html=True)
    
    # Mostrar cards en grid de 4 columnas para centrocampistas
    cols = st.columns(4)
    for i, player in enumerate(position_groups["CM-CDM"]):
        with cols[i]:
            st.markdown(create_player_card(player, "⚪", "CM-CDM"), unsafe_allow_html=True)

with tab5:
    st.markdown("<h3 style='margin-bottom: 1.5rem; text-align: center;'>🟠 Mediapuntas</h3>", unsafe_allow_html=True)
    
    # Mostrar cards en grid de 3 columnas para mediapuntas
    cols = st.columns(3)
    for i, player in enumerate(position_groups["CAM"]):
        with cols[i]:
            st.markdown(create_player_card(player, "🟠", "CAM"), unsafe_allow_html=True)

with tab6:
    st.markdown("<h3 style='margin-bottom: 1.5rem; text-align: center;'>🟣 Extremos</h3>", unsafe_allow_html=True)
    
    # Mostrar cards en grid de 4 columnas para extremos
    cols = st.columns(4)
    for i, player in enumerate(position_groups["LW-RW"]):
        with cols[i]:
            st.markdown(create_player_card(player, "🟣", "LW-RW"), unsafe_allow_html=True)

with tab7:
    st.markdown("<h3 style='margin-bottom: 1.5rem; text-align: center;'>🔴 Delanteros</h3>", unsafe_allow_html=True)
    
    # Mostrar cards en grid de 2 columnas para delanteros
    cols = st.columns(2)
    for i, player in enumerate(position_groups["ST"]):
        with cols[i]:
            st.markdown(create_player_card(player, "🔴", "ST"), unsafe_allow_html=True)

 