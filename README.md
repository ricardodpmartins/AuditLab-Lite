
# AuditLab Lite

## 1. Apresentação do projeto

O AuditLab Lite é um projeto desenvolvido no âmbito da unidade curricular de Arquitetura e Padrões de Software, do ano letivo 2026/2027.

O objetivo é desenvolver um Activity Provider para a plataforma Inven!RA, disponibilizando uma atividade educativa relacionada com o controlo de acessos a sistemas de informação.

Na atividade prevista, os alunos irão analisar dados fictícios de contas de utilizador e identificar possíveis irregularidades. Um exemplo consiste na identificação de contas que permanecem ativas após a saída dos respetivos colaboradores.

A aplicação deverá avaliar as respostas dos alunos e disponibilizar indicadores sobre o desempenho na atividade.

Nesta primeira fase, o desenvolvimento concentra-se na implementação dos serviços REST necessários à comunicação com a Inven!RA. A atividade do aluno e o respetivo mecanismo de avaliação ainda não estão implementados.

## 2. Tecnologias utilizadas

O projeto utiliza as seguintes tecnologias:

- Python: linguagem de programação utilizada no desenvolvimento.
- FastAPI: framework responsável pela implementação dos serviços REST.
- Uvicorn: servidor utilizado para executar a aplicação FastAPI.
- Pytest: ferramenta utilizada na execução dos testes automatizados.
- HTTPX: biblioteca utilizada pelo cliente de testes.
- Git: sistema de controlo de versões.
- GitHub: plataforma escolhida para alojar o repositório do projeto.
- Render: plataforma prevista para disponibilizar o Activity Provider através da Internet.

O desenvolvimento é realizado no Visual Studio Code, em ambiente Windows.

## 3. Arquitetura inicial

A arquitetura prevista para o AuditLab Lite contempla a separação entre a integração com a Inven!RA, a interface Web, a gestão da atividade, a avaliação das respostas, a gestão dos resultados e a persistência dos dados.

Nesta primeira fase, foi implementada apenas a componente inicial de integração com a Inven!RA, concentrando os serviços REST no ficheiro main.py.

Esta organização permite responder aos requisitos da primeira entrega sem introduzir antecipadamente componentes que ainda não são necessários.

A arquitetura poderá evoluir nas fases seguintes, à medida que forem implementadas a atividade do aluno, a avaliação das respostas e a persistência dos resultados.

### 3.1. Organização dos ficheiros

A estrutura principal do projeto é a seguinte:

    AuditLab-Lite/
        main.py
        requirements.txt
        README.md
        .gitignore
        tests/
            test_api.py

O ficheiro main.py contém a aplicação FastAPI e os serviços REST.

O ficheiro requirements.txt identifica as dependências necessárias à execução da aplicação.

O ficheiro README.md documenta o objetivo, a estrutura e o funcionamento do projeto.

O ficheiro .gitignore identifica os ficheiros e diretórios que não devem ser incluídos no repositório Git.

O ficheiro tests/test_api.py contém os testes automatizados dos serviços REST.

O ambiente virtual Python é criado localmente na pasta .venv, que não deve ser enviada para o GitHub.

## 4. Serviços REST implementados

A primeira fase do AuditLab Lite disponibiliza cinco serviços REST, correspondentes aos pedidos previstos na especificação da Inven!RA.

| Método | Endpoint | Descrição |
|---|---|---|
| GET | /config | Apresenta a página de configuração da atividade. |
| GET | /json-params | Devolve os parâmetros disponíveis na página de configuração. |
| GET | /user | Recebe o identificador de uma instância e devolve o respetivo URL. |
| GET | /analytics-list | Devolve a lista de indicadores disponíveis na atividade. |
| POST | /analytics | Devolve resultados fictícios relativos à atividade. |

Existe também um endpoint adicional, GET /, que apresenta informações sobre o projeto e os endereços dos serviços.

### 4.1. Configuração da atividade

O serviço GET /config devolve uma página HTML com os campos utilizados para configurar a atividade.

Estão disponíveis dois parâmetros:

