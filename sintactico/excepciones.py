"""
Errores del analizador sintáctico

Hecho por Alejandro Osorio Osorio y Maria Paula Ruiz.

Aquí están los tipos de error sintáctico, el contexto que necesita p_error y
que PLY no le pasa, y crear_error, que arma el error a partir del token que
el parser no esperaba.
"""

from errores import Error, calcular_posicion, resumir
from sintactico.config import (
    NOMBRES_TOKEN, CATEGORIAS, CIERRES, ESTRUCTURALES, MAX_ESPERADOS,
)


# Tipos de error sintáctico
FALTA_PUNTO_Y_COMA = 'FALTA_PUNTO_Y_COMA'                # falta el punto y coma al final de la línea
TOKEN_INESPERADO = 'TOKEN_INESPERADO'                    # $a = * 3;
FIN_DE_ARCHIVO_INESPERADO = 'FIN_DE_ARCHIVO_INESPERADO'  # falta cerrar un '{'


class Contexto:
    """Datos del análisis actual para que p_error los pueda leer."""
    parser = None   # lo asigna sintactico.builder
    fuente = ''     # código fuente que se está analizando
    flujo = None    # FlujoTokens, sabe cuál fue el token anterior
    fin_cortado = False  # True si el lexer se comió el final por un error léxico
    errores = []    # errores encontrados hasta ahora


contexto = Contexto()


# Qué se esperaba
def _reducir(parser, pila, accion):
    """Aplica una reducción sobre una copia de la pila de estados."""
    produccion = parser.productions[-accion]
    del pila[len(pila) - produccion.len:]
    pila.append(parser.goto[pila[-1]][produccion.name])


def tokens_validos(parser):
    """
    Devuelve los terminales que el parser aceptaría en este momento.

    La tabla LALR de PLY mezcla contextos y por eso no basta con mirar la fila
    del estado actual. Lo que se hace es probar cada terminal sobre una copia
    de la pila, aplicando las reducciones pendientes, hasta llegar a un
    desplazamiento, que quiere decir que es válido, o a un error.
    """
    base = list(parser.statestack)
    # Un estado que solo sabe reducir siempre por la misma producción se
    # reduce antes de mirar qué se acepta después
    while True:
        acciones = set(parser.action[base[-1]].values())
        if len(acciones) != 1 or min(acciones) >= 0:
            break
        _reducir(parser, base, acciones.pop())

    validos = []
    for terminal in parser.action[base[-1]]:
        if terminal in ('error', '$end'):
            continue
        pila = list(base)
        while True:
            estado = pila[-1]
            accion = parser.defaulted_states.get(estado)
            if accion is None:
                accion = parser.action[estado].get(terminal)
            if accion is None:
                break
            if accion > 0:
                validos.append(terminal)
                break
            _reducir(parser, pila, accion)
    return validos


def categoria(validos):
    """Devuelve la situación que se reconoce según lo que acepta el parser, o None."""
    for token, texto in CATEGORIAS:
        if token in validos:
            return texto
    return None


def describir_esperados(validos):
    """Arma el texto de "se esperaba". Si no hay nada útil que decir devuelve vacío."""
    situacion = categoria(validos)
    if situacion:
        partes = [situacion] + [NOMBRES_TOKEN[t] for t in CIERRES if t in validos]
    else:
        partes = [NOMBRES_TOKEN[t] for t in ESTRUCTURALES if t in validos]
        if not partes and len(validos) <= MAX_ESPERADOS:
            partes = [NOMBRES_TOKEN.get(t, t) for t in validos]
    if len(partes) > 1:
        return ', '.join(partes[:-1]) + ' o ' + partes[-1]
    return ''.join(partes)


# Construcción del error
def _fin_de(token):
    """Posición absoluta justo después de un token."""
    return token.lexpos + len(str(token.value))


def _linea(ctx, lexpos):
    return calcular_posicion(ctx.fuente, lexpos)[0]


def _lexema(token):
    """Lexema entre comillas para los mensajes, corto y en una sola línea."""
    texto = resumir(token.value, 20)
    return f'"{texto}"' if "'" in texto else f"'{texto}'"


def crear_error(token, ctx):
    """
    Convierte la falla del parser en un error sintáctico.

    El token es el que el parser no esperaba, o None si el archivo se acabó
    antes de tiempo. Se toma como un punto y coma olvidado cuando el parser lo
    aceptaría justo después de una expresión y el token que falló está en otra
    línea, es un } o es el fin del archivo. En ese caso el error se marca al
    final de la instrucción anterior, que es donde el programador lo olvidó.
    """
    anterior = ctx.flujo.anterior
    validos = tokens_validos(ctx.parser)
    esperado = describir_esperados(validos)
    detalle = f", se esperaba {esperado}" if esperado else ''

    fin_anterior = _fin_de(anterior) if anterior else 0
    if token is None:
        lexpos, lexema = fin_anterior, ''
        olvido = 'SEMI' in validos and categoria(validos) is None
    else:
        lexpos, lexema = token.lexpos, _lexema(token)
        olvido = ('SEMI' in validos and anterior is not None and
                  categoria(validos) is None and
                  (token.type == 'RBRACE' or
                   _linea(ctx, token.lexpos) > _linea(ctx, fin_anterior)))

    if olvido:
        tipo = FALTA_PUNTO_Y_COMA
        lexpos = fin_anterior
        mensaje = ("falta ';' al final del archivo" if token is None
                   else f"falta ';' antes de {lexema}")
    elif token is None:
        tipo = FIN_DE_ARCHIVO_INESPERADO
        mensaje = f"fin de archivo inesperado{detalle}"
    else:
        tipo = TOKEN_INESPERADO
        mensaje = f"token inesperado {lexema}{detalle}"

    linea, columna = calcular_posicion(ctx.fuente, lexpos)
    return Error(tipo, mensaje, linea, columna, lexema)
