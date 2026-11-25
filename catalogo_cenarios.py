
"""
Catálogo de cenários fictícios do AuditLab Lite.

Este módulo reúne dez exercícios relacionados com o controlo de acessos.
Cada exercício apresenta registos fictícios, uma política de análise e
uma chave de correção previamente definida.

Todos os cenários são construídos através do CenarioBuilder.
As regras automáticas de deteção serão desenvolvidas separadamente.
"""

from construtor_cenarios import CenarioBuilder
from modelos import Cenario, ValorCampo


DATA_REFERENCIA = "2026-11-25"


def criar_cenario(
    identificador: str,
    titulo: str,
    descricao: str,
    politica: str,
    tipo_resposta: str,
    registos: list[dict],
    chave: list[str],
) -> Cenario:
    """
    Constrói um cenário com os elementos fornecidos pelo catálogo.

    Esta função representa o cliente do Builder. Define a informação
    comum, acrescenta os registos e solicita a construção do objeto final.
    """

    builder = (
        CenarioBuilder()
        .definir_identificacao(identificador, titulo, descricao)
        .definir_politica(DATA_REFERENCIA, politica)
        .definir_tipo_resposta(tipo_resposta)
    )

    # Adiciona os registos através do Builder, sem criar diretamente o objeto Cenario.
    for registo in registos:
        builder.adicionar_registo(
            identificador=registo["id"],
            dados=registo["dados"],
            identificador_resposta=registo.get("resposta"),
        )

    # A chave de correção é validada pelo Builder antes de criar o cenário.
    return builder.definir_chave(chave).construir()


def cenario_c01() -> Cenario:
    """
    Cria o exercício sobre contas ativas de ex-colaboradores.

    O aluno deve identificar contas que continuam ativas após o prazo
    de desativação, quando não existe uma exceção autorizada.
    """

    registos = [
        {
            "id": "U001",
            "dados": {
                "colaborador_id": "E101",
                "estado_colaborador": "Desligado",
                "data_saida": "2026-10-10",
                "estado_conta": "Ativa",
                "excecao_valida": False,
            },
        },
        {
            "id": "U002",
            "dados": {
                "colaborador_id": "E102",
                "estado_colaborador": "Desligado",
                "data_saida": "2026-11-15",
                "estado_conta": "Desativada",
                "excecao_valida": False,
            },
        },
        {
            "id": "U003",
            "dados": {
                "colaborador_id": "E103",
                "estado_colaborador": "Ativo",
                "data_saida": None,
                "estado_conta": "Ativa",
                "excecao_valida": False,
            },
        },
        {
            "id": "U004",
            "dados": {
                "colaborador_id": "E104",
                "estado_colaborador": "Desligado",
                "data_saida": "2026-11-20",
                "estado_conta": "Ativa",
                "excecao_valida": True,
                "fim_excecao": "2026-11-30",
            },
        },
        {
            "id": "U005",
            "dados": {
                "colaborador_id": "E105",
                "estado_colaborador": "Desligado",
                "data_saida": "2026-09-01",
                "estado_conta": "Ativa",
                "excecao_valida": False,
            },
        },
    ]

    return criar_cenario(
        "C01",
        "Contas ativas de ex-colaboradores",
        "Identificar contas ativas após a saída dos colaboradores.",
        "As contas devem ser desativadas até ao final do dia da saída, salvo exceção válida.",
        "conta_id",
        registos,
        ["U001", "U005"],
    )


def cenario_c02() -> Cenario:
    """
    Cria o exercício sobre autenticações posteriores à saída.

    Apenas as autenticações bem-sucedidas e sem autorização válida
    devem ser consideradas não conformes.
    """

    registos = [
        {
            "id": "L001",
            "dados": {
                "conta_id": "U011",
                "data_saida": "2026-11-10T18:00:00",
                "data_login": "2026-11-12T09:15:00",
                "resultado": "Sucesso",
                "autorizacao_valida": False,
            },
        },
        {
            "id": "L002",
            "dados": {
                "conta_id": "U012",
                "data_saida": "2026-11-15T18:00:00",
                "data_login": "2026-11-14T16:30:00",
                "resultado": "Sucesso",
                "autorizacao_valida": False,
            },
        },
        {
            "id": "L003",
            "dados": {
                "conta_id": "U013",
                "data_saida": "2026-11-20T18:00:00",
                "data_login": "2026-11-22T11:20:00",
                "resultado": "Falha",
                "autorizacao_valida": False,
            },
        },
        {
            "id": "L004",
            "dados": {
                "conta_id": "U014",
                "data_saida": "2026-11-18T18:00:00",
                "data_login": "2026-11-19T20:30:00",
                "resultado": "Sucesso",
                "autorizacao_valida": True,
            },
        },
        {
            "id": "L005",
            "dados": {
                "conta_id": "U015",
                "data_saida": "2026-11-01T18:00:00",
                "data_login": "2026-11-05T08:10:00",
                "resultado": "Sucesso",
                "autorizacao_valida": False,
            },
        },
    ]

    return criar_cenario(
        "C02",
        "Logins posteriores à saída",
        "Identificar autenticações após o fim do vínculo laboral.",
        "Não são permitidos logins bem-sucedidos após a saída sem autorização válida.",
        "login_id",
        registos,
        ["L001", "L005"],
    )


