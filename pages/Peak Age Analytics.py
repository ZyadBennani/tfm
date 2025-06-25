import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import io
import os
from scipy import stats
import sys

# Configuración de la página
st.set_page_config(page_title="Peak Age Analytics", page_icon="📊", layout="wide")

# Importar funciones de navegación
sys.path.append('..')
from utils.navigation import show_home_button, show_page_header, show_navbar_switch_page

# Mostrar botón de volver al inicio
show_home_button()

# Mostrar header de la página
show_page_header("Peak Age Analytics")

# Construcción del DataFrame (solo para cálculos internos)
# DataFrame con los datos
data = {
    "Posición": ["GK", "DC", "RB-LB", "CM-C", "W-ST"],
    "Edad_min": [29, 27, 26, 26, 24],
    "Edad_max": [33, 29, 28, 28, 26]
}
df_prime = pd.DataFrame(data)

# Función para crear el gráfico de edad pico con curvas gaussianas
def plot_peak_age(df):
    """
    Crea curvas gaussianas (montañas) mostrando el rendimiento por edad para cada posición
    Diseño inspirado en HudlStatsBomb Player Radar
    
    Parameters:
    df (DataFrame): DataFrame con columnas 'Posición', 'Edad_min', 'Edad_max'
    
    Returns:
    matplotlib.figure.Figure: Figura del gráfico
    """
    
    # Validación
    assert df.shape == (5, 3), f"DataFrame debe tener forma (5, 3), actual: {df.shape}"
    
    # Configuración del gráfico con estilo oscuro
    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(14, 10))
    fig.patch.set_facecolor('#1e1e1e')  # Fondo oscuro como HudlStatsBomb
    ax.set_facecolor('#1e1e1e')
    
    # Colores vibrantes para cada posición (similar a HudlStatsBomb)
    colors = ['#FF4B4B', '#00D4FF', '#FFD93D', '#6BCF7F', '#FF6B6B']
    text_color = '#FFFFFF'
    grid_color = '#333333'
    
    # Rango de edades para las curvas (desde 18 hasta 38 años)
    edad_range = np.linspace(18, 38, 200)
    
    # Configurar el espacio vertical para cada posición
    y_offset = 0
    spacing = 1.5  # Espaciado entre curvas
    
    # Crear curvas gaussianas para cada posición
    for i, (_, row) in enumerate(df.iterrows()):
        # Calcular parámetros de la distribución gaussiana
        edad_pico = (row['Edad_min'] + row['Edad_max']) / 2  # Centro de la montaña
        
        # Crear una curva gaussiana balanceada (punto medio)
        # Usar diferentes desviaciones para subida y bajada (más realista)
        rendimiento = np.zeros_like(edad_range)
        
        for j, edad in enumerate(edad_range):
            if edad <= edad_pico:
                # Fase ascendente: moderadamente gradual desde los 18
                sigma_up = 3.5  # Subida moderada
                rendimiento[j] = np.exp(-0.5 * ((edad - edad_pico) / sigma_up) ** 2)
            else:
                # Fase descendente: declive moderado 
                sigma_down = 3.0  # Bajada moderada
                rendimiento[j] = np.exp(-0.5 * ((edad - edad_pico) / sigma_down) ** 2)
        
        # Ajustar la curva para que tenga valores lógicos pero no tan extremos
        # Rendimiento mínimo en los extremos (18 y 35+ años) más moderado
        rendimiento_min = 0.08  # 8% del máximo en los extremos
        rendimiento_max = 1.0   # 100% en el pico
        
        # Normalizar y escalar
        rendimiento_normalizado = rendimiento * (rendimiento_max - rendimiento_min) + rendimiento_min
        rendimiento_normalizado = rendimiento_normalizado * 0.8  # Altura de la montaña
        
        # Posición vertical de esta curva
        y_base = y_offset
        y_values = y_base + rendimiento_normalizado
        
        # Dibujar la curva gaussiana (montaña) con 3 colores por fases
        # Colores para las fases de carrera
        color_desarrollo = '#FFD93D'  # Amarillo - Desarrollo
        color_prime = '#6BCF7F'       # Verde - Prime/Peak
        color_declive = '#FF6B6B'     # Rojo - Declive
        
        # Dividir en 3 tramos según las fases
        # Tramo 1: Desarrollo (desde inicio hasta edad_min)
        mask_desarrollo = edad_range <= row['Edad_min']
        if np.any(mask_desarrollo):
            ax.fill_between(edad_range[mask_desarrollo], y_base, y_values[mask_desarrollo], 
                           color=color_desarrollo, alpha=0.8, label=row['Posición'] if i == 0 else "")
            ax.plot(edad_range[mask_desarrollo], y_values[mask_desarrollo], 
                   color=color_desarrollo, linewidth=3, alpha=0.9)
        
        # Tramo 2: Prime/Peak (desde edad_min hasta edad_max)
        mask_prime = (edad_range >= row['Edad_min']) & (edad_range <= row['Edad_max'])
        if np.any(mask_prime):
            ax.fill_between(edad_range[mask_prime], y_base, y_values[mask_prime], 
                           color=color_prime, alpha=0.8)
            ax.plot(edad_range[mask_prime], y_values[mask_prime], 
                   color=color_prime, linewidth=3, alpha=0.9)
        
        # Tramo 3: Declive (desde edad_max hasta final)
        mask_declive = edad_range >= row['Edad_max']
        if np.any(mask_declive):
            ax.fill_between(edad_range[mask_declive], y_base, y_values[mask_declive], 
                           color=color_declive, alpha=0.8)
            ax.plot(edad_range[mask_declive], y_values[mask_declive], 
                   color=color_declive, linewidth=3, alpha=0.9)
        
        # Marcar el rango del peak con dos puntos blancos y línea
        # Encontrar los índices correspondientes a las edades min y max del peak
        edad_min_idx = np.argmin(np.abs(edad_range - row['Edad_min']))
        edad_max_idx = np.argmin(np.abs(edad_range - row['Edad_max']))
        
        # Puntos blancos en las edades min y max del peak (con borde verde)
        ax.scatter([edad_range[edad_min_idx], edad_range[edad_max_idx]], 
                  [y_values[edad_min_idx], y_values[edad_max_idx]], 
                  color='white', s=120, zorder=10, 
                  edgecolors='#6BCF7F', linewidths=3)  # Borde verde (color del peak)
        
        # Línea blanca siguiendo la curva entre los dos puntos del peak
        peak_range_x = edad_range[edad_min_idx:edad_max_idx+1]
        peak_range_y = y_values[edad_min_idx:edad_max_idx+1]
        ax.plot(peak_range_x, peak_range_y, 
                color='white', linewidth=4, zorder=9, alpha=0.9)
        
        # Etiqueta de la posición a la izquierda de la curva (más a la izquierda)
        ax.text(15.2, y_base + 0.4, row['Posición'], fontsize=13, fontweight='bold', color=text_color, ha='right', va='center')
        
        # Etiqueta del rango de edad pico
        rango_text = f"{int(row['Edad_min'])}-{int(row['Edad_max'])}"
        ax.text(edad_pico, y_base + 0.9, rango_text, 
                fontsize=10, fontweight='bold', color='white',
                ha='center', va='bottom',
                bbox=dict(boxstyle="round,pad=0.2", facecolor='#6BCF7F', alpha=0.8))
        
        # Incrementar offset para la siguiente posición
        y_offset += spacing
    
    # Configuración de ejes
    ax.set_xlim(14, 40)
    ax.set_ylim(-0.4, y_offset + 0.5)
    # Eliminar título del eje Y para evitar solapamiento
    ax.set_ylabel('')
    # Añadir título centrado arriba de la gráfica, desplazado a la derecha
    # ax.set_title('Rendimiento Relativo', fontsize=18, fontweight='bold', color='#003366', loc='center', pad=25, x=0.28)
    ax.set_xlabel('Edad (años)', fontsize=14, fontweight='bold', color=text_color)
    
    # Grid sutil
    ax.grid(True, axis='x', alpha=0.2, linestyle='-', color=grid_color)
    ax.set_axisbelow(True)
    
    # Líneas verticales de referencia
    for age in [20, 25, 30, 35]:
        ax.axvline(x=age, color=grid_color, alpha=0.3, linestyle='--', linewidth=1)
        ax.text(age, y_offset + 0.3, f'{age}', ha='center', va='bottom', 
                color=text_color, fontsize=10, alpha=0.7)
    
    # Personalizar spines
    for spine in ax.spines.values():
        spine.set_visible(False)
    
    # Personalizar ticks
    ax.set_xticks([20, 25, 30, 35])  # Solo mostrar estos valores
    ax.tick_params(axis='x', colors=text_color, labelsize=12)
    ax.tick_params(axis='y', colors=text_color, labelsize=12)
    
    # Quitar ticks del eje Y (ya que es rendimiento relativo)
    ax.set_yticks([])
    

    
    # Leyenda de fases de carrera
    phases_y = 0.95
    ax.text(0.98, phases_y, '🚀 Desarrollo (Pre-Peak)', transform=ax.transAxes, 
            ha='right', va='top', color='#FFD93D', fontsize=10, fontweight='bold')
    ax.text(0.98, phases_y - 0.05, '⭐ Prime (Peak)', transform=ax.transAxes, 
            ha='right', va='top', color='#6BCF7F', fontsize=10, fontweight='bold')
    ax.text(0.98, phases_y - 0.10, '📉 Declive (Post-Peak)', transform=ax.transAxes, 
            ha='right', va='top', color='#FF6B6B', fontsize=10, fontweight='bold')
    
    # Ajustar márgenes
    plt.tight_layout()
    
    # Guardar la imagen
    plt.savefig('peak_age_by_position.png', dpi=300, bbox_inches='tight', 
                facecolor='#1e1e1e', edgecolor='none')
    
    return fig

