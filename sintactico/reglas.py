"""
Gramática del analizador sintáctico

Hecho por Alejandro Osorio Osorio y Maria Paula Ruiz.

Gramática de una parte de PHP escrita con el yacc de PLY. Solo revisa la
sintaxis y no construye nada, por eso todas las reglas terminan en pass.

El archivo empieza con la precedencia de operadores y sigue con el programa
y las sentencias, las declaraciones de funciones, clases, interfaces y
traits, las expresiones, las listas auxiliares y al final el manejo de
errores.

No están la sintaxis alterna con endif o endwhile, enum, goto, yield, global
ni static dentro de funciones.
"""

from lexico.config import TOKENS_COMPLETOS
from sintactico.excepciones import contexto, crear_error, FALTA_PUNTO_Y_COMA

tokens = TOKENS_COMPLETOS
start = 'programa'


# ----- Precedencia, de menor a mayor como en PHP 8 -----
precedence = (
    ('nonassoc', 'T_DOUBLE_ARROW'),          # cuerpo de una función flecha
    ('nonassoc', 'SIN_ELSE'),                # if sin else, resuelve el else colgante
    ('nonassoc', 'T_ELSE', 'T_ELSEIF'),
    ('left', 'T_LOGICAL_OR'),
    ('left', 'T_LOGICAL_XOR'),
    ('left', 'T_LOGICAL_AND'),
    ('right', 'T_PRINT', 'T_INCLUDE', 'T_INCLUDE_ONCE', 'T_REQUIRE', 'T_REQUIRE_ONCE'),
    ('right', 'EQUALS', 'T_PLUS_EQUAL', 'T_MINUS_EQUAL', 'T_MUL_EQUAL',
     'T_DIV_EQUAL', 'T_CONCAT_EQUAL', 'T_MOD_EQUAL', 'T_POW_EQUAL',
     'T_AND_EQUAL', 'T_OR_EQUAL', 'T_XOR_EQUAL', 'T_SL_EQUAL', 'T_SR_EQUAL',
     'T_COALESCE_EQUAL'),
    ('left', 'QUESTION', 'COLON'),
    ('right', 'T_COALESCE'),
    ('left', 'T_BOOLEAN_OR'),
    ('left', 'T_BOOLEAN_AND'),
    ('left', 'PIPE'),
    ('left', 'CARET'),
    ('left', 'AMP'),
    ('nonassoc', 'T_IS_EQUAL', 'T_IS_NOT_EQUAL', 'T_IS_IDENTICAL',
     'T_IS_NOT_IDENTICAL', 'T_SPACESHIP'),
    ('nonassoc', 'LT', 'T_IS_SMALLER_OR_EQUAL', 'GT', 'T_IS_GREATER_OR_EQUAL'),
    ('left', 'CONCAT'),
    ('left', 'T_SL', 'T_SR'),
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIVIDE', 'MOD'),
    ('right', 'NOT'),
    ('nonassoc', 'T_INSTANCEOF'),
    ('right', 'UNARIO'),                     # signos que van delante de una expresión
    ('right', 'T_POW'),
    ('right', 'T_NEW', 'T_CLONE'),
)


# ----- Programa y sentencias -----

def p_programa(p):
    'programa : lista_sentencias'
    pass


def p_lista_sentencias(p):
    '''lista_sentencias : lista_sentencias sentencia
                        | empty'''
    pass


def p_lista_sentencias_error(p):
    '''lista_sentencias : lista_sentencias error SEMI
                        | lista_sentencias error bloque'''
    pass    # se descarta lo que está mal hasta el siguiente punto y coma o bloque


def p_bloque(p):
    'bloque : LBRACE lista_sentencias RBRACE'
    pass


def p_bloque_error(p):
    'bloque : LBRACE lista_sentencias error RBRACE'
    pass    # se descarta lo que está mal hasta el cierre del bloque


