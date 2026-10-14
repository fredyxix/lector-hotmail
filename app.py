# archivo: app.py
import streamlit as st
import requests
import imaplib
import email
from email.header import decode_header

st.set_page_config(page_title="Quick Read Hotmail", layout="centered")

css_styles = """
<link rel="stylesheet" type="text/css" href="https://unpkg.com/@phosphor-icons/web@2.1.1/src/regular/style.css" />
<link rel="stylesheet" type="text/css" href="https://unpkg.com/@phosphor-icons/web@2.1.1/src/fill/style.css" />
<link rel="stylesheet" type="text/css" href="https://unpkg.com/@phosphor-icons/web@2.1.1/src/duotone/style.css" />
<style>
.header-container {
    display: flex;
    align-items: center;
    gap: 16px;
    margin-bottom: 16px;
}
.icon-box {
    background-color: #fff0e6;
    color: #ff5500;
    width: 54px;
    height: 54px;
    border-radius: 14px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 28px;
    flex-shrink: 0;
}
.header-title {
    margin: 0 !important;
    padding: 0 !important;
    font-size: 24px !important;
    font-weight: 700 !important;
    color: #1f2937 !important;
    line-height: 1.2 !important;
}
.header-subtitle {
    margin: 4px 0 0 0 !important;
    font-size: 14px !important;
    color: #6b7280 !important;
}
.label-title {
    font-weight: 600;
    font-size: 14px;
    color: #1f2937;
    margin-bottom: 8px;
    display: flex;
    align-items: center;
    gap: 6px;
}
div.stButton > button {
    background-color: #f25c05 !important;
    color: white !important;
    font-weight: 600 !important;
    border-radius: 10px !important;
    border: none !important;
    padding: 14px 24px !important;
    width: 100% !important;
    font-size: 16px !important;
    box-shadow: 0 4px 10px rgba(242, 92, 5, 0.25) !important;
}
div.stButton > button:hover {
    background-color: #d95002 !important;
    color: white !important;
}
div.stButton > button p {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    margin: 0;
    font-size: 16px !important;
    font-weight: 600 !important;
}
.empty-box {
    text-align: center;
    padding: 45px 20px;
    border: 1px solid #e5e7eb;
    border-radius: 14px;
    background-color: #fafafa;
    color: #6b7280;
    margin-top: 20px;
}
.code-card {
    background-color: #fff7ed;
    border: 1px solid #fed7aa;
    border-radius: 12px;
    padding: 18px;
    margin: 15px 0;
    text-align: center;
}
</style>
"""
st.markdown(css_styles, unsafe_allow_html=True)

st.markdown("""
<div class="header-container">
    <div class="icon-box">
        <i class="ph-duotone ph-envelope-open"></i>
    </div>
    <div>
        <div class="header-title">Quick Read Hotmail</div>
        <div class="header-subtitle">Quick access & OAuth2 Token Generator</div>
    </div>
</div>
""", unsafe_allow_html=True)

tab_lector, tab_generador = st.tabs(["📩 Read Emails", "🔑 Generar Nuevo Token"])

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
    st.markdown('<div class="label-title"><i class="ph ph-key"></i> Email Credentials</div>', unsafe_allow_html=True)
    credenciales = st.text_area(
        "Email Credentials",
        placeholder="email|password|refresh_token|client_id",
        height=115,
        label_visibility="collapsed"
    )

    if st.button("✉️ Read Emails", use_container_width=True):
        if not credenciales or "|" not in credenciales:
            st.warning("Ingresa los datos en el formato exacto: email|password|refresh_token|client_id")
        else:
            partes = [p.strip() for p in credenciales.strip().split("|")]
            if len(partes) < 4:
                st.error("Formato incompleto. Asegúrate de incluir las 4 partes separadas por '|'.")
            else:
                correo, password, refresh_token, client_id = partes[0], partes[1], partes[2], partes[3]
                with st.spinner("Autenticando y buscando mensajes en Microsoft..."):
                    token_data = obtener_access_token_multivia(client_id, refresh_token)
                    
                    if "access_token" not in token_data:
                        st.error("❌ El refresh_token ha expirado (invalid_grant). Ve a la pestaña '🔑 Generar Nuevo Token' arriba para renovarlo con tu contraseña.")
                        with st.expander("Detalle técnico devuelto por Microsoft"):
                            st.json(token_data)
                    else:
                        access_token = token_data["access_token"]
                        nuevo_refresh = token_data.get("refresh_token", refresh_token)
                        
                        with st.expander("🔄 Ver credencial con Token Renovado (Guárdalo para que no expire)"):
                            st.code(f"{correo}|{password}|{nuevo_refresh}|{client_id}", language="text")
                            
                        try:
                            correos = leer_via_graph_api(access_token, cantidad=10)
                            if correos is None:
                                correos = leer_correos_imap(correo, access_token, cantidad=10)
                                
                            if not correos:
                                st.markdown("""
                                <div class="empty-box">
                                    <i class="ph-fill ph-tray" style="font-size: 48px; color: #d1d5db;"></i>
                                    <div style="margin: 12px 0 4px 0; color: #1f2937; font-size: 18px; font-weight: 700;">No Emails Found</div>
                                    <div style="margin: 0; font-size: 14px;">The inbox is currently empty</div>
                                </div>
                                """, unsafe_allow_html=True)
                            else:
                                st.markdown(f"""
                                <div style="display:flex; align-items:center; gap:8px; color:#059669; font-weight:600; margin: 15px 0;">
                                    <i class="ph-fill ph-check-circle" style="font-size: 20px;"></i>
                                    <span>{len(correos)} correos recientes cargados de {correo}</span>
                                </div>
                                """, unsafe_allow_html=True)
                                
                                for idx, c in enumerate(correos):
                                    with st.expander(f"{c['asunto']}  —  {c['remitente']}", expanded=(idx == 0)):
                                        st.markdown(f"""
                                        <div style="font-size: 13px; color: #6b7280; margin-bottom: 10px; display: flex; gap: 15px; flex-wrap: wrap;">
                                            <span><i class="ph ph-user"></i> {c['remitente']}</span>
                                            <span><i class="ph ph-calendar-blank"></i> {c['fecha']}</span>
                                        </div>
                                        """, unsafe_allow_html=True)
                                        st.components.v1.html(c["cuerpo"], height=350, scrolling=True)
                        except Exception as e:
                            st.error(f"Error al abrir bandeja: {str(e)}")
    else:
        st.markdown("""
        <div class="empty-box">
            <i class="ph-fill ph-tray" style="font-size: 52px; color: #d1d5db;"></i>
            <div style="margin: 12px 0 6px 0; color: #1f2937; font-size: 18px; font-weight: 700;">No Emails Yet</div>
            <div style="margin: 0; font-size: 14px;">Enter your credentials above to read your emails</div>
        </div>
        """, unsafe_allow_html=True)

