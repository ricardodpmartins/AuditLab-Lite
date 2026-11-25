# AuditLab Lite

Projeto desenvolvido no âmbito da unidade curricular **Arquitetura e Padrões de Software**, no ano letivo 2026/2027.

## 1. Apresentação do projeto

O AuditLab Lite é um Activity Provider em desenvolvimento para a plataforma Inven!RA. O objetivo é disponibilizar uma atividade educativa sobre controlo de acessos a sistemas de informação, na qual os alunos analisam registos fictícios e identificam situações que não cumprem políticas de acesso definidas para cada exercício.

O projeto inclui cinco serviços REST com respostas demonstrativas, um catálogo de dez cenários fictícios, um motor de regras de análise e a implementação do padrão de criação **Builder**. A interface de resolução da atividade, a recolha de respostas dos alunos e a integração dos resultados reais nos serviços de analytics ainda não estão implementadas.

## 2. Tecnologias utilizadas

O projeto utiliza Python, FastAPI, Uvicorn e testes automatizados com Pytest. Os testes dos serviços REST utilizam o cliente de testes do FastAPI, com suporte HTTPX. O desenvolvimento é realizado no Visual Studio Code, em Windows, e o controlo de versões é efetuado com Git e GitHub.

O serviço público de demonstração está alojado no Render:

https://auditlab-lite.onrender.com

## 3. Organização e arquitetura

A implementação atual está dividida em módulos com responsabilidades distintas:

```text
AuditLab-Lite/
├── main.py
├── modelos.py
├── construtor_cenarios.py
├── catalogo_cenarios.py
├── regras_auditoria.py
├── requirements.txt
├── README.md
├── .gitignore
└── tests/
    ├── test_api.py
    ├── test_builder.py
    ├── test_catalogo.py
    └── test_regras_auditoria.py
```

Os diagramas UML são preparados à parte no Draw.io e devem acompanhar o código na entrega. Quando forem copiados para o projeto, podem ficar em `docs/uml/`.

O ficheiro `main.py` implementa os serviços REST e as respostas de demonstração da Inven!RA. O módulo `modelos.py` define os objetos `Registo` e `Cenario`. A classe `CenarioBuilder`, em `construtor_cenarios.py`, reúne e valida os dados antes de construir cada cenário. O módulo `catalogo_cenarios.py` define os dez exercícios e utiliza o Builder para os criar. O módulo `regras_auditoria.py` aplica as regras de deteção aos dados fictícios.

Esta separação distingue a criação dos cenários da análise dos dados. Na versão atual, os módulos de cenários e regras ainda não estão ligados à atividade Web apresentada ao aluno nem ao serviço REST de analytics.

## 4. Serviços REST da Inven!RA

Os cinco serviços pedidos para a fase inicial encontram-se implementados no FastAPI e devolvem dados de exemplo.

| Método | Endpoint | Finalidade |
|---|---|---|
| GET | `/config` | Apresentar a página HTML de configuração da atividade. |
| GET | `/json-params` | Identificar os parâmetros configuráveis e respetivos tipos. |
| GET | `/user` | Receber o identificador de uma instância e devolver um URL demonstrativo. |
| GET | `/analytics-list` | Disponibilizar a lista de indicadores de analytics. |
| POST | `/analytics` | Devolver resultados fictícios associados ao formato esperado pela plataforma. |

O endpoint adicional `GET /` apresenta informações sobre o projeto e os endereços dos serviços. O endpoint `GET /atividade/{activity_id}` apresenta uma página demonstrativa. Este último não constitui uma implementação do serviço `Provide activity`.

### 4.1. Configuração e parâmetros

O serviço `GET /config` devolve uma página HTML com os campos `scenario_set` e `max_attempts`. A página não contém um botão de submissão, porque a recolha dos valores cabe à Inven!RA.

O serviço `GET /json-params` devolve os parâmetros com os nomes correspondentes aos atributos `name` da página HTML:

```json
[
  {"name": "scenario_set", "type": "text/plain"},
  {"name": "max_attempts", "type": "integer"}
]
```

Na página de configuração atual, o conjunto de cenários apresentado é ainda demonstrativo. Os dez cenários do catálogo Python não estão ligados a esta seleção.

### 4.2. Deploy

O serviço `GET /user` recebe provisoriamente um parâmetro `activityID` e devolve um URL associado à instância. Por exemplo:

```text
GET /user?activityID=teste001
```

O resultado no ambiente público segue o formato:

```text
https://auditlab-lite.onrender.com/atividade/teste001
```

