
"""
Testes automatizados do padrão Builder do AuditLab Lite.

Os testes verificam a construção de cenários e o funcionamento das validações estruturais.
"""

import pytest

from construtor_cenarios import CenarioBuilder


def criar_builder_base(tipo_resposta="conta_id"):
    """
    Cria um Builder com os elementos comuns necessários aos testes.
    """

    return (
        CenarioBuilder()
        .definir_identificacao(
            "C01",
            "Contas ativas de ex-colaboradores",
            "Identificar contas que permanecem ativas após a saída do colaborador."
        )
        .definir_politica(
            "2026-11-25",
            "As contas devem ser desativadas após a saída do colaborador."
        )
        .definir_tipo_resposta(tipo_resposta)
    )


def test_criar_cenario_c01():
    """
    Verifica se é possível construir um cenário com respostas identificadas por conta.
    """

    cenario = (
        criar_builder_base()
        .adicionar_registo(
            "U001",
            {
                "colaborador_id": "E101",
                "estado_conta": "Ativa",
                "estado_colaborador": "Desligado",
            }
        )
        .adicionar_registo(
            "U002",
            {
                "colaborador_id": "E102",
                "estado_conta": "Desativada",
                "estado_colaborador": "Desligado",
            }
        )
        .definir_chave(["U001"])
        .construir()
    )

    assert cenario.identificador == "C01"
    assert len(cenario.registos) == 2
    assert cenario.tipo_resposta == "conta_id"
    assert cenario.chave_correcao == ("U001",)


def test_criar_cenario_c03():
    """
    Verifica se vários registos podem estar associados à mesma resposta por colaborador.
    """

    cenario = (
        criar_builder_base("colaborador_id")
        .adicionar_registo(
            "U021",
            {
                "colaborador_id": "E201",
                "tipo_conta": "Normal",
            },
            identificador_resposta="E201"
        )
        .adicionar_registo(
            "U022",
            {
                "colaborador_id": "E201",
                "tipo_conta": "Normal",
            },
            identificador_resposta="E201"
        )
        .adicionar_registo(
            "U023",
            {
                "colaborador_id": "E202",
                "tipo_conta": "Administrativa",
            },
            identificador_resposta="E202"
        )
        .definir_chave(["E201"])
        .construir()
    )

    assert len(cenario.registos) == 3
    assert cenario.tipo_resposta == "colaborador_id"
    assert cenario.chave_correcao == ("E201",)


def test_rejeitar_cenario_sem_registos():
    """
    Confirma que não é possível construir um cenário sem registos.
    """

    builder = criar_builder_base()

    with pytest.raises(ValueError, match="pelo menos um registo"):
        builder.construir()


def test_rejeitar_identificadores_duplicados():
    """
    Confirma que dois registos não podem ter o mesmo identificador.
    """

    builder = (
        criar_builder_base()
        .adicionar_registo("U001", {"estado_conta": "Ativa"})
        .adicionar_registo("U001", {"estado_conta": "Bloqueada"})
    )

    with pytest.raises(ValueError, match="duplicados"):
        builder.construir()


def test_rejeitar_chave_com_referencia_inexistente():
    """
    Confirma que a chave de correção não pode identificar registos inexistentes.
    """

    builder = (
        criar_builder_base()
        .adicionar_registo("U001", {"estado_conta": "Ativa"})
        .definir_chave(["U999"])
    )

    with pytest.raises(ValueError, match="referências inexistentes"):
        builder.construir()


def test_rejeitar_tipo_resposta_desconhecido():
    """
    Confirma que o tipo de resposta deve corresponder a um dos tipos previstos.
    """

    builder = (
        criar_builder_base("tipo_desconhecido")
        .adicionar_registo("U001", {"estado_conta": "Ativa"})
    )

    with pytest.raises(ValueError, match="tipo de resposta"):
        builder.construir()


def test_rejeitar_chave_duplicada():
    """
    Confirma que a chave de correção não pode conter identificadores repetidos.
    """

    builder = (
        criar_builder_base()
        .adicionar_registo("U001", {"estado_conta": "Ativa"})
        .definir_chave(["U001", "U001"])
    )

    with pytest.raises(ValueError, match="duplicados"):
        builder.construir()


def test_proteger_dados_dos_registos():
    """
    Confirma que alterações ao dicionário original não modificam os dados guardados.
    """

    dados = {"estado_conta": "Ativa"}

    builder = (
        criar_builder_base()
        .adicionar_registo("U001", dados)
        .definir_chave(["U001"])
    )

    # Altera o dicionário original depois de o registo ter sido adicionado.
    dados["estado_conta"] = "Desativada"

    cenario = builder.construir()

    assert cenario.registos[0].dados["estado_conta"] == "Ativa"

    # Confirma que os dados do cenário não podem ser modificados diretamente.
    with pytest.raises(TypeError):
        cenario.registos[0].dados["estado_conta"] = "Bloqueada"
