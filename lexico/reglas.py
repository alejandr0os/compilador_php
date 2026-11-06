"""
Reglas del analizador léxico

Hecho por Alejandro Osorio Osorio y Maria Paula Ruiz.

Aquí están todas las reglas con las que PLY reconoce los tokens de PHP. Las
más sencillas son solo una expresión regular guardada en una variable que se
llama t_php_ más el nombre del token. Las que necesitan más lógica son
funciones y en ellas la expresión regular va en la primera línea.
"""

import re

from errores import resumir
from lexico.config import CONVERSIONES, PALABRAS_RESERVADAS
from lexico.excepciones import (
    registrar_error,
    CARACTER_ILEGAL, CADENA_SIN_CERRAR, COMENTARIO_SIN_CERRAR,
    NUMERO_MAL_FORMADO, VARIABLE_INVALIDA,
    HEREDOC_MALFORMADO, HEREDOC_SIN_CERRAR,
)


# ----- Modo HTML, todo lo que está fuera de las etiquetas PHP -----

def t_open_tag(t):
    # Etiquetas de apertura <?php, <? y <?=
    # Al encontrar una el lexer pasa al modo php. Si es <?= el token es
    # T_OPEN_TAG_WITH_ECHO y si no es T_OPEN_TAG
    r'<\?[pP][hH][pP]\b|<\?=|<\?'
    t.lexer.begin('php')
    t.type = 'T_OPEN_TAG_WITH_ECHO' if '=' in t.value else 'T_OPEN_TAG'
    return t


def t_inline_html(t):
    # Todo el texto que no sea una etiqueta de apertura se guarda como un solo
    # token de HTML. Se cuentan sus saltos de línea para no perder la cuenta
    r'(?:[^<]|<(?!\?))+'
    t.type = 'T_INLINE_HTML'
    t.lexer.lineno += t.value.count('\n')
    return t


# ----- Modo PHP, etiqueta de cierre y espacios -----

def t_php_T_CLOSE_TAG(t):
    # Etiqueta de cierre ?> que devuelve el lexer al modo HTML
    r'\?>'
    t.lexer.begin('INITIAL')
    return t


# Espacios, tabulaciones y retornos de carro se ignoran en modo php
t_php_ignore = ' \t\r\f\v'


def t_php_newline(t):
    # Los saltos de línea no son tokens pero hay que contarlos para que los
    # errores salgan con la línea correcta
    r'\n+'
    t.lexer.lineno += len(t.value)
    # no se devuelve nada y PLY lo descarta


# ----- Atributos de PHP 8 y comentarios -----

def t_php_T_ATTRIBUTE(t):
    # Inicio de un atributo de PHP 8, el #[ que va antes de clases, funciones
    # y parámetros
    r'\#\['
    return t


def t_php_T_COMMENT(t):
    # Comentarios de una línea con // o con # y comentarios de bloque /* */
    # Los que empiezan con /** son de documentación y salen como T_DOC_COMMENT.
    # Los demás salen como T_COMMENT
    r'//(?:(?!\?>)[^\n])*|\#(?:(?!\?>)[^\n])*|/\*[\s\S]*?\*/'
    t.type = 'T_DOC_COMMENT' if t.value.startswith('/**') else 'T_COMMENT'
    t.lexer.lineno += t.value.count('\n')
    return t


def t_php_ERR_COMENTARIO(t):
    # Error léxico de un comentario /* que nunca se cierra
    # Solo llega aquí si la regla anterior no encontró el */ de cierre. Como
    # hace PHP, el comentario se come el resto del archivo y se entrega como un
    # comentario normal
    r'/\*[\s\S]*'
    registrar_error(
        t.lexer, COMENTARIO_SIN_CERRAR,
        "comentario de bloque sin cerrar: falta '*/'",
        t.lexpos, resumir(t.value)
    )
    t.lexer.lineno += t.value.count('\n')
    t.type = 'T_COMMENT'
    return t


