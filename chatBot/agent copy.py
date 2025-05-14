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

CAMINHO_PASTA_ATUAL = os.getcwd()

openai_api_key = os.getenv("OPENAI_API_KEY")
os.environ["OPENAI_API_KEY"] = openai_api_key
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
        margin: 0;
        font-size:35px !important;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Lato:wght@400;700&display=swap');

    .big-font {
        margin: 0;
        font-size: 35px !important;
        text-align: center;
        font-family: 'Lato', sans-serif;
        font-weight: 700;
        color: white;
    }
    </style>
    <div class="big-font">🤖 CHATBOT VENT</div>
    """, unsafe_allow_html=True)

    # Adicionando uma linha cinza claro
    st.markdown('<hr style="border-top: 1px solid #35E4DB;">', unsafe_allow_html=True)
  
    for mensagem in mensagens:
        if mensagem['role'] == 'user':
            chat = st.chat_message(mensagem['role'], avatar = '👨‍💼')
            chat.markdown(mensagem['content'])
        else:
            chat = st.chat_message(mensagem['role'], avatar='🤖')
            chat.markdown(mensagem['content'])

    #Markdown chat
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Lato:wght@400;700&display=swap');
    .stMarkdown p {
        font-size: 18px;
        font-family: 'Lato', sans-serif;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

    prompt = st.chat_input('Sinta-se à vontade, fale com nosso assistente')
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
    st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Lato:wght@400;700&display=swap');
    .stButton > button {
        background-color: #399994 !important;
        color: white !important;
        border: none !important;
        padding: 10px 15px !important;
        text-align: center !important;
        text-decoration: none !important;
        display: inline-block !important;
        font-size: 16px !important;
        font-family: 'Lato', sans-serif;
        margin: 0px 2px !important;
        cursor: pointer !important;
        border-radius: 20px !important;
        transition: background-color 0.3s !important;
    }
    .stButton > button:hover {
        background-color: #399994 !important;
        opacity: 0.8;
        transform: scale(1.02);
    }

    /* Estilo para fixar o logo no canto inferior esquerdo */
    .logo-container {
        position: fixed;
        bottom: 15px;
        left: 15px;
    }

    .logo-container img {
        width: 80px; /* Ajuste o tamanho do logo conforme necessário */
    }
    </style>
    """,
    unsafe_allow_html=True
    )

    # Conteúdo da aba de conversas
    st.button('➕ Nova conversa', on_click=seleciona_conversa, args=('', ), use_container_width=True)
    st.markdown('')
    conversas = listar_conversas()
    for nome_arquivo in conversas:
        nome_mensagem = desconverte_nome_mensagem(nome_arquivo).capitalize()
        if len(nome_mensagem) == 30:
            nome_mensagem += '...'
        st.button(nome_mensagem,
                  on_click=seleciona_conversa,
                  args=(nome_arquivo,),
                  disabled=nome_arquivo == st.session_state['conversa_atual'],
                  use_container_width=True)

    # Adicionar o logo na parte inferior esquerda
    st.markdown(f"""
    <div class="logo-container">
        <img src="data:image/svg+xml;base64,{image_to_base64(f'{CAMINHO_PASTA_ATUAL}/logo-vent-azul.svg')}" alt="Logo">
    </div>
    """, unsafe_allow_html=True)

def seleciona_conversa(nome_arquivo):
    if nome_arquivo == '':
        st.session_state['mensagens'] = []
    else:
        mensagem = ler_mensagem_por_nome_arquivo(nome_arquivo)
        st.session_state['mensagens'] = mensagem
    st.session_state['conversa_atual'] = nome_arquivo

def mostra_login():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Lato:wght@400;700&display=swap');
    .login-page {{
        display: flex;
        justify-content: center;
        align-items: center;
        height: 30vh;
        flex-direction: column;
    }}
    .login-container {{
        text-align: center;
    }}
    .login-container img {{
        width: 250px;
        margin-bottom: 20px;
    }}
    .login-container h1 {{
        font-size: 20px;
        font-family: 'Lato', sans-serif;
        margin-bottom: 20px;
    }}
    .login-container a {{
        background-color: #35E4DB;
        opacity: 1;
        color: black;
        padding: 10px 20px;
        text-decoration: none;
        border-radius: 5px;
        font-size: 16px;
        font-family: 'Lato', sans-serif;
    }}
    .botao-login{{
        display: inline-block;
        justify-content: center;
    }}
    .botao-login:hover{{
        transform: scale(1.12);
    }}
    </style>
    <div class="login-page">
        <div class="login-container">
            <img src="data:image/svg+xml;base64,{}" />
            <h1>Que bom te ver aqui no CHATBOT VENT! Faça login para começar.</h1>
            <div class="botao-login">
                <a href="{}" target="_self">Fazer Login</a>
            </div>
        </div>
    </div>
    """.format(image_to_base64(f"{CAMINHO_PASTA_ATUAL}/logo-vent-azul.svg"), os.getenv("LOGIN_URL")), unsafe_allow_html=True)

def image_to_base64(image_path):
    import base64
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()
    return encoded_string

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