def p_sentencia_simple(p):
    '''sentencia : bloque
                 | expresion SEMI
                 | SEMI
                 | T_INLINE_HTML
                 | T_ECHO lista_expresiones SEMI
                 | T_UNSET LPAREN lista_variables RPAREN SEMI
                 | T_RETURN SEMI
                 | T_RETURN expresion SEMI
                 | T_BREAK SEMI
                 | T_BREAK T_LNUMBER SEMI
                 | T_CONTINUE SEMI
                 | T_CONTINUE T_LNUMBER SEMI
                 | T_THROW expresion SEMI
                 | T_DECLARE LPAREN T_STRING EQUALS expresion RPAREN SEMI
                 | declaracion
                 | lista_atributos declaracion'''
    pass


def p_sentencia_if(p):
    '''sentencia : T_IF LPAREN expresion RPAREN sentencia %prec SIN_ELSE
                 | T_IF LPAREN expresion RPAREN sentencia parte_else'''
    pass


def p_parte_else(p):
    '''parte_else : T_ELSE sentencia
                  | T_ELSEIF LPAREN expresion RPAREN sentencia %prec SIN_ELSE
                  | T_ELSEIF LPAREN expresion RPAREN sentencia parte_else'''
    pass


def p_sentencia_bucles(p):
    '''sentencia : T_WHILE LPAREN expresion RPAREN sentencia
                 | T_DO sentencia T_WHILE LPAREN expresion RPAREN SEMI
                 | T_FOR LPAREN expresiones_opt SEMI expresiones_opt SEMI expresiones_opt RPAREN sentencia
                 | T_FOREACH LPAREN expresion T_AS destino_foreach RPAREN sentencia'''
    pass


def p_lista_variables(p):
    '''lista_variables : lista_variables COMMA variable
                       | variable'''
    pass


def p_destino_foreach(p):
    '''destino_foreach : variable
                       | AMP variable
                       | arreglo
                       | variable T_DOUBLE_ARROW variable
                       | variable T_DOUBLE_ARROW AMP variable
                       | variable T_DOUBLE_ARROW arreglo'''
    pass


def p_sentencia_switch(p):
    'sentencia : T_SWITCH LPAREN expresion RPAREN LBRACE lista_casos RBRACE'
    pass


def p_sentencia_switch_error(p):
    'sentencia : T_SWITCH LPAREN expresion RPAREN LBRACE lista_casos error RBRACE'
    pass


def p_lista_casos(p):
    '''lista_casos : lista_casos caso
                   | empty'''
    pass


def p_caso(p):
    '''caso : T_CASE expresion COLON lista_sentencias
            | T_DEFAULT COLON lista_sentencias'''
    pass


def p_sentencia_try(p):
    '''sentencia : T_TRY bloque lista_catch
                 | T_TRY bloque lista_catch T_FINALLY bloque
                 | T_TRY bloque T_FINALLY bloque'''
    pass


def p_lista_catch(p):
    '''lista_catch : lista_catch catch
                   | catch'''
    pass


def p_catch(p):
    'catch : T_CATCH LPAREN tipos_catch variable_catch RPAREN bloque'
    pass


def p_tipos_catch(p):
    '''tipos_catch : tipos_catch PIPE nombre
                   | nombre'''
    pass


def p_variable_catch(p):
    '''variable_catch : T_VARIABLE
                      | empty'''
    pass


# ----- Declaraciones -----

def p_declaracion(p):
    '''declaracion : funcion
                   | clase
                   | interface
                   | trait
                   | constante
                   | T_NAMESPACE nombre_relativo SEMI
                   | T_USE lista_usos SEMI'''
    pass


def p_lista_usos(p):
    '''lista_usos : lista_usos COMMA uso
                  | uso'''
    pass


def p_uso(p):
    '''uso : nombre
           | nombre T_AS T_STRING'''
    pass


def p_lista_atributos(p):
    '''lista_atributos : lista_atributos atributo
                       | atributo'''
    pass