O identificador da instância é guardado apenas em memória e não existe persistência dos dados. O nome `activityID` neste pedido GET permanece provisório, porque a especificação consultada não explicita o nome do parâmetro recebido pelo serviço de deploy.

### 4.3. Indicadores disponíveis

O serviço `GET /analytics-list` disponibiliza quatro indicadores quantitativos:

| Indicador | Tipo | Significado previsto |
|---|---|---|
| `respostas_corretas` | `integer` | Número de respostas corretas. |
| `pontuacao` | `integer` | Pontuação da atividade. |
| `tentativas_utilizadas` | `integer` | Número de tentativas utilizadas. |
| `concluida` | `boolean` | Indicação de conclusão da atividade. |

A resposta distingue `quantAnalytics` de `qualAnalytics`. Nesta versão, não existem indicadores qualitativos.

### 4.4. Consulta de analytics

O serviço `POST /analytics` recebe um objeto JSON com o identificador da instância:

```json
{"activityID": "teste001"}
```

Atualmente, devolve resultados fixos de um aluno fictício, sem consultar respostas reais ou o motor de regras:

```json
[
  {
    "inveniraStdID": "1001",
    "quantAnalytics": [
      {"name": "respostas_corretas", "type": "integer", "value": 4},
      {"name": "pontuacao", "type": "integer", "value": 80},
      {"name": "tentativas_utilizadas", "type": "integer", "value": 1},
      {"name": "concluida", "type": "boolean", "value": true}
    ],
    "qualAnalytics": []
  }
]
```

O identificador recebido é validado pelo FastAPI, mas ainda não é utilizado para selecionar resultados específicos.

## 5. Implementação do padrão Builder

### 5.1. Escolha do padrão

Os cenários do AuditLab Lite são compostos por vários elementos: identificação, descrição, data de referência, política aplicável, tipo de resposta, registos fictícios e chave de correção.

Foi considerada a utilização do Factory Method. No entanto, como os exercícios partilham uma estrutura comum e variam sobretudo nos dados e nas políticas, o Builder revelou-se uma opção mais adequada para organizar a construção por etapas e validar a consistência do objeto final.

### 5.2. Estrutura e funcionamento

A classe `CenarioBuilder`, definida em `construtor_cenarios.py`, disponibiliza os seguintes métodos:

| Método | Responsabilidade |
|---|---|
| `definir_identificacao()` | Definir identificador, título e descrição. |
| `definir_politica()` | Definir a data de referência e a política do cenário. |
| `definir_tipo_resposta()` | Indicar o tipo de identificador esperado na resposta. |
| `adicionar_registo()` | Acrescentar os registos fictícios. |
| `definir_chave()` | Definir os identificadores da resposta esperada. |
| `construir()` | Validar os elementos e criar um objeto `Cenario`. |

Os métodos de configuração devolvem a própria instância do Builder, permitindo encadear as chamadas. Esta abordagem corresponde a uma variante fluente do padrão. Não foi criada uma classe `Director`, uma vez que a função `criar_cenario()`, em `catalogo_cenarios.py`, coordena diretamente a construção.

O método `construir()` valida os campos obrigatórios, a data de referência, a unicidade dos identificadores e a existência das referências presentes na chave de correção. Quando encontra dados inconsistentes, lança um erro e não cria o cenário.

Os objetos finais são representados por `Cenario` e `Registo`, definidos em `modelos.py`. O processo de construção protege as coleções internas contra alterações diretas.

### 5.3. Aplicação ao catálogo

O mesmo Builder é utilizado para construir dez cenários fictícios:

| Código | Cenário |
|---|---|
| C01 | Contas ativas de ex-colaboradores. |
| C02 | Logins posteriores à saída. |
| C03 | Múltiplas contas associadas ao mesmo colaborador. |
| C04 | Contas sem login há mais de um ano. |
| C05 | Acessos de prestadores fora de horas. |
| C06 | Privilégios sem justificação. |
| C07 | Contas de prestadores com contratos terminados. |
| C08 | Contas genéricas ou de serviço sem responsável. |
| C09 | Palavras-passe configuradas sem expiração, fora da política fictícia. |
| C10 | Permissões mantidas após mudança de função. |

O catálogo contém **51 registos fictícios** e **20 respostas esperadas**. As respostas são definidas no catálogo, enquanto as funções de `regras_auditoria.py` calculam autonomamente os casos não conformes a partir dos dados. Os testes comparam os resultados calculados com as chaves previamente definidas.

