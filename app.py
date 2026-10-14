# archivo: app.py
import streamlit as st
import requests
import imaplib
import email
from email.header import decode_header
from email.utils import parsedate_to_datetime
from datetime import datetime
import html

st.set_page_config(
    page_title="Outlook QuickReader",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ==========================================
# SISTEMA DE DISEÑO CSS (MODERNO, ALINEADO Y RESPONSIVO)
# ==========================================
modern_ui_css = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

/* Tipografía global segura (SIN romper Material Icons como 'visibility') */
html, body, .stApp, p, h1, h2, h3, h4, label, input, textarea, button {
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
}

/* Fondo general con contraste suave para que las tarjetas blancas resalten */
.stApp {
    background-color: #f1f5f9;
    color: #0f172a;
}

/* Ocultar barra superior y pie de página de Streamlit */
div[data-testid="stToolbar"], footer, header {
    display: none !important;
}

/* Contenedor principal centrado y bien proporcionado */
.block-container {
    max-width: 720px !important;
    padding-top: 2rem !important;
    padding-bottom: 4rem !important;
    padding-left: 1.25rem !important;
    padding-right: 1.25rem !important;
}

/* Banner Principal Superior (Dark Slate) */
.hero-header {
    background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
    border-radius: 16px;
    padding: 24px 28px;
    color: #ffffff;
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 12px;
    margin-bottom: 20px;
    box-shadow: 0 10px 25px -5px rgba(15, 23, 42, 0.15);
    border: 1px solid rgba(255, 255, 255, 0.08);
}

.hero-title {
    font-size: 22px;
    font-weight: 700;
    color: #ffffff !important;
    margin: 0;
    letter-spacing: -0.02em;
}

.hero-subtitle {
    font-size: 13px;
    color: #94a3b8 !important;
    margin: 4px 0 0 0;
    font-weight: 400;
}

.hero-badge {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 11px;
    font-weight: 600;
    color: #38bdf8;
    background: rgba(56, 189, 248, 0.12);
    border: 1px solid rgba(56, 189, 248, 0.25);
    padding: 6px 12px;
    border-radius: 999px;
    white-space: nowrap;
}

/* Pestañas estilo Segmented Control (Píldora moderna) */
.stTabs [data-baseweb="tab-list"] {
    background-color: #e2e8f0;
    padding: 5px;
    border-radius: 12px;
    gap: 6px;
    border-bottom: none !important;
    margin-bottom: 16px;
}

.stTabs [data-baseweb="tab"] {
    flex: 1;
    justify-content: center;
    height: 40px;
    border-radius: 8px !important;
    background-color: transparent !important;
    color: #475569 !important;
    font-weight: 600 !important;
    font-size: 13.5px !important;
    border: none !important;
    transition: all 0.15s ease;
}

.stTabs [aria-selected="true"] {
    background-color: #ffffff !important;
    color: #0f172a !important;
    box-shadow: 0 2px 8px rgba(15, 23, 42, 0.08) !important;
}

.stTabs [data-baseweb="tab-highlight"] {
    display: none !important;
}

/* Tarjetas blancas (st.container(border=True)) */
div[data-testid="stVerticalBlockBorderWrapper"] {
    background-color: #ffffff !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 16px !important;
    padding: 22px !important;
    box-shadow: 0 4px 12px -2px rgba(15, 23, 42, 0.04) !important;
    margin-bottom: 16px !important;
}

/* Etiquetas de los campos (Labels) perfectamente alineadas */
div[data-testid="stWidgetLabel"] p {
    font-size: 13px !important;
    font-weight: 600 !important;
    color: #1e293b !important;
    margin-bottom: 4px !important;
}

/* Contenedores de Inputs y Textareas limpios (Sin fondo gris feo) */
div[data-baseweb="input"],
div[data-baseweb="textarea"],
div[data-baseweb="select"] > div {
    background-color: #f8fafc !important;
    border: 1.5px solid #cbd5e1 !important;
    border-radius: 10px !important;
    transition: all 0.15s ease !important;
}

div[data-baseweb="input"] > div {
    background-color: transparent !important;
    border: none !important;
}

div[data-baseweb="input"] input,
div[data-baseweb="textarea"] textarea {
    background-color: transparent !important;
    color: #0f172a !important;
    font-size: 13.5px !important;
    padding: 10px 12px !important;
}

div[data-baseweb="textarea"] textarea {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 12.5px !important;
    line-height: 1.5 !important;
}

div[data-baseweb="input"]:focus-within,
div[data-baseweb="textarea"]:focus-within,
div[data-baseweb="select"] > div:focus-within {
    background-color: #ffffff !important;
    border-color: #2563eb !important;
    box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.12) !important;
}

