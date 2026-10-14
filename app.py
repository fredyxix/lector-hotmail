# archivo: app.py
import streamlit as st
import requests
import imaplib
import email
from email.header import decode_header
from email.utils import parsedate_to_datetime
from datetime import datetime
import html

# Configuración de página sin emojis ni adornos artificiales
st.set_page_config(
    page_title="Outlook QuickReader",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==========================================
# ESTILOS CSS (UI SOBRIA, CORPORATIVA Y SIN ICONOS IA)
# ==========================================
clean_ui_css = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
    --bg-app: #f8fafc;
    --surface: #ffffff;
    --border: #e2e8f0;
    --border-strong: #cbd5e1;
    --text-main: #0f172a;
    --text-muted: #64748b;
    --brand: #0067b8;
    --brand-hover: #005293;
    --success-bg: #f0fdf4;
    --success-text: #15803d;
    --success-border: #bbf7d0;
}

html, body, [class*="st-"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    color: var(--text-main);
}

.stApp {
    background-color: var(--bg-app);
}

/* Ocultar cromado innecesario de Streamlit */
div[data-testid="stToolbar"], footer, header {
    visibility: hidden;
    height: 0;
}

.block-container {
    max-width: 1120px !important;
    padding-top: 2rem !important;
    padding-bottom: 3rem !important;
}

/* Cabecera superior minimalista */
.top-bar {
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    padding-bottom: 16px;
    margin-bottom: 24px;
    border-bottom: 1px solid var(--border);
}

.brand-title {
    font-size: 20px;
    font-weight: 700;
    color: var(--text-main);
    letter-spacing: -0.02em;
    margin: 0;
}

.brand-subtitle {
    font-size: 13px;
    color: var(--text-muted);
    margin: 4px 0 0 0;
}

.protocol-badge {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 11px;
    font-weight: 500;
    color: #475569;
    background: #f1f5f9;
    border: 1px solid var(--border);
    padding: 4px 10px;
    border-radius: 4px;
}

/* Pestañas de navegación limpias */
.stTabs [data-baseweb="tab-list"] {
    gap: 24px;
    background-color: transparent;
    border-bottom: 1px solid var(--border);
    padding: 0;
}

.stTabs [data-baseweb="tab"] {
    height: 42px;
    background: transparent !important;
    color: var(--text-muted);
    font-weight: 500;
    font-size: 14px;
    padding: 0 4px;
    border: none !important;
}

.stTabs [aria-selected="true"] {
    color: var(--brand) !important;
    font-weight: 600 !important;
    border-bottom: 2px solid var(--brand) !important;
}

/* Contenedores con borde nativos de Streamlit */
div[data-testid="stVerticalBlockBorderWrapper"] {
    background-color: var(--surface);
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    box-shadow: 0 1px 2px rgba(15, 23, 42, 0.03);
}

/* Inputs y Textareas */
div[data-baseweb="textarea"] textarea, 
div[data-baseweb="input"] input {
    border-radius: 6px !important;
    border: 1px solid var(--border-strong) !important;
    font-size: 13px !important;
    background-color: var(--surface) !important;
    color: var(--text-main) !important;
}

div[data-baseweb="textarea"] textarea {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 12.5px !important;
}

div[data-baseweb="textarea"] textarea:focus, 
div[data-baseweb="input"] input:focus {
    border-color: var(--brand) !important;
    box-shadow: 0 0 0 2px rgba(0, 103, 184, 0.12) !important;
}

/* Botones primarios y secundarios */
div.stButton > button[kind="primary"] {
    background-color: var(--brand) !important;
    color: #ffffff !important;
    font-weight: 500 !important;
    border-radius: 6px !important;
    border: 1px solid var(--brand) !important;
    padding: 8px 16px !important;
    font-size: 13.5px !important;
    transition: background-color 0.15s ease;
}

div.stButton > button[kind="primary"]:hover {
    background-color: var(--brand-hover) !important;
}

