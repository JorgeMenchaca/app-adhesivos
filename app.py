from datetime import datetime, timedelta
import uuid
import pandas as pd
import streamlit as st
from streamlit_gsheets import GSheetsConnection

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(
    page_title="Gestión de Folios",
    page_icon="📦",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# 2. ESTADO DE NAVEGACIÓN (Control de pantallas)
if "pantalla" not in st.session_state:
    st.session_state["pantalla"] = "formulario"

# 3. ESTILOS CSS PERSONALIZADOS Y FORZADO DE TEMA CLARO
st.markdown(
    """
    <style>
    /* Ocultar elementos de Streamlit */
    #MainMenu, footer, header, [data-testid="stSidebar"] {display: none !important;}
    
    .stApp {
        background-color: #F8FAFC;
    }
    
    .block-container {
        max-width: 520px !important;
        padding-top: 1.5rem !important;
        padding-bottom: 2rem !important;
    }
    
    /* FORZAR COLOR OSCURO EN TODOS LOS TÍTULOS Y ETIQUETAS */
    label, p, span, h1, h2, h3, .stMarkdown {
        color: #0F172A !important;
        font-family: 'Inter', system-ui, sans-serif !important;
    }
    
    /* Estilo de las etiquetas de los inputs */
    [data-testid="stWidgetLabel"] p {
        font-weight: 600 !important;
        font-size: 14px !important;
        color: #1E293B !important;
        margin-bottom: 4px !important;
    }
    
    /* ESTILO MODERNO PARA LOS DROPDOWNS (SELECTBOX) */
    div[data-baseweb="select"] > div {
        background-color: #F8FAFC !important;
        border: 1px solid #CBD5E1 !important;
        border-radius: 10px !important;
        color: #0F172A !important;
    }
    
    div[data-baseweb="select"] * {
        color: #0F172A !important;
        background-color: transparent !important;
    }
    
    /* Contenedor tipo Tarjeta */
    [data-testid="stForm"] {
        background-color: #FFFFFF !important;
        border-radius: 16px !important;
        border: 1px solid #E2E8F0 !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.04) !important;
        padding: 24px !important;
    }
    
    /* Tarjetas del QR */
    .info-card {
        background-color: #F1F5F9;
        border-radius: 12px;
        padding: 12px 16px;
        margin-bottom: 8px;
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

    /* BOTÓN AZUL MODERNO A ANCHO COMPLETO */
    div.stButton > button {
        width: 100% !important;
        background-color: #0284C7 !important;
        color: white !important;
        border: none !important;
        padding: 12px 24px !important;
        font-size: 16px !important;
        font-weight: 700 !important;
        border-radius: 10px !important;
        box-shadow: 0 4px 6px -1px rgba(2, 132, 199, 0.2) !important;
        transition: all 0.2s ease !important;
    }
    div.stButton > button:hover {
        background-color: #0369A1 !important;
    }
    
    /* Tarjeta de Historial */
    .historial-item {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 14px 16px;
        margin-bottom: 12px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }
    .badge-estatus {
        background-color: #DEF7EC;
        color: #03543F !important;
        font-size: 11px;
        font-weight: 700;
        padding: 3px 8px;
        border-radius: 12px;
        float: right;
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
        df_folios = conn.read(worksheet="FOLIOS", ttl=0)
        df_adhesivos = conn.read(worksheet="ADHESIVOS", ttl=0)
        df_prioridad = conn.read(worksheet="PRIORIDAD", ttl=0)
    except Exception as e:
        st.error("⚠️ Error de conexión con Google Sheets.")
        st.stop()

    query_params = st.query_params
    linea_qr = query_params.get("linea", "AUTO WRAPPERS 780B")
    cabina_qr = query_params.get("cabina", "1")
    adhesivo_qr = query_params.get("adhesivo", None)

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
        "<h2 style='text-align: center; font-weight: 800; margin-bottom: 2px;'>Nuevo Folio</h2>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<p style='text-align: center; color: #64748B !important; font-size: 13px; margin-bottom: 20px;'>Registro de material vía QR</p>",
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

    # FORMULARIO CON ESTILO CLARO
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

            # Redirigir a la pantalla de Historial
            st.session_state["pantalla"] = "historial"
            st.rerun()


# ==============================================================================
# PANTALLA 2: HISTORIAL (Últimos 4 días, de más nuevo a más viejo)
# ==============================================================================
elif st.session_state["pantalla"] == "historial":

    st.markdown(
        "<h2 style='text-align: center; font-weight: 800; margin-bottom: 2px;'>Folios Recientes</h2>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<p style='text-align: center; color: #64748B !important; font-size: 13px; margin-bottom: 20px;'>Registros de los últimos 4 días</p>",
        unsafe_allow_html=True,
    )

    # Cargar folios más recientes
    df_folios = conn.read(worksheet="FOLIOS", ttl=0)

    if not df_folios.empty and "FechaCreacion" in df_folios.columns:
        # Convertir FechaCreacion a objeto DateTime
        df_folios["Fecha_dt"] = pd.to_datetime(
            df_folios["FechaCreacion"], errors="coerce"
        )

        # Filtrar: Hoy menos 4 días
        hace_4_dias = pd.Timestamp.now() - pd.Timedelta(days=4)
        df_filtrado = df_folios[df_folios["Fecha_dt"] >= hace_4_dias].copy()

        # Ordenar de más nuevo a más viejo
        df_filtrado = df_filtrado.sort_values(by="Fecha_dt", ascending=False)

        if not df_filtrado.empty:
            for _, row in df_filtrado.iterrows():
                st.markdown(
                    f"""
                    <div class="historial-item">
                        <span class="badge-estatus">{row.get('Estatus', 'NUEVO')}</span>
                        <div style="font-size: 12px; color: #64748B; font-weight: 600;">
                            Folio #{row.get('ID_Folio', '')} • {row.get('FechaCreacion', '')}
                        </div>
                        <div style="font-size: 15px; font-weight: 700; color: #0F172A; margin-top: 4px;">
                            {row.get('Linea', '')} (Cabina {row.get('Cabina', '')})
                        </div>
                        <div style="font-size: 13px; color: #334155; margin-top: 2px;">
                            🧪 <b>{row.get('Adhesivo', '')}</b> — 📦 {row.get('Botes', '')} Bote(s)
                        </div>
                    </div>
                """,
                    unsafe_allow_html=True,
                )
        else:
            st.info("No hay folios registrados en los últimos 4 días.")
    else:
        st.info("No hay registros en la base de datos.")

    st.markdown(
        "<div style='margin-bottom: 16px;'></div>", unsafe_allow_html=True
    )

    if st.button("➕ CREAR OTRO FOLIO"):
        st.session_state["pantalla"] = "formulario"
        st.rerun()
