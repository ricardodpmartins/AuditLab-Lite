
"""
Modelos de dados utilizados nos cenários do AuditLab Lite.

Este módulo define os objetos que representam os registos apresentados
ao aluno e os cenários de auditoria construídos pela aplicação.

Os modelos são independentes das regras de deteção e dos serviços REST.
"""

from dataclasses import dataclass
from typing import Mapping


# Define os tipos de valores aceites nos campos dos registos fictícios.
ValorCampo = str | int | bool | None


@dataclass(frozen=True)
class Registo:
    """
    Representa um registo fictício que será analisado pelo aluno.

    O identificador distingue o registo no conjunto de dados do cenário.

    O identificador_resposta corresponde ao elemento que o aluno deve
    selecionar durante a atividade. Pode representar uma conta, um
    colaborador, um evento de login ou uma atribuição de permissões.

    O atributo dados contém os campos específicos do exercício.
    """

    identificador: str
    identificador_resposta: str
    dados: Mapping[str, ValorCampo]


@dataclass(frozen=True)
class Cenario:
    """
    Representa um cenário de auditoria depois de construído e validado.

    O cenário reúne a informação apresentada ao aluno e a chave de
    correção utilizada posteriormente pelo motor de avaliação.

    A chave de correção deve permanecer separada dos dados enviados
    para a interface do aluno, para não revelar as respostas esperadas.

    A opção frozen=True impede a alteração direta dos atributos.
    As coleções internas também devem ser protegidas pelo Builder.
    """

    identificador: str
    titulo: str
    descricao: str
    data_referencia: str
    politica: str
    tipo_resposta: str
    registos: tuple[Registo, ...]
    chave_correcao: tuple[str, ...]
