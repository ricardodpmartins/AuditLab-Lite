
"""
Testes automatizados do catálogo de cenários do AuditLab Lite.

Os testes verificam a criação dos dez exercícios, as quantidades
de registos, as chaves de correção e a consistência das referências.
"""

import pytest

from catalogo_cenarios import obter_catalogo, obter_cenario
from construtor_cenarios import CenarioBuilder
from modelos import Cenario


# Define os resultados esperados de acordo com a matriz funcional do projeto.
CASOS_ESPERADOS = [
    ("C01", 5, "conta_id", ("U001", "U005")),
    ("C02", 5, "login_id", ("L001", "L005")),
    ("C03", 6, "colaborador_id", ("E201", "E203")),
    ("C04", 5, "conta_id", ("U031", "U035")),
    ("C05", 5, "login_id", ("L022", "L025")),
    ("C06", 5, "atribuicao_id", ("A002", "A004")),
    ("C07", 5, "conta_id", ("U061", "U065")),
    ("C08", 5, "conta_id", ("U071", "U075")),
    ("C09", 5, "conta_id", ("U081", "U085")),
    ("C10", 5, "atribuicao_id", ("A011", "A015")),
]


@pytest.mark.parametrize(
    "identificador,quantidade,tipo_resposta,chave",
    CASOS_ESPERADOS,
)
def test_cenario_corresponde_ao_catalogo(
    identificador,
    quantidade,
    tipo_resposta,
    chave,
):
    """
    Confirma que cada cenário possui os registos e a chave esperados.

    Este teste verifica a correspondência com a matriz funcional
    previamente definida para os dez exercícios.
    """

    cenario = obter_cenario(identificador)

    assert isinstance(cenario, Cenario)
    assert cenario.identificador == identificador
    assert cenario.data_referencia == "2026-11-25"
    assert cenario.tipo_resposta == tipo_resposta
    assert len(cenario.registos) == quantidade
    assert cenario.chave_correcao == chave


def test_catalogo_contem_dez_cenarios():
    """
    Confirma que o catálogo inclui todos os cenários previstos.
    """

    catalogo = obter_catalogo()

    identificadores_esperados = {
        f"C{numero:02d}"
        for numero in range(1, 11)
    }

    assert set(catalogo) == identificadores_esperados
    assert len(catalogo) == 10


def test_catalogo_contem_51_registos():
    """
    Confirma a quantidade total de registos fictícios do catálogo.
    """

    catalogo = obter_catalogo()

    total = sum(
        len(cenario.registos)
        for cenario in catalogo.values()
    )

    assert total == 51


def test_catalogo_contem_20_respostas():
    """
    Confirma a quantidade total de respostas esperadas nos exercícios.
    """

    catalogo = obter_catalogo()

    total = sum(
        len(cenario.chave_correcao)
        for cenario in catalogo.values()
    )

    assert total == 20


@pytest.mark.parametrize(
    "identificador",
    [f"C{numero:02d}" for numero in range(1, 11)],
)
def test_chave_referencia_respostas_existentes(identificador):
    """
    Confirma que todas as respostas esperadas existem nos registos.

    A comparação considera o identificador de resposta, que pode
    ser diferente do identificador do próprio registo.
    """

    cenario = obter_cenario(identificador)

    respostas_disponiveis = {
        registo.identificador_resposta
        for registo in cenario.registos
    }

    assert set(cenario.chave_correcao).issubset(respostas_disponiveis)


def test_c03_identifica_colaboradores():
    """
    Confirma que o cenário C03 utiliza colaboradores como resposta.

    Duas contas do mesmo colaborador podem partilhar um identificador
    de resposta sem serem consideradas registos duplicados.
    """

    cenario = obter_cenario("C03")

    contas_e201 = [
        registo
        for registo in cenario.registos
        if registo.identificador_resposta == "E201"
    ]

    assert len(contas_e201) == 2
    assert cenario.tipo_resposta == "colaborador_id"
    assert "E201" in cenario.chave_correcao


def test_registos_sao_independentes_entre_construcoes():
    """
    Confirma que duas construções não partilham objetos de cenário.

    Os dados dos registos permanecem protegidos contra alterações
    diretas depois de o cenário ser construído.
    """

    primeiro = obter_cenario("C01")
    segundo = obter_cenario("C01")

    assert primeiro is not segundo
    assert primeiro.registos is not segundo.registos

    with pytest.raises(TypeError):
        primeiro.registos[0].dados["estado_conta"] = "Desativada"


def test_cenario_inexistente():
    """
    Confirma que o catálogo rejeita identificadores desconhecidos.
    """

    with pytest.raises(ValueError, match="não existe"):
        obter_cenario("C99")


def test_catalogo_utiliza_builder(monkeypatch):
    """
    Confirma que a construção de um cenário passa pelo Builder.

    O teste acompanha a chamada ao método construir() sem alterar
    o comportamento original da implementação.
    """

    chamadas = []
    construir_original = CenarioBuilder.construir

    def acompanhar_construcao(self):
        chamadas.append(True)
        return construir_original(self)

    monkeypatch.setattr(
        CenarioBuilder,
        "construir",
        acompanhar_construcao,
    )

    cenario = obter_cenario("C01")

    assert cenario.identificador == "C01"
    assert len(chamadas) == 1
