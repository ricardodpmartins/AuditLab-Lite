
"""
AuditLab Lite

Protótipo de um Activity Provider para a plataforma Inven!RA, desenvolvido no âmbito da unidade curricular de Arquitetura e Padrões de Software.

O projeto tem como objetivo disponibilizar uma atividade educativa na qual os alunos analisam dados fictícios e identificam possíveis falhas no controlo de acessos a sistemas de informação.

Nesta primeira fase, são implementados cinco serviços REST para comunicação com a Inven!RA:

1. GET /config: apresenta a página de configuração da atividade.
2. GET /json-params: identifica os parâmetros disponíveis na configuração.
3. GET /user: recebe o identificador de uma instância e devolve o respetivo URL.
4. GET /analytics-list: apresenta os indicadores disponíveis na atividade.
5. POST /analytics: devolve os resultados associados a uma atividade.

Os serviços devolvem dados de exemplo. A lógica de avaliação dos alunos e a persistência dos resultados serão desenvolvidas posteriormente.

Os formatos dos serviços seguem a especificação apresentada no documento "Activity Providers na Inven!RA", de Leonel Morgado e Fernando Cassola (2022).

O nome do parâmetro GET utilizado no serviço de deploy ainda necessita de confirmação, uma vez que não está explicitamente identificado na especificação.
"""


# ==============================================================
# 1. IMPORTAÇÃO DAS BIBLIOTECAS
# ==============================================================

# Função utilizada para converter caracteres especiais em entidades HTML.
from html import escape

# Função utilizada para codificar caracteres especiais em endereços URL.
from urllib.parse import quote

# Componentes do FastAPI necessários para criar serviços REST e tratar pedidos HTTP.
from fastapi import FastAPI, Query, Request

# Classes que permitem devolver respostas HTML e texto simples.
from fastapi.responses import HTMLResponse, PlainTextResponse

# Classe utilizada para definir e validar a estrutura dos dados recebidos em JSON.
from pydantic import BaseModel


# ==============================================================
# 2. INICIALIZAÇÃO DA APLICAÇÃO
# ==============================================================

# Criação da aplicação FastAPI, com identificação do projeto e da versão atual.
# O FastAPI disponibiliza automaticamente a documentação dos serviços no endereço /docs.
app = FastAPI(
    title="AuditLab Lite",
    version="0.1.0"
)


# ==============================================================
# 3. ARMAZENAMENTO TEMPORÁRIO DAS INSTÂNCIAS
# ==============================================================

# Conjunto que guarda os identificadores das instâncias recebidas através do serviço de deploy.
# A estrutura set impede a existência de identificadores duplicados.
# Os dados ficam apenas em memória e são perdidos quando o processo é reiniciado.
# Nesta fase, ainda não existe uma base de dados nem persistência dos resultados.
instancias_demo: set[str] = set()


# ==============================================================
# 4. MODELO DE DADOS PARA O PEDIDO DE ANALYTICS
# ==============================================================

class AnalyticsPedido(BaseModel):
    """
    Define a estrutura JSON esperada no pedido de consulta de analytics.

    A Inven!RA envia o identificador da instância da atividade através do campo activityID.

    Exemplo de pedido:
    {"activityID": "teste001"}

    O FastAPI utiliza este modelo para validar os dados recebidos antes de executar o serviço.
    """

    activityID: str


# ==============================================================
# 5. PÁGINA INICIAL DO ACTIVITY PROVIDER
# ==============================================================

@app.get("/")
def inicio(request: Request):
    """
    Devolve informações gerais sobre o AuditLab Lite e os endereços dos serviços REST.

    Este endpoint não corresponde a nenhum dos cinco serviços obrigatórios da Inven!RA. Foi acrescentado para identificar a aplicação e apresentar os serviços disponíveis.

    Os endereços são construídos a partir do URL base do pedido, evitando a definição de um domínio fixo no código.
    """

    # Obtém o endereço base da aplicação e remove a barra final, caso exista.
    base = str(request.base_url).rstrip("/")

    # Apresenta a identificação do projeto, a fase de desenvolvimento e os cinco serviços REST.
    return {
        "projeto": "AuditLab Lite",
        "fase": "Semana 1: serviços REST com dados de exemplo",
        "servicos": {
            "config_url": f"{base}/config",
            "json_params_url": f"{base}/json-params",
            "user_url": f"{base}/user",
            "analytics_url": f"{base}/analytics",
            "analytics_list_url": f"{base}/analytics-list",
        },
    }