def p_atributo(p):
    'atributo : T_ATTRIBUTE lista_items_atributo RBRACKET'
    pass


def p_lista_items_atributo(p):
    '''lista_items_atributo : lista_items_atributo COMMA item_atributo
                            | item_atributo'''
    pass


def p_item_atributo(p):
    '''item_atributo : nombre
                     | nombre LPAREN argumentos RPAREN'''
    pass    # solo un nombre o un nombre con argumentos, no cualquier expresión


def p_funcion(p):
    'funcion : T_FUNCTION T_STRING LPAREN parametros RPAREN retorno_opt bloque'
    pass


def p_clase(p):
    '''clase : T_CLASS T_STRING extiende_opt implementa_opt cuerpo_miembros
             | modificadores_clase T_CLASS T_STRING extiende_opt implementa_opt cuerpo_miembros'''
    pass


def p_interface(p):
    'interface : T_INTERFACE T_STRING extiende_lista_opt cuerpo_miembros'
    pass


def p_trait(p):
    'trait : T_TRAIT T_STRING cuerpo_miembros'
    pass


def p_cuerpo_miembros(p):
    '''cuerpo_miembros : LBRACE lista_miembros RBRACE
                       | LBRACE lista_miembros error RBRACE'''
    pass    # se descarta lo que está mal hasta el cierre de la clase


def p_modificadores_clase(p):
    '''modificadores_clase : modificadores_clase modificador_clase
                           | modificador_clase'''
    pass


def p_modificador_clase(p):
    '''modificador_clase : T_ABSTRACT
                         | T_FINAL
                         | T_READONLY'''
    pass


def p_extiende_opt(p):
    '''extiende_opt : T_EXTENDS nombre
                    | empty'''
    pass


def p_extiende_lista_opt(p):
    '''extiende_lista_opt : T_EXTENDS lista_nombres
                          | empty'''
    pass


def p_implementa_opt(p):
    '''implementa_opt : T_IMPLEMENTS lista_nombres
                      | empty'''
    pass


def p_lista_nombres(p):
    '''lista_nombres : lista_nombres COMMA nombre
                     | nombre'''
    pass


def p_lista_miembros(p):
    '''lista_miembros : lista_miembros miembro
                      | empty'''
    pass


def p_lista_miembros_error(p):
    '''lista_miembros : lista_miembros error SEMI
                      | lista_miembros error bloque'''
    pass


def p_miembro(p):
    '''miembro : miembro_base
               | lista_atributos miembro_base'''
    pass


def p_miembro_base(p):
    '''miembro_base : T_USE lista_nombres SEMI
                    | constante_o_metodo
                    | modificadores_miembro resto_miembro'''
    pass


def p_resto_miembro(p):
    '''resto_miembro : tipo_opt T_VARIABLE inicial_opt SEMI
                     | constante_o_metodo'''
    pass


def p_constante_o_metodo(p):
    '''constante_o_metodo : constante
                          | T_FUNCTION T_STRING LPAREN parametros RPAREN retorno_opt cuerpo_metodo'''
    pass


def p_constante(p):
    'constante : T_CONST T_STRING EQUALS expresion SEMI'
    pass


def p_cuerpo_metodo(p):
    '''cuerpo_metodo : bloque
                     | SEMI'''
    pass


def p_modificadores_miembro(p):
    '''modificadores_miembro : modificadores_miembro modificador_miembro
                             | modificador_miembro'''
    pass


def p_modificador_miembro(p):
    '''modificador_miembro : T_PUBLIC
                           | T_PRIVATE
                           | T_PROTECTED
                           | T_STATIC
                           | T_ABSTRACT
                           | T_FINAL
                           | T_READONLY
                           | T_VAR'''
    pass


# ----- Expresiones -----

