"""
Configuración del analizador léxico

Hecho por Alejandro Osorio Osorio y Maria Paula Ruiz.

Aquí están los estados del lexer, las palabras reservadas de PHP y la lista
de todos los tokens que se pueden reconocer.
"""


# Estados del lexer. INITIAL es el estado por defecto y corresponde al HTML
# que está fuera de las etiquetas. El estado php es el que se usa dentro de
# <?php ... ?>
LEXER_STATES = (
    ('php', 'exclusive'),
)


# Palabras reservadas de PHP. Se reconocen sin importar mayúsculas y
# minúsculas, igual que en PHP. Los nombres de los tokens son los mismos que
# usa la función token_get_all de PHP

PALABRAS_RESERVADAS = {
    # Control de flujo
    'if': 'T_IF',
    'else': 'T_ELSE',
    'elseif': 'T_ELSEIF',
    'endif': 'T_ENDIF',
    'while': 'T_WHILE',
    'endwhile': 'T_ENDWHILE',
    'do': 'T_DO',
    'for': 'T_FOR',
    'endfor': 'T_ENDFOR',
    'foreach': 'T_FOREACH',
    'endforeach': 'T_ENDFOREACH',
    'as': 'T_AS',
    'switch': 'T_SWITCH',
    'endswitch': 'T_ENDSWITCH',
    'case': 'T_CASE',
    'default': 'T_DEFAULT',
    'break': 'T_BREAK',
    'continue': 'T_CONTINUE',
    'goto': 'T_GOTO',
    'return': 'T_RETURN',

    # Excepciones
    'try': 'T_TRY',
    'catch': 'T_CATCH',
    'finally': 'T_FINALLY',
    'throw': 'T_THROW',

    # Programación orientada a objetos
    'class': 'T_CLASS',
    'interface': 'T_INTERFACE',
    'trait': 'T_TRAIT',
    'enum': 'T_ENUM',
    'extends': 'T_EXTENDS',
    'implements': 'T_IMPLEMENTS',
    'abstract': 'T_ABSTRACT',
    'final': 'T_FINAL',
    'readonly': 'T_READONLY',
    'public': 'T_PUBLIC',
    'private': 'T_PRIVATE',
    'protected': 'T_PROTECTED',
    'static': 'T_STATIC',
    'var': 'T_VAR',
    'const': 'T_CONST',
    'new': 'T_NEW',
    'clone': 'T_CLONE',
    'instanceof': 'T_INSTANCEOF',
    'function': 'T_FUNCTION',
    'fn': 'T_FN',
    'namespace': 'T_NAMESPACE',
    'use': 'T_USE',
    'insteadof': 'T_INSTEADOF',

    # Construcciones del lenguaje como echo, print o isset
    'echo': 'T_ECHO',
    'print': 'T_PRINT',
    'eval': 'T_EVAL',
    'exit': 'T_EXIT',
    'die': 'T_EXIT',
    'isset': 'T_ISSET',
    'unset': 'T_UNSET',
    'empty': 'T_EMPTY',
    'list': 'T_LIST',
    'array': 'T_ARRAY',
    'callable': 'T_CALLABLE',
    'global': 'T_GLOBAL',
    'include': 'T_INCLUDE',
    'include_once': 'T_INCLUDE_ONCE',
    'require': 'T_REQUIRE',
    'require_once': 'T_REQUIRE_ONCE',
    'declare': 'T_DECLARE',
    'enddeclare': 'T_ENDDECLARE',
    'match': 'T_MATCH',
    'yield': 'T_YIELD',

    # Operadores que se escriben con palabras
    'and': 'T_LOGICAL_AND',
    'or': 'T_LOGICAL_OR',
    'xor': 'T_LOGICAL_XOR',

    # Literales especiales
    'true': 'T_TRUE',
    'false': 'T_FALSE',
    'null': 'T_NULL',
}


# Tokens que no son palabras reservadas. Están agrupados en etiquetas,
# literales, comentarios, operadores y símbolos de un solo carácter

TOKENS_BASICOS = [
    # Etiquetas y HTML que va por fuera de PHP
    'T_OPEN_TAG',
    'T_OPEN_TAG_WITH_ECHO',
    'T_CLOSE_TAG',
    'T_INLINE_HTML',

    # Identificadores y literales
    'T_VARIABLE',
    'T_STRING',
    'T_LNUMBER',
    'T_DNUMBER',
    'T_CONSTANT_ENCAPSED_STRING',
    'T_HEREDOC',
    'T_NOWDOC',

    # Comentarios y atributos
    'T_COMMENT',
    'T_DOC_COMMENT',
    'T_ATTRIBUTE',

    # Operadores de múltiples caracteres
    'T_OBJECT_OPERATOR',
    'T_NULLSAFE_OBJECT_OPERATOR',
    'T_DOUBLE_ARROW',
    'T_DOUBLE_COLON',
    'T_ELLIPSIS',
    'T_INC',
    'T_DEC',
    'T_POW',
    'T_POW_EQUAL',
    'T_IS_EQUAL',
    'T_IS_IDENTICAL',
    'T_IS_NOT_EQUAL',
    'T_IS_NOT_IDENTICAL',
    'T_IS_SMALLER_OR_EQUAL',
    'T_IS_GREATER_OR_EQUAL',
    'T_SPACESHIP',
    'T_BOOLEAN_AND',
    'T_BOOLEAN_OR',
    'T_COALESCE',
    'T_COALESCE_EQUAL',
    'T_CONCAT_EQUAL',
    'T_PLUS_EQUAL',
    'T_MINUS_EQUAL',
    'T_MUL_EQUAL',
    'T_DIV_EQUAL',
    'T_MOD_EQUAL',
    'T_AND_EQUAL',
    'T_OR_EQUAL',
    'T_XOR_EQUAL',
    'T_SL_EQUAL',
    'T_SR_EQUAL',
    'T_SL',
    'T_SR',
    'T_NS_SEPARATOR',

    # Conversiones de tipo como (int) o (string)
    'T_INT_CAST',
    'T_DOUBLE_CAST',
    'T_STRING_CAST',
    'T_BOOL_CAST',
    'T_ARRAY_CAST',
    'T_OBJECT_CAST',

    # Símbolos de un solo carácter
    'LPAREN',
    'RPAREN',
    'LBRACE',
    'RBRACE',
    'LBRACKET',
    'RBRACKET',
    'SEMI',
    'COMMA',
    'COLON',
    'QUESTION',
    'AT',
    'BACKTICK',
    'DOLLAR',
    'PLUS',
    'MINUS',
    'TIMES',
    'DIVIDE',
    'MOD',
    'CONCAT',
    'EQUALS',
    'LT',
    'GT',
    'NOT',
    'AMP',
    'PIPE',
    'CARET',
    'TILDE',
]

# Qué token corresponde a cada conversión según la palabra que va entre los
# paréntesis. Igual que en PHP no importa si está en mayúsculas o minúsculas
CONVERSIONES = {
    'int': 'T_INT_CAST', 'integer': 'T_INT_CAST',
    'float': 'T_DOUBLE_CAST', 'double': 'T_DOUBLE_CAST',
    'string': 'T_STRING_CAST', 'binary': 'T_STRING_CAST',
    'bool': 'T_BOOL_CAST', 'boolean': 'T_BOOL_CAST',
    'array': 'T_ARRAY_CAST',
    'object': 'T_OBJECT_CAST',
}

# La lista completa es la de tokens básicos más las palabras reservadas
TOKENS_COMPLETOS = TOKENS_BASICOS + sorted(set(PALABRAS_RESERVADAS.values()))
