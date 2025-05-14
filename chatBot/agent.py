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

# Configuração da página deve estar no início
st.set_page_config(layout="wide")


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

df = pd.read_excel("respostas_contratos.xlsx")
#df = pd.DataFrame()
def criar_agent(df):
    return create_pandas_dataframe_agent(
        llm,
        df,
        prefix=agent_prompt_prefix,
        verbose=True,
        agent_type=AgentType.OPENAI_FUNCTIONS,
        allow_dangerous_code=True
    )

agent = criar_agent(df)
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

def processar_arquivo_upload(arquivo):
    global agent #, df
    extensao = arquivo.name.split('.')[-1].lower()
    if extensao == 'csv':
        df = pd.read_csv(arquivo)
    elif extensao in ['xls', 'xlsx']:
        df = pd.read_excel(arquivo)
    else:
        st.error('Formato de arquivo não suportado.')
        return

    agent = criar_agent(df)
    st.success('Arquivo processado com sucesso! Você já pode fazer perguntas sobre os dados.')

def inicializacao():
    if not 'mensagens' in st.session_state:
        st.session_state.mensagens = []
    if not 'conversa_atual' in st.session_state:
        st.session_state.conversa_atual = ''

def pagina_principal():

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

    st.markdown('<div class="big-font">🤖 ChatBot Ventify</div>', unsafe_allow_html=True)

    # Adicionando uma linha cinza claro
    st.markdown('<hr style="border-top: 1px solid #0C2D78;">', unsafe_allow_html=True)
  
    for mensagem in mensagens:
        if mensagem['role'] == 'user':
            chat = st.chat_message(mensagem['role'], avatar = '👨‍💼')
            chat.markdown(mensagem['content'])
        else:
            chat = st.chat_message(mensagem['role'], avatar='🤖')
            chat.markdown(mensagem['content'])
    
    arquivo_upload = st.file_uploader("Escolha um arquivo CSV ou Excel", type=["xls", "xlsx"],label_visibility='collapsed')
    if arquivo_upload:
        processar_arquivo_upload(arquivo_upload)
    
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

def pagina_perguntas_prontas():
    # Exibindo o título da página
    st.markdown("""
    <style>
    .big-font {
        font-size:35px !important;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)
    st.markdown('<div class="big-font">🤖 ChatBot Ventify</div>', unsafe_allow_html=True)
    st.markdown('<hr style="border-top: 1px solid #35E4DB;">', unsafe_allow_html=True)

    # Carregar os dados do DataFrame (garanta que o DataFrame esteja corretamente carregado em `df`)
    global df  # Use o DataFrame que você já carregou no início do script

    # Verifica se o DataFrame está vazio
    if df.empty:
        st.error("O DataFrame está vazio. Faça o upload de um arquivo válido.")
        return

    # Seleciona a coluna do DataFrame que representa os contratos
    coluna_contrato = 'Contrato'  # Substitua pelo nome correto da coluna que contém os contratos
    #colunas_disponiveis = list(df.columns)

    # Criar seletores para contrato e informação desejada
    contrato_selecionado = st.selectbox("Selecione o contrato:", df[coluna_contrato].unique())

    #Mexendo para pegar apenas as colunas referentes ao tipo do contrato
    df_intermediario = df.loc[df[coluna_contrato]==contrato_selecionado]

    if df_intermediario['Tipo do contrato'].iloc[0] == 'obra':
        colunas_disponiveis = ['Quem é o licenciante da obra?','Qual o prazo da licença para exibição da obra?',
                               'Qual o prazo de vigência do contrato?','Quando começa a contar o prazo da licença?',
                               'Qual o valor da licença?','A obra pode ser exibida em plataformas parceiras?',
                               'A obra pode ser exibida na IC Play?','A licença pode ser renovada?',
                               'Qual prazo para retirada da obra da IC Play após a rescisão do contrato?',
                               'Qual território posso exibir a obra?']
        
    elif df_intermediario['Tipo do contrato'].iloc[0] == 'festival':
        colunas_disponiveis = ['Qual o nome e edição do Festival?','Qual o tipo de parceria a Fundação vai ter com o Festival?',
                               'A parceria com o Festival é por quantos anos?','A parceria com o Festival é renovável automaticamente?',
                               'Qual é o Prêmio Ic Play deste Festival?','Por qual prazo as obras do Festival serão licenciadas para o Ic Play?',
                               'É possível rescindir o contrato com o festival ou com a parceira a critério da Fundação Itaú?',
                               'O Festival pode licenciar diretamente as obras para o Ic Play?','Se interrompidos os serviços contratados, o que é devido?',
                               'Quais obrigações ou contrapartidas a Licenciante ou Parceira tem no contrato?']

    informacao_desejada = st.selectbox("Selecione a informação que deseja obter:", [col for col in colunas_disponiveis if col != coluna_contrato])

    # Botão para buscar a informação
    if st.button("Buscar Informação"):
        # Filtragem do DataFrame com base no contrato selecionado
        resultado = df[df[coluna_contrato] == contrato_selecionado]

        if not resultado.empty:
            # Exibindo o valor desejado da coluna
            valor_desejado = resultado[informacao_desejada].iloc[0]
            st.success(f"{valor_desejado}")
        else:
            st.error("Contrato não encontrado no DataFrame.")

def tab_conversas():
    st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Lato:wght@400;700&display=swap');
    .stButton > button {
        background-color: #EC7000 !important;
        opacity: 0.8;
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
        background-color: #EC7000 !important;
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
        width: 60px; /* Ajuste o tamanho do logo conforme necessário */
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
        <img src="data:image/svg+xml;base64,{image_to_base64(f'{CAMINHO_PASTA_ATUAL}/logo_itau.svg')}" alt="Logo">
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
        width: 200px;
        margin-bottom: 20px;
    }}
    .login-container h1 {{
        font-size: 20px;
        font-family: 'Lato', sans-serif;
        margin-bottom: 20px;
    }}
    .login-container a {{
        background-color: #EC7000;
        opacity: 0.8;
        color: white;
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
            <h1>Que bom te ver aqui no ChatBot Ventify! Faça login para começar.</h1>
            <div class="botao-login">
                <a href="{}" target="_self">Fazer Login</a>
            </div>
        </div>
    </div>
    """.format(image_to_base64(f"{CAMINHO_PASTA_ATUAL}/logo_itau.svg"), os.getenv("LOGIN_URL")), unsafe_allow_html=True)

def image_to_base64(image_path):
    import base64
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()
    return encoded_string

def main():
    inicializacao()
    
    # Opção de seleção entre as duas páginas iniciais
    escolha = st.radio(
        "Como deseja usar o ChatBot Ventify?",
        ("Conversar com o Chat", "Perguntas Prontas"),
        horizontal=True,
        index=1
    )

    if escolha == "Conversar com o Chat":
        pagina_principal()
        with st.sidebar:
            st.header("Conversas")
            tab_conversas()
    elif escolha == "Perguntas Prontas":
        pagina_perguntas_prontas()       
        

if __name__ == '__main__':
    main()
