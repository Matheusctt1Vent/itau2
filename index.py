import streamlit as st
import login
import principal
from PIL import Image

icone = Image.open("imagens/icone.png")

autenticado = st.session_state.get('autenticado', False)

if not autenticado:
    st.set_page_config(
    page_title='Fundação Itaú',
    page_icon=icone, 
    layout="centered",
    initial_sidebar_state='auto',
    menu_items={
        'Get Help': 'https://www.extremelycoolapp.com/help',
        'Report a bug': "https://www.extremelycoolapp.com/bug",
        'About': "# This is a header. This is an *extremely* cool app!"
    }
)

else:
    st.set_page_config(
    page_title='Fundação Itaú',
    page_icon=icone, 
    layout="wide",
    initial_sidebar_state='auto',
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