with tab_generador:
    st.markdown("### 🔑 Generar un nuevo Refresh Token")
    st.caption("Si una cuenta te da error `invalid_grant`, genera aquí un token nuevo iniciando sesión con su correo y contraseña.")
    
    col1, col2 = st.columns(2)
    with col1:
        gen_email = st.text_input("Correo (Email)", placeholder="ejemplo@outlook.com")
    with col2:
        gen_pass = st.text_input("Contraseña (Password)", placeholder="TuContraseña123")
        
    gen_client_id = st.text_input(
        "Client ID (Deja el predeterminado si el tuyo da error)", 
        value="9e5f94bc-e8a4-4e73-b8be-63364c29d753"
    )
    
    if st.button("1️⃣ Solicitar Código de Vinculación", use_container_width=True):
        url_device = "https://login.microsoftonline.com/common/oauth2/v2.0/devicecode"
        # Ámbito simplificado y compatible sin conflictos
        scopes = "offline_access Mail.Read"
        r = requests.post(url_device, data={"client_id": gen_client_id.strip(), "scope": scopes})
        datos_dev = r.json()
        
        if "user_code" in datos_dev:
            st.session_state["device_code"] = datos_dev["device_code"]
            st.session_state["user_code"] = datos_dev["user_code"]
            st.session_state["verification_uri"] = datos_dev.get("verification_uri", "https://microsoft.com/devicelogin")
        else:
            st.error("Ese Client ID no permite vinculación directa.")
            st.json(datos_dev)
            
    if "user_code" in st.session_state:
        st.markdown(f"""
        <div class="code-card">
            <div style="font-size: 14px; color: #9a3412; margin-bottom: 6px;">Paso A: Copia este código de vinculación:</div>
            <div style="font-size: 28px; font-weight: 800; letter-spacing: 3px; color: #ea580c; margin-bottom: 12px;">{st.session_state['user_code']}</div>
            <a href="{st.session_state['verification_uri']}" target="_blank" style="display: inline-block; background-color: #1f2937; color: white; padding: 10px 20px; border-radius: 8px; text-decoration: none; font-weight: 600;">
                🔗 Paso B: Abrir Microsoft Login e ingresar código
            </a>
            <div style="font-size: 12px; color: #6b7280; margin-top: 10px;">
                (Abre el enlace en ventana de incógnito, inicia sesión con <b>{gen_email or 'el correo'}</b> y acepta los permisos).
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("2️⃣ Ya inicié sesión, ¡Obtener mi Nuevo Token!", use_container_width=True):
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
                st.success("✅ ¡Nuevo Refresh Token generado con éxito! Copia tu nueva línea:")
                st.code(linea_final, language="text")
                # Limpiar el código usado para que no se repita
                del st.session_state["user_code"]
            else:
                st.warning("Todavía no has completado el inicio de sesión en el enlace de Microsoft o el código expiró.")
                with st.expander("Ver respuesta de Microsoft"):
                    st.json(res_tok)