# Visualización principal
st.markdown('''
<div style="text-align: center; margin: 40px 0 30px 0;">
    <h2 style="
        font-size: 2.5em;
        font-weight: 700;
        color: #2c3e50;
        margin-bottom: 10px;
        letter-spacing: 1px;">
        Análisis de rendimiento por edad
    </h2>
    <h3 style="
            font-size: 1.5em;
            font-weight: 400;
            color: #7f8c8d;
            margin-top: 0;
            letter-spacing: 0.5px;
        ">Metodología Anselmo Ruiz</h3>
</div>
''', unsafe_allow_html=True)


# --- REDISEÑO UNIFORME ---
# Título y explicación arriba (ya está, solo mejoro el espaciado)
st.markdown("""
<style>
.tabla-peak {
    width: 100%;
    border-collapse: separate;
    border-spacing: 0 0;
    margin-top: 12px;
    font-family: Arial, sans-serif;
}
.tabla-peak th {
    background: linear-gradient(90deg, #004D98 60%, #b50a2e 100%);
    color: #fff;
    padding: 16px 8px 12px 8px;
    font-size: 1.1em;
    border-radius: 18px 18px 0 0;
    font-weight: bold;
}
.tabla-peak td {
    background: #fff;
    color: #003366;
    padding: 14px 12px;
    vertical-align: middle;
    font-size: 1.05em;
    border-bottom: 1px solid #e0e0e0;
    text-align: center;
}
.tabla-peak tr:last-child td {
    border-radius: 0 0 18px 18px;
}
</style>
""", unsafe_allow_html=True)