A aplicação do Builder não deve ser confundida com a execução das regras de auditoria. O Builder constrói e valida a estrutura dos cenários. O motor de regras analisa os dados de cada exercício.

### 5.4. Diagramas UML

O **diagrama de componentes** identifica o catálogo, o construtor e os modelos, bem como os portos, a interface arquitetural de construção e a dependência dos modelos de dados. A designação `IConstrucaoCenario` representa o contrato das operações públicas utilizadas pelo catálogo. Não corresponde a uma interface Python formalmente declarada no projeto.

O **diagrama de sequência** mostra a criação do cenário C01, incluindo a inicialização do Builder, a definição dos elementos, a adição dos cinco registos, a validação, a criação do objeto `Cenario` e o respetivo retorno ao catálogo.

Ambos os diagramas concentram-se no padrão de criação, sem representar todo o funcionamento do Activity Provider.

## 6. Instalação e execução no Windows

O projeto foi desenvolvido e testado localmente com Python 3.14.10. Na pasta principal do projeto, podem executar-se os seguintes comandos no PowerShell:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn main:app --reload
```

A aplicação fica disponível em `http://127.0.0.1:8000` e a documentação interativa da API em `http://127.0.0.1:8000/docs`.

A opção `--reload` destina-se ao desenvolvimento local e permite reiniciar o servidor quando são alterados ficheiros Python.

## 7. Testes automatizados

Os testes estão organizados em quatro ficheiros:

| Ficheiro | Âmbito |
|---|---|
| `tests/test_api.py` | Serviços REST e respostas demonstrativas. |
| `tests/test_builder.py` | Construção de cenários e validações estruturais. |
| `tests/test_catalogo.py` | Estrutura e consistência dos dez cenários. |
| `tests/test_regras_auditoria.py` | Resultados das regras de deteção e comparação com as chaves. |

As dependências dos testes podem ser instaladas no ambiente virtual com:

```powershell
.\.venv\Scripts\python.exe -m pip install pytest httpx
```

Para executar todos os testes:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

Na validação local de **25 de novembro de 2026**, foram obtidos **73 testes aprovados**. Foi apresentado um aviso de descontinuação relacionado com a utilização do cliente de testes da Starlette e do HTTPX, sem falhas nos testes.

Estes resultados demonstram o funcionamento dos casos previstos na bateria de testes. Não comprovam ainda uma integração efetiva com uma instância real da Inven!RA.

## 8. Publicação no Render

O projeto foi publicado num Web Service do Render, a partir do repositório GitHub. O serviço público de demonstração está disponível em:

https://auditlab-lite.onrender.com

A configuração utilizada inclui a linguagem Python, o ramo `main`, o comando de instalação `pip install -r requirements.txt` e o comando de arranque:

```text
uvicorn main:app --host 0.0.0.0 --port $PORT
```

Os cinco serviços REST foram verificados através do endereço público na primeira fase do projeto.

**Importante:** os módulos do Builder, do catálogo e das regras foram guardados em commits locais posteriores. À data desta documentação, ainda não foi confirmado o envio desses commits para o GitHub nem a sua publicação no Render. A versão pública não deve, por isso, ser considerada equivalente à versão local mais recente.

## 9. Limitações e desenvolvimento futuro

A implementação atual tem as seguintes limitações:

1. As instâncias de demonstração são guardadas em memória e não persistem após o reinício do processo.
2. O serviço `POST /analytics` devolve valores fixos, sem recolher respostas dos alunos nem consultar o motor de regras.
3. A interface de resolução dos cenários pelos alunos ainda não foi implementada.
4. O serviço `Provide activity`, previsto na especificação da Inven!RA, ainda não foi desenvolvido, conforme o âmbito definido para esta fase da atividade prática.
5. O parâmetro utilizado no pedido GET de deploy precisa de confirmação durante a integração real.
6. Os cenários e as regras têm finalidade educativa. Não cobrem todas as situações, exceções e evidências necessárias numa auditoria real.

As próximas etapas poderão incluir a interface de resolução, a avaliação das respostas dos alunos, a persistência de instâncias e resultados e a integração completa com a Inven!RA.

## 10. Referências

Morgado, L., & Cassola, F. (2022). *Activity Providers na Inven!RA*. Documento de apoio disponibilizado na unidade curricular de Arquitetura e Padrões de Software, Universidade Aberta.

Gamma, E., Helm, R., Johnson, R., & Vlissides, J. (1995). *Design Patterns: Elements of Reusable Object-Oriented Software*. Addison-Wesley.