# ----- Literales, cadenas, números y variables -----

def t_php_T_CONSTANT_ENCAPSED_STRING(t):
    # Cadenas entre comillas simples o dobles
    # En las simples solo \' y \\ son especiales. Las dobles se guardan como un
    # solo token porque en esta fase no se revisa la interpolación
    r'''
    '([^'\\]|\\[\s\S])*'   # Comillas simples
    |
    "([^"\\]|\\[\s\S])*"   # Comillas dobles
    '''
    # Una cadena puede ocupar varias líneas y hay que contarlas
    t.lexer.lineno += t.value.count('\n')
    return t


def t_php_ERR_CADENA(t):
    # Error léxico de una cadena que abre con ' o con " y nunca se cierra
    # Solo llega aquí si la regla anterior no encontró la comilla de cierre.
    # La cadena se come el resto del archivo, como en PHP, y se entrega igual
    # para que el parser no se encuentre un hueco
    r'''
    '([^'\\]|\\[\s\S])*
    |
    "([^"\\]|\\[\s\S])*
    '''
    tipo = 'simples' if t.value[0] == "'" else 'dobles'
    registrar_error(
        t.lexer, CADENA_SIN_CERRAR,
        f"cadena entre comillas {tipo} sin cerrar: falta {t.value[0]}",
        t.lexpos, resumir(t.value)
    )
    t.lexer.lineno += t.value.count('\n')
    t.type = 'T_CONSTANT_ENCAPSED_STRING'
    return t


def t_php_T_LNUMBER(t):
    # Números enteros y decimales en todos los formatos de PHP
    # Hexadecimal 0x1AF, binario 0b1010, octal 0o755 o 0755, enteros con
    # separadores como 1_000_000 y decimales como 3.14 o 6.02e23
    #
    # La regla toma todo lo que parece un número, o sea un dígito seguido de
    # letras, dígitos, guiones bajos o puntos, y después lo valida. Así algo
    # como 123abc, 0x, 0b102, 1.2.3 o 089 sale como un solo error y no se parte
    # en tokens falsos. El número inválido se entrega de todas formas para que
    # el parser no se encuentre un hueco en la expresión
    r'(?:[0-9](?:\w|\.(?!\.)|(?<=[eE])[+-](?=[0-9]))*|\.[0-9](?:\w|(?<=[eE])[+-](?=[0-9]))*)'
    v = t.value

    # En 0xE+1 el signo no es parte del número, es una suma de 14 y 1
    signo = re.search(r'[+-]', v)
    if signo and v[:2].lower() == '0x':
        v = t.value = v[:signo.start()]
        t.lexer.lexpos = t.lexpos + len(v)

    if not _numero_valido(v):
        registrar_error(
            t.lexer, NUMERO_MAL_FORMADO,
            f"número mal formado '{resumir(v)}': {_motivo_numero_invalido(v)}",
            t.lexpos, resumir(v)
        )

    # Determinar si es un número flotante o entero
    if '.' in v or (('e' in v or 'E' in v) and v[:2].lower() != '0x'):
        t.type = 'T_DNUMBER'
    else:
        t.type = 'T_LNUMBER'
    return t


_NUMERO_VALIDO = re.compile(r'''
    (?:
        0[xX][0-9a-fA-F][0-9a-fA-F_]*         # Hexadecimal
      | 0[bB][01][01_]*                       # Binario
      | 0[oO][0-7][0-7_]*                     # Octal (nuevo)
      | 0[0-7][0-7_]*                         # Octal (antiguo)
      | (?:[0-9][0-9_]*\.(?:[0-9][0-9_]*)?    # Flotante: 1.5  1.  .5
        |  \.[0-9][0-9_]*)
        (?:[eE][+-]?[0-9][0-9_]*)?            # Con exponente opcional
      | [0-9][0-9_]*[eE][+-]?[0-9][0-9_]*     # Notación científica
      | [0-9][0-9_]*                          # Decimal simple
    )
''', re.VERBOSE)