def cenario_c03() -> Cenario:
    """
    Cria o exercício sobre múltiplas contas do mesmo colaborador.

    Cada registo representa uma conta, mas a resposta identifica
    o colaborador que possui contas adicionais não justificadas.
    """

    contas = [
        ("U021", "E201", "Normal", "Ativa", "Atividade diária", False),
        ("U022", "E201", "Normal", "Ativa", "Atividade diária", False),
        ("U023", "E202", "Normal", "Ativa", "Atividade diária", False),
        ("U024", "E202", "Administrativa", "Ativa", "Administração técnica", True),
        ("U025", "E203", "Normal", "Ativa", "Atividade diária", False),
        ("U026", "E203", "Normal", "Ativa", "Atividade diária", False),
    ]

    registos = []

    # Os registos partilham o identificador de resposta quando pertencem ao mesmo colaborador.
    for conta_id, colaborador_id, tipo, estado, finalidade, autorizacao in contas:
        registos.append({
            "id": conta_id,
            "resposta": colaborador_id,
            "dados": {
                "colaborador_id": colaborador_id,
                "tipo_conta": tipo,
                "estado_conta": estado,
                "finalidade": finalidade,
                "autorizacao_adicional": autorizacao,
            },
        })

    return criar_cenario(
        "C03",
        "Múltiplas contas do mesmo colaborador",
        "Identificar colaboradores com contas adicionais sem justificação.",
        "As contas individuais adicionais exigem finalidade distinta e autorização documentada.",
        "colaborador_id",
        registos,
        ["E201", "E203"],
    )


def cenario_c04() -> Cenario:
    """
    Cria o exercício sobre contas sem login há mais de um ano.

    O período de inatividade é comparado com a data de referência
    e são consideradas as exceções autorizadas.
    """

    contas = [
        ("U031", "Ativa", "Individual", "2025-06-10", False),
        ("U032", "Ativa", "Individual", "2026-09-20", False),
        ("U033", "Desativada", "Individual", "2024-01-12", False),
        ("U034", "Ativa", "Individual", "2025-03-05", True),
        ("U035", "Ativa", "Individual", "2025-11-01", False),
    ]

    registos = [
        {
            "id": conta_id,
            "dados": {
                "estado_conta": estado,
                "tipo_conta": tipo,
                "ultimo_login": ultimo_login,
                "excecao_valida": excecao,
            },
        }
        for conta_id, estado, tipo, ultimo_login, excecao in contas
    ]

    return criar_cenario(
        "C04",
        "Contas sem login há mais de um ano",
        "Identificar contas individuais ativas com inatividade prolongada.",
        "São não conformes as contas individuais ativas sem login há mais de 365 dias e sem exceção válida.",
        "conta_id",
        registos,
        ["U031", "U035"],
    )


