# archivo: app.py
import streamlit as st
import requests
import imaplib
import email
from email.header import decode_header
from email.utils import parsedate_to_datetime
from datetime import datetime, timezone
import html

st.set_page_config(
    page_title="Outlook QuickReader",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ==========================================
# CSS AVANZADO COMPATIBLE CON STREAMLIT CLOUD
# ==========================================
polished_css = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

:root {
    --primary-color: #2563eb !important;
}

html, body, .stApp, p, label, input, textarea, button {
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
}

.stApp {
    background-color: #f1f5f9 !important;
    color: #0f172a !important;
}

div[data-testid="stToolbar"], footer, header {
    display: none !important;
}

.block-container {
    max-width: 700px !important;
    padding-top: 1.5rem !important;
    padding-bottom: 3.5rem !important;
    padding-left: 1rem !important;
    padding-right: 1rem !important;
}

/* Cabecera Principal Limpia */
.hero-header {
    background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
    border-radius: 14px;
    padding: 20px 24px;
    color: #ffffff;
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 12px;
    margin-bottom: 16px;
    box-shadow: 0 8px 20px -4px rgba(15, 23, 42, 0.14);
}

.hero-title {
    font-size: 20px !important;
    font-weight: 700 !important;
    color: #ffffff !important;
    margin: 0 !important;
    padding: 0 !important;
    letter-spacing: -0.02em;
    line-height: 1.2 !important;
}

.hero-subtitle {
    font-size: 13px !important;
    color: #94a3b8 !important;
    margin: 4px 0 0 0 !important;
    font-weight: 400 !important;
}

/* Pestañas Segmented Control */
div[data-testid="stTabs"] [data-baseweb="tab-list"] {
    background-color: #e2e8f0 !important;
    padding: 4px !important;
    border-radius: 10px !important;
    gap: 4px !important;
    border-bottom: none !important;
    margin-bottom: 14px !important;
}

div[data-testid="stTabs"] button[data-baseweb="tab"] {
    flex: 1 !important;
    justify-content: center !important;
    height: 38px !important;
    border-radius: 7px !important;
    background-color: transparent !important;
    color: #475569 !important;
    font-weight: 600 !important;
    font-size: 13px !important;
    border: none !important;
    margin: 0 !important;
}

div[data-testid="stTabs"] button[data-baseweb="tab"] p {
    color: inherit !important;
    font-weight: 600 !important;
    font-size: 13px !important;
}

div[data-testid="stTabs"] button[data-baseweb="tab"][aria-selected="true"] {
    background-color: #ffffff !important;
    color: #2563eb !important;
    box-shadow: 0 1px 4px rgba(15, 23, 42, 0.08) !important;
}

div[data-testid="stTabs"] button[data-baseweb="tab"][aria-selected="true"] p {
    color: #2563eb !important;
}

div[data-testid="stTabs"] [data-baseweb="tab-highlight"],
div[data-testid="stTabs"] [data-baseweb="tab-border"] {
    display: none !important;
    background-color: transparent !important;
    height: 0px !important;
}

/* Tarjetas Blancas Reales */
div[data-testid="stVerticalBlockBorderWrapper"],
div[class*="st-key-card_"] {
    background-color: #ffffff !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 14px !important;
    padding: 20px !important;
    box-shadow: 0 2px 10px rgba(15, 23, 42, 0.03) !important;
}

.card-header {
    margin-bottom: 14px;
    padding-bottom: 12px;
    border-bottom: 1px solid #f1f5f9;
}

.card-title {
    font-size: 15px !important;
    font-weight: 700 !important;
    color: #0f172a !important;
    margin: 0 0 3px 0 !important;
    line-height: 1.3 !important;
}

.card-desc {
    font-size: 12.5px !important;
    color: #64748b !important;
    margin: 0 !important;
    line-height: 1.4 !important;
}

/* Labels, Inputs y Placeholders */
div[data-testid="stWidgetLabel"] p {
    font-size: 12.5px !important;
    font-weight: 600 !important;
    color: #334155 !important;
}

div[data-baseweb="input"],
div[data-baseweb="textarea"],
div[data-baseweb="select"] > div {
    background-color: #f8fafc !important;
    border: 1px solid #cbd5e1 !important;
    border-radius: 8px !important;
}

div[data-baseweb="input"] input::placeholder,
div[data-baseweb="textarea"] textarea::placeholder {
    color: #94a3b8 !important;
    opacity: 1 !important;
}

div[data-baseweb="input"]:focus-within,
div[data-baseweb="textarea"]:focus-within,
div[data-baseweb="select"] > div:focus-within {
    background-color: #ffffff !important;
    border-color: #2563eb !important;
    box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.12) !important;
}

