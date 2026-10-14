# archivo: app.py
import streamlit as st
import requests
import imaplib
import email
from email.header import decode_header

# Configuración de la página
st.set_page_config(page_title="Quick Read Hotmail", layout="centered")

# Inyección de Phosphor Icons (vía CDN) y Estilos CSS con SVG integrado en el botón
st.markdown("""
    <link rel="stylesheet" type="text/css" href="https://unpkg.com/@phosphor-icons/web@2.1.1/src/regular/style.css" />
    <link rel="stylesheet" type="text/css" href="https://unpkg.com/@phosphor-icons/web@2.1.1/src/fill/style.css" />
    <link rel="stylesheet" type="text/css" href="https://unpkg.com/@phosphor-icons/web@2.1.1/src/duotone/style.css" />
    <style>
    /* Cabecera estilo tarjeta con icono SVG/Phosphor */
    .header-container {
        display: flex;
        align-items: center;
        gap: 16px;
        margin-bottom: 20px;
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
        box-shadow: 0 2px 5px rgba(255, 85, 0, 0.1);
    }
    .header-title {
        margin: 0;
        font-size: 24px;
        font-weight: 700;
        color: #1f2937;
    }
    .header-subtitle {
        margin: 2px 0 0 0;
        font-size: 14px;
        color: #6b7280;
    }
    
    /* Botón naranja con icono SVG incrustado vía CSS */
    div.stButton > button:first-child {
        background-color: #f25c05;
        color: white;
        font-weight: 600;
        border-radius: 8px;
        border: none;
        padding: 12px 24px;
        width: 100%;
        font-size: 16px;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 8px;
        box-shadow: 0 4px 6px rgba(242, 92, 5, 0.2);
        transition: all 0.2s ease;
    }
    div.stButton > button:first-child:hover {
        background-color: #d95002;
        color: white;
        border: none;
    }
    div.stButton > button:first-child::before {
        content: "";
        display: inline-block;
        width: 20px;
        height: 20px;
        margin-right: 6px;
        background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 256 256'%3E%3Cpath fill='white' d='M224,48H32a8,8,0,0,0-8,8V192a16,16,0,0,0,16,16H216a16,16,0,0,0,16-16V56A8,8,0,0,0,224,48Zm-96,85.15L52.57,64H203.43ZM98.71,128,40,181.81V74.19Zm11.84,10.85,12,11.05a8,8,0,0,0,10.82,0l12-11.05,58,53.15H52.57ZM157.29,128,216,74.18V181.82Z'/%3E%3C/svg%3E");
        background-size: contain;
        background-repeat: no-repeat;
    }

    /* Caja de estado vacío */
    .empty-box {
        text-align: center;
        padding: 45px 20px;
        border: 1px solid #f0f0f0;
        border-radius: 12px;
        background-color: #fafafa;
        color: #6b7280;
        margin-top: 15px;
    }
    .label-title {
        font-weight: 600;
        font-size: 14px;
        color: #374151;
        margin-bottom: 6px;
        display: flex;
        align-items: center;
        gap: 6px;
    }
    </style>
""", unsafe_allow_html=True)

# Cabecera con Phosphor Icon (ph-duotone ph-envelope-open)
st.markdown("""
    <div class="header-container">
        <div class="icon-box">
            <i class="ph-duotone ph-envelope-open"></i>
        </div>
        <div>
            <h1 class="header-title">Quick Read Hotmail</h1>
            <p class="header-subtitle">Quick access to read Hotmail/Outlook emails</p>
        </div>
    </div>
""", unsafe_allow_html=True)

# Etiqueta con icono Phosphor
st.markdown('<div class="label-title"><i class="ph ph-key"></i> Email Credentials</div>', unsafe_allow_html=True)

credenciales = st.text_area(
    "Email Credentials",
    placeholder="email|password|refresh_token|client_id",
    height=115,
    label_visibility="collapsed"
)

def obtener_access_token(client_id, refresh_token):
    url = "https://login.microsoftonline.com/common/oauth2/v2.0/token"
    datos = {
        "client_id": client_id.strip(),
        "refresh_token": refresh_token.strip(),
        "grant_type": "refresh_token",
    }
    respuesta = requests.post(url, data=datos)
    return respuesta.json()

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

# El botón ya incluye el SVG de sobre de correo automáticamente vía CSS
if st.button("Read Emails"):
    if not credenciales or "|" not in credenciales:
        st.warning("Ingresa los datos en el formato exacto: email|password|refresh_token|client_id")
    else:
        partes = credenciales.strip().split("|")
        if len(partes) < 4:
            st.error("Formato incompleto. Asegúrate de incluir las 4 partes separadas por '|'.")
        else:
            correo, password, refresh_token, client_id = partes[0], partes[1], partes[2], partes[3]
            
            with st.spinner("Conectando con el servidor IMAP de Microsoft..."):
                token_data = obtener_access_token(client_id, refresh_token)
                
                if "access_token" not in token_data:
                    st.error("Error al generar el token OAuth2. Verifica que el refresh_token siga activo.")
                    with st.expander("Detalle técnico"):
                        st.json(token_data)
                else:
                    try:
                        correos = leer_correos_imap(correo.strip(), token_data["access_token"], cantidad=10)
                        if not correos:
                            st.markdown("""
                                <div class="empty-box">
                                    <i class="ph-fill ph-tray" style="font-size: 48px; color: #d1d5db;"></i>
                                    <h3 style="margin: 12px 0 4px 0; color: #1f2937; font-size: 18px;">No Emails Found</h3>
                                    <p style="margin: 0; font-size: 14px;">The inbox is currently empty</p>
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
                                        <div style="font-size: 13px; color: #6b7280; margin-bottom: 10px; display: flex; gap: 15px;">
                                            <span><i class="ph ph-user"></i> {c['remitente']}</span>
                                            <span><i class="ph ph-calendar-blank"></i> {c['fecha']}</span>
                                        </div>
                                    """, unsafe_allow_html=True)
                                    st.components.v1.html(c["cuerpo"], height=350, scrolling=True)
                    except Exception as e:
                        st.error(f"Error de conexión IMAP: {str(e)}")
else:
    # Estado inicial idéntico a la captura usando Phosphor Icons (ph-tray)
    st.markdown("""
        <div class="empty-box">
            <i class="ph-fill ph-tray" style="font-size: 52px; color: #d1d5db;"></i>
            <h3 style="margin: 12px 0 6px 0; color: #1f2937; font-size: 18px; font-weight: 700;">No Emails Yet</h3>
            <p style="margin: 0; font-size: 14px;">Enter your credentials above to read your emails</p>
        </div>
    """, unsafe_allow_html=True)