def _numero_valido(v):
    """Dice si v es un número completo y bien escrito."""
    if not _NUMERO_VALIDO.fullmatch(v):
        return False
    # Un octal antiguo no puede tener 8 ni 9, como 089. Pero 09.5 sí es un decimal
    if re.fullmatch(r'0[0-9_]*[89][0-9_]*', v):
        return False
    # El guion bajo solo puede ir entre dos dígitos
    if '__' in v or v.endswith('_'):
        return False
    if v[:2].lower() != '0x' and re.search(r'_[.eE]|[.eE]_|[.eE][+-]_', v):
        return False
    return True


def _motivo_numero_invalido(v):
    """Explica por qué el número no es válido."""
    prefijo = v[:2].lower()
    if '__' in v or v.endswith('_'):
        return "el separador '_' debe ir entre dos dígitos"
    if prefijo == '0x':
        return "literal hexadecimal inválido (se esperan dígitos 0-9 y a-f)"
    if prefijo == '0b':
        return "literal binario inválido (solo se permiten 0 y 1)"
    if prefijo == '0o' or re.fullmatch(r'0[0-9_]+', v):
        return "literal octal inválido (solo se permiten dígitos 0-7)"
    if re.fullmatch(r'[0-9][0-9_]*[^\W\d]\w*', v):
        return "identificador pegado a un número (¿falta un operador o un espacio?)"
    return "formato numérico inválido"


def t_php_T_CAST(t):
    # Conversiones de tipo como (int), (float), (string) o (bool)
    # PHP las toma como un solo token, por eso (int) $x no se confunde con una
    # constante entre paréntesis como (LIMITE). Si la palabra no es un tipo se
    # entrega solo el paréntesis y el lexer sigue justo después de él
    r'\([ \t]*[A-Za-z]+[ \t]*\)'
    tipo = CONVERSIONES.get(t.value[1:-1].strip().lower())
    if tipo is None:
        t.type, t.value = 'LPAREN', '('
        t.lexer.lexpos = t.lexpos + 1
    else:
        t.type = tipo
    return t


def t_php_T_VARIABLE(t):
    # Variables como $nombre o $this
    # Después del $ va una letra o un guion bajo y luego letras, dígitos o
    # guiones bajos. Se aceptan letras de cualquier idioma como ñ, é o 日.
    # Símbolos como ¿ § ¬ o € no son letras y salen como carácter ilegal
    r'\$[^\W\d]\w*'
    return t


def t_php_ERR_VARIABLE(t):
    # Error léxico de una variable que empieza con un dígito, como $1abc
    # Sin esta regla quedaría partida en un $ y un número y nadie avisaría del
    # problema. Se entrega como variable para que el parser no vea un hueco
    r'\$[0-9]\w*'
    registrar_error(
        t.lexer, VARIABLE_INVALIDA,
        f"nombre de variable inválido '{t.value}': no puede empezar con un dígito",
        t.lexpos, t.value
    )
    t.type = 'T_VARIABLE'
    return t


def t_php_T_STRING(t):
    # Identificadores y palabras reservadas
    # Empiezan con letra o guion bajo. Si el nombre es una palabra reservada,
    # sin importar mayúsculas, se devuelve el token de esa palabra. Si no, es
    # un T_STRING
    r'[^\W\d]\w*'
    # se busca en minúsculas porque PHP no distingue mayúsculas en esto
    t.type = PALABRAS_RESERVADAS.get(t.value.lower(), 'T_STRING')
    return t


# ----- Heredoc y nowdoc -----

