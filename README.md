# Compilador de PHP

Proyecto de la materia de Compiladores, hecho por Alejandro Osorio Osorio y Maria Paula Ruiz.

Es un compilador de PHP escrito en Python con PLY. Por ahora tiene las dos primeras fases, el analizador léxico y el analizador sintáctico.

El analizador léxico lee el código fuente y lo convierte en una lista de tokens, cada uno con su línea y su posición. Si encuentra algo que no está bien escrito, como un número con letras o una cadena que nunca se cierra, guarda el error y sigue leyendo el resto del archivo.

El analizador sintáctico recibe esos tokens y revisa que sigan la gramática de PHP. Usa un parser LALR y cuando encuentra un error intenta recuperarse para seguir buscando más. Por ejemplo, si falta un punto y coma lo agrega por su cuenta y continúa, y si algo no tiene arreglo descarta tokens hasta el final de la instrucción o del bloque.

## Estructura

```
php_lexer/
├── compilador.py       programa principal, corre las dos fases
├── errores.py          lo que comparten las dos fases para manejar errores
├── demo.py             programa PHP que se usa cuando no se pasa ningún archivo
│
├── lexico/             fase 1, analizador léxico
│   ├── config.py       tokens y palabras reservadas
│   ├── excepciones.py  tipos de error léxico
│   ├── reglas.py       reglas y expresiones regulares de cada token
│   ├── builder.py      construye el lexer con PLY
│   └── analizador.py   analiza el código y muestra la tabla de tokens
│
└── sintactico/         fase 2, analizador sintáctico
    ├── config.py       nombres de los tokens para los mensajes de error
    ├── excepciones.py  tipos de error sintáctico y qué se esperaba en cada caso
    ├── reglas.py       la gramática y la recuperación de errores
    ├── builder.py      construye el parser con PLY
    └── analizador.py   pasa los tokens del lexer al parser
```

## Cómo usarlo

Se necesita Python 3.8 o más reciente y la librería PLY.

```bash
pip install ply
```

Para analizar un archivo

```bash
python compilador.py archivo.php
```

Si además quieres ver la tabla de tokens y cuántas veces aparece cada uno

```bash
python compilador.py --tokens archivo.php
```

Si no se pasa ningún archivo se analiza el programa que está en demo.py.

## Errores que detecta

Ninguna de las dos fases se detiene en el primer error. Se reportan todos los que haya, cada uno con su línea, su columna y una flecha que señala el lugar exacto en el código.

### Errores léxicos

- `CARACTER_ILEGAL` cuando aparece un símbolo que no es parte de PHP, como `€` o un byte de control.
- `VARIABLE_INVALIDA` cuando el nombre de una variable empieza con un número, como `$1contador`.
- `NUMERO_MAL_FORMADO` cuando un número está mal escrito. Pasa con un hexadecimal sin dígitos como `0x`, un binario con dígitos que no son 0 ni 1 como `0b102`, un octal con 8 o 9 como `089`, guiones bajos repetidos o al final como `1__000`, un exponente incompleto como `1e` o letras pegadas a un número como `123abc`.
- `CADENA_SIN_CERRAR` cuando una cadena abre con comilla simple o doble y nunca se cierra.
- `COMENTARIO_SIN_CERRAR` cuando un comentario `/*` nunca llega a su `*/`.
- `HEREDOC_MALFORMADO` cuando después de `<<<` no viene una etiqueta válida.
- `HEREDOC_SIN_CERRAR` cuando un heredoc o un nowdoc no tiene su línea de cierre.

### Errores sintácticos

- `FALTA_PUNTO_Y_COMA` cuando una instrucción no termina en punto y coma, ya sea al final de la línea, antes de una llave de cierre o al final del archivo. El parser agrega el punto y coma que falta y sigue analizando.
- `TOKEN_INESPERADO` cuando aparece un token que la gramática no permite en ese lugar. El mensaje dice qué se esperaba. Algunos casos son un operador sin operando como `$a = 5 + ;`, asignarle algo a un número como `10 = $x;`, un ternario incompleto, un `if` o un `while` sin paréntesis, un `else` sin `if`, un `try` sin `catch`, una función o una clase sin nombre y paréntesis o llaves que no cierran.
- `FIN_DE_ARCHIVO_INESPERADO` cuando el archivo se acaba con un bloque todavía abierto.

### Cómo trabajan juntas las dos fases

Cuando el lexer encuentra un número mal formado, una variable inválida o una cadena, comentario o heredoc sin cerrar, guarda el error y de todas formas le entrega al parser un token del tipo que correspondía. Así `0x` le llega al parser como un número y `$1abc` como una variable, y el parser no reporta un segundo error por algo que ya se reportó.

Una cadena, un comentario o un heredoc sin cerrar se comen el resto del archivo. En ese caso el parser no se queja de que el archivo terminó antes de tiempo, porque eso es parte del mismo error.

Los caracteres ilegales simplemente se saltan, así que a veces dejan un error sintáctico en la misma instrucción.

Si el archivo no tiene ninguna etiqueta `<?` se analiza todo como código PHP. PHP de verdad lo tomaría como HTML, pero así se pueden probar pedazos de código sin tener que escribir `<?php` al principio.

## Qué parte de PHP cubre la gramática

La gramática acepta expresiones, control de flujo, funciones, clases, interfaces, traits, `match`, atributos, funciones anónimas y funciones flecha. También acepta conversiones de tipo como `(int) $x`, `static::` y `new static`, tipos que incluyen `null`, `false`, `true` o `static` y asignaciones como `[$a, $b] = $c` o `list($a, $b) = $c`.

Lo que no cubre es la sintaxis alterna con `endif` o `endwhile`, `enum`, `goto`, `yield`, `global`, las variables `static` dentro de funciones, las clases anónimas, los argumentos con nombre y `throw` usado como expresión.

## Ejemplo

Con este archivo `ejemplo.php`

```php
<?php
$a = 5
$b = 0x;
$c = 5 + ;
echo "fin;
```

el compilador muestra lo siguiente

```text
$ python compilador.py ejemplo.php

ERRORES LÉXICOS
--------------------------------------------------------------------------
  [1] línea 3, columna 6  NUMERO_MAL_FORMADO
      número mal formado '0x': literal hexadecimal inválido (se esperan dígitos 0-9 y a-f)
         3 | $b = 0x;
           |      ^
  [2] línea 5, columna 6  CADENA_SIN_CERRAR
      cadena entre comillas dobles sin cerrar: falta "
         5 | echo "fin;
           |      ^
--------------------------------------------------------------------------
  2 error(es): CADENA_SIN_CERRAR x1, NUMERO_MAL_FORMADO x1

ERRORES SINTÁCTICOS
--------------------------------------------------------------------------
  [1] línea 2, columna 7  FALTA_PUNTO_Y_COMA
      falta ';' antes de '$b'
         2 | $a = 5
           |       ^
  [2] línea 4, columna 10  TOKEN_INESPERADO
      token inesperado ';', se esperaba una expresión
         4 | $c = 5 + ;
           |          ^
--------------------------------------------------------------------------
  2 error(es): FALTA_PUNTO_Y_COMA x1, TOKEN_INESPERADO x1

Total: 2 error(es) léxico(s) y 2 error(es) sintáctico(s).
```
