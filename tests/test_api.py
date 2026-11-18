
"""
Testes automatizados dos serviços REST do AuditLab Lite.

Este ficheiro contém cinco testes que verificam o funcionamento básico dos serviços implementados na primeira fase do projeto.

Os testes utilizam o TestClient do FastAPI para enviar pedidos HTTP à aplicação e verificar as respostas obtidas.

São validados os seguintes aspetos:
1. Identificação dos cinco serviços REST na página inicial.
2. Existência dos campos esperados na página de configuração.
3. Identificação dos parâmetros configuráveis.
4. Funcionamento do serviço de deploy e do URL devolvido.
5. Estrutura da lista de analytics e dos resultados apresentados.

Os testes utilizam dados de demonstração e não verificam ainda a avaliação de respostas dos alunos ou a persistência dos resultados.
"""


# ==============================================================
# 1. IMPORTAÇÃO DAS BIBLIOTECAS
# ==============================================================

# Cliente de testes do FastAPI que permite enviar pedidos HTTP à aplicação sem iniciar um servidor externo.
from fastapi.testclient import TestClient

# Importação da instância principal da aplicação definida no ficheiro main.py.
from main import app


# ==============================================================
# 2. INICIALIZAÇÃO DO CLIENTE DE TESTES
# ==============================================================

# Criação do cliente que será utilizado para executar os pedidos aos serviços REST.
client = TestClient(app)


# ==============================================================
# 3. TESTE DA PÁGINA INICIAL
# ==============================================================

def test_inicio_tem_cinco_servicos():
    """
    Verifica se a página inicial responde corretamente e apresenta os cinco serviços REST previstos para a primeira entrega.

    O teste confirma que o pedido devolve o código HTTP 200 e que o objeto JSON contém exatamente cinco entradas na propriedade servicos.
    """

    # Envia um pedido GET à página inicial.
    resposta = client.get("/")

    # Confirma que o servidor respondeu com sucesso.
    assert resposta.status_code == 200

    # Confirma que a página inicial identifica cinco serviços REST.
    assert len(resposta.json()["servicos"]) == 5


# ==============================================================
# 4. TESTE DA PÁGINA DE CONFIGURAÇÃO
# ==============================================================

def test_config_tem_campos_nomeados_sem_botao_guardar():
    """
    Verifica se a página de configuração contém os campos necessários para a atividade.

    A Inven!RA precisa de identificar os campos através do atributo HTML name, pelo que o teste confirma a existência de scenario_set e max_attempts.

    Também verifica que a página não contém elementos HTML button, uma vez que a recolha e o armazenamento da configuração são da responsabilidade da Inven!RA.
    """

    # Solicita a página HTML de configuração.
    resposta = client.get("/config")

    # Confirma que o pedido foi processado com sucesso.
    assert resposta.status_code == 200

    # Verifica a existência do campo destinado à seleção do conjunto de cenários.
    assert 'name="scenario_set"' in resposta.text

    # Verifica a existência do campo que define o número máximo de tentativas.
    assert 'name="max_attempts"' in resposta.text

    # Confirma que a página não apresenta elementos HTML button.
    assert "<button" not in resposta.text


# ==============================================================
# 5. TESTE DOS PARÂMETROS DE CONFIGURAÇÃO
# ==============================================================

def test_parametros():
    """
    Verifica se o serviço de parâmetros devolve os nomes definidos na página de configuração.

    A resposta deve incluir os parâmetros scenario_set e max_attempts, permitindo à Inven!RA identificar os valores que pode recolher.
    """

    # Envia um pedido GET ao serviço que identifica os parâmetros configuráveis.
    resposta = client.get("/json-params")

    # Confirma que o serviço respondeu com sucesso.
    assert resposta.status_code == 200

    # Compara os nomes recebidos com os dois parâmetros esperados, independentemente da ordem.
    assert {x["name"] for x in resposta.json()} == {"scenario_set", "max_attempts"}


# ==============================================================
# 6. TESTE DO SERVIÇO DE DEPLOY
# ==============================================================

def test_deploy():
    """
    Verifica se o serviço de deploy recebe o identificador da instância e devolve um URL acessível.

    O identificador utilizado no teste contém um espaço para confirmar que esse carácter é codificado corretamente no endereço devolvido.

    O teste verifica também se a página demonstrativa associada à instância responde com sucesso.

    Nesta fase, não são testadas a criação persistente da instância nem a disponibilização da atividade ao aluno.
    """

    # Envia um pedido GET com o identificador fictício da instância.
    resposta = client.get("/user", params={"activityID": "instancia 1"})

    # Confirma que o serviço de deploy respondeu com sucesso.
    assert resposta.status_code == 200

    # Verifica se o URL devolvido contém o identificador com o espaço codificado como %20.
    assert resposta.text.endswith("/atividade/instancia%201")

    # Confirma que o URL devolvido pelo serviço permite aceder à página demonstrativa.
    assert client.get(resposta.text).status_code == 200


# ==============================================================
# 7. TESTE DOS SERVIÇOS DE ANALYTICS
# ==============================================================

def test_analytics():
    """
    Verifica o funcionamento básico dos dois serviços relacionados com analytics.

    Primeiro, confirma que o serviço de listagem dos indicadores está disponível.

    Depois, envia um pedido POST com o identificador de uma instância fictícia e verifica a estrutura dos resultados devolvidos.

    O teste confirma a existência do identificador do aluno, das propriedades obrigatórias dos indicadores quantitativos e da lista de indicadores qualitativos.

    Os valores apresentados são fictícios e não resultam de respostas efetivamente submetidas por alunos.
    """

    # Verifica se o serviço que apresenta os indicadores disponíveis responde com sucesso.
    assert client.get("/analytics-list").status_code == 200

    # Solicita os resultados de uma instância através de um pedido POST com conteúdo JSON.
    resposta = client.post("/analytics", json={"activityID": "instancia 1"})

    # Confirma que o pedido foi processado com sucesso.
    assert resposta.status_code == 200

    # Obtém o primeiro aluno da lista de resultados devolvida pelo serviço.
    aluno = resposta.json()[0]

    # Confirma que o resultado contém o identificador fictício esperado para o aluno.
    assert aluno["inveniraStdID"] == "1001"

    # Verifica se todos os indicadores quantitativos apresentam as propriedades name, type e value.
    assert all(set(x) == {"name", "type", "value"} for x in aluno["quantAnalytics"])

    # Confirma que a lista de indicadores qualitativos está vazia nesta fase do projeto.
    assert aluno["qualAnalytics"] == []