def p_expresion_simple(p):
    '''expresion : T_LNUMBER
                 | T_DNUMBER
                 | T_CONSTANT_ENCAPSED_STRING
                 | T_HEREDOC
                 | T_NOWDOC
                 | T_TRUE
                 | T_FALSE
                 | T_NULL
                 | arreglo
                 | nombre
                 | variable'''
    pass


def p_expresion_binaria(p):
    '''expresion : expresion T_LOGICAL_OR expresion
                 | expresion T_LOGICAL_XOR expresion
                 | expresion T_LOGICAL_AND expresion
                 | expresion T_COALESCE expresion
                 | expresion T_BOOLEAN_OR expresion
                 | expresion T_BOOLEAN_AND expresion
                 | expresion PIPE expresion
                 | expresion CARET expresion
                 | expresion AMP expresion
                 | expresion T_IS_EQUAL expresion
                 | expresion T_IS_NOT_EQUAL expresion
                 | expresion T_IS_IDENTICAL expresion
                 | expresion T_IS_NOT_IDENTICAL expresion
                 | expresion T_SPACESHIP expresion
                 | expresion LT expresion
                 | expresion T_IS_SMALLER_OR_EQUAL expresion
                 | expresion GT expresion
                 | expresion T_IS_GREATER_OR_EQUAL expresion
                 | expresion CONCAT expresion
                 | expresion T_SL expresion
                 | expresion T_SR expresion
                 | expresion PLUS expresion
                 | expresion MINUS expresion
                 | expresion TIMES expresion
                 | expresion DIVIDE expresion
                 | expresion MOD expresion
                 | expresion T_POW expresion'''
    pass


def p_expresion_asignacion(p):
    '''expresion : variable EQUALS expresion
                 | variable EQUALS AMP variable
                 | arreglo EQUALS expresion
                 | T_LIST LPAREN items RPAREN EQUALS expresion
                 | variable T_PLUS_EQUAL expresion
                 | variable T_MINUS_EQUAL expresion
                 | variable T_MUL_EQUAL expresion
                 | variable T_DIV_EQUAL expresion
                 | variable T_CONCAT_EQUAL expresion
                 | variable T_MOD_EQUAL expresion
                 | variable T_POW_EQUAL expresion
                 | variable T_AND_EQUAL expresion
                 | variable T_OR_EQUAL expresion
                 | variable T_XOR_EQUAL expresion
                 | variable T_SL_EQUAL expresion
                 | variable T_SR_EQUAL expresion
                 | variable T_COALESCE_EQUAL expresion'''
    pass


def p_expresion_unaria(p):
    '''expresion : NOT expresion
                 | MINUS expresion %prec UNARIO
                 | PLUS expresion %prec UNARIO
                 | TILDE expresion %prec UNARIO
                 | AT expresion %prec UNARIO
                 | T_INC variable
                 | T_DEC variable
                 | variable T_INC
                 | variable T_DEC
                 | T_CLONE expresion
                 | T_PRINT expresion
                 | T_INCLUDE expresion
                 | T_INCLUDE_ONCE expresion
                 | T_REQUIRE expresion
                 | T_REQUIRE_ONCE expresion
                 | T_INT_CAST expresion %prec UNARIO
                 | T_DOUBLE_CAST expresion %prec UNARIO
                 | T_STRING_CAST expresion %prec UNARIO
                 | T_BOOL_CAST expresion %prec UNARIO
                 | T_ARRAY_CAST expresion %prec UNARIO
                 | T_OBJECT_CAST expresion %prec UNARIO'''
    pass


def p_expresion_operadores_especiales(p):
    '''expresion : expresion T_INSTANCEOF nombre
                 | expresion QUESTION expresion COLON expresion
                 | expresion QUESTION COLON expresion
                 | T_NEW clase_ref LPAREN argumentos RPAREN
                 | T_NEW clase_ref'''
    pass


