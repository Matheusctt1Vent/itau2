import streamlit as st

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

    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        if usuario == "admin" and senha == "1234":
            st.session_state['autenticado'] = True
            st.rerun()
        else:
            st.error("Usuário ou senha incorretos.")

    st.info("Email: admin ; Senha: 1234")
