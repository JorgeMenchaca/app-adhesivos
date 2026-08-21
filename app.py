from datetime import datetime, timedelta
import uuid
import pandas as pd
import streamlit as st
from streamlit_gsheets import GSheetsConnection

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(
    page_title="Gestión de Folios",
    page_icon="🎫",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# 2. ESTADO DE NAVEGACIÓN
if "pantalla" not in st.session_state:
    st.session_state["pantalla"] = "formulario"

# 3. ESTILOS CSS (FONDO DE TICKETS Y CONTENEDOR COMPACTO CON SCROLL INTERNO)
st.markdown(
    """
    <style>
    /* Ocultar menús de Streamlit */
    #MainMenu, footer, header, [data-testid="stSidebar"] {display: none !important;}
    
    /* FONDO DE PATRÓN DE TICKETS / BOLETOS CON CAPA CLARA */
    .stApp {
        background-image: linear-gradient(rgba(248, 250, 252, 0.90), rgba(248, 250, 252, 0.90)), 
                          url('https://images.unsplash.com/photo-1540575467063-178a50c2df87?auto=format&fit=crop&q=80&w=1200') !important;
        background-size: cover !important;
        background-position: center !important;
        background-attachment: fixed !important;
    }
    
    .block-container {
        max-width: 500px !important;
        padding-top: 1.5rem !important;
        padding-bottom: 2rem !important;
    }

    /* FIX DEL BOTÓN 100% ANCHO REAL */
    div[class*="st-key-FormSubmitter-"],
    div[data-testid="stElementContainer"]:has(div[data-testid="stFormSubmitButton"]) {
        width: 100% !important;
        max-width: 100% !important;
    }

    div[data-testid="stFormSubmitButton"],
    div[data-testid="stFormSubmitButton"] > div {
        width: 100% !important;
        max-width: 100% !important;
        display: block !important;
    }
    
    div[data-testid="stFormSubmitButton"] > button,
    button[data-testid="stBaseButton-secondaryFormSubmit"] {
        width: 100% !important;
        min-height: 48px !important;
        background-color: #10B981 !important;
        color: #FFFFFF !important;
        border: none !important;
        padding: 12px 24px !important;
        font-size: 16px !important;
        font-weight: 800 !important;
        border-radius: 10px !important;
        box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3) !important;
        transition: all 0.2s ease !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-top: 10px !important;
    }
    
    div[data-testid="stFormSubmitButton"] > button:hover {
        background-color: #059669 !important;
        color: #FFFFFF !important;
    }
    
    div[data-testid="stFormSubmitButton"] > button p {
        color: #FFFFFF !important;
        font-weight: 800 !important;
        font-size: 16px !important;
    }
    
    /* CENTRAR LOS TÍTULOS DE LOS DROPDOWNS */
    [data-testid="stWidgetLabel"] {
        display: flex !important;
        justify-content: center !important;
        width: 100% !important;
    }
    
    [data-testid="stWidgetLabel"] p {
        text-align: center !important;
        font-weight: 700 !important;
        font-size: 14px !important;
        color: #0F172A !important;
        margin-bottom: 8px !important;
        width: 100% !important;
    }
    
    label, p, span, h1, h2, h3, .stMarkdown {
        font-family: 'Inter', system-ui, sans-serif !important;
    }
    
    [data-testid="stForm"] {
        background-color: #FFFFFF !important;
        border-radius: 20px !important;
        border: 1px solid #E2E8F0 !important;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.05) !important;
        padding: 24px !important;
    }
    
    .info-card {
        background-color: #FFFFFF;
        border-radius: 12px;
        padding: 12px 16px;
        margin-bottom: 8px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.02);
        border: 1px solid #E2E8F0;
        border-left: 4px solid #0284C7;
    }
    .info-label {
        font-size: 11px;
        color: #64748B !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        font-weight: 600;
    }
    .info-value {
        font-size: 15px;
        color: #0F172A !important;
        font-weight: 700;
    }

    /* ------------------------------------------------------------- */
    /* CONTENEDOR DE HISTORIAL COMPACTO CON SCROLL INTERNO */
    /* ------------------------------------------------------------- */
    .historial-box {
        max-height: 380px;
        overflow-y: auto;
        padding-right: 4px;
        margin-bottom: 16px;
    }
    
    /* Personalizar barra de scroll suave */
    .historial-box::-webkit-scrollbar {
        width: 6px;
    }
    .historial-box::-webkit-scrollbar-thumb {
        background-color: #CBD5E1;
        border-radius: 10px;
    }

    .historial-item-compact {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 10px 14px;
        margin-bottom: 8px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.02);
    }
    .badge-estatus {
        background-color: #DEF7EC;
        color: #03543F !important;
        font-size: 10px;
        font-weight: 700;
        padding: 2px 6px;
        border-radius: 10px;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# 4. CONEXIÓN A GOOGLE SHEETS
conn = st.connection("gsheets", type=GSheetsConnection)


# ==============================================================================
# PANTALLA 1: FORMULARIO
# ==============================================================================
if st.session_state["pantalla"] == "formulario":

    try:
        df_folios = conn.read(worksheet="FOLIOS", ttl=5)
        df_adhesivos = conn.read(worksheet="ADHESIVOS", ttl=5)
        df_prioridad = conn.read(worksheet="PRIORIDAD", ttl=5)
    except Exception as e:
        st.error(f"⚠️ Error de conexión con Google Sheets: {e}")
        st.stop()

    query_params = st.query_params
    linea_qr = query_params.get("linea", "AUTO WRAPPERS 780B")
    cabina_qr = query_params.get("cabina", "1")
    adhesivo_qr = query_params.get("adhesivo", None)

    # REGLA ESPECIAL PARA "PRIMER":
    if adhesivo_qr and adhesivo_qr.strip().upper() == "PRIMER":
        adhesivos_disponibles = ["PRIMER"]
        index_adhesivo = 0
    else:
        adhesivos_disponibles = df_adhesivos[
            df_adhesivos["DescripcionLinea"] == linea_qr
        ]["Adhesivo"].dropna().unique().tolist()
        
        if not adhesivos_disponibles:
            adhesivos_disponibles = ["ADHESIVO 09 (GENERAL)"]

        index_adhesivo = 0
        if adhesivo_qr and adhesivo_qr in adhesivos_disponibles:
            index_adhesivo = adhesivos_disponibles.index(adhesivo_qr)

    match_prioridad = df_prioridad[df_prioridad["LINEA"] == linea_qr]
    prioridad_val = (
        match_prioridad["PRIORIDAD"].values[0]
        if not match_prioridad.empty
        else "MEDIA"
    )

    # ENCABEZADO
    st.markdown(
        "<h2 style='text-align: center; font-weight: 800; margin-bottom: 2px; color: #0F172A;'>Nuevo Folio</h2>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<div style='text-align: center; color: #334155; font-size: 14px; font-weight: 600; margin-bottom: 20px;'>Registro de material vía QR</div>",
        unsafe_allow_html=True,
    )

    # TARJETAS QR
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown(
            f"""
            <div class="info-card">
                <div class="info-label">Línea</div>
                <div class="info-value">{linea_qr}</div>
            </div>
        """,
            unsafe_allow_html=True,
        )

    with col_b:
        st.markdown(
            f"""
            <div class="info-card">
                <div class="info-label">Cabina / Prioridad</div>
                <div class="info-value">Cabina {cabina_qr} • <span style="color:#D97706;">{prioridad_val}</span></div>
            </div>
        """,
            unsafe_allow_html=True,
        )

    st.markdown(
        "<div style='margin-bottom: 12px;'></div>", unsafe_allow_html=True
    )

    # FORMULARIO
    with st.form("form_registro", clear_on_submit=True):

        adhesivo_sel = st.selectbox(
            "Adhesivo *", options=adhesivos_disponibles, index=index_adhesivo
        )

        botes_sel = st.selectbox(
            "Cantidad de Botes *", options=["1", "1/2", "1/4"], index=0
        )

        st.markdown(
            "<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True
        )

        btn_guardar = st.form_submit_button("GUARDAR FOLIO")

        if btn_guardar:
            nuevo_id = str(uuid.uuid4())[:8]
            fecha_actual = datetime.now().strftime("%m/%d/%Y %H:%M:%S")

            nuevo_folio = pd.DataFrame(
                [
                    {
                        "ID_Folio": nuevo_id,
                        "FechaCreacion": fecha_actual,
                        "Linea": linea_qr,
                        "Estatus": "NUEVO",
                        "Cabina": cabina_qr,
                        "FechaCerrado": "",
                        "NivelCerrado": "",
                        "NivelActual": "",
                        "DescripcionResolucion": "",
                        "Prioridad": prioridad_val,
                        "Escalacion": "PRIMERA",
                        "UsuarioCreacion": "operador_qr@empresa.com",
                        "UsuarioCerrado": "",
                        "minutosTranscurridos": 0,
                        "Adhesivo": adhesivo_sel,
                        "Botes": botes_sel,
                        "FolioSurtido": "",
                        "Notificado_30min": "",
                        "Notificado_45min": "",
                        "Notificado_60min": "",
                    }
                ]
            )

            df_folios_actualizado = pd.concat(
                [df_folios, nuevo_folio], ignore_index=True
            )
            conn.update(worksheet="FOLIOS", data=df_folios_actualizado)

            st.session_state["pantalla"] = "historial"
            st.rerun()


# ==============================================================================
# PANTALLA 2: HISTORIAL COMPACTO (Últimos 4 días con Scroll Interno)
# ==============================================================================
elif st.session_state["pantalla"] == "historial":

    st.markdown(
        "<h2 style='text-align: center; font-weight: 800; margin-bottom: 2px; color: #0F172A;'>Folios Recientes</h2>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<div style='text-align: center; color: #334155; font-size: 14px; font-weight: 600; margin-bottom: 16px;'>Registros de los últimos 4 días</div>",
        unsafe_allow_html=True,
    )

    try:
        df_folios = conn.read(worksheet="FOLIOS", ttl=5)
    except Exception as e:
        st.error(f"⚠️ Error al consultar historial: {e}")
        st.stop()

    if not df_folios.empty and "FechaCreacion" in df_folios.columns:
        df_folios["Fecha_dt"] = pd.to_datetime(
            df_folios["FechaCreacion"], errors="coerce"
        )
        hace_4_dias = pd.Timestamp.now() - pd.Timedelta(days=4)
        df_filtrado = df_folios[df_folios["Fecha_dt"] >= hace_4_dias].copy()
        df_filtrado = df_filtrado.sort_values(by="Fecha_dt", ascending=False)

        if not df_filtrado.empty:
            # Construir bloque HTML con scroll interno para evitar scroll de pantalla
            items_html = ""
            for _, row in df_filtrado.iterrows():
                items_html += f"""
                <div class="historial-item-compact">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="font-weight: 700; color: #0F172A; font-size: 13px;">
                            #{row.get('ID_Folio', '')} — {row.get('Linea', '')} (Cabina {row.get('Cabina', '')})
                        </span>
                        <span class="badge-estatus">{row.get('Estatus', 'NUEVO')}</span>
                    </div>
                    <div style="font-size: 12px; color: #475569; margin-top: 4px;">
                        🧪 <b>{row.get('Adhesivo', '')}</b> ({row.get('Botes', '')} Bote) • <span style="color:#64748B;">{row.get('FechaCreacion', '')}</span>
                    </div>
                </div>
                """
            
            # Renderizar en la caja con scroll
            st.markdown(f'<div class="historial-box">{items_html}</div>', unsafe_allow_html=True)
        else:
            st.info("No hay folios registrados en los últimos 4 días.")
    else:
        st.info("No hay registros en la base de datos.")

    if st.button("➕ CREAR OTRO FOLIO"):
        st.session_state["pantalla"] = "formulario"
        st.rerun()