# ==============================================================
# 6. SERVIÇO DE CONFIGURAÇÃO DA ATIVIDADE
# ==============================================================

@app.get("/config", response_class=HTMLResponse)
def configuracao():
    """
    Devolve a página HTML utilizada pelo professor ou formador para configurar a atividade.

    A configuração disponibiliza dois parâmetros:
    scenario_set: identifica o conjunto de cenários de controlo de acessos.
    max_attempts: define o número máximo de tentativas permitido ao aluno.

    A página não inclui botões para guardar ou submeter os dados, porque a recolha e o armazenamento da configuração são da responsabilidade da Inven!RA.

    Os campos HTML possuem o atributo name para que a plataforma consiga identificar e recolher os valores definidos pelo professor.
    """

    # Nesta primeira versão, apenas está disponível um conjunto de cenários de demonstração.
    return """<!doctype html>
<html lang="pt">
<head>
    <meta charset="utf-8">
    <title>AuditLab Lite: configuração</title>
</head>
<body>

    <h1>Configuração da atividade AuditLab Lite</h1>

    <!-- Campo de seleção do conjunto de cenários. -->
    <label for="scenario_set">Conjunto de cenários:</label>

    <select id="scenario_set" name="scenario_set">
        <option value="access_control_basic">
            Controlo de acessos: básico
        </option>
    </select>

    <!-- Campo que define o número máximo de tentativas permitido. -->
    <label for="max_attempts">Número máximo de tentativas:</label>

    <input
        id="max_attempts"
        name="max_attempts"
        type="number"
        value="2"
        min="1"
        max="10"
    >

</body>
</html>"""


# ==============================================================
# 7. SERVIÇO DE IDENTIFICAÇÃO DOS PARÂMETROS
# ==============================================================

@app.get("/json-params")
def parametros():
    """
    Devolve a lista dos parâmetros que podem ser recolhidos na página de configuração.

    A Inven!RA consulta este serviço para identificar os campos disponíveis e os respetivos tipos de dados.

    Cada parâmetro contém o nome do campo HTML e o tipo de dados esperado. Os nomes devem corresponder aos atributos name definidos no serviço /config.
    """

    # O conjunto de cenários é identificado por texto e o número máximo de tentativas por um valor inteiro.
    return [
        {
            "name": "scenario_set",
            "type": "text/plain"
        },
        {
            "name": "max_attempts",
            "type": "integer"
        },
    ]


# ==============================================================
# 8. SERVIÇO DE DEPLOY DA ATIVIDADE
# ==============================================================

@app.get("/user", response_class=PlainTextResponse)
def deploy(
    request: Request,
    activityID: str = Query(min_length=1)
):
    """
    Recebe o identificador de uma instância da atividade e devolve o URL correspondente.

    Este serviço é chamado quando o professor pretende disponibilizar a atividade aos alunos através da Inven!RA.

    O parâmetro activityID identifica a instância e é validado pelo FastAPI para garantir que não está vazio.

    O identificador é guardado temporariamente em memória e utilizado na construção do URL devolvido à plataforma.

    Exemplo de pedido:
    GET /user?activityID=teste001

    Exemplo de resposta:
    http://127.0.0.1:8000/atividade/teste001

    O nome activityID é provisório, porque a especificação não identifica explicitamente o nome do parâmetro recebido neste pedido GET.

    A criação persistente das instâncias e a disponibilização da atividade aos alunos serão implementadas numa fase posterior.
    """

    # Regista o identificador da instância no conjunto temporário de demonstração.
    instancias_demo.add(activityID)

    # Obtém o endereço base do servidor.
    base = str(request.base_url).rstrip("/")

    # Codifica o identificador para que possa ser incluído num segmento do URL.
    identificador_url = quote(activityID, safe="")

    # Devolve o endereço da página demonstrativa correspondente à instância.
    return f"{base}/atividade/{identificador_url}"


