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
from PIL import ImageDraw

# Configuración de la página
st.set_page_config(page_title="Campograma FC Barcelona", page_icon="🔵🔴", layout="wide")

# Título
st.title("Plantilla 2024-25")

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

# Estadísticas del equipo - encima del campograma
st.markdown("---")

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

# Campograma principal
col_legend, col_campo = st.columns([1, 4])

# Mostrar estadísticas alineadas con el campograma
with col_campo:
    # Las métricas van dentro de la misma columna que el campograma
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(label="Edad Media", value=f"{average_age:.1f}")

    with col2:
        st.metric(label="Internacionales", value=f"{international_percentage:.0f}%")

    with col3:
        st.metric(label="Cantera", value=f"{cantera_percentage:.0f}%")

    with col4:
        st.metric(label="Jóvenes Sub-23", value=f"{young_percentage:.0f}%")
    
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
    st.markdown("#### 🔴 **ST** (2)")
    st.markdown("#### 🟣 **LW-RW** (4)")
    st.markdown("#### 🟠 **CAM** (3)")
    st.markdown("#### ⚪ **CM-CDM** (4)")
    st.markdown("#### 🟢 **LB-RB** (4)")
    st.markdown("#### 🔵 **CB** (5)")
    st.markdown("#### 🟡 **GK** (3)")

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
    st.markdown("<h4 style='text-align: center;'> Porteros</h4>", unsafe_allow_html=True)
    cols = st.columns(3)  # 3 porteros
    for i, player in enumerate(position_groups["GK"]):
        with cols[i]:
            st.markdown(f"**{player}**")
            player_img = get_circular_player_image(player)
            if player_img:
                st.image(player_img, width=85)
            else:
                st.write("Imagen no disponible")

with tab2:
    st.markdown("<h4 style='text-align: center;'> Centrales</h4>", unsafe_allow_html=True)
    cols = st.columns(5)  # 5 centrales en una línea
    for i, player in enumerate(position_groups["CB"]):
        with cols[i]:
            st.markdown(f"**{player}**")
            player_img = get_circular_player_image(player)
            if player_img:
                st.image(player_img, width=85)
            else:
                st.write("Imagen no disponible")

with tab3:
    st.markdown("<h4 style='text-align: center;'> Laterales</h4>", unsafe_allow_html=True)
    cols = st.columns(4)  # 4 laterales en una línea
    for i, player in enumerate(position_groups["LB-RB"]):
        with cols[i]:
            st.markdown(f"**{player}**")
            player_img = get_circular_player_image(player)
            if player_img:
                st.image(player_img, width=85)
            else:
                st.write("Imagen no disponible")

with tab4:
    st.markdown("<h4 style='text-align: center;'> Centrocampistas</h4>", unsafe_allow_html=True)
    cols = st.columns(4)  # 4 centrocampistas en una línea
    for i, player in enumerate(position_groups["CM-CDM"]):
        with cols[i]:
            st.markdown(f"**{player}**")
            player_img = get_circular_player_image(player)
            if player_img:
                st.image(player_img, width=85)
            else:
                st.write("Imagen no disponible")

with tab5:
    st.markdown("<h4 style='text-align: center;'> Mediapuntas</h4>", unsafe_allow_html=True)
    cols = st.columns(3)  # 3 mediapuntas
    for i, player in enumerate(position_groups["CAM"]):
        with cols[i]:
            st.markdown(f"**{player}**")
            player_img = get_circular_player_image(player)
            if player_img:
                st.image(player_img, width=85)
            else:
                st.write("Imagen no disponible")

with tab6:
    st.markdown("<h4 style='text-align: center;'> Extremos</h4>", unsafe_allow_html=True)
    cols = st.columns(4)  # 4 extremos en una línea
    for i, player in enumerate(position_groups["LW-RW"]):
        with cols[i]:
            st.markdown(f"**{player}**")
            player_img = get_circular_player_image(player)
            if player_img:
                st.image(player_img, width=85)
            else:
                st.write("Imagen no disponible")

with tab7:
    st.markdown("<h4 style='text-align: center;'> Delanteros</h4>", unsafe_allow_html=True)
    cols = st.columns(2)  # 2 delanteros en una línea
    for i, player in enumerate(position_groups["ST"]):
        with cols[i]:
            st.markdown(f"**{player}**")
            player_img = get_circular_player_image(player)
            if player_img:
                st.image(player_img, width=85)
            else:
                st.write("Imagen no disponible") 