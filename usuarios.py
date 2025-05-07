import streamlit as st
import pandas as pd

# Dados simulados
data = {
    "E-mail": ["email@email.com"] * 15,
    "Nome Completo": ["Matheus", "Aline Oliveira Rocha", "Barbara Almeida"] * 5,
    "Último login": ["03/04/2025"] * 15,
    "Data criação": ["03/04/2025"] * 15,
    "Data conf.": ["03/04/2025"] * 15,
    "Perfil": ["Itaú Cultural"] * 15,
}
df = pd.DataFrame(data)


st.header('teste', divider=True)
col1, col2 = st.columns([4, 1])
with col1:
    st.text_input('',placeholder="Pesquisar")
with col2:
    Page_cliente = st.selectbox(
    'Perfis', ['Perfil1', 'Perfil2', 'Perfil3'], 0)

st.dataframe(df, hide_index=True)