div[data-baseweb="textarea"] textarea {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 12px !important;
    line-height: 1.45 !important;
}

/* Expanders (Acordeones de Correos) */
div[data-testid="stExpander"] {
    background-color: #ffffff !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 12px !important;
    box-shadow: 0 2px 6px rgba(15, 23, 42, 0.03) !important;
    margin-bottom: 10px !important;
    overflow: hidden;
}

div[data-testid="stExpander"] summary {
    padding: 12px 16px !important;
}

div[data-testid="stExpander"] summary:hover {
    background-color: #f8fafc !important;
}

div[data-testid="stExpander"] summary p {
    font-size: 13.5px !important;
    font-weight: 500 !important;
    color: #1e293b !important;
}

div[data-testid="stExpander"] summary strong {
    color: #0f172a !important;
    font-weight: 700 !important;
    background-color: #f1f5f9;
    padding: 2px 7px;
    border-radius: 6px;
    font-size: 12px !important;
}

/* Botones Primarios y Secundarios */
div.stButton > button[kind="primary"] {
    background: linear-gradient(180deg, #2563eb 0%, #1d4ed8 100%) !important;
    color: #ffffff !important;
    font-weight: 600 !important;
    font-size: 13.5px !important;
    height: 42px !important;
    border-radius: 8px !important;
    border: 1px solid #1e40af !important;
    box-shadow: 0 2px 5px rgba(37, 99, 235, 0.2) !important;
}

div.stButton > button[kind="primary"]:hover {
    background: linear-gradient(180deg, #1d4ed8 0%, #1e3a8a 100%) !important;
}

div.stButton > button[kind="secondary"] {
    background-color: #f8fafc !important;
    color: #334155 !important;
    font-weight: 600 !important;
    font-size: 13px !important;
    height: 38px !important;
    border-radius: 8px !important;
    border: 1px solid #cbd5e1 !important;
}

/* Barra de Estado de Sincronización */
.sync-bar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: #ecfdf5;
    border: 1px solid #a7f3d0;
    color: #065f46;
    padding: 9px 14px;
    border-radius: 10px;
    font-size: 12.5px;
    font-weight: 600;
    margin-bottom: 12px;
}

/* Cabecera Interna del Correo */
.mail-header-box {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    padding: 14px 16px;
    margin-bottom: 12px;
}

.mail-top-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 8px;
    margin-bottom: 8px;
}

.badge-latest {
    display: inline-block;
    background: #2563eb;
    color: #ffffff;
    font-size: 10.5px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    padding: 3px 9px;
    border-radius: 999px;
}

.badge-recent {
    display: inline-block;
    background: #e2e8f0;
    color: #475569;
    font-size: 10.5px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    padding: 3px 9px;
    border-radius: 999px;
}

.date-highlight {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 12px;
    font-weight: 700;
    color: #1e40af;
    background: #dbeafe;
    border: 1px solid #bfdbfe;
    padding: 4px 10px;
    border-radius: 6px;
}

.mail-subject-line {
    font-size: 15px !important;
    font-weight: 700 !important;
    color: #0f172a !important;
    margin: 0 0 6px 0 !important;
    line-height: 1.35 !important;
}

.mail-meta-line {
    font-size: 12px;
    color: #64748b;
}

.mail-from-strong {
    color: #1e293b;
    font-weight: 600;
}

/* Tarjeta Vacía */
.empty-state-card {
    background: #ffffff;
    border: 1.5px dashed #cbd5e1;
    border-radius: 14px;
    padding: 36px 20px;
    text-align: center;
    margin-top: 8px;
}

.empty-badge {
    display: inline-block;
    font-size: 10.5px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: #2563eb;
    background: #eff6ff;
    border: 1px solid #bfdbfe;
    padding: 3px 10px;
    border-radius: 999px;
    margin-bottom: 10px;
}

