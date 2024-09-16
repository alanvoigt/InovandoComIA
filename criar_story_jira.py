import openai
from jira import JIRA
from dotenv import load_dotenv
import os

# O sistema deve permitir que o usuário faça login usando email e senha e veja seu dashboard.

# Carregar as variáveis do arquivo .env
load_dotenv()

# Configuração da API do OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

# Configuração da API do Jira
jira = JIRA(server=os.getenv("JIRA_SERVER"), basic_auth=(os.getenv("JIRA_EMAIL"), os.getenv("JIRA_API_TOKEN")))

# Função para gerar o título e a história de usuário
def gerar_historia_usuario_e_titulo(requisito):
    prompt = f"""
    Transforme o seguinte requisito em uma história de usuário com critérios de aceitação e forneça também um título adequado para a história:

    Requisito: {requisito}

    Responda no seguinte formato:
    Título: [Título Gerado]
    História de Usuário: [História com Critérios de Aceitação]
    """

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "system", "content": "Você é um assistente que cria histórias de usuário."},
                  {"role": "user", "content": prompt}],
        max_tokens=500,
        temperature=0.7
    )

    resposta = response['choices'][0]['message']['content'].strip()

    # Separar o título da história de usuário
    titulo, historia_usuario = resposta.split("História de Usuário:")
    titulo = titulo.replace("Título:", "").strip()
    historia_usuario = historia_usuario.strip()

    return titulo, historia_usuario

# Função para gerar 3 casos de teste no formato Gherkin
def gerar_testes_gherkin(requisito):
    prompt = f"""
    Gere 3 casos de teste no formato Gherkin para o seguinte requisito:

    Requisito: {requisito}

    Responda no formato:
    Teste 1:
    Dado [condição]
    Quando [ação]
    Então [resultado]

    Teste 2:
    Dado [condição]
    Quando [ação]
    Então [resultado]

    Teste 3:
    Dado [condição]
    Quando [ação]
    Então [resultado]
    """

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "system", "content": "Você é um assistente que cria casos de teste no formato Gherkin."},
                  {"role": "user", "content": prompt}],
        max_tokens=500,
        temperature=0.7
    )

    resposta = response['choices'][0]['message']['content'].strip()
    return resposta

# Função para criar a história no Jira
def criar_historia_no_jira(projeto_key, titulo, descricao):
    issue_dict = {
        'project': {'key': projeto_key},
        'summary': titulo,
        'description': descricao,
        'issuetype': {'name': 'Task'},
    }

    nova_historia = jira.create_issue(fields=issue_dict)
    return nova_historia

# Função para adicionar os casos de teste como comentário no Jira
def adicionar_comentario_jira(issue_key, comentario):
    jira.add_comment(issue_key, comentario)

# Entrada do usuário para o requisito
requisito = input("Digite o requisito: ")

# Gerar o título e a história de usuário com critérios de aceitação
titulo, historia_gerada = gerar_historia_usuario_e_titulo(requisito)

# Criar a história no Jira
projeto_key = "IN"  # Substitua pela chave do seu projeto no Jira
nova_historia = criar_historia_no_jira(projeto_key, titulo, historia_gerada)

# Gerar casos de teste no formato Gherkin
casos_de_teste = gerar_testes_gherkin(requisito)

# Adicionar os casos de teste como comentário na história criada
adicionar_comentario_jira(nova_historia.key, casos_de_teste)

print(f"História criada no Jira: {nova_historia.key}")
print(f"Casos de teste Gherkin adicionados como comentário.")
