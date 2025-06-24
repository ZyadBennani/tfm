import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import os
from PIL import Image, ImageDraw

# Instalar openpyxl si no está disponible
try:
    import openpyxl
except ImportError:
    st.error("⚠️ Necesitas instalar openpyxl para leer archivos Excel: pip install openpyxl")
    st.stop()

# Configuración de la página
st.set_page_config(page_title="Radares Test", page_icon="📊", layout="wide")

# Título
st.title("🧪 Radares Test - Desarrollo Individual")
st.markdown("---")

# Función para cargar datos específicos de cada comparación
@st.cache_data
def load_specific_player_data(filename):
    """Carga datos de un archivo específico para una comparación (CSV o XLSX)"""
    try:
        # Buscar primero en la carpeta "Radares barca vs bayern"
        file_path_radares = f'Datos/Radares barca vs bayern/{filename}'
        file_path_root = f'Datos/{filename}'
        
        # Probar diferentes extensiones y ubicaciones
        possible_paths = [
            file_path_radares,
            file_path_radares.replace('.csv', '.csv.xlsx'),
            file_path_radares.replace('.csv', '.xlsx'),
            file_path_root,
            file_path_root.replace('.csv', '.csv.xlsx'),
            file_path_root.replace('.csv', '.xlsx')
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                st.info(f"📂 Cargando desde: `{path}`")
                if path.endswith('.xlsx'):
                    return pd.read_excel(path)
                else:
                    return pd.read_csv(path, sep=';')
        
        st.error(f"❌ Archivo no encontrado en ninguna ubicación: {filename}")
        st.write("Rutas probadas:")
        for path in possible_paths:
            st.write(f"- {path}")
        return None
        
    except Exception as e:
        st.error(f"Error al cargar {filename}: {str(e)}")
        return None

# Función para obtener métricas de un jugador desde CSV específico
def get_player_metrics_from_specific_csv(df, player_name):
    """Obtiene métricas de un jugador desde un CSV específico"""
    try:
        if df is None:
            return None
            
        player_data = df[df['Jugador'].str.strip() == player_name]
        
        if len(player_data) == 0:
            st.error(f"No se encontraron datos para {player_name}")
            return None
            
        player_data = player_data.iloc[0]
        
        # SOLO obtener las columnas de valores normalizados (mejor para comparar)
        metric_columns = [col for col in df.columns if 'Normalizado' in col and col not in ['Jugador', 'Equipo']]
        
        # Si no hay columnas normalizadas, usar las que no sean Jugador/Equipo y no contengan "Original"
        if not metric_columns:
            metric_columns = [col for col in df.columns if col not in ['Jugador', 'Equipo'] and 'Original' not in col]
        
        metrics = {}
        for col in metric_columns:
            value = player_data[col]
            if pd.notna(value):
                try:
                    # Convertir a float y asegurar que esté entre 0 y 100
                    value = float(str(value).replace(',', '.'))
                    value = max(0, min(100, value))
                    # Limpiar el nombre de la métrica (quitar "Valor Normalizado" del nombre)
                    clean_name = col.replace('Valor Normalizado ', '').replace('Valor Normalizado', '').strip()
                    if clean_name:
                        metrics[clean_name] = value
                    else:
                        metrics[col] = value
                except:
                    continue
        
        return metrics
    except Exception as e:
        st.error(f"Error al obtener métricas para {player_name}: {str(e)}")
        return None

# Función para crear gráfico radar desde archivo específico
def create_radar_from_specific_csv(filename, barca_player, bayern_player, position_name):
    """Crea un radar desde un archivo específico (CSV o XLSX)"""
    df = load_specific_player_data(filename)
    
    if df is None:
        return None
    
    try:
        # Obtener métricas de ambos jugadores
        metrics_barca = get_player_metrics_from_specific_csv(df, barca_player)
        metrics_bayern = get_player_metrics_from_specific_csv(df, bayern_player)
        
        if not metrics_barca or not metrics_bayern:
            st.error(f"No se pudieron obtener métricas para {barca_player} vs {bayern_player}")
            if df is not None:
                st.write("Datos disponibles:")
                st.dataframe(df)
            return None
        
        # 🔍 DEBUGGING: Mostrar qué métricas se encontraron
        st.write("**🔍 Debug - Métricas encontradas:**")
        st.write(f"**{barca_player}:** {list(metrics_barca.keys())}")
        st.write(f"**{bayern_player}:** {list(metrics_bayern.keys())}")
        st.write("**📊 Estructura del archivo:**")
        st.write(f"Columnas totales: {list(df.columns)}")
        
        # Obtener categorías (deben ser las mismas para ambos jugadores)
        categories = list(metrics_barca.keys())
        
        # Verificar que ambos jugadores tengan las mismas métricas
        if set(categories) != set(metrics_bayern.keys()):
            st.warning("⚠️ Los jugadores no tienen las mismas métricas")
            st.write(f"Métricas {barca_player}: {list(metrics_barca.keys())}")
            st.write(f"Métricas {bayern_player}: {list(metrics_bayern.keys())}")
        
        # Obtener valores
        barca_values = [metrics_barca[cat] for cat in categories]
        bayern_values = [metrics_bayern[cat] for cat in categories]
        
        # Crear el gráfico
        fig = go.Figure()
        
        # Datos Barcelona
        fig.add_trace(go.Scatterpolar(
            r=barca_values,
            theta=categories,
            fill='toself',
            name=barca_player,
            line_color='#004D98',  # Azul Barça
            fillcolor='rgba(0, 77, 152, 0.3)',
            connectgaps=True,
            line=dict(color='#004D98', width=3)
        ))
        
        # Datos Bayern
        fig.add_trace(go.Scatterpolar(
            r=bayern_values,
            theta=categories,
            fill='toself',
            name=bayern_player,
            line_color='#DC052D',  # Rojo Bayern
            fillcolor='rgba(220, 5, 45, 0.3)',
            connectgaps=True,
            line=dict(color='#DC052D', width=3)
        ))
        
        # Configurar layout
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100],
                    gridcolor='rgba(128, 128, 128, 0.3)',
                    gridwidth=1
                ),
                angularaxis=dict(
                    direction='clockwise',
                    rotation=90,
                    gridcolor='rgba(128, 128, 128, 0.3)',
                    gridwidth=1,
                    linecolor='rgba(128, 128, 128, 0.6)',
                    linewidth=1
                ),
                bgcolor='rgba(255, 255, 255, 0.9)'
            ),
            showlegend=True,
            title=f"{position_name}: {barca_player} vs {bayern_player}",
            height=500,
            margin=dict(t=50, b=50, l=50, r=50)
        )
        
        return fig
    except Exception as e:
        st.error(f"Error al crear el gráfico: {str(e)}")
        return None

