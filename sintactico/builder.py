"""
Construcción del analizador sintáctico

Hecho por Alejandro Osorio Osorio y Maria Paula Ruiz.

Arma el parser con PLY una sola vez cuando se importa el módulo, igual que
se hace con el lexer.
"""

import sys

try:
    import ply.yacc as yacc
except ImportError:
    sys.exit("PLY es requerido: pip install ply")

from sintactico import reglas
from sintactico.excepciones import contexto


def construir_parser():
    """
    Genera el parser LALR a partir de las reglas.

    Con write_tables en False PLY no crea los archivos parsetab.py y
    parser.out. El logger nulo esconde las advertencias por los tokens del
    lexer que la gramática no usa, como T_GOTO.
    """
    return yacc.yacc(
        module=reglas,
        debug=False,
        write_tables=False,
        errorlog=yacc.NullLogger(),
    )


# PLY no reporta un error si está a menos de 3 tokens del anterior. Con 1 se
# reportan todos y p_error se encarga de ignorar los que salen de la propia
# recuperación
yacc.error_count = 1

# Un solo parser que se reutiliza en todos los análisis
parser = construir_parser()
contexto.parser = parser


def obtener_parser():
    """Devuelve el parser que se construyó al importar este módulo."""
    return parser