# Fila con dos columnas: izquierda tabla, derecha gráfica
col1, col2 = st.columns([1, 2.7], gap="medium")

with col1:
    st.markdown("""
    <table class='tabla-peak'>
        <tr>
            <th>Posición</th>
            <th>Edad mínima</th>
            <th>Edad máxima</th>
        </tr>
        <tr>
            <td>Portero</td><td>29</td><td>33</td>
        </tr>
        <tr>
            <td>Defensa central</td><td>27</td><td>29</td>
        </tr>
        <tr>
            <td>Lateral / Interior</td><td>26</td><td>28</td>
        </tr>
        <tr>
            <td>Mediocentro</td><td>26</td><td>28</td>
        </tr>
        <tr>
            <td>Extremo / Delantero</td><td>24</td><td>26</td>
        </tr>
    </table>
    """, unsafe_allow_html=True)
    st.markdown("""
    <div style='margin-top:18px; color:#003366; font-size:0.98em;'>
    </div>
    """, unsafe_allow_html=True)

with col2:
    # Gráfica con fondo blanco y ejes/líneas en negro
    import matplotlib.pyplot as plt
    import matplotlib as mpl
    def plot_peak_age_big(df):
        plt.style.use('dark_background')
        fig, ax = plt.subplots(figsize=(18, 10))
        fig.patch.set_facecolor('#fff')
        ax.set_facecolor('#fff')
        colors = ['#FF4B4B', '#00D4FF', '#FFD93D', '#6BCF7F', '#FF6B6B']
        text_color = '#222'
        grid_color = '#333333'
        edad_range = np.linspace(14, 40, 200)
        y_offset = 0
        spacing = 1.5
        for i, (_, row) in enumerate(df.iterrows()):
            edad_pico = (row['Edad_min'] + row['Edad_max']) / 2
            rendimiento = np.zeros_like(edad_range)
            for j, edad in enumerate(edad_range):
                if edad <= edad_pico:
                    sigma_up = 3.5
                    rendimiento[j] = np.exp(-0.5 * ((edad - edad_pico) / sigma_up) ** 2)
                else:
                    sigma_down = 3.0
                    rendimiento[j] = np.exp(-0.5 * ((edad - edad_pico) / sigma_down) ** 2)
            rendimiento_min = 0.08
            rendimiento_max = 1.0
            rendimiento_normalizado = rendimiento * (rendimiento_max - rendimiento_min) + rendimiento_min
            rendimiento_normalizado = rendimiento_normalizado * 0.8
            y_base = y_offset
            y_values = y_base + rendimiento_normalizado
            color_desarrollo = '#FFD93D'
            color_prime = '#6BCF7F'
            color_declive = '#FF6B6B'
            mask_desarrollo = edad_range <= row['Edad_min']
            if np.any(mask_desarrollo):
                ax.fill_between(edad_range[mask_desarrollo], y_base, y_values[mask_desarrollo], color=color_desarrollo, alpha=0.8)
                ax.plot(edad_range[mask_desarrollo], y_values[mask_desarrollo], color=color_desarrollo, linewidth=3, alpha=0.9)
            mask_prime = (edad_range >= row['Edad_min']) & (edad_range <= row['Edad_max'])
            if np.any(mask_prime):
                ax.fill_between(edad_range[mask_prime], y_base, y_values[mask_prime], color=color_prime, alpha=0.8)
                ax.plot(edad_range[mask_prime], y_values[mask_prime], color=color_prime, linewidth=3, alpha=0.9)
            mask_declive = edad_range >= row['Edad_max']
            if np.any(mask_declive):
                ax.fill_between(edad_range[mask_declive], y_base, y_values[mask_declive], color=color_declive, alpha=0.8)
                ax.plot(edad_range[mask_declive], y_values[mask_declive], color=color_declive, linewidth=3, alpha=0.9)
            edad_min_idx = np.argmin(np.abs(edad_range - row['Edad_min']))
            edad_max_idx = np.argmin(np.abs(edad_range - row['Edad_max']))
            ax.scatter([edad_range[edad_min_idx], edad_range[edad_max_idx]], [y_values[edad_min_idx], y_values[edad_max_idx]], color='white', s=120, zorder=10, edgecolors='#6BCF7F', linewidths=3)
            peak_range_x = edad_range[edad_min_idx:edad_max_idx+1]
            peak_range_y = y_values[edad_min_idx:edad_max_idx+1]
            ax.plot(peak_range_x, peak_range_y, color='white', linewidth=4, zorder=9, alpha=0.9)
            ax.text(15.2, y_base + 0.4, row['Posición'], fontsize=13, fontweight='bold', color=text_color, ha='right', va='center')
            rango_text = f"{int(row['Edad_min'])}-{int(row['Edad_max'])}"
            ax.text(edad_pico, y_base + 0.9, rango_text, fontsize=10, fontweight='bold', color='white', ha='center', va='bottom', bbox=dict(boxstyle="round,pad=0.2", facecolor='#6BCF7F', alpha=0.8))
            y_offset += spacing
        ax.set_xlim(14, 40)
        ax.set_ylim(-0.4, y_offset + 0.5)
        ax.set_xlabel('Edad (años)', fontsize=14, fontweight='bold', color=text_color)
        # ax.set_ylabel('Rendimiento Relativo', fontsize=14, fontweight='bold', color=text_color, labelpad=-50)
        ax.grid(True, axis='x', alpha=0.2, linestyle='-', color=grid_color)
        ax.set_axisbelow(True)
        for age in [20, 25, 30, 35]:
            ax.axvline(x=age, color=grid_color, alpha=0.3, linestyle='--', linewidth=1)
            ax.text(age, y_offset + 0.3, f'{age}', ha='center', va='bottom', color=text_color, fontsize=10, alpha=0.7)
        for spine in ax.spines.values():
            spine.set_visible(True)
            spine.set_color('#222')
            spine.set_linewidth(1.2)
        ax.xaxis.label.set_color('#222')
        ax.yaxis.label.set_color('#222')
        ax.tick_params(axis='x', colors='#222')
        ax.tick_params(axis='y', colors='#222')
        for label in ax.get_xticklabels() + ax.get_yticklabels():
            label.set_color('#222')
        ax.set_yticks([])
        phases_y = 0.95
        ax.text(0.98, phases_y, '🚀 Desarrollo (Pre-Peak)', transform=ax.transAxes, ha='right', va='top', color='#FFD93D', fontsize=10, fontweight='bold')
        ax.text(0.98, phases_y - 0.05, '⭐ Prime (Peak)', transform=ax.transAxes, ha='right', va='top', color='#6BCF7F', fontsize=10, fontweight='bold')
        ax.text(0.98, phases_y - 0.10, '📉 Declive (Post-Peak)', transform=ax.transAxes, ha='right', va='top', color='#FF6B6B', fontsize=10, fontweight='bold')
        return fig
    fig = plot_peak_age_big(df_prime)
    # Cambiar fondo a blanco y ejes/líneas en negro
    fig.patch.set_facecolor('#fff')
    ax = fig.axes[0]
    ax.set_facecolor('#fff')
    for spine in ax.spines.values():
        spine.set_visible(True)
        spine.set_color('#222')
        spine.set_linewidth(1.2)
    ax.xaxis.label.set_color('#222')
    ax.yaxis.label.set_color('#222')
    ax.tick_params(axis='x', colors='#222')
    ax.tick_params(axis='y', colors='#222')
    for label in ax.get_xticklabels() + ax.get_yticklabels():
        label.set_color('#222')
    st.pyplot(fig, use_container_width=True)