/* Caja de Código de Vinculación */
.oauth-box {
    background: #f8fafc;
    border: 1px solid #cbd5e1;
    border-radius: 12px;
    padding: 20px;
    text-align: center;
    margin: 14px 0;
}

.oauth-code {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 26px;
    font-weight: 700;
    letter-spacing: 4px;
    color: #0f172a;
    background: #ffffff;
    border: 1.5px solid #94a3b8;
    border-radius: 8px;
    padding: 8px 20px;
    display: inline-block;
    margin: 10px 0 14px 0;
}

.oauth-link {
    display: inline-block;
    background: #0f172a;
    color: #ffffff !important;
    text-decoration: none !important;
    font-weight: 600;
    font-size: 13px;
    padding: 9px 18px;
    border-radius: 8px;
}
</style>
"""
st.markdown(polished_css, unsafe_allow_html=True)

# ==========================================
# INICIALIZACIÓN DE SESSION STATE
# ==========================================
MAX_CORREOS = 5

for key, default in {
    "correos": None,
    "credencial_actualizada": "",
    "credenciales_input": "",
    "correo_activo": ""
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# ==========================================
# FUNCIONES DE CONEXIÓN, FECHA Y ORDENAMIENTO
# ==========================================
def parsear_fecha_y_timestamp(fecha_str):
    if not fecha_str:
        return "Fecha desconocida", 0.0
    try:
        if "T" in fecha_str:
            dt = datetime.fromisoformat(fecha_str.replace("Z", "+00:00"))
        else:
            dt = parsedate_to_datetime(fecha_str)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.strftime("%d %b %Y, %H:%M"), dt.timestamp()
    except Exception:
        return fecha_str[:22], 0.0

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
                font-size: 13.5px;
                line-height: 1.6;
                color: #1e293b;
                background-color: #ffffff;
                margin: 0;
                padding: 8px 4px;
                word-wrap: break-word;
            }}
            a {{ color: #2563eb; }}
            img {{ max-width: 100%; height: auto; border-radius: 4px; }}
            pre {{
                white-space: pre-wrap;
                font-family: ui-monospace, monospace;
                font-size: 12.5px;
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

def leer_via_graph_api(access_token, cantidad=MAX_CORREOS):
    headers = {"Authorization": f"Bearer {access_token}"}
    url = f"https://graph.microsoft.com/v1.0/me/messages?$top={cantidad}&$orderby=receivedDateTime desc&$select=subject,from,receivedDateTime,body"
    r = requests.get(url, headers=headers, timeout=12)
    if r.status_code != 200:
        return None
    datos = r.json()
    lista_correos = []
    for msg in datos.get("value", [])[:cantidad]:
        remitente_info = msg.get("from", {}).get("emailAddress", {})
        nombre = remitente_info.get("name", "").strip()
        direccion = remitente_info.get("address", "").strip()
        remitente = f"{nombre} <{direccion}>" if nombre and nombre != direccion else direccion
        fecha_fmt, ts = parsear_fecha_y_timestamp(msg.get("receivedDateTime", ""))
        lista_correos.append({
            "asunto": msg.get("subject") or "(Sin asunto)",
            "remitente": remitente or "Desconocido",
            "fecha": fecha_fmt,
            "ts": ts,
            "cuerpo": msg.get("body", {}).get("content", "")
        })
    lista_correos.sort(key=lambda x: x["ts"], reverse=True)
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

def leer_correos_imap(correo, access_token, cantidad=MAX_CORREOS):
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
                fecha_fmt, ts = parsear_fecha_y_timestamp(msg.get("Date", ""))
                lista_correos.append({
                    "asunto": decodificar_texto(msg.get("Subject", "(Sin asunto)")),
                    "remitente": decodificar_texto(msg.get("From", "Desconocido")),
                    "fecha": fecha_fmt,
                    "ts": ts,
                    "cuerpo": extraer_cuerpo(msg)
                })
    mail.logout()
    lista_correos.sort(key=lambda x: x["ts"], reverse=True)
    return lista_correos

# ==========================================
# CABECERA SUPERIOR (SIN DETALLES TÉCNICOS)
# ==========================================
st.markdown("""
<div class="hero-header">
    <div>
        <div class="hero-title">Outlook QuickReader</div>
        <div class="hero-subtitle">Consulta rápida de bandeja de entrada</div>
    </div>
