import streamlit as st
from streamlit_oauth import OAuth2Component
from jose import jwt
import os

def mostrar():
    hide_streamlit_style = """
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}

        .stApp {
            background-color: #E6F4FF;
        }

        input[type="text"], input[type="password"] {
        background-color: white !important;
        color: black !important;
        border: 2px solid #b7b7b7 !important;
        border-radius: 7px !important;
        padding: 10px !important;
        }


    </style>
    """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)

    st.image("imagens/Logo.png")
    
    client_id = os.getenv("GOOGLE_CLIENT_ID") or st.secrets.get("GOOGLE_CLIENT_ID")
    client_secret = os.getenv("GOOGLE_CLIENT_SECRET") or st.secrets.get("GOOGLE_CLIENT_SECRET")
    allowed_domain = os.getenv("ALLOWED_DOMAIN") or st.secrets.get("ALLOWED_DOMAIN")
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

    if token != None:
        token2 = token.get("hd")
        if token2 != allowed_domain:
            st.error("Acesso permitido apenas para contas corporativas.")
            return

        st.session_state['autenticado'] = True
        st.rerun() 
