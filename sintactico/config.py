"""
Configuración del analizador sintáctico

Hecho por Alejandro Osorio Osorio y Maria Paula Ruiz.

Aquí está lo que el parser necesita saber de los tokens del lexer y lo que
usa para escribir mensajes de error que se entiendan.
"""

from lexico.config import PALABRAS_RESERVADAS


# Tokens del lexer que el parser no necesita ver
TOKENS_IGNORADOS = {'T_COMMENT', 'T_DOC_COMMENT', 'T_OPEN_TAG'}

# Tokens que PHP trata como si fueran otro. El ?> cuenta como un punto y
# coma y el <?= cuenta como echo
TOKENS_EQUIVALENTES = {
    'T_CLOSE_TAG': 'SEMI',
    'T_OPEN_TAG_WITH_ECHO': 'T_ECHO',
}


# Cómo se nombra cada token en los mensajes de "se esperaba"
NOMBRES_TOKEN = {
    'SEMI': "';'", 'COMMA': "','", 'COLON': "':'",
    'LPAREN': "'('", 'RPAREN': "')'",
    'LBRACE': "'{'", 'RBRACE': "'}'",
    'LBRACKET': "'['", 'RBRACKET': "']'",
    'EQUALS': "'='", 'T_DOUBLE_ARROW': "'=>'",
    'T_VARIABLE': 'una variable', 'T_STRING': 'un identificador',
}
# Las palabras reservadas se escriben tal cual, por ejemplo T_ELSE sale como 'else'
for _palabra, _token in PALABRAS_RESERVADAS.items():
    NOMBRES_TOKEN.setdefault(_token, f"'{_palabra}'")


# Situaciones que se reconocen porque el parser acepta cierto token en ellas.
# Cada par tiene el token que la identifica y cómo se dice en el mensaje.
# Se usa la primera que coincida
CATEGORIAS = (
    ('T_IF', 'una sentencia'),
    ('T_CONST', 'un miembro de clase'),
    ('T_CASE', "'case' o 'default'"),
    ('T_LNUMBER', 'una expresión'),
)

# Cierres que siempre vale la pena mencionar
CIERRES = ('RPAREN', 'RBRACKET', 'RBRACE')

# Tokens que se mencionan cuando no hay ninguna situación reconocida. Los
# demás serían ruido, por ejemplo todos los operadores que pueden ir después
# de una expresión
ESTRUCTURALES = (
    'SEMI', 'RPAREN', 'RBRACKET', 'RBRACE', 'COMMA', 'COLON', 'T_DOUBLE_ARROW',
    'LBRACE', 'T_AS', 'T_VARIABLE', 'T_STRING',
)

# Si no hay nada más que decir solo se listan los esperados cuando son pocos
MAX_ESPERADOS = 6
