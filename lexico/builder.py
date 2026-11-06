"""
Construcción del analizador léxico

Hecho por Alejandro Osorio Osorio y Maria Paula Ruiz.

Junta las reglas y la configuración y arma el lexer con PLY. Esto se hace
una sola vez, cuando se importa el módulo, y después todos los análisis usan
ese mismo lexer.
"""

import sys

try:
    import ply.lex as lex
except ImportError:
    sys.exit("PLY es requerido: pip install ply")

# Estados y tokens del lexer
from lexico.config import LEXER_STATES, TOKENS_COMPLETOS

# Al importar las reglas PLY las encuentra y las registra
from lexico import reglas


def construir_lexer():
    """
    Arma el lexer de PHP con PLY.

    Primero les pasa a las reglas los estados y la lista de tokens. El estado
    INITIAL es para el HTML y el estado php es para el código. Después
    ply.lex genera el lexer leyendo todas las reglas del módulo reglas.
    """
    reglas.states = LEXER_STATES
    reglas.tokens = TOKENS_COMPLETOS

    lexer_generado = lex.lex(module=reglas)
    return lexer_generado


# Se construye un solo lexer y se reutiliza en todos los análisis
lexer = construir_lexer()
lexer.errores = []  # aquí se van guardando los errores léxicos del análisis actual


def obtener_lexer():
    """Devuelve el lexer que se construyó al importar este módulo."""
    return lexer
