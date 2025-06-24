import streamlit as st
import os
import base64

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
        <style>
        .home-button-container {
            position: fixed;
            top: 20px;
            left: 20px;
            z-index: 999;
            background: linear-gradient(135deg, #004D98, #A50044);
            border-radius: 50px;
            padding: 12px 24px;
            box-shadow: 0 4px 15px rgba(0, 77, 152, 0.3);
            border: 2px solid rgba(255, 255, 255, 0.2);
            backdrop-filter: blur(10px);
            transition: all 0.3s ease;
        }
        
        .home-button-container:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(0, 77, 152, 0.4);
            background: linear-gradient(135deg, #0056b3, #b8004d);
        }
        
        .home-button {
            color: white !important;
            text-decoration: none !important;
            font-weight: 600;
            font-size: 14px;
            display: flex;
            align-items: center;
            gap: 8px;
            letter-spacing: 0.5px;
        }
        
        .home-icon {
            font-size: 16px;
        }
        
        @media (max-width: 768px) {
            .home-button-container {
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
    st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #004D98, #A50044);
            padding: 20px;
            border-radius: 15px;
            margin-bottom: 20px;
            text-align: center;
            box-shadow: 0 4px 15px rgba(0, 77, 152, 0.3);
        ">
            <h1 style="
                color: white;
                margin: 0;
                font-size: 2.5em;
                font-weight: 700;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            ">{icon} {title}</h1>
            {f'<p style="color: rgba(255,255,255,0.9); margin: 10px 0 0 0; font-size: 1.1em;">{subtitle}</p>' if subtitle else ''}
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
                background: linear-gradient(135deg, #004D98, #A50044);
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
                        font-weight: 900;
                        letter-spacing: 1px;
                    ">FCB.LAB</h2>
                    <p style="
                        color: rgba(255,255,255,0.8);
                        margin: 0;
                        font-size: 0.8em;
                    ">Laboratorio de Análisis</p>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True) 