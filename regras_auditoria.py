"""
Regras de auditoria utilizadas nos exercícios do AuditLab Lite.

Este módulo analisa os registos fictícios dos dez cenários e identifica as situações que não cumprem as políticas definidas.

O motor de regras é independente do padrão Builder. Recebe cenários já construídos e devolve os identificadores dos elementos não conformes.

As regras representam políticas fictícias para fins educativos e não devem ser interpretadas como critérios universais de auditoria.
"""

from collections import defaultdict
from datetime import date, datetime, time, timedelta
from typing import Callable

from modelos import Cenario, Registo


def obter_data(valor: str) -> date:
    """Converte uma data em formato ISO para permitir comparações cronológicas."""
    return date.fromisoformat(valor)


def obter_data_hora(valor: str) -> datetime:
    """Converte uma data e hora em formato ISO para permitir comparações cronológicas."""
    return datetime.fromisoformat(valor)


def excecao_em_vigor(
    dados: Registo,
    referencia: date,
    campo_indicador: str = "excecao_valida",
    campo_fim: str | None = None,
) -> bool:
    """Verifica se existe uma exceção autorizada e se a sua validade abrange a data de referência."""

    if dados.dados.get(campo_indicador) is not True:
        return False

    if campo_fim is None:
        return True

    fim = dados.dados.get(campo_fim)

    if fim is None:
        return False

    return obter_data(fim) >= referencia


def detetar_c01(cenario: Cenario) -> set[str]:
    """Identifica contas ativas de ex-colaboradores sem exceção válida."""

    referencia = obter_data(cenario.data_referencia)
    resultados = set()

    for registo in cenario.registos:
        dados = registo.dados

        if dados.get("estado_colaborador") != "Desligado":
            continue

        if dados.get("estado_conta") != "Ativa":
            continue

        data_saida = dados.get("data_saida")

        if data_saida is None:
            continue

        if obter_data(data_saida) >= referencia:
            continue

        # Verifica se existe uma exceção válida para a data analisada.
        if dados.get("excecao_valida") is True:
            if excecao_em_vigor(
                registo,
                referencia,
                campo_fim="fim_excecao",
            ):
                continue

        resultados.add(registo.identificador_resposta)

    return resultados


def detetar_c02(cenario: Cenario) -> set[str]:
    """Identifica autenticações bem-sucedidas posteriores à saída do colaborador e sem autorização válida."""

    resultados = set()

    for registo in cenario.registos:
        dados = registo.dados

        if dados.get("resultado") != "Sucesso":
            continue

        saida = obter_data_hora(dados["data_saida"])
        login = obter_data_hora(dados["data_login"])

        if login <= saida:
            continue

        if dados.get("autorizacao_valida") is True:
            continue

        resultados.add(registo.identificador_resposta)

    return resultados


def detetar_c03(cenario: Cenario) -> set[str]:
    """Identifica colaboradores com contas individuais adicionais sem autorização e finalidade distinta."""

    contas_por_colaborador = defaultdict(list)
    resultados = set()

    for registo in cenario.registos:
        dados = registo.dados

        if dados.get("estado_conta") != "Ativa":
            continue

        colaborador_id = dados["colaborador_id"]
        contas_por_colaborador[colaborador_id].append(registo)

    for colaborador_id, contas in contas_por_colaborador.items():
        if len(contas) <= 1:
            continue

        # Considera justificada a conta adicional quando tem autorização e finalidade distinta das restantes contas.
        finalidades = [
            conta.dados.get("finalidade")
            for conta in contas
        ]

        existem_contas_nao_justificadas = False

        for indice, conta in enumerate(contas[1:], start=1):
            dados = conta.dados
            autorizada = dados.get("autorizacao_adicional") is True
            finalidade = dados.get("finalidade")

            finalidade_distinta = (
                bool(finalidade)
                and finalidade not in finalidades[:indice]
            )

            if not (autorizada and finalidade_distinta):
                existem_contas_nao_justificadas = True

        if existem_contas_nao_justificadas:
            resultados.add(colaborador_id)

    return resultados


def detetar_c04(cenario: Cenario) -> set[str]:
    """Identifica contas individuais ativas cujo último login ocorreu há mais de 365 dias."""

    referencia = obter_data(cenario.data_referencia)
    resultados = set()

    for registo in cenario.registos:
        dados = registo.dados

        if dados.get("estado_conta") != "Ativa":
            continue

        if dados.get("tipo_conta") != "Individual":
            continue

        if dados.get("excecao_valida") is True:
            continue

        ultimo_login = dados.get("ultimo_login")

        if ultimo_login is None:
            continue

        dias_inatividade = (
            referencia - obter_data(ultimo_login)
        ).days

        if dias_inatividade > 365:
            resultados.add(registo.identificador_resposta)

    return resultados


