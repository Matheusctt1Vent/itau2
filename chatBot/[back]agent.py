import streamlit as st
from langchain.agents.agent_types import AgentType
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
from langchain_openai import ChatOpenAI
import pandas as pd
from dotenv import load_dotenv
import os
import pickle
from pathlib import Path
import re
from unidecode import unidecode
from PIL import Image
import webbrowser
import jwt


# CARREGEMENTO DE CREDENCIAIS E CRIAÇÃO DE PASTAS ==============================

load_dotenv()

PASTA_MENSAGENS = Path(__file__).parent / 'mensagens'
PASTA_MENSAGENS.mkdir(exist_ok=True)
CACHE_DESCONVERTE = {}

openai_api_key = os.getenv("OPENAI_API_KEY")

# CRIAÇÃO DO AGENTE ============================================================

llm = ChatOpenAI(model="gpt-3.5-turbo")

agent_prompt_prefix = """
Você se chama JB, e está trabalhando com um dataframe pandas no python, o nome do dataframe é 'df'."""

df = pd.read_excel("BASE_PROCESSOS.xlsx")

agent = create_pandas_dataframe_agent(
    llm,
    df,
    prefix=agent_prompt_prefix,
    verbose=True,
    agent_type=AgentType.OPENAI_FUNCTIONS,   
)

# FUNÇÕES PARA LEITURA E SALVAMENTO DE CONVERSAS  ============================

def converte_nome_mensagem(nome_mensagem):
    nome_arquivo = unidecode(nome_mensagem)
    nome_arquivo = re.sub('\W+', '', nome_arquivo).lower()
    return  nome_arquivo

def desconverte_nome_mensagem(nome_arquivo):
    if not nome_arquivo in CACHE_DESCONVERTE:
        nome_mensagem = ler_mensagem_por_nome_arquivo(nome_arquivo, key='nome_mensagem')
        CACHE_DESCONVERTE[nome_arquivo] = nome_mensagem
    return CACHE_DESCONVERTE[nome_arquivo]

def retorna_nome_da_mensagem(mensagens):
    nome_mensagem = ''
    for mensagem in mensagens:
        if mensagem['role'] == 'user':
            nome_mensagem = mensagem['content'][:30]
            break
    return nome_mensagem

def salvar_mensagens(mensagens):
    if len(mensagens) == 0:
        return False
    nome_mensagem = retorna_nome_da_mensagem(mensagens)
    nome_arquivo = converte_nome_mensagem(nome_mensagem)
    arquivo_salvar = {'nome_mensagem': nome_mensagem,
                      'nome_arquivo': nome_arquivo,
                      'mensagem': mensagens}
    with open(PASTA_MENSAGENS / nome_arquivo, 'wb') as f:
        pickle.dump(arquivo_salvar, f)

def ler_mensagens(mensagens, key='mensagem'):
    if len(mensagens) == 0:
        return []
    nome_mensagem = retorna_nome_da_mensagem(mensagens)
    nome_arquivo = converte_nome_mensagem(nome_mensagem)
    with open(PASTA_MENSAGENS / nome_arquivo, 'rb') as f:
        mensagens = pickle.load(f)
    return mensagens[key]

def ler_mensagem_por_nome_arquivo(nome_arquivo, key='mensagem'):
    with open(PASTA_MENSAGENS / nome_arquivo, 'rb') as f:
        mensagens = pickle.load(f)
    return mensagens[key]

def assist_chat(prompt):
    response = agent.invoke(prompt)
    output = response['output']
    return output

def listar_conversas():
    conversas = list(PASTA_MENSAGENS.glob('*'))
    conversas = sorted(conversas, key=lambda item: item.stat().st_mtime_ns, reverse=True)
    return [c.stem for c in conversas]



# PÁGINAS ===================================================================

def inicializacao():
    if not 'mensagens' in st.session_state:
        st.session_state.mensagens = []
    if not 'conversa_atual' in st.session_state:
        st.session_state.conversa_atual = ''

def pagina_principal():

    st.set_page_config(layout="wide")

    if 'mensagens' not in st.session_state:
        st.session_state.mensagens = []

    mensagens = st.session_state['mensagens']

    st.markdown("""
    <style>
    .big-font {
        font-size:35px !important;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="big-font">🤖 Jurídico JBS Chatbot</div>', unsafe_allow_html=True)

    # Adicionando uma linha cinza claro
    st.markdown('<hr style="border-top: 1px solid #dddddd;">', unsafe_allow_html=True)
  
    for mensagem in mensagens:
        if mensagem['role'] == 'user':
            chat = st.chat_message(mensagem['role'], avatar = '👨‍💼')
            chat.markdown(mensagem['content'])
        else:
            chat = st.chat_message(mensagem['role'], avatar='🤖')
            chat.markdown(mensagem['content'])

    prompt = st.chat_input('Fale com nosso assistente')
    if prompt:
        nova_mensagem = {'role':'user',
                         'content': prompt}
        
        chat = st.chat_message(nova_mensagem['role'], avatar = '👨‍💼')
        chat.markdown(nova_mensagem['content'])
        mensagens.append(nova_mensagem)

        chat = st.chat_message('assistant', avatar='🤖')
        resposta = assist_chat(prompt)

        nova_mensagem = {'role':'assistant',
                         'content': resposta}
        chat.markdown(nova_mensagem['content'])
        mensagens.append(nova_mensagem)

        st.session_state['mensagens'] = mensagens
        salvar_mensagens(mensagens)

def tab_conversas():
    st.button('➕ Nova conversa',
                on_click=seleciona_conversa,
                args=('', ),
                use_container_width=True)
    st.markdown('')
    conversas = listar_conversas()
    for nome_arquivo in conversas:
        nome_mensagem = desconverte_nome_mensagem(nome_arquivo).capitalize()
        if len(nome_mensagem) == 30:
            nome_mensagem += '...'
        st.button(nome_mensagem,
            on_click=seleciona_conversa,
            args=(nome_arquivo, ),
            disabled=nome_arquivo==st.session_state['conversa_atual'],
            use_container_width=True)

def seleciona_conversa(nome_arquivo):
    if nome_arquivo == '':
        st.session_state['mensagens'] = []
    else:
        mensagem = ler_mensagem_por_nome_arquivo(nome_arquivo)
        st.session_state['mensagens'] = mensagem
    st.session_state['conversa_atual'] = nome_arquivo

def mostra_login():
    st.markdown('<a href="'+os.getenv("LOGIN_URL")+'" target="_self">Fazer Login</a>', unsafe_allow_html=True)

def main():
    inicializacao()
    if not 'token' in st.query_params:
        mostra_login()

    if 'token' in st.query_params:
        try:
            # TODO: Validação provisória de token, o melhor é validar via integração com api da plataforma
            jwt.decode(st.query_params.token, key=os.getenv("JWT_SECRET_KEY"), algorithms=['HS512'])
        except:
            mostra_login()
        else:
            pagina_principal()
            with st.sidebar:
                st.header("Conversas")
                tab_conversas()         
        

if __name__ == '__main__':
    main()