div.stButton > button[kind="secondary"] {
    background-color: var(--surface) !important;
    color: var(--text-main) !important;
    font-weight: 500 !important;
    border-radius: 6px !important;
    border: 1px solid var(--border-strong) !important;
    padding: 8px 16px !important;
    font-size: 13px !important;
}

div.stButton > button[kind="secondary"]:hover {
    background-color: #f1f5f9 !important;
}

/* Cabecera de lectura de correo */
.mail-view-header {
    border-bottom: 1px solid var(--border);
    padding-bottom: 14px;
    margin-bottom: 14px;
}

.mail-subject {
    font-size: 17px;
    font-weight: 600;
    color: var(--text-main);
    margin: 0 0 8px 0;
    line-height: 1.35;
}

.mail-meta-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 12.5px;
    color: var(--text-muted);
}

.mail-sender {
    color: #334155;
    font-weight: 500;
}

/* Estados vacíos sobrios */
.empty-box {
    text-align: center;
    padding: 48px 24px;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 8px;
}

.empty-title {
    font-size: 14px;
    font-weight: 600;
    color: var(--text-main);
    margin-bottom: 4px;
}

.empty-desc {
    font-size: 13px;
    color: var(--text-muted);
    margin: 0;
}

/* Barra de estado */
.status-pill {
    display: inline-block;
    background: var(--success-bg);
    color: var(--success-text);
    border: 1px solid var(--success-border);
    padding: 4px 10px;
    border-radius: 4px;
    font-size: 12px;
    font-weight: 500;
}

/* Panel de código de dispositivo */
.device-code-panel {
    background: #f8fafc;
    border: 1px solid var(--border-strong);
    border-radius: 8px;
    padding: 24px;
    text-align: center;
    margin: 16px 0;
}

.device-code-value {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 28px;
    font-weight: 700;
    letter-spacing: 3px;
    color: var(--text-main);
    background: var(--surface);
    border: 1px solid var(--border);
    display: inline-block;
    padding: 8px 20px;
    border-radius: 6px;
    margin: 12px 0 16px 0;
}

.external-link-btn {
    display: inline-block;
    background: var(--text-main);
    color: #ffffff !important;
    padding: 9px 18px;
    border-radius: 6px;
    text-decoration: none !important;
    font-weight: 500;
    font-size: 13px;
}
.external-link-btn:hover {
    background: #1e293b;
}
</style>
"""
st.markdown(clean_ui_css, unsafe_allow_html=True)

# ==========================================
# INICIALIZACIÓN DE ESTADO (SESSION STATE)
# ==========================================
if "correos" not in st.session_state:
    st.session_state["correos"] = None
if "metodo_usado" not in st.session_state:
    st.session_state["metodo_usado"] = ""
if "credencial_actualizada" not in st.session_state:
    st.session_state["credencial_actualizada"] = ""
if "credenciales_input" not in st.session_state:
    st.session_state["credenciales_input"] = ""
if "correo_seleccionado_idx" not in st.session_state:
    st.session_state["correo_seleccionado_idx"] = 0

# ==========================================
# FUNCIONES DE BACKEND Y FORMATEO
# ==========================================
def formatear_fecha(fecha_str):
    if not fecha_str:
        return "Fecha no disponible"
    try:
        # Intento formato ISO 8601 (Microsoft Graph)
        if "T" in fecha_str:
            dt = datetime.fromisoformat(fecha_str.replace("Z", "+00:00"))
            return dt.strftime("%d %b %Y, %H:%M")
        # Intento formato RFC 2822 (IMAP)
        dt = parsedate_to_datetime(fecha_str)
        return dt.strftime("%d %b %Y, %H:%M")
    except Exception:
        return fecha_str[:22]

def envolver_html_correo(contenido_html):
    """Asegura que el cuerpo del correo tenga tipografía limpia y fondo blanco dentro del iframe."""
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
                font-size: 14px;
                line-height: 1.5;
                color: #1e293b;
                background-color: #ffffff;
                margin: 0;
                padding: 8px 4px;
                word-wrap: break-word;
            }}
            a {{ color: #0067b8; }}
            img {{ max-width: 100%; height: auto; }}
            pre {{
                white-space: pre-wrap;
                font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
                font-size: 13px;
                background: #f8fafc;
                padding: 12px;
                border-radius: 6px;
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
# CABECERA PRINCIPAL
# ==========================================
st.markdown("""
<div class="top-bar">
    <div>
        <h1 class="brand-title">Outlook QuickReader</h1>
        <p class="brand-subtitle">Cliente de lectura directa y gestión de sesiones OAuth2 (Graph API / XOAUTH2 IMAP)</p>
    </div>
    <span class="protocol-badge">OAuth 2.0 / TLS 1.3</span>