/* Ocultar el botón de mostrar contraseña si la fuente de iconos falla en móvil */
div[data-baseweb="input"] button {
    display: none !important;
}

/* Botón Primario (Modern Blue / Dark Hover) */
div.stButton > button[kind="primary"] {
    background: linear-gradient(180deg, #2563eb 0%, #1d4ed8 100%) !important;
    color: #ffffff !important;
    font-weight: 600 !important;
    font-size: 14px !important;
    height: 44px !important;
    border-radius: 10px !important;
    border: 1px solid #1e40af !important;
    box-shadow: 0 2px 6px rgba(37, 99, 235, 0.25) !important;
    transition: all 0.15s ease !important;
}

div.stButton > button[kind="primary"]:hover {
    background: linear-gradient(180deg, #1d4ed8 0%, #1e3a8a 100%) !important;
    box-shadow: 0 4px 12px rgba(37, 99, 235, 0.35) !important;
}

/* Botón Secundario */
div.stButton > button[kind="secondary"] {
    background-color: #ffffff !important;
    color: #334155 !important;
    font-weight: 600 !important;
    font-size: 13.5px !important;
    height: 42px !important;
    border-radius: 10px !important;
    border: 1.5px solid #cbd5e1 !important;
}

div.stButton > button[kind="secondary"]:hover {
    background-color: #f8fafc !important;
    border-color: #94a3b8 !important;
    color: #0f172a !important;
}

/* Encabezado interno de secciones */
.section-header {
    margin-bottom: 16px;
    padding-bottom: 12px;
    border-bottom: 1px solid #f1f5f9;
}

.section-title {
    font-size: 16px;
    font-weight: 700;
    color: #0f172a;
    margin: 0 0 4px 0;
}

.section-desc {
    font-size: 13px;
    color: #64748b;
    margin: 0;
}

/* Tarjeta de estado vacío elegante */
.empty-state-card {
    background: #ffffff;
    border: 1.5px dashed #cbd5e1;
    border-radius: 16px;
    padding: 40px 24px;
    text-align: center;
    margin-top: 8px;
}

.empty-badge {
    display: inline-block;
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: #475569;
    background: #f1f5f9;
    padding: 4px 10px;
    border-radius: 6px;
    margin-bottom: 10px;
}

.empty-title {
    font-size: 15px;
    font-weight: 700;
    color: #0f172a;
    margin: 0 0 6px 0;
}

.empty-text {
    font-size: 13px;
    color: #64748b;
    max-width: 420px;
    margin: 0 auto;
    line-height: 1.5;
}

/* Visor de Correo */
.mail-card-header {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 16px 18px;
    margin-bottom: 14px;
}

.mail-subject {
    font-size: 16px;
    font-weight: 700;
    color: #0f172a;
    margin: 0 0 8px 0;
    line-height: 1.35;
}

.mail-meta {
    display: flex;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 8px;
    font-size: 12.5px;
    color: #64748b;
}

.mail-sender-pill {
    color: #1e293b;
    font-weight: 600;
}

/* Panel de Código de Dispositivo OAuth */
.oauth-box {
    background: #f8fafc;
    border: 1.5px solid #cbd5e1;
    border-radius: 14px;
    padding: 24px 20px;
    text-align: center;
    margin: 18px 0;
}

.oauth-step {
    font-size: 11.5px;
    font-weight: 700;
    color: #2563eb;
    text-transform: uppercase;
    letter-spacing: 0.06em;
}

.oauth-code {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 28px;
    font-weight: 700;
    letter-spacing: 4px;
    color: #0f172a;
    background: #ffffff;
    border: 1.5px solid #94a3b8;
    border-radius: 10px;
    padding: 10px 22px;
    display: inline-block;
    margin: 12px 0 16px 0;
    box-shadow: 0 2px 4px rgba(0,0,0,0.04);
}

.oauth-link {
    display: inline-block;
    background: #0f172a;
    color: #ffffff !important;
    text-decoration: none !important;
    font-weight: 600;
    font-size: 13.5px;
    padding: 10px 20px;
    border-radius: 8px;
}

/* Píldora de estado conectado */
.sync-bar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: #ecfdf5;
    border: 1px solid #a7f3d0;
    color: #065f46;
    padding: 10px 16px;
    border-radius: 10px;
    font-size: 13px;
    font-weight: 600;
    margin-bottom: 14px;
}
</style>
"""
st.markdown(modern_ui_css, unsafe_allow_html=True)

# ==========================================
# INICIALIZACIÓN DE SESSION STATE
# ==========================================
for key, default in {
    "correos": None,
    "metodo_usado": "",
    "credencial_actualizada": "",
    "credenciales_input": "",
    "correo_idx": 0
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# ==========================================
# FUNCIONES DE CONEXIÓN Y LECTURA
# ==========================================
def formatear_fecha(fecha_str):
    if not fecha_str:
        return ""
    try:
        if "T" in fecha_str:
            dt = datetime.fromisoformat(fecha_str.replace("Z", "+00:00"))
            return dt.strftime("%d %b %Y, %H:%M")
        dt = parsedate_to_datetime(fecha_str)
        return dt.strftime("%d %b %Y, %H:%M")
    except Exception:
        return fecha_str[:22]

def envolver_html_correo(contenido_html):
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                font-size: 14px;
                line-height: 1.6;
                color: #1e293b;
                background-color: #ffffff;
                margin: 0;
                padding: 12px;
                word-wrap: break-word;
            }}
            a {{ color: #2563eb; }}
            img {{ max-width: 100%; height: auto; border-radius: 4px; }}
            pre {{
                white-space: pre-wrap;
                font-family: ui-monospace, monospace;
                font-size: 13px;
                background: #f8fafc;
                padding: 12px;
                border-radius: 8px;
                border: 1px solid #e2e8f0;
            }}
        </style>
    </head>
    <body>{contenido_html}</body>
    </html>
    """

def obtener_access_token_multivia(client_id, refresh_token):
    endpoints = [
        ("https://login.microsoftonline.com/common/oauth2/v2.0/token", {
            "client_id": client_id.strip(),
            "refresh_token": refresh_token.strip(),
            "grant_type": "refresh_token",
        }),
        ("https://login.microsoftonline.com/consumers/oauth2/v2.0/token", {
            "client_id": client_id.strip(),
            "refresh_token": refresh_token.strip(),
            "grant_type": "refresh_token",
        }),
        ("https://login.live.com/oauth20_token.srf", {
            "client_id": client_id.strip(),
            "refresh_token": refresh_token.strip(),
            "grant_type": "refresh_token",
        })
    ]
    ultimo_error = {}
    for url, datos in endpoints:
        try:
            r = requests.post(url, data=datos, timeout=10)
            res_json = r.json()
            if "access_token" in res_json:
                return res_json
            ultimo_error = res_json
        except Exception as e:
            ultimo_error = {"error": str(e)}
    return ultimo_error

def leer_via_graph_api(access_token, cantidad=15):
    headers = {"Authorization": f"Bearer {access_token}"}
    url = f"https://graph.microsoft.com/v1.0/me/messages?$top={cantidad}&$select=subject,from,receivedDateTime,body"
    r = requests.get(url, headers=headers, timeout=12)
    if r.status_code != 200:
        return None
    datos = r.json()
    lista_correos = []
    for msg in datos.get("value", []):
        remitente_info = msg.get("from", {}).get("emailAddress", {})
        nombre = remitente_info.get("name", "").strip()
        direccion = remitente_info.get("address", "").strip()
        remitente = f"{nombre} <{direccion}>" if nombre and nombre != direccion else direccion
        lista_correos.append({
            "asunto": msg.get("subject") or "(Sin asunto)",
            "remitente": remitente or "Desconocido",
            "fecha": formatear_fecha(msg.get("receivedDateTime", "")),
            "cuerpo": msg.get("body", {}).get("content", "")
        })
    return lista_correos

def decodificar_texto(texto):
    if not texto:
        return ""
    partes = decode_header(texto)
    resultado = ""
    for parte, codificacion in partes:
        if isinstance(parte, bytes):
            resultado += parte.decode(codificacion or "utf-8", errors="ignore")
        else:
            resultado += parte
    return resultado

def extraer_cuerpo(msg):
    cuerpo_html = ""
    cuerpo_texto = ""
    if msg.is_multipart():
        for part in msg.walk():
            tipo = part.get_content_type()
            disp = str(part.get("Content-Disposition"))
            if "attachment" not in disp:
                if tipo == "text/plain" and not cuerpo_texto:
                    payload = part.get_payload(decode=True)
                    if payload:
                        cuerpo_texto = payload.decode(errors="ignore")
                elif tipo == "text/html" and not cuerpo_html:
                    payload = part.get_payload(decode=True)
                    if payload:
                        cuerpo_html = payload.decode(errors="ignore")
    else:
        tipo = msg.get_content_type()
        payload = msg.get_payload(decode=True)
        if payload:
            if tipo == "text/html":
                cuerpo_html = payload.decode(errors="ignore")
            else:
                cuerpo_texto = payload.decode(errors="ignore")
    return cuerpo_html if cuerpo_html else f"<pre>{html.escape(cuerpo_texto)}</pre>"

def leer_correos_imap(correo, access_token, cantidad=15):
    auth_string = f"user={correo}\x01auth=Bearer {access_token}\x01\x01"
    mail = imaplib.IMAP4_SSL("outlook.office365.com", 993)
    mail.authenticate("XOAUTH2", lambda x: auth_string.encode("utf-8"))
    mail.select("INBOX")
    estado, mensajes = mail.search(None, "ALL")
    ids_correos = mensajes[0].split()
    if not ids_correos:
        mail.logout()
        return []
    ultimos_ids = ids_correos[-cantidad:][::-1]
    lista_correos = []
    for i in ultimos_ids:
        res, msg_data = mail.fetch(i, "(RFC822)")
        for response_part in msg_data:
            if isinstance(response_part, tuple):
                msg = email.message_from_bytes(response_part[1])
                lista_correos.append({
                    "asunto": decodificar_texto(msg.get("Subject", "(Sin asunto)")),
                    "remitente": decodificar_texto(msg.get("From", "Desconocido")),
                    "fecha": formatear_fecha(msg.get("Date", "")),
                    "cuerpo": extraer_cuerpo(msg)
                })
    mail.logout()
    return lista_correos

# ==========================================
# CABECERA SUPERIOR (HERO BANNER)
# ==========================================
st.markdown("""
<div class="hero-header">
    <div>
        <h1 class="hero-title">Outlook QuickReader</h1>
        <p class="hero-subtitle">Sincronización directa por Graph API e IMAP XOAUTH2</p>
    </div>
    <span class="hero-badge">OAUTH 2.0</span>
</div>
""", unsafe_allow_html=True)

tab_lector, tab_generador = st.tabs(["Bandeja de Entrada", "Generador de Token OAuth2"])

# ==========================================
# PESTAÑA 1: BANDEJA DE ENTRADA
# ==========================================
with tab_lector:
    with st.container(border=True):
        st.markdown("""
        <div class="section-header">
            <h2 class="section-title">Credenciales de conexión</h2>
            <p class="section-desc">Pega tu línea de acceso completa para autenticar y descargar tu bandeja.</p>
        </div>
        """, unsafe_allow_html=True)
        
        credenciales = st.text_area(
            "Cadena de acceso (email|password|refresh_token|client_id)",
            value=st.session_state["credenciales_input"],
            placeholder="usuario@outlook.com|contraseña|M.C501...|9e5f94bc-e8a4-4e73-b8be-63364c29d753",
            height=95
        )
        st.session_state["credenciales_input"] = credenciales
        
        col_btn, col_limit = st.columns([2.2, 1])
        with col_limit:
            cantidad_mensajes = st.selectbox(
                "Cantidad a cargar",
                options=["10 mensajes", "20 mensajes", "35 mensajes", "50 mensajes"],
                index=0,
                label_visibility="collapsed"
            )
            limite_num = int(cantidad_mensajes.split()[0])
        with col_btn:
            consultar_btn = st.button("Sincronizar Bandeja de Entrada", type="primary", use_container_width=True)

    if consultar_btn:
        if not credenciales or "|" not in credenciales:
            st.warning("Formato requerido: email|password|refresh_token|client_id")
        else:
            partes = [p.strip() for p in credenciales.strip().split("|")]
            if len(partes) < 4 or not all([partes[0], partes[2], partes[3]]):
                st.error("Faltan datos en la cadena. Verifica que incluya las 4 partes separadas por '|'.")
            else:
                correo, password, refresh_token, client_id = partes[0], partes[1], partes[2], partes[3]
                with st.spinner("Autenticando sesión OAuth2 con Microsoft..."):
                    token_data = obtener_access_token_multivia(client_id, refresh_token)
                    
                    if "access_token" not in token_data:
                        st.error("El Refresh Token expiró o es inválido (invalid_grant). Genera uno nuevo en la pestaña 'Generador de Token OAuth2'.")
                        with st.expander("Ver respuesta del servidor"):
                            st.json(token_data)
                    else:
                        access_token = token_data["access_token"]
                        nuevo_refresh = token_data.get("refresh_token", refresh_token)
                        st.session_state["credencial_actualizada"] = f"{correo}|{password}|{nuevo_refresh}|{client_id}"
                        
                        try:
                            correos = leer_via_graph_api(access_token, cantidad=limite_num)
                            if correos is not None:
                                st.session_state["metodo_usado"] = "Microsoft Graph API"
                            else:
                                correos = leer_correos_imap(correo, access_token, cantidad=limite_num)
                                st.session_state["metodo_usado"] = "IMAP XOAUTH2"
                                
                            st.session_state["correos"] = correos
                            st.session_state["correo_idx"] = 0
                        except Exception as e:
                            st.error(f"Error al leer la bandeja: {str(e)}")

    # Mostrar Bandeja si hay sesión activa
    if st.session_state["correos"] is not None:
        correos = st.session_state["correos"]
        
        st.markdown(f"""
        <div class="sync-bar">
            <span>Sesión activa vía {st.session_state['metodo_usado']}</span>
            <span>{len(correos)} mensajes recibidos</span>
        </div>
        """, unsafe_allow_html=True)

        if st.session_state["credencial_actualizada"]:
            with st.expander("Copiar credencial con Refresh Token renovado"):
                st.code(st.session_state["credencial_actualizada"], language="text")

        if len(correos) == 0:
            st.markdown("""
            <div class="empty-state-card">
                <span class="empty-badge">Bandeja vacía</span>
                <h3 class="empty-title">No hay mensajes</h3>
                <p class="empty-text">La cuenta se autenticó correctamente pero no tiene correos en la bandeja de entrada.</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            with st.container(border=True):
                filtro = st.text_input(
                    "Buscar en la bandeja",
                    placeholder="Filtrar por asunto o remitente..."
                )
                
                correos_filtrados = [
                    c for c in correos
                    if filtro.lower() in c["asunto"].lower() or filtro.lower() in c["remitente"].lower()
                ] if filtro else correos

                if not correos_filtrados:
                    st.info("No hay mensajes que coincidan con tu búsqueda.")
                else:
                    opciones_indices = list(range(len(correos_filtrados)))
                    
                    def formatear_opcion(i):
                        c = correos_filtrados[i]
                        rem = c["remitente"].split("<")[0].strip() or c["remitente"]
                        return f"{ i + 1 }. {c['asunto'][:55]}  —  {rem[:28]} ({c['fecha']})"

                    seleccion = st.selectbox(
                        f"Seleccionar mensaje ({len(correos_filtrados)} disponibles)",
                        options=opciones_indices,
                        format_func=formatear_opcion,
                        index=min(st.session_state["correo_idx"], len(correos_filtrados) - 1)
                    )
                    st.session_state["correo_idx"] = seleccion
                    correo_actual = correos_filtrados[seleccion]

                    # Botones de navegación rápida Anterior / Siguiente
                    col_prev, col_pos, col_next = st.columns([1, 1.5, 1])
                    with col_prev:
                        if st.button("Anterior", type="secondary", disabled=(seleccion == 0), use_container_width=True):
                            st.session_state["correo_idx"] = max(0, seleccion - 1)
                            st.rerun()
                    with col_pos:
                        st.markdown(
                            f"<div style='text-align:center; padding-top:10px; font-size:12.5px; font-weight:600; color:#64748b;'>Mensaje {seleccion + 1} de {len(correos_filtrados)}</div>",
                            unsafe_allow_html=True
                        )
                    with col_next:
                        if st.button("Siguiente", type="secondary", disabled=(seleccion >= len(correos_filtrados) - 1), use_container_width=True):
                            st.session_state["correo_idx"] = min(len(correos_filtrados) - 1, seleccion + 1)
                            st.rerun()

                    st.markdown("<hr style='border:none; border-top:1px solid #e2e8f0; margin: 14px 0;'>", unsafe_allow_html=True)

                    asunto_seguro = html.escape(correo_actual["asunto"])
                    remitente_seguro = html.escape(correo_actual["remitente"])
                    fecha_segura = html.escape(correo_actual["fecha"])

                    st.markdown(f"""
                    <div class="mail-card-header">
                        <h3 class="mail-subject">{asunto_seguro}</h3>
                        <div class="mail-meta">
                            <span>De: <span class="mail-sender-pill">{remitente_seguro}</span></span>
                            <span>{fecha_segura}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    st.components.v1.html(
                        envolver_html_correo(correo_actual["cuerpo"]),
                        height=440,
                        scrolling=True
                    )
    else:
        st.markdown("""
        <div class="empty-state-card">
            <span class="empty-badge">Listo para conectar</span>
            <h3 class="empty-title">Ninguna sesión sincronizada</h3>
            <p class="empty-text">Introduce tu cadena de credenciales en la tarjeta superior y pulsa "Sincronizar Bandeja de Entrada" para visualizar tus correos.</p>
        </div>
        """, unsafe_allow_html=True)

# ==========================================
# PESTAÑA 2: GENERADOR DE TOKEN OAUTH2
# ==========================================
with tab_generador:
    with st.container(border=True):
        st.markdown("""
        <div class="section-header">
            <h2 class="section-title">Autorización por Código de Dispositivo (OAuth 2.0)</h2>
            <p class="section-desc">Vincula tu cuenta oficial de Microsoft para obtener un Refresh Token nuevo sin exponer tus credenciales.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Fila 1: 2 columnas limpias con etiquetas cortas que nunca se parten
        col_mail, col_pass = st.columns(2)
        with col_mail:
            gen_email = st.text_input(
                "Correo electrónico",
                placeholder="usuario@outlook.com"
            )
        with col_pass:
            gen_pass = st.text_input(
                "Contraseña (opcional para cadena)",
                type="password",
                placeholder="••••••••••••"
            )
            
        # Fila 2: Client ID a ancho completo para que el UUID se lea entero sin cortarse
        gen_client_id = st.text_input(
            "Client ID de la aplicación (Azure AD / Thunderbird)",
            value="9e5f94bc-e8a4-4e73-b8be-63364c29d753"
        )
        
        st.markdown("<div style='height: 6px;'></div>", unsafe_allow_html=True)
        
        if st.button("Solicitar Código de Vinculación", type="primary", use_container_width=True):
            if not gen_email or not gen_client_id:
                st.warning("Completa al menos el correo electrónico y el Client ID.")
            else:
                url_device = "https://login.microsoftonline.com/common/oauth2/v2.0/devicecode"
                scopes = "offline_access Mail.Read"
                try:
                    r = requests.post(url_device, data={"client_id": gen_client_id.strip(), "scope": scopes}, timeout=10)
                    datos_dev = r.json()
                    
                    if "user_code" in datos_dev:
                        st.session_state["device_code"] = datos_dev["device_code"]
                        st.session_state["user_code"] = datos_dev["user_code"]
                        st.session_state["verification_uri"] = datos_dev.get("verification_uri", "https://microsoft.com/devicelogin")
                    else:
                        st.error("Microsoft rechazó la generación del código.")
                        st.json(datos_dev)
                except Exception as e:
                    st.error(f"Error de conexión: {str(e)}")

        if "user_code" in st.session_state:
            st.markdown(f"""
            <div class="oauth-box">
                <div class="oauth-step">Paso 1 — Autorización en Microsoft</div>
                <div class="oauth-code">{st.session_state['user_code']}</div>
                <div>
                    <a href="{st.session_state['verification_uri']}" target="_blank" class="oauth-link">
                        Abrir portal de activación de Microsoft
                    </a>
                </div>
                <p style="font-size: 12.5px; color: #64748b; margin: 14px 0 0 0;">
                    Abre el enlace en una pestaña de incógnito, inicia sesión con <b>{html.escape(gen_email)}</b> e introduce el código.
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            col_ok, col_cancel = st.columns([2, 1])
            with col_ok:
                if st.button("Confirmar y Obtener Refresh Token", type="primary", use_container_width=True):
                    url_token = "https://login.microsoftonline.com/common/oauth2/v2.0/token"
                    r_tok = requests.post(url_token, data={
                        "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
                        "client_id": gen_client_id.strip(),
                        "device_code": st.session_state["device_code"]
                    }, timeout=10)
                    res_tok = r_tok.json()
                    
                    if "refresh_token" in res_tok:
                        nuevo_rt = res_tok["refresh_token"]
                        pass_val = gen_pass.strip() if gen_pass else "PASSWORD"
                        linea_final = f"{gen_email.strip()}|{pass_val}|{nuevo_rt}|{gen_client_id.strip()}"
                        st.session_state["credencial_generada_nueva"] = linea_final
                        del st.session_state["user_code"]
                        st.rerun()
                    else:
                        err = res_tok.get("error", "")
                        if err == "authorization_pending":
                            st.info("Aún no has finalizado la autorización en la página de Microsoft.")
                        else:
                            st.error(f"Error al canjear el código: {res_tok.get('error_description', err)}")
            with col_cancel:
                if st.button("Cancelar", type="secondary", use_container_width=True):
                    del st.session_state["user_code"]
                    st.rerun()

        if "credencial_generada_nueva" in st.session_state:
            st.markdown("<hr style='border:none; border-top:1px solid #e2e8f0; margin: 16px 0;'>", unsafe_allow_html=True)
            st.success("Credencial generada exitosamente:")
            st.code(st.session_state["credencial_generada_nueva"], language="text")
            if st.button("Enviar esta credencial a la Bandeja de Entrada", type="secondary", use_container_width=True):
                st.session_state["credenciales_input"] = st.session_state["credencial_generada_nueva"]
                st.info("Listo. Abre la pestaña 'Bandeja de Entrada' y pulsa 'Sincronizar Bandeja de Entrada'.")
