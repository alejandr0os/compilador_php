"""
Errores del compilador

Hecho por Alejandro Osorio Osorio y Maria Paula Ruiz.

Aquí está lo que usan las dos fases para manejar los errores. La clase Error
guarda cada error léxico o sintáctico, calcular_posicion saca la línea y la
columna, resumir acorta los lexemas largos y mostrar_errores imprime el
reporte de cada fase.
"""

from collections import Counter
from dataclasses import dataclass


@dataclass
class Error:
    tipo: str
    mensaje: str
    linea: int
    columna: int
    lexema: str = ''


def calcular_posicion(datos, lexpos):
    """Pasa una posición absoluta a línea y columna, contando las dos desde 1."""
    linea = datos.count('\n', 0, lexpos) + 1
    inicio_linea = datos.rfind('\n', 0, lexpos) + 1
    return linea, lexpos - inicio_linea + 1


def resumir(texto, maximo=30):
    """Deja el lexema en una sola línea y lo corta con ... si es muy largo."""
    texto = str(texto).replace('\n', '\\n')
    return texto if len(texto) <= maximo else texto[:maximo] + '...'


def mostrar_errores(errores, codigo_fuente, titulo):
    """
    Imprime el reporte de errores de una fase.

    De cada error muestra el número, la línea y la columna, el tipo y el
    mensaje. Debajo pone la línea del código con una flecha ^ en la columna
    donde está el error.
    """
    print(f'\n{titulo}')
    print('-' * 74)

    if not errores:
        print(f'  Sin {titulo.lower()}.')
        return

    # Se parte solo por \n, igual que en calcular_posicion. splitlines también
    # corta en otros caracteres como \x0c o U+2028 y eso desordenaba el reporte
    lineas = [l.rstrip('\r') for l in codigo_fuente.split('\n')]

    for i, e in enumerate(errores, 1):
        print(f"  [{i}] línea {e.linea}, columna {e.columna}  {e.tipo}")
        print(f"      {e.mensaje}")
        if 1 <= e.linea <= len(lineas):
            texto = lineas[e.linea - 1].replace('\t', ' ')
            print(f"      {e.linea:>4} | {texto}")
            print(f"           | {' ' * (e.columna - 1)}^")

    por_tipo = Counter(e.tipo for e in errores)
    print('-' * 74)
    print(f"  {len(errores)} error(es): " +
          ', '.join(f"{t} x{n}" for t, n in sorted(por_tipo.items())))
