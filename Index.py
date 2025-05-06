import streamlit as st
from PIL import Image

icone = Image.open("Fundação Itaú/imagens/icone.png")

st.set_page_config(
    page_title='Fundação Itaú',
    page_icon=icone,  # Passa o objeto de imagem diretamente
    layout="wide",
    initial_sidebar_state='auto',
    menu_items={
        'Get Help': 'https://www.extremelycoolapp.com/help',
        'Report a bug': "https://www.extremelycoolapp.com/bug",
        'About': "# This is a header. This is an *extremely* cool app!"
    }
)



pages = {
    "Navegação": [
        st.Page("organizacoes.py", title="Organizações", icon=":material/corporate_fare:"),
        st.Page("perfis.py", title="Meus Perfis", icon=":material/sell:"),
        st.Page("usuarios.py", title="Usuários", icon=":material/group:")
    ]
}
pg = st.navigation(pages)
pg.run()

st.logo('Fundação Itaú/imagens/Logo.png',size='medium',icon_image='Fundação Itaú/imagens/Logo.png')

with st.sidebar.popover('Matheus', icon=":material/person:", use_container_width=False):
    col1, col2 = st.columns([1.2, 1])  # coluna da esquerda um pouco maior

    with col1:
        st.markdown("<div style='padding-right:0px;'><h4>MATHEUS COSTA DA TRINDADE</h4></div>", unsafe_allow_html=True)

    with col2:
        st.markdown("""
            <div style='border-left: 2px solid #ccc; padding-left: 10px;'>
                <p style='margin-bottom: 0;'>Account</p>
                <p style='margin-top: 4px;'>Log out</p>
            </div>
        """, unsafe_allow_html=True)
        st.write("teste")