def t_php_T_HEREDOC(t):
    # Heredoc y nowdoc, que son bloques de texto de varias líneas
    #
    # El heredoc permite meter variables dentro del texto
    # $x = <<<EOT
    # Hola $nombre
    # EOT;
    #
    # El nowdoc lleva la etiqueta entre comillas simples y deja el texto tal cual
    # $x = <<<'EOT'
    # Texto sin cambios
    # EOT;
    #
    # Esto no se puede hacer con una sola expresión regular porque la línea de
    # cierre tiene que repetir la etiqueta del inicio. Por eso la regla solo
    # reconoce el <<< y el resto se busca a mano
    r'<<<'
    lexer = t.lexer
    data = lexer.lexdata

    # Hasta dónde llega la línea del encabezado
    nl = data.find('\n', lexer.lexpos)
    header = data[lexer.lexpos:nl] if nl >= 0 else data[lexer.lexpos:]

    # El encabezado debe ser <<<EOT, <<<'EOT' o <<<"EOT"
    m = re.match(
        r"[ \t]*(?P<q>['\"]?)(?P<label>[A-Za-z_]\w*)(?P=q)[ \t]*\r?$",
        header
    )
    if not m:
        # Si el encabezado está mal se guarda el error, se entrega como heredoc
        # y el análisis sigue en la línea siguiente
        registrar_error(
            lexer, HEREDOC_MALFORMADO,
            "encabezado heredoc/nowdoc malformado después de '<<<': "
            "se esperaba <<<ETIQUETA o <<<'ETIQUETA' y luego un salto de línea",
            t.lexpos, resumir('<<<' + header.strip())
        )
        lexer.lexpos = nl if nl >= 0 else len(data)
        t.type = 'T_HEREDOC'
        return t

    label, nowdoc = m.group('label'), m.group('q') == "'"

    # Si después del encabezado no hay salto de línea tampoco hay cuerpo ni
    # cierre, así que la búsqueda empieza después del final y el heredoc queda
    # sin cerrar
    if nl < 0:
        nl = len(data)

    # Patrón de la línea de cierre
    term = re.compile(r'[ \t]*' + re.escape(label) + r'(?![A-Za-z0-9_])')

    # Buscar la línea de cierre
    body_start, end, pos = nl + 1, -1, nl + 1
    while pos <= len(data):
        line_end = data.find('\n', pos)
        if line_end < 0:
            line_end = len(data)

        # Revisar si esta línea es la de cierre
        if term.match(data, pos, line_end):
            end = pos
            break

        if line_end == len(data):
            break

        pos = line_end + 1

    if end < 0:
        # Error léxico porque no hay línea de cierre. Todo lo que sigue sería
        # parte del heredoc, así que se consume hasta el final del archivo
        registrar_error(
            lexer, HEREDOC_SIN_CERRAR,
            f"heredoc/nowdoc '{label}' sin cerrar: no se encontró la línea "
            f"que termina con '{label}'",
            t.lexpos, resumir('<<<' + header.strip())
        )
        lexer.lineno += data[t.lexpos:].count('\n')
        lexer.lexpos = len(data)
        t.value = data[body_start:]
        t.type = 'T_NOWDOC' if nowdoc else 'T_HEREDOC'
        return t

    # Sacar el contenido y decidir si es heredoc o nowdoc
    t.value = data[body_start:end]
    lexer.lexpos = term.match(data, end).end()
    lexer.lineno += data[t.lexpos:lexer.lexpos].count('\n')
    t.type = 'T_NOWDOC' if nowdoc else 'T_HEREDOC'
    return t


# ----- Operadores de varios caracteres -----
# PLY ordena estas reglas de la más larga a la más corta, así === se prueba
# antes que == y == antes que =

# De tres caracteres o más
t_php_T_NULLSAFE_OBJECT_OPERATOR = r'\?->'        # ?->
t_php_T_COALESCE_EQUAL            = r'\?\?='      # ??=
t_php_T_SPACESHIP                 = r'<=>'        # <=>
t_php_T_IS_IDENTICAL              = r'==='        # ===
t_php_T_IS_NOT_IDENTICAL          = r'!=='        # !==
t_php_T_SL_EQUAL                  = r'<<='        # <<=
t_php_T_SR_EQUAL                  = r'>>='        # >>=
t_php_T_POW_EQUAL                 = r'\*\*='      # **=