def cenario_c05() -> Cenario:
    """
    Cria o exercício sobre acessos de prestadores fora de horas.

    O horário autorizado para os prestadores é das 08h00 às 18h00,
    de segunda a sexta-feira, salvo autorização excecional.
    """

    eventos = [
        ("L021", "U041", "Prestador", "2026-11-23T10:30:00", "Sucesso", False),
        ("L022", "U042", "Prestador", "2026-11-23T22:15:00", "Sucesso", False),
        ("L023", "U043", "Prestador", "2026-11-21T14:20:00", "Sucesso", True),
        ("L024", "U044", "Interno", "2026-11-24T21:00:00", "Sucesso", False),
        ("L025", "U045", "Prestador", "2026-11-24T06:45:00", "Sucesso", False),
    ]

    registos = [
        {
            "id": login_id,
            "dados": {
                "conta_id": conta_id,
                "tipo_utilizador": tipo,
                "data_login": data_login,
                "resultado": resultado,
                "excecao_valida": excecao,
            },
        }
        for login_id, conta_id, tipo, data_login, resultado, excecao in eventos
    ]

    return criar_cenario(
        "C05",
        "Acessos de prestadores fora de horas",
        "Identificar acessos de prestadores fora do horário autorizado.",
        "Os prestadores apenas podem aceder de segunda a sexta-feira, entre as 08h00 e as 18h00, salvo exceção válida.",
        "login_id",
        registos,
        ["L022", "L025"],
    )


def cenario_c06() -> Cenario:
    """
    Cria o exercício sobre atribuições de privilégios administrativos.

    A avaliação considera cada atribuição e verifica a existência
    de justificação funcional e autorização válida.
    """

    atribuicoes = [
        ("A001", "U051", "Administrador de sistema", "Privilegiado", "Administração de servidores", True),
        ("A002", "U052", "Administrador de base de dados", "Privilegiado", None, False),
        ("A003", "U053", "Consulta de relatórios", "Normal", "Consulta operacional", True),
        ("A004", "U054", "Administrador de segurança", "Privilegiado", "Suporte técnico", False),
        ("A005", "U055", "Administrador de aplicações", "Privilegiado", "Manutenção de aplicações", True),
    ]

    registos = [
        {
            "id": atribuicao_id,
            "dados": {
                "conta_id": conta_id,
                "perfil": perfil,
                "nivel_privilegio": nivel,
                "justificacao": justificacao,
                "autorizacao_valida": autorizacao,
            },
        }
        for atribuicao_id, conta_id, perfil, nivel, justificacao, autorizacao in atribuicoes
    ]

    return criar_cenario(
        "C06",
        "Privilégios sem justificação",
        "Identificar atribuições de privilégios administrativos não autorizadas.",
        "Os privilégios administrativos exigem justificação funcional e autorização válida.",
        "atribuicao_id",
        registos,
        ["A002", "A004"],
    )


def cenario_c07() -> Cenario:
    """
    Cria o exercício sobre prestadores com períodos de acesso terminados.

    O fim do contrato e o fim do acesso são representados separadamente,
    pois nem sempre correspondem à mesma data.
    """

    contas = [
        ("U061", "P301", "2026-10-31", "2026-10-31", "Ativa", False, None),
        ("U062", "P302", "2026-11-15", "2026-11-15", "Desativada", False, None),
        ("U063", "P303", "2026-12-31", "2026-12-31", "Ativa", False, None),
        ("U064", "P304", "2026-11-10", "2026-11-10", "Ativa", True, "2026-11-30"),
        ("U065", "P305", "2026-11-01", "2026-11-05", "Ativa", False, None),
    ]

    registos = [
        {
            "id": conta_id,
            "dados": {
                "prestador_id": prestador_id,
                "data_fim_contrato": fim_contrato,
                "data_fim_acesso": fim_acesso,
                "estado_conta": estado,
                "prorrogacao_valida": prorrogacao,
                "fim_prorrogacao": fim_prorrogacao,
            },
        }
        for conta_id, prestador_id, fim_contrato, fim_acesso, estado, prorrogacao, fim_prorrogacao in contas
    ]

    return criar_cenario(
        "C07",
        "Contratos de prestadores terminados",
        "Identificar contas ativas após o período autorizado de acesso.",
        "As contas devem ser desativadas após o fim do acesso autorizado, salvo prorrogação válida.",
        "conta_id",
        registos,
        ["U061", "U065"],
    )


def cenario_c08() -> Cenario:
    """
    Cria o exercício sobre contas genéricas ou de serviço sem responsável.

    A política aplica-se apenas às contas ativas não nominativas.
    """

    contas = [
        ("U071", "Genérica", "Ativa", None, "Operações"),
        ("U072", "Serviço", "Ativa", "E401", "Integração de sistemas"),
        ("U073", "Individual", "Ativa", "E402", "Atividade diária"),
        ("U074", "Genérica", "Desativada", None, "Acesso antigo"),
        ("U075", "Serviço", "Ativa", None, "Execução de tarefas"),
    ]

    registos = [
        {
            "id": conta_id,
            "dados": {
                "tipo_conta": tipo,
                "estado_conta": estado,
                "responsavel_id": responsavel,
                "finalidade": finalidade,
            },
        }
        for conta_id, tipo, estado, responsavel, finalidade in contas
    ]

    return criar_cenario(
        "C08",
        "Contas genéricas sem responsável",
        "Identificar contas genéricas ou de serviço sem responsável definido.",
        "Todas as contas genéricas e de serviço ativas devem ter um responsável identificado.",
        "conta_id",
        registos,
        ["U071", "U075"],
    )