</div>
""", unsafe_allow_html=True)

tab_lector, tab_generador = st.tabs(["Bandeja de Entrada", "Generar Acceso"])

# ==========================================
# PESTAÑA 1: BANDEJA DE ENTRADA
# ==========================================
with tab_lector:
    hay_sesion = st.session_state["correos"] is not None
    titulo_expander = (
        f"Cuenta activa: {st.session_state['correo_activo']} (Cambiar cuenta)"
        if hay_sesion else "Credenciales de acceso"
    )

    with st.expander(titulo_expander, expanded=not hay_sesion):
        credenciales = st.text_area(
            "Cadena de acceso (email|password|refresh_token|client_id)",
            value=st.session_state["credenciales_input"],
            placeholder="usuario@outlook.com|clave123|M.C102_token_ejemplo...|a1b2c3d4-e5f6-1234-a1b2-c3d4e5f61234",
            height=88
        )
        st.session_state["credenciales_input"] = credenciales
        
        consultar_btn = st.button(
            "Consultar últimos 5 correos",
            type="primary",
            use_container_width=True
        )

    if consultar_btn:
        if not credenciales or "|" not in credenciales:
            st.warning("Formato requerido: email|password|refresh_token|client_id")
        else:
            partes = [p.strip() for p in credenciales.strip().split("|")]
            if len(partes) < 4 or not all([partes[0], partes[2], partes[3]]):
                st.error("Faltan datos en la cadena. Verifica que incluya las 4 partes separadas por '|'.")
            else:
                correo, password, refresh_token, client_id = partes[0], partes[1], partes[2], partes[3]
                with st.spinner("Sincronizando mensajes recientes..."):
                    token_data = obtener_access_token_multivia(client_id, refresh_token)
                    
                    if "access_token" not in token_data:
                        st.error("La sesión ha expirado. Genera una nueva credencial en la pestaña 'Generar Acceso'.")
                    else:
                        access_token = token_data["access_token"]
                        nuevo_refresh = token_data.get("refresh_token", refresh_token)
                        st.session_state["credencial_actualizada"] = f"{correo}|{password}|{nuevo_refresh}|{client_id}"
                        st.session_state["correo_activo"] = correo
                        
                        try:
                            correos = leer_via_graph_api(access_token, cantidad=MAX_CORREOS)
                            if correos is None:
                                correos = leer_correos_imap(correo, access_token, cantidad=MAX_CORREOS)
                                
                            st.session_state["correos"] = correos[:MAX_CORREOS]
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error al cargar los mensajes: {str(e)}")

    # Renderizado de los 5 Correos Colapsables (Del más reciente al más antiguo)
    if st.session_state["correos"] is not None:
        correos = st.session_state["correos"][:MAX_CORREOS]
        
        st.markdown(f"""
        <div class="sync-bar">
            <span>Bandeja sincronizada</span>
            <span>{len(correos)} correos recientes</span>
        </div>
        """, unsafe_allow_html=True)

        if st.session_state["credencial_actualizada"]:
            with st.expander("Ver credencial actualizada"):
                st.code(st.session_state["credencial_actualizada"], language="text")

        if len(correos) == 0:
            st.markdown("""
            <div class="empty-state-card">
                <span class="empty-badge">Sin mensajes</span>
                <div class="card-title">Bandeja de entrada vacía</div>
                <p class="card-desc">No se encontraron correos recientes en esta cuenta.</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            for idx, c in enumerate(correos):
                es_mas_reciente = (idx == 0)
                remitente_corto = c["remitente"].split("<")[0].strip() or c["remitente"]
                asunto_corto = c["asunto"][:46] + ("..." if len(c["asunto"]) > 46 else "")
                
                # Sin numeración; resalta fecha/hora en negrita y agrega etiqueta al más reciente
                if es_mas_reciente:
                    titulo_acordeon = f"**[MÁS RECIENTE] {c['fecha']}**  —  {asunto_corto} · {remitente_corto[:22]}"
                else:
                    titulo_acordeon = f"**{c['fecha']}**  —  {asunto_corto} · {remitente_corto[:22]}"

                with st.expander(titulo_acordeon, expanded=es_mas_reciente):
                    asunto_seguro = html.escape(c["asunto"])
                    remitente_seguro = html.escape(c["remitente"])
                    fecha_segura = html.escape(c["fecha"])
                    
                    badge_html = (
                        '<span class="badge-latest">Más reciente</span>'
                        if es_mas_reciente else
                        '<span class="badge-recent">Correo recibido</span>'
                    )

                    st.markdown(f"""
                    <div class="mail-header-box">
                        <div class="mail-top-row">
                            {badge_html}
                            <span class="date-highlight">{fecha_segura}</span>
                        </div>
                        <div class="mail-subject-line">{asunto_seguro}</div>
                        <div class="mail-meta-line">
                            De: <span class="mail-from-strong">{remitente_seguro}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    st.components.v1.html(
                        envolver_html_correo(c["cuerpo"]),
                        height=380,
                        scrolling=True
                    )
    else:
        st.markdown("""
        <div class="empty-state-card">
            <span class="empty-badge">Listo para consultar</span>
            <div class="card-title">Ninguna cuenta cargada</div>
            <p class="card-desc">Pega tu cadena de acceso arriba y pulsa "Consultar últimos 5 correos" para ver tus mensajes.</p>
        </div>
        """, unsafe_allow_html=True)

# ==========================================
# PESTAÑA 2: GENERAR ACCESO
# ==========================================
with tab_generador:
    with st.container(border=True, key="card_oauth_gen"):
        st.markdown("""
        <div class="card-header">
            <div class="card-title">Vincular cuenta de correo</div>
            <div class="card-desc">Genera una credencial de acceso rápida mediante código de verificación de Microsoft.</div>
        </div>
        """, unsafe_allow_html=True)
        
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
                placeholder="Ingresa tu contraseña"
            )
            
        gen_client_id = st.text_input(
            "Client ID",
            placeholder="a1b2c3d4-e5f6-1234-a1b2-c3d4e5f61234"
        )
        
        st.markdown("<div style='height: 4px;'></div>", unsafe_allow_html=True)
        
        if st.button("Solicitar Código de Vinculación", type="primary", use_container_width=True):
            if not gen_email or not gen_client_id:
                st.warning("Completa el correo electrónico y el Client ID.")
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
                        st.error("No se pudo generar el código. Verifica que el Client ID sea válido.")
                except Exception as e:
                    st.error(f"Error de conexión: {str(e)}")

        if "user_code" in st.session_state:
            st.markdown(f"""
            <div class="oauth-box">
                <div style="font-size: 11px; font-weight: 700; color: #2563eb; text-transform: uppercase; letter-spacing: 0.06em;">
                    Código de verificación
                </div>
                <div class="oauth-code">{st.session_state['user_code']}</div>
                <div>
                    <a href="{st.session_state['verification_uri']}" target="_blank" class="oauth-link">
                        Abrir página de activación de Microsoft
                    </a>
                </div>
                <p style="font-size: 12px; color: #64748b; margin: 12px 0 0 0;">
                    Abre el enlace en modo incógnito, inicia sesión con <b>{html.escape(gen_email)}</b> e ingresa el código.
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            col_ok, col_cancel = st.columns([2, 1])
            with col_ok:
                if st.button("Confirmar y Obtener Credencial", type="primary", use_container_width=True):
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
                            st.info("Aún no has finalizado la autorización en la ventana de Microsoft.")
                        else:
                            st.error("No se pudo completar la vinculación. Solicita un nuevo código.")
            with col_cancel:
                if st.button("Cancelar", type="secondary", use_container_width=True):
                    del st.session_state["user_code"]
                    st.rerun()

        if "credencial_generada_nueva" in st.session_state:
            st.markdown("<hr style='border:none; border-top:1px solid #e2e8f0; margin: 14px 0;'>", unsafe_allow_html=True)
            st.success("Credencial generada exitosamente:")
            st.code(st.session_state["credencial_generada_nueva"], language="text")
            if st.button("Usar esta credencial en la Bandeja de Entrada", type="secondary", use_container_width=True):
                st.session_state["credenciales_input"] = st.session_state["credencial_generada_nueva"]
                st.info("Credencial cargada en la pestaña 'Bandeja de Entrada'.")