# Definir las comparaciones y sus archivos CSV correspondientes
comparisons_config = {
    "Porteros": {
        "csv": "gk_szczesny_neuer.csv",
        "barca_player": "Wojciech Szczesny",
        "bayern_player": "Manuel Neuer",
        "position": "GK"
    },
    "Centrales Izquierdos": {
        "csv": "lcb_inigo_alaba.csv",
        "barca_player": "Inigo Martinez",
        "bayern_player": "David Alaba",
        "position": "LCB"
    },
    "Centrales Derechos": {
        "csv": "rcb_cubarsi_boateng.csv",
        "barca_player": "Pau Cubarsi",
        "bayern_player": "Jerome Boateng",
        "position": "RCB"
    },
    "Laterales Izquierdos": {
        "csv": "lb_balde_davies.csv",
        "barca_player": "Alejandro Balde",
        "bayern_player": "Alphonso Davies",
        "position": "LB"
    },
    "Laterales Derechos": {
        "csv": "rb_kounde_pavard.csv",
        "barca_player": "Jules Kounde",
        "bayern_player": "Benjamin Pavard",
        "position": "RB"
    },
    "Mediocentros Defensivos": {
        "csv": "cm_dejong_kimmich.csv",
        "barca_player": "Frenkie De Jong",
        "bayern_player": "Joshua Kimmich",
        "position": "CDM"
    },
    "Mediocentros": {
        "csv": "cm_pedri_goretzka.csv",
        "barca_player": "Pedri",
        "bayern_player": "Leon Goretzka",
        "position": "CM"
    },
    "Mediocentros Ofensivos": {
        "csv": "cam_olmo_muller.csv",
        "barca_player": "Dani Olmo",
        "bayern_player": "Thomas Muller",
        "position": "CAM"
    },
    "Extremos Izquierdos": {
        "csv": "lw_raphinha_coman.csv",
        "barca_player": "Raphinha",
        "bayern_player": "Kingsley Coman",
        "position": "LW"
    },
    "Extremos Derechos": {
        "csv": "rw_yamal_gnabry.csv",
        "barca_player": "Lamine Yamal",
        "bayern_player": "Serge Gnabry",
        "position": "RW"
    },
    "Delanteros": {
        "csv": "st_lewandowski_lewandowski.csv",
        "barca_player": "Robert Lewandowski",
        "bayern_player": "Robert Lewandowski",
        "position": "ST"
    }
}

