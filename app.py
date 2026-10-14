# archivo: app.py
import streamlit as st
import requests
import imaplib
import email
from email.header import decode_header

st.set_page_config(page_title="Outlook QuickReader", page_icon="⚡", layout="centered")

modern_css = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');

html, body, [class*="st-"] {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}

div[data-testid="stToolbar"] {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

.main-card {
    background: #ffffff;
    border: 1px solid #eaeaea;
    border-radius: 16px;
    padding: 24px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.03);
    margin-bottom: 20px;
}

.app-header {
    display: flex;
    align-items: center;
    gap: 14px;
    margin-bottom: 24px;
    border-bottom: 1px solid #f0f0f0;
    padding-bottom: 18px;
}

.app-logo {
    width: 48px;
    height: 48px;
    background: linear-gradient(135deg, #FF6B35 0%, #F25C05 100%);
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-size: 22px;
    box-shadow: 0 4px 12px rgba(242, 92, 5, 0.2);
}

.app-title {
    font-size: 20px;
    font-weight: 700;
    color: #111827;
    margin: 0;
    letter-spacing: -0.3px;
}

.app-subtitle {
    font-size: 13px;
    color: #6b7280;
    margin: 2px 0 0 0;
}

.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    background-color: #f8fafc;
    padding: 6px;
    border-radius: 12px;
    border: 1px solid #e2e8f0;
}

.stTabs [data-baseweb="tab"] {
    height: 38px;
    border-radius: 8px;
    color: #64748b;
    font-weight: 600;
    font-size: 13px;
    border: none !important;
}

.stTabs [aria-selected="true"] {
    background-color: #ffffff !important;
    color: #0f172a !important;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);
}

div[data-baseweb="textarea"] textarea, div[data-baseweb="input"] input {
    border-radius: 10px !important;
    border-color: #cbd5e1 !important;
    font-size: 14px !important;
    padding: 12px !important;
}
div[data-baseweb="textarea"] textarea:focus, div[data-baseweb="input"] input:focus {
    border-color: #f25c05 !important;
    box-shadow: 0 0 0 3px rgba(242, 92, 5, 0.1) !important;
}

div.stButton > button {
    background: #f25c05 !important;
    color: white !important;
    font-weight: 600 !important;
    border-radius: 10px !important;
    border: none !important;
    padding: 12px 20px !important;
    width: 100% !important;
    font-size: 14px !important;
    box-shadow: 0 4px 12px rgba(242, 92, 5, 0.2) !important;
    transition: all 0.2s ease;
}
div.stButton > button:hover {
    background: #d95002 !important;
    box-shadow: 0 6px 16px rgba(242, 92, 5, 0.3) !important;
}

.empty-state {
    text-align: center;
    padding: 40px 20px;
    background: #fafafa;
    border: 1px dashed #e2e8f0;
    border-radius: 12px;
    color: #64748b;
    margin-top: 16px;
}
.empty-state-title {
    font-size: 16px;
    font-weight: 600;
    color: #1e293b;
    margin-bottom: 4px;
}
.empty-state-desc {
    font-size: 13px;
    color: #64748b;
    margin: 0;
}
</style>
<link rel="stylesheet" type="text/css" href="https://unpkg.com/@phosphor-icons/web@2.1.1/src/regular/style.css" />
<link rel="stylesheet" type="text/css" href="https://unpkg.com/@phosphor-icons/web@2.1.1/src/fill/style.css" />
"""
st.markdown(modern_css, unsafe_allow_html=True)

st.markdown("""
<div class="main-card">
    <div class="app-header">
        <div class="app-logo">
            <i class="ph-duotone ph-envelope-simple-open"></i>
        </div>
        <div>
            <h1 class="app-title">Outlook QuickReader</h1>
            <p class="app-subtitle">Gestión segura y lectura rápida por tokens OAuth2</p>
        </div>
    </div>
