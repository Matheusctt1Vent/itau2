import streamlit as st
import os
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

def mostrar():
    st.image("imagens/Logo.png")
    
    with open('config.yaml') as file:
        config = yaml.load(file, Loader=SafeLoader)

    authenticator = stauth.Authenticate(
        config['credentials'],
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days']
    )

    try:
        authenticator.experimental_guest_login('Login with Google',
                                            provider='google',
                                            oauth2=config['oauth2'],
                                            use_container_width=True)
    except Exception as e:
        st.error(e)

    if st.session_state.get('authentication_status'):
        st.session_state['authentication_status'] = None
        st.session_state['autenticado'] = True
        st.rerun()
    elif st.session_state.get('authentication_status') is False:
        st.error('Este Dominio não esta autorizado, recarregue a pagina e tente novamente!!!')
