import streamlit as st
from streamlit_oauth import OAuth2Component
from google.oauth2 import id_token
from google.auth.transport import requests
from jose import jwt
import os

def mostrar():
    hide_streamlit_style = """
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
    </style>
    """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)

    st.image("imagens/Logo.png")
    
    client_id = os.getenv("GOOGLE_CLIENT_ID") or st.secrets.get("GOOGLE_CLIENT_ID")
    client_secret = os.getenv("GOOGLE_CLIENT_SECRET") or st.secrets.get("GOOGLE_CLIENT_SECRET")
    allowed_domains_raw = os.getenv("ALLOWED_DOMAIN") or st.secrets.get("ALLOWED_DOMAIN")
    allowed_domains = [d.strip() for d in allowed_domains_raw.split(",")]

    redirect_uri = "https://plataforma-itau-testes.streamlit.app" 

    oauth2 = OAuth2Component(
        client_id=client_id,
        client_secret=client_secret,
        authorize_endpoint="https://accounts.google.com/o/oauth2/v2/auth",
        token_endpoint="https://oauth2.googleapis.com/token",
    )
    
    col1, col2, col3 = st.columns([1.8, 3, 1])
    with col2:
        token = oauth2.authorize_button(
            name="Entrar com Google",
            redirect_uri=redirect_uri,
            scope="openid email profile",
            key="google-login"
        )
    if token is not None:
        
        tokenTest = token.get("token")
        id_token2 = tokenTest.get("id_token")
        if id_token:
            decoded = id_token.verify_oauth2_token(id_token2,requests.Request())
            st.write(decoded)
            domain = decoded.get("hd")
            nomeUsuario = decoded.get("name")
            
            if domain not in allowed_domains:
                st.error("Este domínio não esta permitido nesta plataforma, recarregue a página e tente novamente!!!")
                return
            
        st.session_state['autenticado'] = True
        st.session_state['nomeUsuario'] = nomeUsuario
        st.rerun()