# ==============================================================
# 9. PÁGINA DEMONSTRATIVA DA INSTÂNCIA
# ==============================================================

@app.get("/atividade/{activity_id}", response_class=HTMLResponse)
def pagina_destino_demo(activity_id: str):
    """
    Apresenta uma página HTML associada ao identificador da instância recebido no URL.

    Esta página permite verificar que o endereço devolvido pelo serviço de deploy é acessível.

    Não corresponde ao serviço Provide activity previsto na especificação da Inven!RA. A atividade destinada ao aluno será desenvolvida posteriormente.
    """

    # Converte caracteres especiais do identificador em entidades HTML para evitar a interpretação de código HTML.
    identificador_html = escape(activity_id)

    # Devolve uma página informativa com o identificador da instância.
    return (
        "<!doctype html><html lang='pt'><meta charset='utf-8'>"
        "<title>AuditLab Lite</title><body><h1>AuditLab Lite</h1>"
        f"<p>Instância de demonstração: {identificador_html}</p>"
        "<p>A atividade do aluno será implementada numa fase posterior.</p>"
        "</body></html>"
    )


# ==============================================================
# 10. SERVIÇO DE LISTAGEM DE ANALYTICS
# ==============================================================

@app.get("/analytics-list")
def lista_analytics():
    """
    Devolve a lista dos indicadores que o AuditLab Lite prevê recolher.

    A Inven!RA consulta este serviço para identificar os indicadores disponíveis e associá-los aos objetivos de aprendizagem.

    A resposta contém duas categorias:
    qualAnalytics: indicadores qualitativos.
    quantAnalytics: indicadores quantitativos.

    Nesta fase, são definidos quatro indicadores quantitativos:
    respostas_corretas: número de respostas corretas do aluno.
    pontuacao: pontuação obtida na atividade.
    tentativas_utilizadas: número de tentativas realizadas.
    concluida: indica se o aluno concluiu a atividade.

    Os indicadores estão definidos, mas ainda não existe recolha efetiva de resultados.
    """

    # A atividade ainda não disponibiliza indicadores qualitativos.
    # Os quatro indicadores quantitativos serão utilizados quando o mecanismo de avaliação estiver implementado.
    return {
        "qualAnalytics": [],
        "quantAnalytics": [
            {
                "name": "respostas_corretas",
                "type": "integer"
            },
            {
                "name": "pontuacao",
                "type": "integer"
            },
            {
                "name": "tentativas_utilizadas",
                "type": "integer"
            },
            {
                "name": "concluida",
                "type": "boolean"
            },
        ],
    }


# ==============================================================
# 11. SERVIÇO DE CONSULTA DE ANALYTICS
# ==============================================================

@app.post("/analytics")
def analytics(pedido: AnalyticsPedido):
    """
    Devolve os resultados associados a uma instância da atividade.

    A Inven!RA envia um pedido HTTP POST com um objeto JSON que contém o identificador da instância.

    Exemplo de pedido:
    {"activityID": "teste001"}

    A estrutura do pedido é validada através do modelo AnalyticsPedido.

    A resposta consiste numa lista de alunos, identificados pelo campo inveniraStdID, e pelos respetivos indicadores quantitativos e qualitativos.

    Cada indicador quantitativo contém três propriedades:
    name: nome do indicador.
    type: tipo de dados.
    value: valor registado.

    Nesta primeira versão, os resultados são fictícios e não resultam da execução de uma atividade.

    O identificador recebido é validado, mas ainda não é utilizado para selecionar os resultados. Por esse motivo, todos os pedidos devolvem os mesmos dados de demonstração.
    """

    # Resultados fictícios associados a um aluno de demonstração.
    # Os valores apresentados não são calculados pelo AuditLab Lite nesta fase.
    return [
        {
            "inveniraStdID": "1001",
            "quantAnalytics": [
                {
                    "name": "respostas_corretas",
                    "type": "integer",
                    "value": 4
                },
                {
                    "name": "pontuacao",
                    "type": "integer",
                    "value": 80
                },
                {
                    "name": "tentativas_utilizadas",
                    "type": "integer",
                    "value": 1
                },
                {
                    "name": "concluida",
                    "type": "boolean",
                    "value": True
                },
            ],
            "qualAnalytics": [],
        }
    ]