# --- BLOQUE DE CSS GLOBAL FCB.LAB ---
st.markdown('''
    <!-- Importar fuentes Google Fonts clásicas y elegantes -->
    <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700&family=Montserrat:wght@300;400;500;600&family=Source+Sans+Pro:wght@300;400;500;600&display=swap" rel="stylesheet">
    <style>
    :root {
        --font-title: 'Playfair Display', serif;
        --font-subtitle: 'Montserrat', sans-serif;
        --font-body: 'Source Sans Pro', sans-serif;
        --barca-primary: #004D98;
        --barca-secondary: #a5001c;
    }
    .liga-card, .team-card, .centered-header, .main-content {
        box-shadow: 0 8px 32px 0 rgba(0,77,152,0.18), 0 1.5px 8px 0 rgba(165,0,28,0.10);
        backdrop-filter: blur(8px) saturate(120%);
        background: linear-gradient(135deg, rgba(255,255,255,0.85) 60%, rgba(0,77,152,0.08) 100%);
        border: 1.5px solid rgba(0,77,152,0.10);
    }
    .centered-header {
        background: linear-gradient(135deg, #004D98 60%, #a5001c 100%);
        color: #fff;
    }
    .liga-card, .team-card {
        border-radius: 18px;
        margin: 15px;
        transition: box-shadow 0.3s, transform 0.3s;
    }
    .liga-card:hover, .team-card:hover {
        box-shadow: 0 16px 40px 0 rgba(0,77,152,0.22), 0 2px 12px 0 rgba(165,0,28,0.13);
        transform: translateY(-6px) scale(1.02);
        border-color: #004D98;
    }
    .stButton button {
        background: linear-gradient(135deg, #004D98 60%, #a5001c 100%);
        color: #fff;
        border: none;
        border-radius: 30px;
        padding: 12px 28px;
        font-family: var(--font-subtitle) !important;
        font-weight: 600;
        font-size: 1.08em;
        box-shadow: 0 2px 12px rgba(0,77,152,0.10);
        transition: background 0.25s, box-shadow 0.25s, transform 0.15s;
        outline: none;
        cursor: pointer;
        letter-spacing: 0.5px;
    }
    .stButton button:hover {
        background: linear-gradient(135deg, #003366 60%, #a5001c 100%);
        box-shadow: 0 6px 20px rgba(0,77,152,0.18);
        transform: translateY(-2px) scale(1.03);
    }
    .stButton button:active {
        background: linear-gradient(135deg, #002244 60%, #7a0010 100%);
        box-shadow: 0 2px 8px rgba(0,77,152,0.10);
        transform: scale(0.98);
    }
    .stButton button:disabled {
        background: #e0e0e0;
        color: #aaa;
        cursor: not-allowed;
        box-shadow: none;
    }
    .stSelectbox > div > div, .stTextInput > div > input, .stNumberInput > div > input, .stSlider > div {
        background: rgba(255,255,255,0.85) !important;
        border: 2px solid #004D98 !important;
        border-radius: 12px !important;
        color: #2c3e50 !important;
        box-shadow: 0 2px 8px rgba(0,77,152,0.08);
        font-family: var(--font-body) !important;
        font-size: 1.05em !important;
        transition: border 0.2s, box-shadow 0.2s;
    }
    .stSelectbox > div > div:focus-within, .stTextInput > div > input:focus, .stNumberInput > div > input:focus, .stSlider > div:focus-within {
        border: 2.5px solid #a5001c !important;
        box-shadow: 0 0 0 3px rgba(165,0,28,0.13);
        outline: none !important;
    }
    .stSelectbox > div > div::placeholder, .stTextInput > div > input::placeholder, .stNumberInput > div > input::placeholder {
        color: #888 !important;
        opacity: 1 !important;
        font-style: italic;
    }
    .stSlider > div [role=slider] {
        background: linear-gradient(90deg, #004D98 0%, #a5001c 100%) !important;
        border-radius: 8px !important;
        box-shadow: 0 2px 8px rgba(0,77,152,0.10);
    }
    .stSlider > div [role=slider]:focus {
        outline: 2.5px solid #a5001c !important;
        box-shadow: 0 0 0 3px rgba(165,0,28,0.13) !important;
    }
    body, .main-content, .stApp {
        font-family: var(--font-body) !important;
    }
    h1 {
        font-family: var(--font-title) !important;
        font-weight: 600 !important;
        letter-spacing: 1px !important;
    }
    h2, h3 {
        font-family: var(--font-subtitle) !important;
        font-weight: 500 !important;
        letter-spacing: 0.5px !important;
    }
    h4, h5, h6 {
        font-family: var(--font-subtitle) !important;
        font-weight: 400 !important;
    }
    p, .stMarkdown, .stText, div, span {
        font-family: var(--font-body) !important;
        line-height: 1.6 !important;
    }
    .stButton button {
        font-family: var(--font-subtitle) !important;
        font-weight: 500 !important;
        letter-spacing: 0.5px !important;
    }
    .team-name {
        font-family: var(--font-subtitle) !important;
        font-weight: 500 !important;
        letter-spacing: 0.5px !important;
    }
    .stSelectbox, .stSlider, .stNumberInput {
        font-family: var(--font-body) !important;
    }
    </style>
''', unsafe_allow_html=True)
# --- FIN BLOQUE CSS GLOBAL ---

show_navbar_switch_page()
