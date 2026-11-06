"""
Errores del analizador léxico

Hecho por Alejandro Osorio Osorio y Maria Paula Ruiz.

Aquí están los tipos de error léxico y la función registrar_error. Las reglas
la usan para ir guardando los errores en lugar de imprimirlos apenas
aparecen. Así al final se pueden mostrar todos y en orden.
"""

from errores import Error, calcular_posicion


# Tipos de error léxico
CARACTER_ILEGAL = 'CARACTER_ILEGAL'              # símbolo fuera del alfabeto
CADENA_SIN_CERRAR = 'CADENA_SIN_CERRAR'          # una cadena que nunca se cierra
COMENTARIO_SIN_CERRAR = 'COMENTARIO_SIN_CERRAR'  # un /* que nunca se cierra
NUMERO_MAL_FORMADO = 'NUMERO_MAL_FORMADO'        # 0x, 0b2, 123abc, 1.2.3 ...
VARIABLE_INVALIDA = 'VARIABLE_INVALIDA'          # $1abc
HEREDOC_MALFORMADO = 'HEREDOC_MALFORMADO'        # <<< sin etiqueta válida
HEREDOC_SIN_CERRAR = 'HEREDOC_SIN_CERRAR'        # falta la línea de cierre

# Estos errores se comen el resto del archivo. Si aparece uno, que el archivo
# termine de golpe no es culpa del programa sino de ese error
HASTA_EL_FINAL = {CADENA_SIN_CERRAR, COMENTARIO_SIN_CERRAR, HEREDOC_SIN_CERRAR}


def registrar_error(lexer, tipo, mensaje, lexpos, lexema=''):
    """Guarda un error léxico en la lista de errores del lexer."""
    linea, columna = calcular_posicion(lexer.lexdata, lexpos)
    lexer.errores.append(Error(tipo, mensaje, linea, columna, lexema))
