import streamlit as st
import login
import principal
from PIL import Image

icone = Image.open("imagens/icone.png")

autenticado = st.session_state.get('autenticado', False)
acesso = st.session_state.get('acesso', '')
nomeCompUsuario = st.session_state.get('nomeCompUsuario', '')
nomeUsuario = st.session_state.get('nomeUsuario', '')
st.set_page_config(
    page_title='Fundação Itaú',
    page_icon=icone,
    layout="wide" if autenticado else "centered",
    initial_sidebar_state='auto' if autenticado else 'collapsed',
    menu_items={
        'Get Help': 'https://www.extremelycoolapp.com/help',
        'Report a bug': "https://www.extremelycoolapp.com/bug",
        'About': "# This is a header. This is an *extremely* cool app!"
    }
)


if autenticado:
    principal.mostrar()
else:
    login.mostrar()
