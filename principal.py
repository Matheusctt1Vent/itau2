import streamlit as st
import chatBot.teste2 as chatBot
def mostrar():
    nomeUsuario = st.session_state['nomeUsuario']
    acesso = st.sidebar.radio("Acesso Chat Bot:", options=["Admin", "Fechado"])
    pages = {
        "Navegação": [
            st.Page("organizacoes.py", title="Organizações", icon=":material/corporate_fare:"),
            st.Page("perfis.py", title="Meus Perfis", icon=":material/sell:"),
            st.Page("usuarios.py", title="Usuários", icon=":material/group:"),
            st.Page(lambda: chatBot.main(acesso), title="ChatBot", icon=":material/smart_toy:")
        ]
    }
    pg = st.navigation(pages)
    pg.run()

    st.logo('.\\imagens\\Logo.png',size='medium',icon_image='.\\imagens\\Logo.png')

    with st.sidebar.popover('User', icon=":material/person:", use_container_width=False):
        col1, col2 = st.columns([1,2])
        
        with col1:
            st.image('imagens/user.png',width=150)

        with col2:
            st.markdown(
                f"<div style='padding-right:0px;padding-top:15hpx;'><h4>{nomeUsuario}</h4></div>",
                unsafe_allow_html=True
            )

            st.markdown("</div>", unsafe_allow_html=True)
      
            if st.button("Log out", key="logout_button"):
                st.session_state['autenticado'] = False
                st.rerun()
            

            st.markdown("</div>", unsafe_allow_html=True)