- scenario_set: conjunto de cenários de controlo de acessos.
- max_attempts: número máximo de tentativas permitido ao aluno.

A página não possui botões para guardar ou submeter a configuração, porque a Inven!RA é responsável pela recolha e pelo armazenamento dos valores definidos pelo professor.

Nesta fase, apenas está disponível um conjunto de cenários de demonstração.

### 4.2. Identificação dos parâmetros

O serviço GET /json-params devolve uma lista JSON que identifica os campos disponíveis na página de configuração e os respetivos tipos de dados.

Exemplo de resposta:

```json
[
  {
    "name": "scenario_set",
    "type": "text/plain"
  },
  {
    "name": "max_attempts",
    "type": "integer"
  }
]
```

Os nomes apresentados correspondem aos atributos HTML name definidos na página de configuração.

### 4.3. Deploy da atividade

O serviço GET /user recebe o identificador de uma instância da atividade e devolve o URL correspondente.

Exemplo de pedido:

    GET /user?activityID=teste001

Exemplo de resposta em ambiente local:

    http://127.0.0.1:8000/atividade/teste001

O identificador recebido é guardado temporariamente em memória e utilizado para construir o endereço da instância.

O nome do parâmetro activityID é provisório, porque o documento de especificação não identifica explicitamente o nome do parâmetro enviado neste pedido GET.

O endpoint GET /atividade/{activity_id} apresenta uma página demonstrativa associada ao identificador recebido.

Esta página não implementa o serviço Provide activity, que será desenvolvido numa fase posterior.

### 4.4. Lista de indicadores disponíveis

O serviço GET /analytics-list devolve os indicadores que o AuditLab Lite prevê recolher durante a execução da atividade.

Foram definidos quatro indicadores quantitativos:

| Indicador | Tipo | Descrição |
|---|---|---|
| respostas_corretas | integer | Número de respostas corretas do aluno. |
| pontuacao | integer | Pontuação obtida na atividade. |
| tentativas_utilizadas | integer | Número de tentativas realizadas. |
| concluida | boolean | Indica se o aluno concluiu a atividade. |

A resposta contém as propriedades quantAnalytics e qualAnalytics.

Nesta fase, não foram definidos indicadores qualitativos.

Os indicadores quantitativos estão identificados, mas ainda não existe recolha efetiva de resultados.

### 4.5. Consulta de analytics

O serviço POST /analytics recebe um objeto JSON com o identificador da instância cujos resultados se pretende consultar.

Exemplo de pedido:

```json
{
  "activityID": "teste001"
}
```

A resposta contém uma lista de alunos e os respetivos indicadores.

Exemplo de resposta:

```json
[
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
        "value": true
      }
    ],
    "qualAnalytics": []
  }
]
```

Nesta primeira versão, os resultados são fictícios e não correspondem à execução de uma atividade por um aluno.

O identificador recebido é validado pelo FastAPI, mas ainda não é utilizado para selecionar resultados específicos.

## 5. Instalação e execução no Windows

### 5.1. Requisitos

Para executar o projeto localmente, é necessário ter o Python instalado.

O desenvolvimento e os testes iniciais foram realizados com Python 3.14.10.

### 5.2. Criar o ambiente virtual

Abrir a pasta do projeto no Visual Studio Code e executar os seguintes comandos no terminal PowerShell:

```powershell
cd C:\Users\rdpma\ARQ\AuditLab-Lite

py -m venv .venv
```

O ambiente virtual permite instalar as dependências do projeto sem interferir diretamente com outras instalações Python do computador.

### 5.3. Instalar as dependências

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### 5.4. Executar o servidor

```powershell
.\.venv\Scripts\python.exe -m uvicorn main:app --reload
```

Após o arranque, a aplicação fica disponível no endereço:

    http://127.0.0.1:8000

A documentação interativa dos serviços REST pode ser consultada em:

    http://127.0.0.1:8000/docs

O parâmetro --reload permite reiniciar automaticamente o servidor quando são detetadas alterações ao código durante o desenvolvimento.

## 6. Testes automatizados

