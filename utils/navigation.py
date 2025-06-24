import streamlit as st
import os
import base64
import random

def get_image_base64(image_path):
    """Convierte una imagen a base64 para mostrarla en HTML"""
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode()
    except Exception as e:
        print(f"Error loading image {image_path}: {str(e)}")
        return ""

def show_home_button():
    """Muestra un botón estilizado para volver al inicio de la aplicación"""
    # Estilos CSS para el botón de inicio
    st.markdown("""
        <!-- Importar fuentes Google Fonts clásicas y elegantes -->
        <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700&family=Montserrat:wght@300;400;500;600&family=Source+Sans+Pro:wght@300;400;500;600&display=swap" rel="stylesheet">
        
        <style>
        /* Variables de fuentes */
        :root {
            --font-title: 'Playfair Display', serif;
            --font-subtitle: 'Montserrat', sans-serif;
            --font-body: 'Source Sans Pro', sans-serif;
        }
        
        /* Aplicar tipografía elegante globalmente */
        .stApp, .main-content, body {
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
        
        <style>
        .fcb-home-button-v2 {
            position: fixed;
            top: 20px;
            left: 20px;
            z-index: 999;
            background: linear-gradient(135deg, #004D98, #a5001c) !important;
            border-radius: 50px;
            padding: 12px 24px;
            box-shadow: 0 4px 15px rgba(0, 77, 152, 0.3);
            border: 2px solid rgba(255, 255, 255, 0.2);
            backdrop-filter: blur(10px);
            transition: all 0.3s ease;
        }
        
        .fcb-home-button-v2:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(0, 77, 152, 0.4);
            background: linear-gradient(135deg, #0056b3, #c2001f) !important;
        }
        
        @media (max-width: 768px) {
            .fcb-home-button-v2 {
                position: relative;
                top: auto;
                left: auto;
                margin: 10px auto;
                display: inline-block;
            }
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Crear el contenedor del botón usando columnas para mayor control
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        # Botón de volver al inicio con estilos personalizados
        if st.button("🏠 Volver al Inicio", key="home_button", help="Regresar a la página principal"):
            st.switch_page("inicio.py")
    
    # Alternativa con HTML personalizado (comentada por si se prefiere)
    """
    st.markdown('''
        <div class="home-button-container">
            <a href="#" class="home-button" onclick="window.location.reload()">
                <span class="home-icon">🏠</span>
                <span>Volver al Inicio</span>
            </a>
        </div>
    ''', unsafe_allow_html=True)
    """

def show_page_header(title, subtitle=None, icon="⚽"):
    """Muestra un header consistente para todas las páginas"""
    # Crear un ID único para evitar conflictos de cache
    header_id = f"fcb_header_{random.randint(1000, 9999)}"
    
    # CSS Global con máxima prioridad
    st.markdown(f"""
        <style>
        #{header_id} {{
            background: linear-gradient(135deg, #004D98, #a5001c) !important;
            padding: 20px !important;
            border-radius: 15px !important;
            margin-bottom: 20px !important;
            text-align: center !important;
            box-shadow: 0 4px 15px rgba(0, 77, 152, 0.3) !important;
            width: 100% !important;
            box-sizing: border-box !important;
        }}
        #{header_id} h1 {{
            color: white !important;
            margin: 0 !important;
            font-size: 2.5em !important;
            font-weight: 700 !important;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3) !important;
            font-family: var(--font-title) !important;
            letter-spacing: 1px !important;
        }}
        #{header_id} p {{
            color: rgba(255,255,255,0.9) !important;
            margin: 10px 0 0 0 !important;
            font-size: 1.1em !important;
            font-family: var(--font-subtitle) !important;
            font-weight: 400 !important;
        }}
        </style>
        
        <div id="{header_id}">
            <h1>{icon} {title}</h1>
            {f'<p>{subtitle}</p>' if subtitle else ''}
        </div>
    """, unsafe_allow_html=True)

def show_fcb_lab_brand():
    """Muestra la marca FCB.LAB de manera consistente"""
    # Buscar el logo del Barcelona
    barca_logo_path = None
    
    # Buscar en las rutas posibles
    possible_paths = [
        os.path.join("static", "wetransfer_players_2025-06-18_1752", "LOGHI_PNG", "LA_LIGA", "SQUADRE", "Barcelona.png"),
        os.path.join("static", "logos", "Barcelona.png"),
        os.path.join("static", "logos", "barcelona.png")
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            barca_logo_path = path
            break
    
    st.markdown(f"""
        <div style="
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 10px auto 20px auto;
            max-width: 400px;
        ">
            <div style="
                background: linear-gradient(135deg, #004D98, #a5001c);
                border-radius: 15px;
                padding: 15px 25px;
                display: flex;
                align-items: center;
                gap: 15px;
                box-shadow: 0 4px 15px rgba(0, 77, 152, 0.3);
            ">
                {f'<img src="data:image/png;base64,{get_image_base64(barca_logo_path)}" style="width: 40px; height: auto; border-radius: 50%;" />' if barca_logo_path else ''}
                <div>
                    <h2 style="
                        color: white;
                        margin: 0;
                        font-size: 1.5em;
                        font-weight: 700;
                        letter-spacing: 1px;
                        font-family: var(--font-title);
                    ">FCB.LAB</h2>
                    <p style="
                        color: rgba(255,255,255,0.8);
                        margin: 0;
                        font-size: 0.8em;
                        font-family: var(--font-subtitle);
                        font-weight: 400;
                    ">Laboratorio de Análisis</p>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True) 