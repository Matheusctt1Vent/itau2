import streamlit as st
import pandas as pd

col1, col2,col3 = st.columns([4, 0.8,.18])

with col1:
    st.header('Meus Perfis')
with col2:
    @st.dialog("Criação de Perfil")
    def criarPerfil():
        nomePerfil = st.text_input("Nome Completo")

        emailPerfil = st.text_input("Email")

        perfil = st.text_input("Perfil")

        if st.button("Submit"):
            st.rerun()

    if "vote" not in st.session_state:
        if st.button("﹢ Adicionar Novo Perfil",use_container_width=True):
            criarPerfil()
    else:
        f"You voted for {st.session_state.vote['item']} because {st.session_state.vote['reason']}"
with col3:
    st.button('',icon=":material/download:",key='bp2')

col5, col6 = st.columns([4, 1])
with col5:
    #Utilizar select para puxar o perfil pesquisado do banco
    pesquisaPerfil = st.text_input('',placeholder="Pesquisar")
with col6:
    Page_cliente = st.selectbox(
    'Organização', ['Perfil1', 'Perfil2', 'Perfil3'], 0)
# Dados simulados
    data = {
        "E-mail": ["email@email.com"] * 15,
        "Nome Completo": ["Matheus", "Aline Oliveira Rocha", "Barbara Almeida"] * 5,
        "Último login": ["03/04/2025"] * 15,
        "Data criação": ["03/04/2025"] * 15,
        "Data conf.": ["03/04/2025"] * 15,
        "Perfil": ["Itaú Cultural"] * 15,
    }

    #Tabela utilizada para viisual
    df = pd.DataFrame(data)

st.dataframe(df, hide_index=True)

#Utilizar para fazer um select para puxar os dados de perfis desabilitados

toggleOn = st.toggle('Exibir Perfis Desabilitados')
