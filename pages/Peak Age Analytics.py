import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import io
import os
from scipy import stats

# Configuración de la página
st.set_page_config(page_title="Peak Age Analytics", page_icon="📊", layout="wide")

# Título y contexto
st.title("📊 Career & Peak-Age Analytics")
st.markdown("**Basado en la metodología de Anselmo Ruiz de Alarcón**")

# Construcción del DataFrame (solo para cálculos internos)
# DataFrame con los datos
data = {
    "Posición": ["Portero", "Defensa central", "Lateral / Interior", "Mediocentro", "Extremo / Delantero"],
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
        
        # Etiqueta de la posición
        ax.text(17, y_base + 0.4, row['Posición'], 
                fontsize=12, fontweight='bold', color='white',
                ha='right', va='center')
        
        # Etiqueta del rango de edad pico
        rango_text = f"{int(row['Edad_min'])}-{int(row['Edad_max'])}"
        ax.text(edad_pico, y_base + 0.9, rango_text, 
                fontsize=10, fontweight='bold', color='white',
                ha='center', va='bottom',
                bbox=dict(boxstyle="round,pad=0.2", facecolor='#6BCF7F', alpha=0.8))
        
        # Incrementar offset para la siguiente posición
        y_offset += spacing
    
    # Configuración de ejes
    ax.set_xlim(18, 40)  # Mover más a la derecha para dar espacio
    ax.set_ylim(-0.4, y_offset + 0.5)
    ax.set_xlabel('Edad (años)', fontsize=14, fontweight='bold', color=text_color)
    ax.set_ylabel('Rendimiento Relativo', fontsize=14, fontweight='bold', color=text_color, labelpad=20)
    
    # Título moderno
    ax.set_title('PEAK AGE ANALYTICS\nCurvas de Rendimiento por Posición (Career Performance)', 
                fontsize=18, fontweight='bold', pad=25, color=text_color,
                bbox=dict(boxstyle="round,pad=0.5", facecolor='#333333', alpha=0.8))
    
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
    ax.text(0.98, phases_y, '🚀 Desarrollo (18-22)', transform=ax.transAxes, 
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
st.markdown("---")
st.markdown("## 2. Visualización: Career Performance Curves")

# Crear y mostrar el gráfico
fig = plot_peak_age(df_prime)

# Mostrar en Streamlit
st.pyplot(fig)

# Análisis e interpretación
st.markdown("---")
st.markdown("## 3. Análisis e Interpretación")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### 🥅 Porteros")
    st.markdown("""
    **Rango: 29-33 años**
    
    - Mayor longevidad deportiva
    - Experiencia y lectura del juego crucial
    - Menor desgaste físico
    - Madurez mental determinante
    """)

with col2:
    st.markdown("### 🛡️ Defensas")
    st.markdown("""
    **Centrales: 27-29 años**
    **Laterales: 26-28 años**
    
    - Equilibrio entre físico y experiencia
    - Liderazgo defensivo
    - Capacidad de anticipación
    """)

with col3:
    st.markdown("### ⚡ Atacantes")
    st.markdown("""
    **Extremos/Delanteros: 24-26 años**
    
    - Pico de velocidad y explosividad
    - Menor dependencia de experiencia
    - Máximo rendimiento físico
    """)

# Aplicaciones prácticas
st.markdown("---")
st.markdown("## 4. Aplicaciones Prácticas")

st.markdown("""
### 🎯 Para Directores Deportivos:

1. **Fichajes estratégicos**: Identificar jugadores en su ventana de máximo rendimiento
2. **Planificación de plantilla**: Equilibrar jugadores en diferentes fases de carrera
3. **Valoración económica**: Ajustar ofertas según la edad y posición del jugador
4. **Renovaciones**: Decidir la duración de contratos basándose en el pico esperado

### 📊 Para Análisis de Rendimiento:

1. **Expectativas realistas**: Ajustar expectativas según edad y posición
2. **Desarrollo de cantera**: Planificar la progresión de jóvenes talentos
3. **Transiciones de carrera**: Identificar cuándo un jugador puede cambiar de posición
4. **Mercado de traspasos**: Evaluar el momento óptimo para vender/comprar
""")