def p_expresion_construcciones(p):
    '''expresion : T_ISSET LPAREN lista_expresiones RPAREN
                 | T_EMPTY LPAREN expresion RPAREN
                 | T_EXIT
                 | T_EXIT LPAREN expresion_opt RPAREN'''
    pass


def p_expresion_funciones_anonimas(p):
    '''expresion : T_FUNCTION LPAREN parametros RPAREN usa_opt retorno_opt bloque
                 | T_FN LPAREN parametros RPAREN retorno_opt T_DOUBLE_ARROW expresion'''
    pass


def p_usa_opt(p):
    '''usa_opt : T_USE LPAREN lista_usa RPAREN
               | empty'''
    pass


def p_lista_usa(p):
    '''lista_usa : lista_usa COMMA uso_variable
                 | uso_variable'''
    pass


def p_uso_variable(p):
    '''uso_variable : T_VARIABLE
                    | AMP T_VARIABLE'''
    pass


def p_expresion_match(p):
    'expresion : T_MATCH LPAREN expresion RPAREN LBRACE brazos RBRACE'
    pass


def p_brazos(p):
    '''brazos : lista_brazos
              | lista_brazos COMMA
              | empty'''
    pass


def p_lista_brazos(p):
    '''lista_brazos : lista_brazos COMMA brazo
                    | brazo'''
    pass


def p_brazo(p):
    '''brazo : lista_expresiones T_DOUBLE_ARROW expresion
             | T_DEFAULT T_DOUBLE_ARROW expresion'''
    pass


def p_variable(p):
    '''variable : T_VARIABLE
                | DOLLAR T_VARIABLE
                | DOLLAR LBRACE expresion RBRACE
                | derreferenciable LBRACKET expresion RBRACKET
                | derreferenciable LBRACKET RBRACKET
                | derreferenciable T_OBJECT_OPERATOR T_STRING
                | derreferenciable T_NULLSAFE_OBJECT_OPERATOR T_STRING
                | derreferenciable T_OBJECT_OPERATOR T_STRING LPAREN argumentos RPAREN
                | derreferenciable T_NULLSAFE_OBJECT_OPERATOR T_STRING LPAREN argumentos RPAREN
                | T_VARIABLE LPAREN argumentos RPAREN
                | nombre LPAREN argumentos RPAREN
                | clase_ref T_DOUBLE_COLON T_VARIABLE
                | clase_ref T_DOUBLE_COLON T_STRING
                | clase_ref T_DOUBLE_COLON T_CLASS
                | clase_ref T_DOUBLE_COLON T_STRING LPAREN argumentos RPAREN'''
    pass


def p_clase_ref(p):
    '''clase_ref : nombre
                 | T_STATIC'''
    pass    # lo que va antes de :: o después de new, un nombre o static


def p_derreferenciable(p):
    '''derreferenciable : variable
                        | LPAREN expresion RPAREN'''
    pass    # admite [] y -> pero no se le puede asignar nada, así que (1) = 2 falla


def p_expresion_parentesis(p):
    'expresion : LPAREN expresion RPAREN'
    pass


def p_nombre_relativo(p):
    '''nombre_relativo : T_STRING
                       | nombre_relativo T_NS_SEPARATOR T_STRING'''
    pass    # un namespace no puede empezar con el separador \


def p_nombre(p):
    '''nombre : T_STRING
              | T_NS_SEPARATOR T_STRING
              | nombre T_NS_SEPARATOR T_STRING'''
    pass


# ----- Listas auxiliares -----

def p_lista_expresiones(p):
    '''lista_expresiones : lista_expresiones COMMA expresion
                         | expresion'''
    pass


def p_expresiones_opt(p):
    '''expresiones_opt : lista_expresiones
                       | empty'''
    pass


def p_expresion_opt(p):
    '''expresion_opt : expresion
                     | empty'''
    pass


def p_argumentos(p):
    '''argumentos : lista_argumentos
                  | lista_argumentos COMMA
                  | empty'''
    pass