def detetar_c05(cenario: Cenario) -> set[str]:
    """Identifica logins de prestadores fora dos dias ou horários autorizados."""

    resultados = set()
    inicio_autorizado = time(8, 0)
    fim_autorizado = time(18, 0)

    for registo in cenario.registos:
        dados = registo.dados

        if dados.get("tipo_utilizador") != "Prestador":
            continue

        if dados.get("resultado") != "Sucesso":
            continue

        if dados.get("excecao_valida") is True:
            continue

        momento = obter_data_hora(dados["data_login"])

        dia_util = momento.weekday() < 5

        horario_autorizado = (
            inicio_autorizado <= momento.time() <= fim_autorizado
        )

        if not dia_util or not horario_autorizado:
            resultados.add(registo.identificador_resposta)

    return resultados


def detetar_c06(cenario: Cenario) -> set[str]:
    """Identifica atribuições administrativas sem justificação funcional ou autorização válida."""

    resultados = set()

    for registo in cenario.registos:
        dados = registo.dados

        if dados.get("nivel_privilegio") != "Privilegiado":
            continue

        justificacao = dados.get("justificacao")
        autorizacao = dados.get("autorizacao_valida") is True

        justificacao_presente = (
            isinstance(justificacao, str)
            and bool(justificacao.strip())
        )

        if not justificacao_presente or not autorizacao:
            resultados.add(registo.identificador_resposta)

    return resultados


def detetar_c07(cenario: Cenario) -> set[str]:
    """Identifica contas ativas de prestadores cujo período autorizado de acesso terminou."""

    referencia = obter_data(cenario.data_referencia)
    resultados = set()

    for registo in cenario.registos:
        dados = registo.dados

        if dados.get("estado_conta") != "Ativa":
            continue

        fim_acesso = obter_data(dados["data_fim_acesso"])

        if fim_acesso >= referencia:
            continue

        prorrogacao = excecao_em_vigor(
            registo,
            referencia,
            campo_indicador="prorrogacao_valida",
            campo_fim="fim_prorrogacao",
        )

        if not prorrogacao:
            resultados.add(registo.identificador_resposta)

    return resultados


def detetar_c08(cenario: Cenario) -> set[str]:
    """Identifica contas genéricas e de serviço ativas sem responsável definido."""

    resultados = set()

    for registo in cenario.registos:
        dados = registo.dados

        if dados.get("estado_conta") != "Ativa":
            continue

        if dados.get("tipo_conta") not in {"Genérica", "Serviço"}:
            continue

        responsavel = dados.get("responsavel_id")

        if not isinstance(responsavel, str) or not responsavel.strip():
            resultados.add(registo.identificador_resposta)

    return resultados


def detetar_c09(cenario: Cenario) -> set[str]:
    """Identifica contas ativas com palavra-passe sem expiração e sem exceção autorizada."""

    resultados = set()

    for registo in cenario.registos:
        dados = registo.dados

        if dados.get("estado_conta") != "Ativa":
            continue

        if dados.get("password_nunca_expira") is not True:
            continue

        if dados.get("excecao_valida") is True:
            continue

        resultados.add(registo.identificador_resposta)

    return resultados


def detetar_c10(cenario: Cenario) -> set[str]:
    """Identifica permissões não autorizadas que permanecem atribuídas após o prazo de revisão da função."""

    referencia = obter_data(cenario.data_referencia)
    prazo_revisao = timedelta(days=5)
    resultados = set()

    for registo in cenario.registos:
        dados = registo.dados

        if dados.get("prevista_na_nova_funcao") is True:
            continue

        if dados.get("excecao_valida") is True:
            continue

        data_mudanca = obter_data(dados["data_mudanca"])

        if referencia > data_mudanca + prazo_revisao:
            resultados.add(registo.identificador_resposta)

    return resultados


# Associa cada cenário à função que aplica a respetiva política fictícia.
REGRAS: dict[str, Callable[[Cenario], set[str]]] = {
    "C01": detetar_c01,
    "C02": detetar_c02,
    "C03": detetar_c03,
    "C04": detetar_c04,
    "C05": detetar_c05,
    "C06": detetar_c06,
    "C07": detetar_c07,
    "C08": detetar_c08,
    "C09": detetar_c09,
    "C10": detetar_c10,
}


def analisar_cenario(cenario: Cenario) -> set[str]:
    """Aplica a regra correspondente ao cenário e devolve os identificadores não conformes."""

    regra = REGRAS.get(cenario.identificador)

    if regra is None:
        raise ValueError(
            f"Não existe uma regra de auditoria para {cenario.identificador}."
        )

    return regra(cenario)


def validar_chave_correcao(cenario: Cenario) -> bool:
    """Compara os resultados calculados com a chave de correção definida no catálogo."""

    resultados_calculados = analisar_cenario(cenario)
    respostas_esperadas = set(cenario.chave_correcao)

    return resultados_calculados == respostas_esperadas