def cenario_c09() -> Cenario:
    """
    Cria o exercício sobre contas com palavra-passe sem expiração.

    A conformidade é determinada pela política fictícia do exercício,
    que admite exceções autorizadas para contas de serviço.
    """

    contas = [
        ("U081", "Individual", "Ativa", True, False),
        ("U082", "Individual", "Ativa", False, False),
        ("U083", "Serviço", "Ativa", True, True),
        ("U084", "Individual", "Desativada", True, False),
        ("U085", "Serviço", "Ativa", True, False),
    ]

    registos = [
        {
            "id": conta_id,
            "dados": {
                "tipo_conta": tipo,
                "estado_conta": estado,
                "password_nunca_expira": nunca_expira,
                "excecao_valida": excecao,
            },
        }
        for conta_id, tipo, estado, nunca_expira, excecao in contas
    ]

    return criar_cenario(
        "C09",
        "Palavras-passe sem expiração",
        "Identificar contas que não cumprem a política fictícia de expiração.",
        "As contas individuais ativas devem ter expiração configurada. As contas de serviço exigem exceção válida para não expirar.",
        "conta_id",
        registos,
        ["U081", "U085"],
    )


def cenario_c10() -> Cenario:
    """
    Cria o exercício sobre permissões mantidas após mudança de função.

    A política prevê cinco dias de calendário para rever os acessos.
    As permissões não autorizadas após esse prazo são não conformes.
    """

    atribuicoes = [
        ("A011", "U091", "2026-11-01", "Gestão de pagamentos", False, False),
        ("A012", "U092", "2026-11-10", "Consulta de relatórios", True, False),
        ("A013", "U093", "2026-11-15", "Administração de utilizadores", False, True),
        ("A014", "U094", "2026-11-23", "Aprovação de compras", False, False),
        ("A015", "U095", "2026-10-01", "Aprovação de fornecedores", False, False),
    ]

    registos = [
        {
            "id": atribuicao_id,
            "dados": {
                "conta_id": conta_id,
                "data_mudanca": data_mudanca,
                "permissao": permissao,
                "prevista_na_nova_funcao": prevista,
                "excecao_valida": excecao,
            },
        }
        for atribuicao_id, conta_id, data_mudanca, permissao, prevista, excecao in atribuicoes
    ]

    return criar_cenario(
        "C10",
        "Permissões mantidas após mudança de função",
        "Identificar permissões não autorizadas após uma mudança de função.",
        "As permissões devem ser revistas até cinco dias de calendário após a mudança, salvo exceção válida.",
        "atribuicao_id",
        registos,
        ["A011", "A015"],
    )


# Associa cada identificador à função responsável pela construção do respetivo cenário.
CRIADORES_CENARIOS = {
    "C01": cenario_c01,
    "C02": cenario_c02,
    "C03": cenario_c03,
    "C04": cenario_c04,
    "C05": cenario_c05,
    "C06": cenario_c06,
    "C07": cenario_c07,
    "C08": cenario_c08,
    "C09": cenario_c09,
    "C10": cenario_c10,
}


def obter_cenario(identificador: str) -> Cenario:
    """
    Constrói e devolve o cenário correspondente ao identificador.

    Cada chamada cria um novo objeto, evitando partilhar o estado
    do Builder entre exercícios independentes.
    """

    if identificador not in CRIADORES_CENARIOS:
        raise ValueError(f"O cenário {identificador} não existe no catálogo.")

    return CRIADORES_CENARIOS[identificador]()


def obter_catalogo() -> dict[str, Cenario]:
    """
    Constrói e devolve todos os cenários disponíveis no catálogo.

    Os dez exercícios utilizam o mesmo processo de construção
    e as validações definidas no CenarioBuilder.
    """

    return {
        identificador: criador()
        for identificador, criador in CRIADORES_CENARIOS.items()
    }
