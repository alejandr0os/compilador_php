#!/usr/bin/env python3
"""
Compilador de PHP hecho con PLY

Hecho por Alejandro Osorio Osorio y Maria Paula Ruiz.

Este es el programa principal. Lee un archivo PHP, lo pasa primero por el
analizador léxico, que lo convierte en tokens, y luego por el analizador
sintáctico, que revisa esos tokens contra la gramática. Al final muestra los
errores que encontró cada fase.

Antes de usarlo hay que instalar PLY con pip install ply

Formas de ejecutarlo
    python compilador.py                         analiza el programa de demo
    python compilador.py archivo.php             analiza un archivo
    python compilador.py --tokens archivo.php    muestra también los tokens
"""

import argparse
import sys

from demo import DEMO_PHP
from errores import mostrar_errores
from lexico.analizador import analizar, mostrar_tokens, resumir_tokens
from lexico.excepciones import HASTA_EL_FINAL
from sintactico.analizador import analizar_sintaxis


def leer_codigo_fuente(ruta):
    """Lee el archivo que se pasó por consola. Si no hay ninguno usa el demo."""
    if ruta is None:
        print('(Sin archivo - analizando código de demostración)')
        return DEMO_PHP
    try:
        with open(ruta, encoding='utf-8', errors='replace') as fh:
            return fh.read()
    except OSError as excepcion:
        sys.exit(f"No se puede leer {ruta}: {excepcion}")


def main():
    argumentos = argparse.ArgumentParser(
        description='Compilador de PHP: análisis léxico y sintáctico.')
    argumentos.add_argument('archivo', nargs='?',
                            help='archivo PHP a analizar (por defecto, el demo)')
    argumentos.add_argument('--tokens', action='store_true',
                            help='mostrar la tabla y la frecuencia de tokens')
    opciones = argumentos.parse_args()

    codigo_fuente = leer_codigo_fuente(opciones.archivo)

    # Fase 1, análisis léxico
    tokens, errores_lexicos = analizar(codigo_fuente)
    if opciones.tokens:
        print()
        mostrar_tokens(tokens)
        resumir_tokens(tokens)

    # Fase 2, análisis sintáctico
    fin_cortado = any(e.tipo in HASTA_EL_FINAL for e in errores_lexicos)
    errores_sintacticos = analizar_sintaxis(tokens, codigo_fuente, fin_cortado)

    mostrar_errores(errores_lexicos, codigo_fuente, 'ERRORES LÉXICOS')
    mostrar_errores(errores_sintacticos, codigo_fuente, 'ERRORES SINTÁCTICOS')

    print()
    if not errores_lexicos and not errores_sintacticos:
        print('Análisis léxico y sintáctico correctos.')
        return

    print(f'Total: {len(errores_lexicos)} error(es) léxico(s) y '
          f'{len(errores_sintacticos)} error(es) sintáctico(s).')
    sys.exit(1)


if __name__ == '__main__':
    main()