def p_lista_argumentos(p):
    '''lista_argumentos : lista_argumentos COMMA argumento
                        | argumento'''
    pass


def p_argumento(p):
    '''argumento : expresion
                 | T_ELLIPSIS expresion'''
    pass


def p_arreglo(p):
    '''arreglo : LBRACKET items RBRACKET
               | T_ARRAY LPAREN items RPAREN'''
    pass


def p_items(p):
    '''items : items COMMA item_opt
             | item_opt'''
    pass    # acepta huecos como en [, $b] = $c y, como en PHP,
            # un arreglo como [1, , 2] se rechaza después y no aquí


def p_item_opt(p):
    '''item_opt : item
                | empty'''
    pass


def p_item(p):
    '''item : expresion
            | expresion T_DOUBLE_ARROW expresion
            | T_ELLIPSIS expresion'''
    pass


def p_parametros(p):
    '''parametros : lista_parametros
                  | lista_parametros COMMA
                  | empty'''
    pass


def p_lista_parametros(p):
    '''lista_parametros : lista_parametros COMMA parametro
                        | parametro'''
    pass


def p_parametro(p):
    'parametro : modificadores_param_opt tipo_opt ref_opt variadico_opt T_VARIABLE inicial_opt'
    pass


def p_modificadores_param_opt(p):
    '''modificadores_param_opt : modificadores_param
                               | empty'''
    pass


def p_modificadores_param(p):
    '''modificadores_param : modificadores_param modificador_param
                           | modificador_param'''
    pass


def p_modificador_param(p):
    '''modificador_param : T_PUBLIC
                         | T_PRIVATE
                         | T_PROTECTED
                         | T_READONLY'''
    pass


def p_ref_opt(p):
    '''ref_opt : AMP
               | empty'''
    pass


def p_variadico_opt(p):
    '''variadico_opt : T_ELLIPSIS
                     | empty'''
    pass


def p_inicial_opt(p):
    '''inicial_opt : EQUALS expresion
                   | empty'''
    pass


def p_retorno_opt(p):
    '''retorno_opt : COLON tipo
                   | COLON T_STATIC
                   | COLON QUESTION T_STATIC
                   | empty'''
    pass


def p_tipo_opt(p):
    '''tipo_opt : tipo
                | empty'''
    pass


def p_tipo(p):
    '''tipo : tipo_base
            | QUESTION tipo_base
            | tipo PIPE tipo_base'''
    pass


def p_tipo_base(p):
    '''tipo_base : nombre
                 | T_NULL
                 | T_FALSE
                 | T_TRUE
                 | T_ARRAY
                 | T_CALLABLE'''
    pass


def p_empty(p):
    'empty :'
    pass


# ----- Manejo de errores -----

def p_error(p):
    """
    PLY la llama cuando el parser recibe un token que no puede aceptar. Si p
    es None el archivo se terminó antes de tiempo.

    Guarda el error y se recupera para seguir y poder reportar varios errores
    en la misma corrida. Si faltaba un punto y coma lo mete y continúa. Para
    los demás errores están las reglas que usan el símbolo especial error en
    las listas de sentencias y de miembros, en los bloques y en el switch. Con
    ellas el parser abandona lo que estaba armando y descarta tokens hasta un
    punto y coma o una llave.
    """
    if (p is not None and p.type == 'error') or contexto.parser.symstack[-1].type == 'error':
        return          # ya hay una recuperación en curso y su error ya se reportó
    if p is None and contexto.fin_cortado:
        return          # un error léxico se comió el final y ese error ya se reportó

    error = crear_error(p, contexto)
    contexto.errores.append(error)

    if error.tipo == FALTA_PUNTO_Y_COMA:
        # Se mete el punto y coma que faltaba y el parser sigue desde el
        # token que falló, así no se pierde código
        contexto.parser.errok()
        return contexto.flujo.insertar_punto_y_coma(p)
