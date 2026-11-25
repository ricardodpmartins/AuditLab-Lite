
"""
Implementação do padrão Builder para os cenários do AuditLab Lite.

O Builder permite construir um cenário através de várias operações,
sem exigir que todos os elementos sejam fornecidos de uma só vez.

Antes de criar o objeto final, verifica se os dados estão completos
e se a chave de correção contém referências válidas.

A implementação segue uma variante fluente do padrão Builder.
"""

from datetime import date
from types import MappingProxyType

from modelos import Cenario, Registo, ValorCampo


class CenarioBuilder:
    """
    Responsável pela construção e validação dos cenários de auditoria.

    Os métodos de configuração devolvem a própria instância do Builder,
    permitindo encadear as operações de construção.

    O método construir() valida os dados e devolve um objeto Cenario.
    """

    def __init__(self):
        """
        Inicializa o Builder com os campos vazios.

        Cada instância representa um processo de construção independente.
        """

        self._identificador = ""
        self._titulo = ""
        self._descricao = ""
        self._data_referencia = ""
        self._politica = ""
        self._tipo_resposta = ""
        self._registos: list[Registo] = []
        self._chave_correcao: list[str] = []

    def definir_identificacao(
        self,
        identificador: str,
        titulo: str,
        descricao: str
    ):
        """
        Define o identificador, o título e a descrição do cenário.

        Devolve o Builder para permitir continuar a construção.
        """

        self._identificador = identificador
        self._titulo = titulo
        self._descricao = descricao

        return self

    def definir_politica(
        self,
        data_referencia: str,
        politica: str
    ):
        """
        Define a data de referência e a política do exercício.

        A política indica os critérios que o aluno deve considerar
        ao analisar os registos apresentados.
        """

        self._data_referencia = data_referencia
        self._politica = politica

        return self

    def definir_tipo_resposta(self, tipo_resposta: str):
        """
        Define o tipo de identificador utilizado na chave de correção.

        Os tipos permitidos correspondem aos diferentes objetos
        que podem ser avaliados nos cenários do AuditLab Lite.
        """

        self._tipo_resposta = tipo_resposta

        return self

    def adicionar_registo(
        self,
        identificador: str,
        dados: dict[str, ValorCampo],
        identificador_resposta: str | None = None
    ):
        """
        Adiciona um registo fictício ao cenário em construção.

        Quando não é indicado um identificador de resposta,
        utiliza o identificador do próprio registo.

        É criada uma cópia dos dados para impedir que alterações
        ao dicionário original modifiquem o registo guardado.
        """

        resposta = (
            identificador
            if identificador_resposta is None
            else identificador_resposta
        )

        registo = Registo(
            identificador=identificador,
            identificador_resposta=resposta,
            dados=MappingProxyType(dict(dados))
        )

        self._registos.append(registo)

        return self

    def definir_chave(self, identificadores: list[str]):
        """
        Define os identificadores que constituem a resposta esperada.

        A lista é copiada para impedir alterações externas durante
        o processo de construção do cenário.
        """

        self._chave_correcao = list(identificadores)

        return self

    def construir(self) -> Cenario:
        """
        Valida os dados e constrói o cenário.

        O processo verifica os campos obrigatórios, a data de referência,
        os identificadores dos registos e a consistência da chave de correção.

        Quando encontra uma inconsistência, interrompe a construção
        e apresenta uma mensagem através de ValueError.
        """

        # Verifica os elementos de identificação e configuração do cenário.
        campos_obrigatorios = {
            "identificador": self._identificador,
            "título": self._titulo,
            "descrição": self._descricao,
            "data de referência": self._data_referencia,
            "política": self._politica,
            "tipo de resposta": self._tipo_resposta,
        }

        for nome, valor in campos_obrigatorios.items():
            if not isinstance(valor, str) or not valor.strip():
                raise ValueError(f"O campo {nome} é obrigatório.")

        # Confirma que a data de referência está no formato ISO e é válida.
        try:
            date.fromisoformat(self._data_referencia)
        except ValueError as erro:
            raise ValueError(
                "A data de referência deve estar no formato AAAA-MM-DD."
            ) from erro

        # Limita o tipo de resposta aos identificadores previstos no catálogo.
        tipos_permitidos = {
            "conta_id",
            "login_id",
            "colaborador_id",
            "atribuicao_id",
        }

        if self._tipo_resposta not in tipos_permitidos:
            raise ValueError("O tipo de resposta não é reconhecido.")

        # Um cenário deve ter pelo menos um registo para ser analisado.
        if not self._registos:
            raise ValueError(
                "O cenário deve conter pelo menos um registo."
            )

        identificadores = [
            registo.identificador
            for registo in self._registos
        ]

        # Rejeita identificadores vazios ou de tipos incorretos.
        if any(
            not isinstance(identificador, str)
            or not identificador.strip()
            for identificador in identificadores
        ):
            raise ValueError(
                "Todos os registos devem ter identificadores válidos."
            )

        # Impede a existência de dois registos com o mesmo identificador.
        if len(identificadores) != len(set(identificadores)):
            raise ValueError(
                "Existem identificadores de registos duplicados."
            )

        for registo in self._registos:

            # Cada registo precisa de um identificador de resposta válido.
            if (
                not isinstance(registo.identificador_resposta, str)
                or not registo.identificador_resposta.strip()
            ):
                raise ValueError(
                    "O identificador de resposta é obrigatório."
                )

            # Os registos sem dados não permitem realizar a análise.
            if not registo.dados:
                raise ValueError(
                    f"O registo {registo.identificador} não tem dados."
                )

            # Valida os nomes e os tipos dos valores presentes nos registos.
            for campo, valor in registo.dados.items():

                if not isinstance(campo, str) or not campo.strip():
                    raise ValueError(
                        "Os nomes dos campos devem ser válidos."
                    )

                if valor is not None and type(valor) not in {
                    str, int, bool
                }:
                    raise ValueError(
                        f"O campo {campo} contém um tipo não suportado."
                    )

        # Confirma que os elementos da chave são identificadores válidos.
        if any(
            not isinstance(identificador, str)
            or not identificador.strip()
            for identificador in self._chave_correcao
        ):
            raise ValueError(
                "A chave de correção contém identificadores inválidos."
            )

        # A mesma resposta não deve aparecer repetida na chave de correção.
        if len(self._chave_correcao) != len(set(self._chave_correcao)):
            raise ValueError(
                "A chave de correção contém identificadores duplicados."
            )

        # Reúne todos os identificadores que podem ser selecionados pelo aluno.
        respostas_disponiveis = {
            registo.identificador_resposta
            for registo in self._registos
        }

        # Verifica se a chave contém referências que não existem nos dados.
        respostas_inexistentes = (
            set(self._chave_correcao) - respostas_disponiveis
        )

        if respostas_inexistentes:
            raise ValueError(
                "A chave de correção contém referências inexistentes: "
                + ", ".join(sorted(respostas_inexistentes))
            )

        # Cria o objeto final com coleções protegidas contra alterações diretas.
        return Cenario(
            identificador=self._identificador,
            titulo=self._titulo,
            descricao=self._descricao,
            data_referencia=self._data_referencia,
            politica=self._politica,
            tipo_resposta=self._tipo_resposta,
            registos=tuple(self._registos),
            chave_correcao=tuple(self._chave_correcao),
        )
