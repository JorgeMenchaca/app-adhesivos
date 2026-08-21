from datetime import datetime
import uuid
import pandas as pd
import streamlit as st
from streamlit_gsheets import GSheetsConnection

# 1. CONFIGURACIÓN DE PÁGINA (Minimalista)
st.set_page_config(
    page_title="Captura de Folios",
    page_icon="📦",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# 2. ESTILOS CSS PERSONALIZADOS (Interfaz limpia tipo App Móvil)
st.markdown(
    """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    [data-testid="stSidebar"] {display: none;}
    
    .stApp {
        background-color: #F8FAFC;
    }
    
    .block-container {
        max-width: 500px !important;
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
    }
    
    [data-testid="stForm"] {
        background-color: #FFFFFF;
        border-radius: 16px;
        border: 1px solid #E2E8F0;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.03);
        padding: 24px;
    }
    
    .info-card {
        background-color: #F1F5F9;
        border-radius: 12px;
        padding: 12px 16px;
        margin-bottom: 8px;
        border-left: 4px solid #0284C7;
    }
    .info-label {
        font-size: 11px;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        font-weight: 600;
    }
    .info-value {
        font-size: 15px;
        color: #0F172A;
        font-weight: 600;
    }

    div.stButton > button {
        width: 100%;
        background-color: #0284C7 !important;
        color: white !important;
        border: none !important;
        padding: 12px 24px !important;
        font-size: 16px !important;
        font-weight: 600 !important;
        border-radius: 10px !important;
        box-shadow: 0 2px 4px rgba(2, 132, 199, 0.2);
        transition: all 0.2s ease;
    }
    div.stButton > button:hover {
        background-color: #0369A1 !important;
        transform: translateY(-1px);
    }
    </style>
""",
    unsafe_allow_html=True,
)

# 3. CONEXIÓN A GOOGLE SHEETS
conn = st.connection("gsheets", type=GSheetsConnection)

try:
    df_folios = conn.read(worksheet="FOLIOS", ttl=0)
    df_adhesivos = conn.read(worksheet="ADHESIVOS", ttl=0)
    df_prioridad = conn.read(worksheet="PRIORIDAD", ttl=0)
except Exception as e:
    st.error("⚠️ Error de conexión con Google Sheets.")
    st.stop()

# 4. CAPTURA DE PARÁMETROS DESDE EL CÓDIGO QR
query_params = st.query_params
linea_qr = query_params.get("linea", "AUTO WRAPPERS 780B")
cabina_qr = query_params.get("cabina", "1")
adhesivo_qr = query_params.get(
    "adhesivo", None
)  # Nuevo parámetro capturado del QR

# 5. FILTRADO Y SELECCIÓN AUTOMÁTICA EN TIEMPO REAL
adhesivos_disponibles = df_adhesivos[
    df_adhesivos["DescripcionLinea"] == linea_qr
]["Adhesivo"].dropna().unique().tolist()

if not adhesivos_disponibles:
    adhesivos_disponibles = ["ADHESIVO 09 (GENERAL)"]

# Determinar el índice por defecto del Adhesivo enviando por QR
index_adhesivo = 0
if adhesivo_qr and adhesivo_qr in adhesivos_disponibles:
    index_adhesivo = adhesivos_disponibles.index(adhesivo_qr)

# Buscar Prioridad en la pestaña PRIORIDAD
match_prioridad = df_prioridad[df_prioridad["LINEA"] == linea_qr]
prioridad_val = (
    match_prioridad["PRIORIDAD"].values[0]
    if not match_prioridad.empty
    else "MEDIA"
)


# 6. ESTRUCTURA VISUAL

st.markdown(
    "<h2 style='text-align: center; color: #0F172A; margin-bottom: 4px; font-weight: 700;'>Nuevo Folio</h2>",
    unsafe_allow_html=True,
)
st.markdown(
    "<p style='text-align: center; color: #64748B; font-size: 14px; margin-bottom: 24px;'>Registro de material vía QR</p>",
    unsafe_allow_html=True,
)

# Tarjetas informativas superiores (Línea, Cabina, Prioridad)
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

st.markdown("<div style='margin-bottom: 12px;'></div>", unsafe_allow_html=True)

# Formulario
with st.form("form_minimalista", clear_on_submit=True):

    # Dropdown de Adhesivos (Pre-seleccionado automáticamente si venía en el QR)
    adhesivo_sel = st.selectbox(
        "Adhesivo *", options=adhesivos_disponibles, index=index_adhesivo
    )

    # Dropdown de Botes con las opciones exactas: 1, 1/2 y 1/4
    botes_sel = st.selectbox(
        "Cantidad de Botes *", options=["1", "1/2", "1/4"], index=0
    )

    st.markdown(
        "<div style='margin-bottom: 16px;'></div>", unsafe_allow_html=True
    )

    btn_guardar = st.form_submit_button("GUARDAR FOLIO")

    # 7. GUARDAR EN GOOGLE SHEETS
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

        st.toast(f"¡Folio {nuevo_id} guardado con éxito!", icon="🎉")
        st.success(
            f"✅ **Folio registrado correctamente**\n\nID Asignado: `{nuevo_id}`"
        )