# De dos caracteres
t_php_T_IS_SMALLER_OR_EQUAL       = r'<='         # <=
t_php_T_IS_GREATER_OR_EQUAL       = r'>='         # >=
t_php_T_BOOLEAN_AND               = r'&&'         # &&
t_php_T_BOOLEAN_OR                = r'\|\|'       # ||
t_php_T_POW                       = r'\*\*'       # **
t_php_T_CONCAT_EQUAL              = r'\.='        # .=
t_php_T_PLUS_EQUAL                = r'\+='        # +=
t_php_T_MINUS_EQUAL               = r'-='         # -=
t_php_T_MUL_EQUAL                 = r'\*='        # *=
t_php_T_DIV_EQUAL                 = r'/='         # /=
t_php_T_MOD_EQUAL                 = r'%='         # %=
t_php_T_AND_EQUAL                 = r'&='         # &=
t_php_T_OR_EQUAL                  = r'\|='        # |=
t_php_T_XOR_EQUAL                 = r'\^='        # ^=
t_php_T_SL                        = r'<<'         # <<
t_php_T_SR                        = r'>>'         # >>
t_php_T_IS_EQUAL                  = r'=='         # ==
t_php_T_IS_NOT_EQUAL              = r'!=(?!=)|<>' # != y <>, sin tomar el != de !==
t_php_T_DOUBLE_ARROW              = r'=>'         # =>
t_php_T_OBJECT_OPERATOR           = r'->'         # ->
t_php_T_DOUBLE_COLON              = r'::'         # ::
t_php_T_ELLIPSIS                  = r'\.\.\.'     # ...
t_php_T_COALESCE                  = r'\?\?'       # ??
t_php_T_NS_SEPARATOR              = r'\\'         # \ que separa los namespaces
t_php_T_INC                       = r'\+\+'       # ++
t_php_T_DEC                       = r'--'         # --


# ----- Delimitadores y operadores de un carácter -----

t_php_LPAREN                      = r'\('
t_php_RPAREN                      = r'\)'
t_php_LBRACE                      = r'\{'
t_php_RBRACE                      = r'\}'
t_php_LBRACKET                    = r'\['
t_php_RBRACKET                    = r'\]'
t_php_SEMI                        = r';'
t_php_COMMA                       = r','
t_php_COLON                       = r':'
t_php_QUESTION                    = r'\?'
t_php_AT                          = r'@'         # para suprimir errores
t_php_BACKTICK                    = r'`'
t_php_DOLLAR                      = r'\$'        # para variables variables como $$a
t_php_PLUS                        = r'\+'
t_php_MINUS                       = r'-'
t_php_TIMES                       = r'\*'
t_php_DIVIDE                      = r'/'
t_php_MOD                         = r'%'
t_php_CONCAT                      = r'\.'
t_php_EQUALS                      = r'='
t_php_LT                          = r'<'
t_php_GT                          = r'>'
t_php_NOT                         = r'!'
t_php_AMP                         = r'&'
t_php_PIPE                        = r'\|'
t_php_CARET                       = r'\^'
t_php_TILDE                       = r'~'


# ----- Errores léxicos -----

def t_php_error(t):
    """
    Se llama cuando un carácter no encaja con ninguna regla en modo php, por
    ejemplo ¿ § € o ¬. Se guarda el error con su línea y su columna y se salta
    ese carácter para seguir con el resto del archivo.
    """
    _caracter_ilegal(t)


def t_error(t):
    """Lo mismo que t_php_error pero para el modo HTML."""
    _caracter_ilegal(t)


def _caracter_ilegal(t):
    c = t.value[0]
    registrar_error(
        t.lexer, CARACTER_ILEGAL,
        f"carácter ilegal {c!r} (U+{ord(c):04X}): no pertenece al alfabeto de PHP",
        t.lexpos, c
    )
    t.lexer.skip(1)
