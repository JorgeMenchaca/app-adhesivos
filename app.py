from datetime import datetime, timedelta
import uuid
import pandas as pd
import streamlit as st
from streamlit_gsheets import GSheetsConnection

# CLAVE DE ACCESO ADMINISTRADOR
CLAVE_ADMIN = "1234"

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(
    page_title="Dashboard | Gestión de Folios",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# HELPER: HORA ZONA CENTRAL MÉXICO (UTC-6)
def hora_mexico():
    return datetime.utcnow() - timedelta(hours=6)

# 2. ESTADO DE NAVEGACIÓN Y SESIÓN
if "pantalla" not in st.session_state:
    st.session_state["pantalla"] = "formulario"
if "folio_atender" not in st.session_state:
    st.session_state["folio_atender"] = None
if "admin_autenticado" not in st.session_state:
    st.session_state["admin_autenticado"] = False

# 3. ESTILOS CSS CON FORZADO DE TARJETAS BLANCAS Y BORDES DEFINIDOS
st.markdown(
    """
    <style>
    #MainMenu, footer, header {display: none !important;}
    
    [data-testid="stSidebarCollapseButton"], 
    [data-testid="collapsedControl"] {
        display: none !important;
    }

    @media (min-width: 768px) {
        [data-testid="stSidebar"] {
            display: block !important;
            visibility: visible !important;
            min-width: 260px !important;
            max-width: 260px !important;
            transform: none !important;
        }
    }
    
    /* FONDO PRINCIPAL PASTEL */
    .stApp {
        background: radial-gradient(at 0% 0%, rgba(224, 231, 255, 0.7) 0px, transparent 50%),
                    radial-gradient(at 100% 0%, rgba(254, 226, 226, 0.7) 0px, transparent 50%),
                    radial-gradient(at 100% 100%, rgba(243, 232, 255, 0.7) 0px, transparent 50%),
                    radial-gradient(at 0% 100%, rgba(224, 242, 254, 0.7) 0px, transparent 50%),
                    #F8FAFC !important;
        background-attachment: fixed !important;
    }
    
    .block-container {
        max-width: 850px !important;
        padding-top: 1.5rem !important;
        padding-bottom: 2rem !important;
        margin: 0 auto !important;
    }

    /* PANEL IZQUIERDO DASHBOARD */
    [data-testid="stSidebar"] {
        background-color: #0F172A !important;
        border-right: 1px solid #1E293B !important;
        padding-top: 1rem !important;
    }
    
    [data-testid="stSidebar"] p, 
    [data-testid="stSidebar"] span {
        color: #F8FAFC !important;
    }
    
    [data-testid="stSidebar"] div.stButton > button {
        width: 100% !important;
        background-color: #1E293B !important;
        color: #F8FAFC !important;
        border: 1px solid #334155 !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        font-size: 14px !important;
        padding: 10px 16px !important;
        margin-bottom: 4px !important;
        transition: all 0.2s ease !important;
        text-align: left !important;
    }
    
    [data-testid="stSidebar"] div.stButton > button:hover {
        background-color: #0284C7 !important;
        color: #FFFFFF !important;
        border-color: #0284C7 !important;
    }

    /* FIX BOTÓN VERDE EN FORMULARIOS */
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

    /* BOTONES GENERALES DE ATENDER */
    div.stButton > button {
        width: 100% !important;
        min-height: 38px !important;
        background-color: #0284C7 !important;
        color: #FFFFFF !important;
        border: none !important;
        font-weight: 700 !important;
        font-size: 13px !important;
        border-radius: 8px !important;
    }

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

    /* SCROLLBAR GRIS OSCURO (#334155) */
    [data-testid="stElementContainer"] .historial-box,
    div[data-testid="stVerticalBlock"] > div {
        max-height: 420px;
    }
    
    ::-webkit-scrollbar {
        width: 10px !important;
    }
    ::-webkit-scrollbar-track {
        background: #E2E8F0 !important;
        border-radius: 10px !important;
    }
    ::-webkit-scrollbar-thumb {
        background-color: #334155 !important;
        border-radius: 10px !important;
        border: 2px solid #E2E8F0 !important;
    }
    ::-webkit-scrollbar-thumb:hover {
        background-color: #0F172A !important;
    }

    /* ------------------------------------------------------------- */
    /* FORZAR TARJETAS BLANCAS CON BORDE Y SEPARACIÓN EN SURTIDO */
    /* ------------------------------------------------------------- */
    div[data-testid="stHorizontalBlock"] {
        background-color: #FFFFFF !important;
        border: 1.5px solid #CBD5E1 !important;
        border-radius: 12px !important;
        padding: 10px 14px !important;
        margin-bottom: 12px !important;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.03) !important;
        align-items: center !important;
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
        padding: 2px 8px;
        border-radius: 10px;
    }
    .badge-pendiente {
        background-color: #FEF3C7;
        color: #92400E !important;
        font-size: 10px;
        font-weight: 700;
        padding: 2px 8px;
        border-radius: 10px;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# 4. CONEXIÓN A GOOGLE SHEETS
conn = st.connection("gsheets", type=GSheetsConnection)


# ==============================================================================
# PANEL IZQUIERDO DE NAVEGACIÓN (SIDEBAR DASHBOARD FIJO)
# ==============================================================================
with st.sidebar:
    st.markdown(
        """
        <div style='text-align: center; padding: 10px 0;'>
            <h2 style='color: #F8FAFC !important; font-weight: 800; margin: 0;'>📦 Adhesivos</h2>
            <p style='color: #38BDF8 !important; font-size: 12px; font-weight: 600; margin-top: 2px;'>Mesa de Control v2.0</p>
        </div>
        <hr style='border-color: #334155; margin-top: 0; margin-bottom: 16px;'>
    """,
        unsafe_allow_html=True,
    )

    st.markdown("<p style='font-size: 11px; color: #94A3B8 !important; font-weight: 700; text-transform: uppercase;'>Navegación</p>", unsafe_allow_html=True)

    if st.button("📋 Nuevo Folio (QR)", use_container_width=True):
        st.session_state["pantalla"] = "formulario"
        st.rerun()

    if st.button("📜 Historial Reciente", use_container_width=True):
        st.session_state["pantalla"] = "historial"
        st.rerun()

    if st.button("📦 Panel de Surtido", use_container_width=True):
        if st.session_state["admin_autenticado"]:
            st.session_state["pantalla"] = "admin_panel"
        else:
            st.session_state["pantalla"] = "admin_login"
        st.rerun()

    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown(
        """
        <div style='background-color: #1E293B; border-radius: 10px; padding: 12px; text-align: center;'>
            <span style='color: #4ADE80 !important; font-size: 12px; font-weight: 700;'>🟢 Servidor Conectado</span><br>
            <span style='color: #94A3B8 !important; font-size: 11px;'>Base de Datos en Tiempo Real</span>
        </div>
    """,
        unsafe_allow_html=True,
    )


# ==============================================================================
# PANTALLA 1: FORMULARIO (OPERADOR QR)
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

    st.markdown(
        "<h2 style='text-align: center; font-weight: 800; margin-bottom: 2px; color: #0F172A;'>Nuevo Folio</h2>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<div style='text-align: center; color: #334155; font-size: 14px; font-weight: 600; margin-bottom: 20px;'>Registro de material vía QR</div>",
        unsafe_allow_html=True,
    )

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
            fecha_actual = hora_mexico().strftime("%m/%d/%Y %H:%M:%S")

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
                        "Escalacion": "",
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
# PANTALLA 2: HISTORIAL
# ==============================================================================
elif st.session_state["pantalla"] == "historial":

    st.markdown(
        "<h2 style='text-align: center; font-weight: 800; margin-bottom: 2px; color: #0F172A;'>Folios Recientes</h2>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<div style='text-align: center; color: #334155; font-size: 14px; font-weight: 600; margin-bottom: 12px;'>Mostrando los 50 más recientes</div>",
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

        busqueda = st.text_input("🔍 Buscar por ID o Línea...", "", placeholder="Ej: 46e9df62 o 780B")
        if busqueda:
            df_filtrado = df_filtrado[
                df_filtrado["ID_Folio"].astype(str).str.contains(busqueda, case=False, na=False) |
                df_filtrado["Linea"].astype(str).str.contains(busqueda, case=False, na=False)
            ]

        df_filtrado_top = df_filtrado.head(50)

        if not df_filtrado_top.empty:
            items_html = ""
            for _, row in df_filtrado_top.iterrows():
                id_f = str(row.get('ID_Folio', ''))
                lin = str(row.get('Linea', ''))
                cab = str(row.get('Cabina', ''))
                est = str(row.get('Estatus', 'NUEVO'))
                adh = str(row.get('Adhesivo', ''))
                bot = str(row.get('Botes', ''))
                fec = str(row.get('FechaCreacion', ''))

                items_html += f'<div class="historial-item-compact"><div style="display: flex; justify-content: space-between; align-items: center;"><span style="font-weight: 700; color: #0F172A; font-size: 13px;">#{id_f} — {lin} (Cabina {cab})</span><span class="badge-estatus">{est}</span></div><div style="font-size: 12px; color: #475569; margin-top: 4px;">🧪 <b>{adh}</b> ({bot} Bote) • <span style="color:#64748B;">{fec}</span></div></div>'
            
            st.markdown(f'<div class="historial-box">{items_html}</div>', unsafe_allow_html=True)
        else:
            st.info("No se encontraron folios recientes.")
    else:
        st.info("No hay registros en la base de datos.")


# ==============================================================================
# PANTALLA 3: LOGIN DE ADMINISTRADOR
# ==============================================================================
elif st.session_state["pantalla"] == "admin_login":

    st.markdown(
        "<h2 style='text-align: center; font-weight: 800; color: #0F172A;'>Acceso Almacén</h2>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<div style='text-align: center; color: #334155; font-size: 14px; margin-bottom: 20px;'>Ingresa la clave para atender folios</div>",
        unsafe_allow_html=True,
    )

    with st.form("form_login"):
        pass_input = st.text_input("Clave de Acceso", type="password", placeholder="****")
        btn_login = st.form_submit_button("INGRESAR AL PANEL")

        if btn_login:
            if pass_input == CLAVE_ADMIN:
                st.session_state["admin_autenticado"] = True
                st.session_state["pantalla"] = "admin_panel"
                st.rerun()
            else:
                st.error("❌ Clave incorrecta.")


# ==============================================================================
# PANTALLA 4: PANEL DE SURTIDO EN VIVO (TARJETAS BLANCAS CON BORDES GARANTIZADAS)
# ==============================================================================
elif st.session_state["pantalla"] == "admin_panel":

    st.markdown(
        "<h2 style='text-align: center; font-weight: 800; color: #0F172A;'>📦 Panel de Surtido en Vivo</h2>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<div style='text-align: center; color: #334155; font-size: 13px; margin-bottom: 16px;'>⏱️ Sincronizado en vivo (Refresco silencioso cada 60s) • Pendientes (30 días)</div>",
        unsafe_allow_html=True,
    )

    @st.fragment(run_every=60)
    def render_panel_surtido():
        df_folios = conn.read(worksheet="FOLIOS", ttl=0)

        if not df_folios.empty and "FechaCreacion" in df_folios.columns:
            df_folios["Fecha_dt"] = pd.to_datetime(df_folios["FechaCreacion"], errors="coerce")
            hace_30_dias = pd.Timestamp.now() - pd.Timedelta(days=30)
            
            df_pendientes = df_folios[
                (df_folios["Fecha_dt"] >= hace_30_dias) & 
                (df_folios["Estatus"].astype(str).str.upper() != "COMPLETADO")
            ].copy()

            df_pendientes = df_pendientes.sort_values(by="Fecha_dt", ascending=False)

            if not df_pendientes.empty:
                with st.container(height=420):
                    for _, row in df_pendientes.iterrows():
                        f_id = str(row.get('ID_Folio', ''))
                        
                        # LAS COLUMNAS SE ESTILIZAN AUTOMÁTICAMENTE COMO TARJETAS BLANCAS CON BORDE CON CSS
                        col_info, col_btn = st.columns([82, 18], vertical_alignment="center")
                        
                        with col_info:
                            st.markdown(
                                f"""
                                <span class="badge-pendiente">{row.get('Estatus', 'NUEVO')}</span>
                                <div style="font-size: 13px; font-weight: 700; color: #0F172A; margin-top: 2px;">
                                    #{f_id} — {row.get('Linea', '')} (Cabina {row.get('Cabina', '')})
                                </div>
                                <div style="font-size: 11px; color: #475569; margin-top: 2px;">
                                    🧪 <b>{row.get('Adhesivo', '')}</b> ({row.get('Botes', '')} Bote) • Prioridad: <b style="color:#D97706;">{row.get('Prioridad', '')}</b> • <span style="color:#64748B;">{row.get('FechaCreacion', '')}</span>
                                </div>
                            """,
                                unsafe_allow_html=True,
                            )
                        
                        with col_btn:
                            if st.button("✏️ Atender", key=f"atender_btn_{f_id}", use_container_width=True):
                                st.session_state["folio_atender"] = f_id
                                st.session_state["pantalla"] = "admin_detalle"
                                st.rerun()

            else:
                st.success("🎉 ¡Excelente! No hay folios pendientes por surtir en los últimos 30 días.")
        else:
            st.info("No hay registros en la base de datos.")

    render_panel_surtido()


# ==============================================================================
# PANTALLA 5: DETALLE Y RESOLUCIÓN DE FOLIO
# ==============================================================================
elif st.session_state["pantalla"] == "admin_detalle":

    folio_id = st.session_state.get("folio_atender", None)
    df_folios = conn.read(worksheet="FOLIOS", ttl=0)

    folio_data = df_folios[df_folios["ID_Folio"].astype(str) == str(folio_id)]

    if not folio_data.empty:
        row = folio_data.iloc[0]

        st.markdown(
            f"<h2 style='text-align: center; font-weight: 800; color: #0F172A;'>Atender Folio #{folio_id}</h2>",
            unsafe_allow_html=True,
        )

        st.markdown(
            f"""
            <div class="info-card">
                <div style="font-size: 13px; color: #334155;"><b>Línea:</b> {row.get('Linea')} | <b>Cabina:</b> {row.get('Cabina')}</div>
                <div style="font-size: 13px; color: #334155;"><b>Adhesivo:</b> {row.get('Adhesivo')} ({row.get('Botes')} Bote)</div>
                <div style="font-size: 13px; color: #334155;"><b>Prioridad:</b> {row.get('Prioridad')} | <b>Creado:</b> {row.get('FechaCreacion')}</div>
            </div>
        """,
            unsafe_allow_html=True,
        )

        with st.form("form_resolucion"):
            folio_surtido_val = st.text_input("Folio Surtido *", placeholder="Ej: 55546")
            descripcion_res_val = st.text_area("Descripción Resolución *", placeholder="Ej: Surtido completo entregado a cabina.")

            btn_finalizar = st.form_submit_button("✅ FINALIZAR Y CERRAR FOLIO")

            if btn_finalizar:
                if not folio_surtido_val or not descripcion_res_val:
                    st.warning("⚠️ Por favor completa ambos campos obligatorios.")
                else:
                    hora_cierre_dt = hora_mexico()
                    fecha_cerrado_str = hora_cierre_dt.strftime("%m/%d/%Y %H:%M:%S")

                    fecha_creacion_dt = pd.to_datetime(row.get("FechaCreacion"), errors="coerce")
                    if pd.notnull(fecha_creacion_dt):
                        minutos_transcurridos = round((hora_cierre_dt - fecha_creacion_dt).total_seconds() / 60.0, 2)
                    else:
                        minutos_transcurridos = 0

                    nivel_cerrado_val = row.get("Escalacion", "PRIMERA")

                    idx = df_folios[df_folios["ID_Folio"].astype(str) == str(folio_id)].index[0]

                    df_folios.at[idx, "Estatus"] = "COMPLETADO"
                    df_folios.at[idx, "FolioSurtido"] = folio_surtido_val
                    df_folios.at[idx, "DescripcionResolucion"] = descripcion_res_val
                    df_folios.at[idx, "FechaCerrado"] = fecha_cerrado_str
                    df_folios.at[idx, "NivelCerrado"] = nivel_cerrado_val
                    df_folios.at[idx, "UsuarioCerrado"] = "Usuario Adhesivo"
                    df_folios.at[idx, "minutosTranscurridos"] = minutos_transcurridos

                    conn.update(worksheet="FOLIOS", data=df_folios)

                    st.toast(f"¡Folio #{folio_id} cerrado con éxito!", icon="✅")
                    st.session_state["pantalla"] = "admin_panel"
                    st.rerun()

    else:
        st.error("No se encontró la información del folio seleccionado.")

    if st.button("⬅️ Cancelar y Volver"):
        st.session_state["pantalla"] = "admin_panel"
        st.rerun()