# Selector de comparación
st.markdown("## 🎯 Selecciona una comparación para probar")

selected_comparison = st.selectbox(
    "Elige la comparación a testear:",
    options=list(comparisons_config.keys()),
    index=0
)

if selected_comparison:
    config = comparisons_config[selected_comparison]
    
    st.markdown(f"### 📋 Testeando: {selected_comparison}")
    
    # Mostrar información de la configuración
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info(f"**Archivo CSV:** `{config['csv']}`")
    with col2:
        st.success(f"**🔵 Barça:** {config['barca_player']}")
    with col3:
        st.error(f"**🔴 Bayern:** {config['bayern_player']}")
    
    # Botón para generar el radar
    if st.button("🚀 Generar Radar", type="primary"):
        with st.spinner("Generando radar..."):
            fig = create_radar_from_specific_csv(
                config['csv'],
                config['barca_player'],
                config['bayern_player'],
                config['position']
            )
            
            if fig:
                st.success("✅ ¡Radar generado exitosamente!")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.error("❌ Error al generar el radar")

# Información adicional
st.markdown("---")
st.markdown("## 📝 Información sobre los archivos CSV")

with st.expander("📊 Estructura esperada de los archivos CSV"):
    st.markdown("""
    **Formato esperado:**
    ```
    Jugador;Equipo;Metrica1;Metrica2;Metrica3;Metrica4;Metrica5
    Inigo Martinez;Barcelona;85;72;90;65;78
    David Alaba;Bayern;90;68;85;70;75
    ```
    
    **Características importantes:**
    - Separador: punto y coma (;)
    - Ambos jugadores deben tener exactamente las mismas métricas
    - Los valores deben estar entre 0 y 100
    - No debe haber valores vacíos
    """)

with st.expander("📁 Lista de archivos CSV necesarios"):
    st.markdown("**Archivos CSV que deben estar en la carpeta `Datos/`:**")
    for comp_name, config in comparisons_config.items():
        st.markdown(f"- `{config['csv']}` → {config['barca_player']} vs {config['bayern_player']}")

# Estado de los archivos
st.markdown("## 📂 Estado de los archivos CSV")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### ✅ Archivos encontrados")
    found_files = []
    for comp_name, config in comparisons_config.items():
        filename = config['csv']
        # Buscar en diferentes ubicaciones y formatos
        possible_paths = [
            f"Datos/Radares barca vs bayern/{filename}",
            f"Datos/Radares barca vs bayern/{filename.replace('.csv', '.csv.xlsx')}",
            f"Datos/Radares barca vs bayern/{filename.replace('.csv', '.xlsx')}",
            f"Datos/{filename}",
            f"Datos/{filename.replace('.csv', '.csv.xlsx')}",
            f"Datos/{filename.replace('.csv', '.xlsx')}"
        ]
        
        found = False
        for path in possible_paths:
            if os.path.exists(path):
                found_files.append(f"✅ {os.path.basename(path)}")
                found = True
                break
    
    if found_files:
        for file in found_files:
            st.markdown(file)
    else:
        st.markdown("*No se encontraron archivos*")

with col2:
    st.markdown("### ❌ Archivos faltantes")
    missing_files = []
    for comp_name, config in comparisons_config.items():
        filename = config['csv']
        # Buscar en diferentes ubicaciones y formatos
        possible_paths = [
            f"Datos/Radares barca vs bayern/{filename}",
            f"Datos/Radares barca vs bayern/{filename.replace('.csv', '.csv.xlsx')}",
            f"Datos/Radares barca vs bayern/{filename.replace('.csv', '.xlsx')}",
            f"Datos/{filename}",
            f"Datos/{filename.replace('.csv', '.csv.xlsx')}",
            f"Datos/{filename.replace('.csv', '.xlsx')}"
        ]
        
        found = False
        for path in possible_paths:
            if os.path.exists(path):
                found = True
                break
        
        if not found:
            missing_files.append(f"❌ {filename}")
    
    if missing_files:
        for file in missing_files:
            st.markdown(file)
    else:
        st.markdown("*¡Todos los archivos están presentes!*") 