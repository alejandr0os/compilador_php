"""
Funciones principales del analizador sintáctico

Hecho por Alejandro Osorio Osorio y Maria Paula Ruiz.

Aquí se conecta el lexer con el parser. La clase FlujoTokens le va pasando
al parser los tokens que produjo el lexer y analizar_sintaxis corre el parser
y devuelve los errores.
"""

import copy

from ply.lex import LexToken

from sintactico.builder import obtener_parser
from sintactico.config import TOKENS_IGNORADOS, TOKENS_EQUIVALENTES
from sintactico.excepciones import contexto


class FlujoTokens:
    """
    Le entrega al parser los tokens que ya produjo el lexer.

    Se salta los comentarios y la etiqueta <?php. Cambia ?> por un punto y
    coma y <?= por echo, como hace PHP. También recuerda el token anterior
    para saber dónde falta un punto y coma y puede meter uno cuando el
    programador lo olvidó.
    """

    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.anterior = None
        self.actual = None
        self.pendiente = None   # un token que se devolvió y va antes que los demás

    def _siguiente(self):
        while self.pos < len(self.tokens):
            token = self.tokens[self.pos]
            self.pos += 1
            if token.type in TOKENS_IGNORADOS:
                continue
            if token.type in TOKENS_EQUIVALENTES:
                token = copy.copy(token)
                token.type = TOKENS_EQUIVALENTES[token.type]
            elif token.type == 'T_NS_SEPARATOR' and not self._separador_pegado():
                token = copy.copy(token)
                token.type = 'NS_SEPARADOR_SUELTO'   # el parser lo rechaza
            return token
        return None

    def _separador_pegado(self):
        """
        En PHP un nombre como A\\B no puede llevar espacios ni comentarios en
        medio. El separador va pegado al identificador que sigue y también al
        de antes si hay uno.
        """
        actual = self.tokens[self.pos - 1]
        siguiente = self.tokens[self.pos] if self.pos < len(self.tokens) else None
        if (siguiente is None or siguiente.type != 'T_STRING'
                or siguiente.lexpos != actual.lexpos + 1):
            return False
        anterior = self.tokens[self.pos - 2] if self.pos >= 2 else None
        if anterior is not None and anterior.type == 'T_STRING':
            return anterior.lexpos + len(anterior.value) == actual.lexpos
        return True

    def token(self):
        """PLY llama este método cada vez que necesita otro token."""
        if self.pendiente is not None:
            siguiente, self.pendiente = self.pendiente, None
        else:
            siguiente = self._siguiente()
        if siguiente is not None or self.actual is not None:
            self.anterior = self.actual
        self.actual = siguiente
        return siguiente

    def insertar_punto_y_coma(self, inesperado):
        """
        Arregla un punto y coma olvidado.

        Crea el punto y coma que faltaba para que el parser pueda terminar la
        instrucción. El token que causó el error queda guardado para
        entregarse de siguiente, así el análisis sigue desde ahí sin perder
        nada.
        """
        punto_y_coma = LexToken()
        punto_y_coma.type = 'SEMI'
        punto_y_coma.value = ';'
        punto_y_coma.lineno = self.anterior.lineno if self.anterior else 1
        punto_y_coma.lexpos = (self.anterior.lexpos + len(str(self.anterior.value))
                               if self.anterior else 0)
        if inesperado is not None:
            self.pendiente = inesperado
            self.actual = self.anterior
        return punto_y_coma


def analizar_sintaxis(tokens, codigo_fuente, fin_cortado=False):
    """
    Revisa la sintaxis de la lista de tokens que devolvió el analizador léxico.

    Se necesita el código fuente para calcular la línea y la columna de cada
    error. Si fin_cortado es True quiere decir que una cadena, un comentario o
    un heredoc sin cerrar se comió el resto del archivo, y en ese caso no se
    reporta el fin de archivo inesperado porque ya es parte de ese error.

    Devuelve los errores sintácticos en el orden en que aparecen.
    """
    contexto.fuente = codigo_fuente
    contexto.errores = []
    contexto.flujo = FlujoTokens(tokens)
    contexto.fin_cortado = fin_cortado

    obtener_parser().parse(lexer=contexto.flujo)
    return list(contexto.errores)
