
"""
Testes das regras de auditoria do AuditLab Lite.

Os testes verificam se o motor de regras identifica os registos não conformes em cada cenário e se os resultados correspondem às chaves de correção.

Também são testadas alterações aos dados para confirmar que as regras calculam os resultados a partir dos registos recebidos.
"""

from dataclasses import replace
from types import MappingProxyType

import pytest

from catalogo_cenarios import obter_catalogo, obter_cenario
from modelos import Registo
from regras_auditoria import (
    analisar_cenario,
    validar_chave_correcao,
)


# Define os identificadores esperados para os dez exercícios.
RESULTADOS_ESPERADOS = [
    ("C01", {"U001", "U005"}),
    ("C02", {"L001", "L005"}),
    ("C03", {"E201", "E203"}),
    ("C04", {"U031", "U035"}),
    ("C05", {"L022", "L025"}),
    ("C06", {"A002", "A004"}),
    ("C07", {"U061", "U065"}),
    ("C08", {"U071", "U075"}),
    ("C09", {"U081", "U085"}),
    ("C10", {"A011", "A015"}),
]


def alterar_registo(cenario, identificador, **alteracoes):
    """
    Cria uma cópia do cenário com os dados de um registo alterados.

    A função é utilizada apenas nos testes e mantém o cenário original inalterado.
    """

    novos_registos = []

    for registo in cenario.registos:
        if registo.identificador == identificador:
            novos_dados = dict(registo.dados)
            novos_dados.update(alteracoes)

            novo_registo = Registo(
                identificador=registo.identificador,
                identificador_resposta=registo.identificador_resposta,
                dados=MappingProxyType(novos_dados),
            )
        else:
            novo_registo = registo

        novos_registos.append(novo_registo)

    return replace(cenario, registos=tuple(novos_registos))


@pytest.mark.parametrize(
    "identificador,esperados",
    RESULTADOS_ESPERADOS,
)
def test_deteccao_dos_dez_cenarios(identificador, esperados):
    """Confirma que cada regra identifica exatamente os registos esperados."""

    cenario = obter_cenario(identificador)

    assert analisar_cenario(cenario) == esperados


@pytest.mark.parametrize(
    "identificador,esperados",
    RESULTADOS_ESPERADOS,
)
def test_chave_correcao_consistente(identificador, esperados):
    """Confirma que o resultado calculado corresponde à chave guardada no catálogo."""

    cenario = obter_cenario(identificador)

    assert validar_chave_correcao(cenario) is True


def test_c01_conta_desativada_nao_e_sinalizada():
    """Confirma que uma conta desativada deixa de ser sinalizada pela regra C01."""

    original = obter_cenario("C01")
    alterado = alterar_registo(
        original,
        "U001",
        estado_conta="Desativada",
    )

    assert "U001" not in analisar_cenario(alterado)
    assert "U001" in analisar_cenario(original)


def test_c02_login_sem_sucesso_nao_e_sinalizado():
    """Confirma que uma autenticação falhada não é tratada como acesso bem-sucedido."""

    original = obter_cenario("C02")
    alterado = alterar_registo(
        original,
        "L001",
        resultado="Falha",
    )

    assert "L001" not in analisar_cenario(alterado)


def test_c03_conta_adicional_autorizada():
    """Confirma que uma segunda conta com finalidade distinta e autorização válida não é sinalizada."""

    original = obter_cenario("C03")
    alterado = alterar_registo(
        original,
        "U022",
        tipo_conta="Administrativa",
        finalidade="Administração técnica",
        autorizacao_adicional=True,
    )

    assert "E201" not in analisar_cenario(alterado)


def test_c04_conta_com_login_recente():
    """Confirma que uma conta com login recente deixa de ser sinalizada por inatividade."""

    original = obter_cenario("C04")
    alterado = alterar_registo(
        original,
        "U031",
        ultimo_login="2026-11-20",
    )

    assert "U031" not in analisar_cenario(alterado)


def test_c05_acesso_autorizado_fora_de_horas():
    """Confirma que uma autorização excecional afasta a não conformidade de horário."""

    original = obter_cenario("C05")
    alterado = alterar_registo(
        original,
        "L022",
        excecao_valida=True,
    )

    assert "L022" not in analisar_cenario(alterado)


def test_c06_privilegio_com_autorizacao():
    """Confirma que uma atribuição com justificação e autorização deixa de ser sinalizada."""

    original = obter_cenario("C06")
    alterado = alterar_registo(
        original,
        "A002",
        justificacao="Administração autorizada",
        autorizacao_valida=True,
    )

    assert "A002" not in analisar_cenario(alterado)


def test_c07_prorrogacao_de_acesso():
    """Confirma que uma prorrogação válida permite manter a conta ativa durante o período autorizado."""

    original = obter_cenario("C07")
    alterado = alterar_registo(
        original,
        "U061",
        prorrogacao_valida=True,
        fim_prorrogacao="2026-12-15",
    )

    assert "U061" not in analisar_cenario(alterado)


def test_c08_conta_com_responsavel():
    """Confirma que a atribuição de um responsável retira a conta da lista de incumprimentos."""

    original = obter_cenario("C08")
    alterado = alterar_registo(
        original,
        "U071",
        responsavel_id="E450",
    )

    assert "U071" not in analisar_cenario(alterado)


def test_c09_excecao_autorizada():
    """Confirma que uma exceção válida é considerada na análise das palavras-passe sem expiração."""

    original = obter_cenario("C09")
    alterado = alterar_registo(
        original,
        "U081",
        excecao_valida=True,
    )

    assert "U081" not in analisar_cenario(alterado)


def test_c10_permissao_autorizada_na_nova_funcao():
    """Confirma que uma permissão prevista na função atual não é considerada indevida."""

    original = obter_cenario("C10")
    alterado = alterar_registo(
        original,
        "A011",
        prevista_na_nova_funcao=True,
    )

    assert "A011" not in analisar_cenario(alterado)


def test_deteccao_nao_depende_da_chave_guardada():
    """Confirma que o motor calcula as irregularidades sem consultar a chave previamente guardada."""

    original = obter_cenario("C01")
    chave_incorreta = replace(
        original,
        chave_correcao=("U002",),
    )

    assert analisar_cenario(chave_incorreta) == {"U001", "U005"}
    assert validar_chave_correcao(chave_incorreta) is False


def test_cenario_sem_regra():
    """Confirma que um cenário desconhecido não pode ser analisado sem uma regra definida."""

    original = obter_cenario("C01")
    desconhecido = replace(
        original,
        identificador="C99",
    )

    with pytest.raises(ValueError, match="Não existe uma regra"):
        analisar_cenario(desconhecido)


def test_catalogo_completo_tem_chaves_consistentes():
    """Confirma que todos os cenários do catálogo apresentam chaves coerentes com as regras implementadas."""

    catalogo = obter_catalogo()

    assert len(catalogo) == 10

    for cenario in catalogo.values():
        assert validar_chave_correcao(cenario)