""", unsafe_allow_html=True)

tab_lector, tab_generador = st.tabs(["Bandeja de Entrada", "Generar Credencial / Token"])

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

def leer_via_graph_api(access_token, cantidad=10):
    headers = {"Authorization": f"Bearer {access_token}"}
    url = f"https://graph.microsoft.com/v1.0/me/messages?$top={cantidad}&$select=subject,from,receivedDateTime,body"
    r = requests.get(url, headers=headers, timeout=10)
    if r.status_code != 200:
        return None
    datos = r.json()
    lista_correos = []
    for msg in datos.get("value", []):
        remitente_info = msg.get("from", {}).get("emailAddress", {})
        remitente = f"{remitente_info.get('name', '')} <{remitente_info.get('address', '')}>"
        lista_correos.append({
            "asunto": msg.get("subject", "Sin Asunto"),
            "remitente": remitente.strip(),
            "fecha": msg.get("receivedDateTime", ""),
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
    return cuerpo_html if cuerpo_html else f"<pre style='white-space: pre-wrap; font-family: sans-serif;'>{cuerpo_texto}</pre>"

def leer_correos_imap(correo, access_token, cantidad=10):
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
                    "asunto": decodificar_texto(msg.get("Subject", "Sin Asunto")),
                    "remitente": decodificar_texto(msg.get("From", "Desconocido")),
                    "fecha": msg.get("Date", ""),
                    "cuerpo": extraer_cuerpo(msg)
                })
    mail.logout()
    return lista_correos

with tab_lector:
    st.markdown("<p style='font-weight: 600; font-size: 13px; color: #334155; margin-bottom: 6px;'>Credenciales de acceso</p>", unsafe_allow_html=True)
    credenciales = st.text_area(
        "Credenciales",
        placeholder="email|password|refresh_token|client_id",
        height=100,
        label_visibility="collapsed"
    )

    if st.button("Consultar Bandeja de Entrada"):
        if not credenciales or "|" not in credenciales:
            st.warning("Formato requerido: email|password|refresh_token|client_id")
        else:
            partes = [p.strip() for p in credenciales.strip().split("|")]
            if len(partes) < 4:
                st.error("Faltan campos. Asegúrate de incluir las 4 partes separadas por '|'.")
            else:
                correo, password, refresh_token, client_id = partes[0], partes[1], partes[2], partes[3]
                with st.spinner("Estableciendo conexión cifrada con Microsoft..."):
                    token_data = obtener_access_token_multivia(client_id, refresh_token)
                    
                    if "access_token" not in token_data:
                        st.error("El token de sesión ha expirado (invalid_grant). Utiliza la pestaña superior para generar uno nuevo.")
                        with st.expander("Ver diagnóstico técnico"):
                            st.json(token_data)
                    else:
                        access_token = token_data["access_token"]
                        nuevo_refresh = token_data.get("refresh_token", refresh_token)
                        
                        with st.expander("Token actualizado (copia para conservar sesión activa)"):
                            st.code(f"{correo}|{password}|{nuevo_refresh}|{client_id}", language="text")
                            
                        try:
                            correos = leer_via_graph_api(access_token, cantidad=10)
                            if correos is None:
                                correos = leer_correos_imap(correo, access_token, cantidad=10)
                                
                            if not correos:
                                st.markdown("""
                                <div class="empty-state">
                                    <div class="empty-state-title">Bandeja vacía</div>
                                    <p class="empty-state-desc">No se encontraron mensajes recientes en esta cuenta.</p>
                                </div>
                                """, unsafe_allow_html=True)
                            else:
                                st.markdown(f"<p style='color: #059669; font-weight: 600; font-size: 13px; margin: 16px 0;'>✓ Sincronización exitosa: {len(correos)} mensajes recuperados.</p>", unsafe_allow_html=True)
                                
                                for idx, c in enumerate(correos):
                                    with st.expander(f"{c['asunto']}  —  {c['remitente']}", expanded=(idx == 0)):
                                        st.markdown(f"<p style='color: #64748b; font-size: 12px; margin-bottom: 8px;'>Remitente: {c['remitente']} | Fecha: {c['fecha']}</p>", unsafe_allow_html=True)
                                        st.components.v1.html(c["cuerpo"], height=320, scrolling=True)
                        except Exception as e:
                            st.error(f"Error de lectura: {str(e)}")
    else:
        st.markdown("""
        <div class="empty-state">
            <div class="empty-state-title">Sin actividad</div>
            <p class="empty-state-desc">Ingresa tus credenciales arriba para consultar los correos.</p>
        </div>
        """, unsafe_allow_html=True)

with tab_generador:
    st.markdown("<p style='font-size: 14px; font-weight: 600; color: #1e293b; margin-bottom: 4px;'>Generador de Refresh Token OAuth2</p>", unsafe_allow_html=True)
    st.markdown("<p style='font-size: 13px; color: #64748b; margin-bottom: 16px;'>Obtén un nuevo token válido iniciando sesión de forma segura mediante código de dispositivo.</p>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        gen_email = st.text_input("Correo electrónico", placeholder="nombre@outlook.com")
    with col2:
        gen_pass = st.text_input("Contraseña", type="password", placeholder="••••••••")
        
    gen_client_id = st.text_input(
        "Client ID", 
        value="9e5f94bc-e8a4-4e73-b8be-63364c29d753"
    )
    
    if st.button("Generar Código de Autorización"):
        if not gen_email or not gen_pass:
            st.warning("Por favor completa el correo y la contraseña.")
        else:
            url_device = "https://login.microsoftonline.com/common/oauth2/v2.0/devicecode"
            scopes = "offline_access Mail.Read"
            r = requests.post(url_device, data={"client_id": gen_client_id.strip(), "scope": scopes})
            datos_dev = r.json()
            
            if "user_code" in datos_dev:
                st.session_state["device_code"] = datos_dev["device_code"]
                st.session_state["user_code"] = datos_dev["user_code"]
                st.session_state["verification_uri"] = datos_dev.get("verification_uri", "https://microsoft.com/devicelogin")
            else:
                st.error("Error al solicitar código a Microsoft.")
                st.json(datos_dev)
            
    if "user_code" in st.session_state:
        st.markdown(f"""
        <div style="background: #fff7ed; border: 1px solid #ffedd5; border-radius: 12px; padding: 20px; text-align: center; margin-top: 16px;">
            <p style="font-size: 13px; color: #c2410c; font-weight: 600; margin-bottom: 4px;">Código de verificación:</p>
            <div style="font-size: 32px; font-weight: 800; letter-spacing: 4px; color: #ea580c; margin-bottom: 16px;">{st.session_state['user_code']}</div>
            <a href="{st.session_state['verification_uri']}" target="_blank" style="display: inline-block; background: #0f172a; color: white; padding: 10px 20px; border-radius: 8px; text-decoration: none; font-weight: 600; font-size: 13px;">
                Abrir portal de Microsoft
            </a>
            <p style="font-size: 12px; color: #64748b; margin-top: 12px;">
                Abre este enlace en modo incógnito, inicia sesión con <b>{gen_email}</b> e ingresa el código.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Confirmar inicio de sesión y obtener credencial"):
            url_token = "https://login.microsoftonline.com/common/oauth2/v2.0/token"
            r_tok = requests.post(url_token, data={
                "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
                "client_id": gen_client_id.strip(),
                "device_code": st.session_state["device_code"]
            })
            res_tok = r_tok.json()
            if "refresh_token" in res_tok:
                nuevo_rt = res_tok["refresh_token"]
                linea_final = f"{gen_email.strip()}|{gen_pass.strip()}|{nuevo_rt}|{gen_client_id.strip()}"
                st.success("¡Credencial generada exitosamente!")
                st.code(linea_final, language="text")
                del st.session_state["user_code"]
            else:
                st.info("Aún no se ha completado la autorización en la ventana de Microsoft.")