Os testes automatizados encontram-se no ficheiro tests/test_api.py e utilizam o TestClient do FastAPI.

São verificadas as seguintes funcionalidades:

1. Disponibilidade da página inicial e identificação dos cinco serviços REST.
2. Existência dos campos esperados na página de configuração.
3. Identificação dos parâmetros configuráveis.
4. Funcionamento do serviço de deploy e acesso ao URL devolvido.
5. Disponibilidade e estrutura das respostas dos serviços de analytics.

Para instalar as dependências necessárias aos testes:

```powershell
.\.venv\Scripts\python.exe -m pip install pytest httpx
```

Para executar os testes:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

Na validação local realizada em 18 de novembro de 2026, os cinco testes foram concluídos com sucesso.

Foi apresentado um aviso de descontinuação relacionado com a utilização de httpx pelo cliente de testes. O aviso não impediu a execução dos testes.

Estes testes verificam o funcionamento básico dos serviços, mas não comprovam ainda a integração efetiva com a plataforma Inven!RA.

## 7. Publicação no Render

O alojamento do Activity Provider será efetuado através do Render, utilizando o repositório GitHub como origem do código.

A configuração prevista para o Web Service é a seguinte:

| Parâmetro | Valor |
|---|---|
| Language | Python 3 |
| Branch | main |
| Build Command | pip install -r requirements.txt |
| Start Command | uvicorn main:app --host 0.0.0.0 --port $PORT |

Após a publicação, o Render atribui um endereço HTTPS público.

Esse endereço será utilizado para testar os serviços REST fora do ambiente local e para efetuar a submissão da primeira entrega no Moodle.

A publicação e os testes em ambiente público ainda não foram concluídos.

## 8. Limitações da implementação atual

A primeira versão do AuditLab Lite foi desenvolvida para responder aos requisitos da primeira semana da atividade prática.

Existem limitações que serão tratadas nas fases seguintes.

### 8.1. Persistência dos dados

Os identificadores das instâncias são guardados num conjunto Python em memória.

Os dados desaparecem quando o processo é reiniciado e não são partilhados entre diferentes processos.

Ainda não existe uma base de dados.

### 8.2. Resultados fictícios

O serviço de analytics devolve valores fixos para um aluno fictício.

Não existe ainda um mecanismo que recolha respostas dos alunos, calcule pontuações ou associe os resultados a uma instância específica.

### 8.3. Serviço de deploy

O serviço devolve um URL demonstrativo, mas ainda não cria uma instância persistente com dados próprios.

O nome do parâmetro GET utilizado para identificar a instância necessita de confirmação.

### 8.4. Atividade do aluno

A interface onde os alunos irão analisar contas de utilizador e identificar falhas de controlo de acessos ainda não foi implementada.

O endpoint demonstrativo não substitui o serviço Provide activity previsto na especificação da Inven!RA.

### 8.5. Integração com a Inven!RA

Os formatos dos serviços foram definidos com base na documentação disponibilizada na unidade curricular.

Apesar dos testes locais, ainda não foi realizada uma validação integrada com uma instância real da Inven!RA.

## 9. Desenvolvimento previsto

Nas semanas seguintes, o projeto deverá evoluir para incluir:

1. Implementação de um padrão de criação adequado a uma necessidade concreta do AuditLab Lite.
2. Documentação do padrão através de diagramas de componentes e de sequência.
3. Desenvolvimento da interface destinada aos alunos.
4. Implementação dos cenários fictícios de controlo de acessos.
5. Avaliação das respostas e cálculo das pontuações.
6. Persistência das instâncias e dos resultados.
7. Integração do serviço Provide activity com a plataforma Inven!RA.

A implementação do padrão de criação e os respetivos diagramas fazem parte da entrega prevista para 6 de dezembro de 2026.

As restantes funcionalidades serão desenvolvidas de acordo com as fases posteriores do projeto.

## 10. Referências

Morgado, L., & Cassola, F. (2022). *Activity Providers na Inven!RA*. Documento de apoio disponibilizado na unidade curricular de Arquitetura e Padrões de Software, Universidade Aberta.
```