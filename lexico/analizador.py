"""
Funciones principales del analizador léxico

Hecho por Alejandro Osorio Osorio y Maria Paula Ruiz.

Desde aquí se analiza el código y se obtienen los tokens y los errores
léxicos. También están las funciones que imprimen la tabla de tokens y las
estadísticas que se ven con la opción --tokens.
"""

from collections import Counter

from lexico.builder import obtener_lexer


def analizar(codigo_fuente):
    """
    Convierte el código fuente en una lista de tokens.

    El código puede ser PHP puro o HTML con bloques PHP. Si tiene alguna
    etiqueta <? el lexer arranca en modo HTML y si no arranca directamente en
    modo php.

    Devuelve los tokens y los errores léxicos. Un error no detiene el
    análisis. Se guarda, el lexer entrega un token que lo reemplaza y sigue
    con el resto del archivo. Los caracteres ilegales simplemente se saltan.
    """
    lexer = obtener_lexer()
    lexer.input(codigo_fuente)
    lexer.lineno = 1  # en cada análisis el conteo de líneas empieza de nuevo
    lexer.errores = []  # y los errores también

    # Si hay una etiqueta PHP se empieza en modo HTML, como hace PHP.
    # Si no hay ninguna se trata todo el texto como código PHP
    if '<?' in codigo_fuente:
        lexer.begin('INITIAL')
    else:
        lexer.begin('php')

    # Extraer todos los tokens
    tokens = list(iter(lexer.token, None))
    return tokens, list(lexer.errores)


def mostrar_tokens(flujo_tokens):
    """Imprime la tabla de tokens con su línea, su posición, su tipo y su lexema."""
    print(f"{'LÍNEA':>4} {'POS':>6}  {'TIPO':<32}LEXEMA")
    print('-' * 74)

    for token in flujo_tokens:
        # Obtener el valor del token como string
        lexema = repr(str(token.value))

        # Si el lexema es muy largo, truncarlo con puntos suspensivos
        if len(lexema) > 38:
            lexema = lexema[:35] + '...'

        print(f"{token.lineno:>4} {token.lexpos:>6}  {token.type:<32}{lexema}")

    print('-' * 74)
    print(f"{len(flujo_tokens)} tokens")


def resumir_tokens(flujo_tokens):
    """
    Imprime cuántas veces aparece cada tipo de token y el total. Al final
    lista los identificadores y las variables que hay en el código.
    """
    # Contar la frecuencia de cada tipo de token
    frecuencias = Counter(t.type for t in flujo_tokens)

    print('\nFRECUENCIA DE TOKENS')
    print('-' * 74)

    for tipo_token, cantidad in sorted(frecuencias.items()):
        print(f"  {tipo_token:<32}{cantidad:>5}")

    print(f"  {'TOTAL':<32}{len(flujo_tokens):>5}")

    # Extraer identificadores y variables únicas
    identificadores = sorted(
        set(t.value for t in flujo_tokens if t.type == 'T_STRING')
    )
    variables = sorted(
        set(t.value for t in flujo_tokens if t.type == 'T_VARIABLE')
    )

    # Mostrar identificadores
    print(f"\n  IDENTIFICADORES ({len(identificadores)}): " +
          f"{', '.join(identificadores) or '-'}")

    # Mostrar variables
    print(f"  VARIABLES   ({len(variables)}): " +
          f"{', '.join(variables) or '-'}")