</div>
""", unsafe_allow_html=True)

tab_lector, tab_generador = st.tabs(["Bandeja de Entrada", "Generador de Token OAuth2"])

# ==========================================
# PESTAÑA 1: BANDEJA DE ENTRADA
# ==========================================
with tab_lector:
    with st.container(border=True):
        col_input, col_config = st.columns([3.5, 1])
        
        with col_input:
            credenciales = st.text_area(
                "Cadena de conexión (formato: email|password|refresh_token|client_id)",
                value=st.session_state["credenciales_input"],
                placeholder="usuario@outlook.com|contraseña|M.C501...|9e5f94bc-e8a4-4e73-b8be-63364c29d753",
                height=76
            )
            st.session_state["credenciales_input"] = credenciales
            
        with col_config:
            cantidad_mensajes = st.selectbox(
                "Límite de mensajes",
                options=[10, 20, 35, 50],
                index=0
            )
            consultar_btn = st.button("Sincronizar bandeja", type="primary", use_container_width=True)

    # Lógica de sincronización
    if consultar_btn:
        if not credenciales or "|" not in credenciales:
            st.warning("Ingresa una cadena válida con el formato: email|password|refresh_token|client_id")
        else:
            partes = [p.strip() for p in credenciales.strip().split("|")]
            if len(partes) < 4 or not all([partes[0], partes[2], partes[3]]):
                st.error("La cadena está incompleta. Verifica que contenga correo, contraseña, refresh_token y client_id separados por '|'.")
            else:
                correo, password, refresh_token, client_id = partes[0], partes[1], partes[2], partes[3]
                with st.spinner("Autenticando con los servidores de Microsoft..."):
                    token_data = obtener_access_token_multivia(client_id, refresh_token)
                    
                    if "access_token" not in token_data:
                        st.error("El Refresh Token ha expirado o fue revocado (invalid_grant). Genera uno nuevo en la segunda pestaña.")
                        with st.expander("Detalles técnicos de la respuesta"):
                            st.json(token_data)
                    else:
                        access_token = token_data["access_token"]
                        nuevo_refresh = token_data.get("refresh_token", refresh_token)
                        st.session_state["credencial_actualizada"] = f"{correo}|{password}|{nuevo_refresh}|{client_id}"
                        
                        try:
                            correos = leer_via_graph_api(access_token, cantidad=cantidad_mensajes)
                            if correos is not None:
                                st.session_state["metodo_usado"] = "Microsoft Graph API"
                            else:
                                correos = leer_correos_imap(correo, access_token, cantidad=cantidad_mensajes)
                                st.session_state["metodo_usado"] = "IMAP XOAUTH2"
                                
                            st.session_state["correos"] = correos
                            st.session_state["correo_seleccionado_idx"] = 0
                        except Exception as e:
                            st.error(f"Error al recuperar los mensajes: {str(e)}")

    # Renderizado de resultados persistentes en session_state
    if st.session_state["correos"] is not None:
        correos = st.session_state["correos"]
        
        # Barra de estado y token renovado
        col_stat1, col_stat2 = st.columns([2, 2])
        with col_stat1:
            st.markdown(
                f'<div style="margin: 8px 0 14px 0;"><span class="status-pill">Conectado vía {st.session_state["metodo_usado"]} — {len(correos)} mensajes</span></div>',
                unsafe_allow_html=True
            )
        with col_stat2:
            if st.session_state["credencial_actualizada"]:
                with st.expander("Ver credencial con token renovado"):
                    st.code(st.session_state["credencial_actualizada"], language="text")

        if len(correos) == 0:
            st.markdown("""
            <div class="empty-box">
                <div class="empty-title">Bandeja de entrada vacía</div>
                <p class="empty-desc">No se encontraron correos electrónicos en esta cuenta.</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            # Filtro de búsqueda rápida
            filtro = st.text_input(
                "Filtrar mensajes",
                placeholder="Buscar por asunto o remitente...",
                label_visibility="collapsed"
            )
            
            correos_filtrados = [
                c for c in correos
                if filtro.lower() in c["asunto"].lower() or filtro.lower() in c["remitente"].lower()
            ] if filtro else correos

            if not correos_filtrados:
                st.info("Ningún mensaje coincide con el criterio de búsqueda.")
            else:
                # Vista Maestro-Detalle (Lista a la izquierda, Lector a la derecha)
                col_lista, col_lector = st.columns([1.3, 2.2], gap="medium")
                
                with col_lista:
                    with st.container(border=True):
                        st.markdown("<p style='font-size: 12px; font-weight: 600; color: #64748b; text-transform: uppercase; letter-spacing: 0.04em; margin-bottom: 10px;'>Mensajes recibidos</p>", unsafe_allow_html=True)
                        
                        # Asegurar que el índice seleccionado sea válido tras filtrar
                        if st.session_state["correo_seleccionado_idx"] >= len(correos_filtrados):
                            st.session_state["correo_seleccionado_idx"] = 0

                        for idx, c in enumerate(correos_filtrados):
                            es_activo = (idx == st.session_state["correo_seleccionado_idx"])
                            asunto_corto = c["asunto"][:48] + ("..." if len(c["asunto"]) > 48 else "")
                            remitente_corto = c["remitente"].split("<")[0].strip()[:32] or c["remitente"][:32]
                            
                            tipo_btn = "primary" if es_activo else "secondary"
                            etiqueta = f"{asunto_corto}\n{remitente_corto} · {c['fecha']}"
                            
                            if st.button(etiqueta, key=f"mail_item_{idx}", type=tipo_btn, use_container_width=True):
                                st.session_state["correo_seleccionado_idx"] = idx
                                st.rerun()

                with col_lector:
                    correo_actual = correos_filtrados[st.session_state["correo_seleccionado_idx"]]
                    with st.container(border=True):
                        asunto_seguro = html.escape(correo_actual["asunto"])
                        remitente_seguro = html.escape(correo_actual["remitente"])
                        fecha_segura = html.escape(correo_actual["fecha"])
                        
                        st.markdown(f"""
                        <div class="mail-view-header">
                            <h2 class="mail-subject">{asunto_seguro}</h2>
                            <div class="mail-meta-row">
                                <span>De: <span class="mail-sender">{remitente_seguro}</span></span>
                                <span>{fecha_segura}</span>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        cuerpo_formateado = envolver_html_correo(correo_actual["cuerpo"])
                        st.components.v1.html(cuerpo_formateado, height=480, scrolling=True)
    else:
        st.markdown("""
        <div class="empty-box">
            <div class="empty-title">Ninguna sesión cargada</div>
            <p class="empty-desc">Introduce tus credenciales en el panel superior y presiona "Sincronizar bandeja" para cargar los mensajes.</p>
        </div>
        """, unsafe_allow_html=True)

# ==========================================
# PESTAÑA 2: GENERADOR DE TOKEN (DEVICE CODE)
# ==========================================
with tab_generador:
    with st.container(border=True):
        st.markdown("<p style='font-size: 15px; font-weight: 600; color: #0f172a; margin-bottom: 4px;'>Autorización mediante Código de Dispositivo (OAuth 2.0)</p>", unsafe_allow_html=True)
        st.markdown("<p style='font-size: 13px; color: #64748b; margin-bottom: 18px;'>Genera un nuevo Refresh Token oficial sin exponer la contraseña directamente en el flujo de autenticación.</p>", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1.5, 1.2, 1.8])
        with col1:
            gen_email = st.text_input("Correo electrónico", placeholder="usuario@outlook.com")
        with col2:
            gen_pass = st.text_input("Contraseña (para concatenar formato)", type="password", placeholder="••••••••")
        with col3:
            gen_client_id = st.text_input(
                "Client ID de la aplicación",
                value="9e5f94bc-e8a4-4e73-b8be-63364c29d753"
            )
            
        if st.button("Solicitar código de vinculación", type="primary"):
            if not gen_email or not gen_client_id:
                st.warning("El correo electrónico y el Client ID son obligatorios para iniciar la solicitud.")
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
                        st.error("Microsoft rechazó la solicitud de código.")
                        st.json(datos_dev)
                except Exception as e:
                    st.error(f"Error de red al conectar con Microsoft: {str(e)}")

        if "user_code" in st.session_state:
            st.markdown(f"""
            <div class="device-code-panel">
                <div style="font-size: 12px; font-weight: 600; color: #475569; text-transform: uppercase; letter-spacing: 0.05em;">
                    Paso 1: Copia este código de verificación
                </div>
                <div class="device-code-value">{st.session_state['user_code']}</div>
                <div>
                    <a href="{st.session_state['verification_uri']}" target="_blank" class="external-link-btn">
                        Abrir portal de activación de Microsoft
                    </a>
                </div>
                <p style="font-size: 12.5px; color: #64748b; margin-top: 14px; margin-bottom: 0;">
                    Abre el enlace en una ventana privada, inicia sesión con <b>{html.escape(gen_email)}</b> y autoriza el acceso.
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            col_conf, col_cancel = st.columns([2, 1])
            with col_conf:
                if st.button("Ya autoricé el acceso — Obtener Refresh Token", type="primary", use_container_width=True):
                    url_token = "https://login.microsoftonline.com/common/oauth2/v2.0/token"
                    r_tok = requests.post(url_token, data={
                        "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
                        "client_id": gen_client_id.strip(),
                        "device_code": st.session_state["device_code"]
                    }, timeout=10)
                    res_tok = r_tok.json()
                    
                    if "refresh_token" in res_tok:
                        nuevo_rt = res_tok["refresh_token"]
                        pass_val = gen_pass.strip() if gen_pass else "SIN_PASSWORD"
                        linea_final = f"{gen_email.strip()}|{pass_val}|{nuevo_rt}|{gen_client_id.strip()}"
                        st.session_state["credencial_generada_nueva"] = linea_final
                        del st.session_state["user_code"]
                        st.rerun()
                    else:
                        error_code = res_tok.get("error", "")
                        if error_code == "authorization_pending":
                            st.info("Aún estamos esperando que completes la autorización en la pestaña de Microsoft.")
                        else:
                            st.error(f"No se pudo obtener el token: {res_tok.get('error_description', error_code)}")
            with col_cancel:
                if st.button("Cancelar solicitud", type="secondary", use_container_width=True):
                    del st.session_state["user_code"]
                    st.rerun()

        if "credencial_generada_nueva" in st.session_state:
            st.success("Credencial generada correctamente. Copia la línea inferior o envíala directo al lector:")
            st.code(st.session_state["credencial_generada_nueva"], language="text")
            if st.button("Usar esta credencial en la Bandeja de Entrada", type="secondary"):
                st.session_state["credenciales_input"] = st.session_state["credencial_generada_nueva"]
                st.info("Credencial cargada. Cambia a la pestaña 'Bandeja de Entrada' y presiona 'Sincronizar bandeja'.")
