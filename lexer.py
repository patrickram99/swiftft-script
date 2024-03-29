# id 1 para ruff LSP
from ply import lex as lex
from ply import yacc

keywords = {
  'isme' : 'START_FUN',
  'hi' : 'RETURN',
  'imtheproblem' : 'END_FUN',

  'loverera' : 'IF',
  'redera' : 'ELSE_IF',
  'repera' : 'ELSE',
  
  'me' : 'FOR',
  'e' : 'TO_FOR',
  'ee' : 'BREAK_FOR',
  
  'ooh' : 'WHILE',
  'oohooh': 'BREAK_WHILE',


  'speaknow' : 'PRINT',

  'enchanted' : 'DECLARE_VAR',


  'thpage': 'FLOAT_TYPE',
  'twenty' : 'INT_TYPE',
  'meetyou' : 'BOOLEAN',

  'BadBlood' : 'FALSE',
  'SparksFly' : 'TRUE',

  'thpage' : 'FLOAT',
  'twenty' : 'INT',
  'wonderstruck' : 'STRING'


}


tokens = list(keywords.values()) + [
    'D_EQUAL','EQUALS', 'PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'POWER',
    'LPAREN', 'RPAREN', 'LT', 'LE', 'GT', 'GE', 'NE',
    'COMMA', 'SEMI', 'ID', 'NEWLINE', 'COLON', 'LB', 'RB'
]


# Expresiones regulares para operadores
t_D_EQUAL = r'=='
t_EQUALS = r'='

t_PLUS = r'\+'
t_MINUS = r'-'
t_TIMES = r'\*'
t_POWER = r'\^'
t_DIVIDE = r'/'

t_LPAREN = r'\('
t_RPAREN = r'\)'

t_LT = r'<'
t_LE = r'<='
t_GT = r'>'
t_GE = r'>='

t_LB = r'{'
t_RB = r'}'

t_NE = r'<>'
t_COMMA = r'\,'
t_SEMI = r';'
t_COLON = r'\:'

# Expresion regular para declarar variable
def t_DECLARE_VAR(t): r'enchanted'; return t

# Expresiones regulares para datos
def t_INT(t): r'\d+'; return t 
def t_FLOAT(t): r'((\d*\.\d+)(E[\+-]?\d+)?|([1-9]\d*E[\+-]?\d+))'; return t
def t_STRING(t): r'\".*?\"'; return t;


# Expresiones regulares para palabras reservadas con funciones
def t_START_FUN(t): r'isme'; return t
def t_RETURN(t): r'hi'; return t
def t_END_FUN(t): r'imtheproblem'; return t

# Expresiones regulares para imprimir en consola
def t_PRINT(t): r'speaknow'; return t

# Expresiones regulares para logica condicional
def t_IF(t): r'loverera'; return t
def t_ELSE(t): r'repera'; return t
def t_ELSE_IF(t): r'redera'; return t

# Expresiones regulares tipos de datos 
def t_FLOAT_TYPE(t): r'thpage'; return t
def t_INT_TYPE(t): r'twenty'; return t
def t_BOOLEAN(t): r'meetYou'; return t

# Expresiones regulares for loops
def t_FOR_LOOP(t): r'me'; return t
def t_TO_FOR(t): 
  r'e'
  t.type = keywords.get(t.value, 'TO_FOR')
  return t
def t_BREAK_FOR(t): r'ee'; return t

# Expresiones regulares while looops
def t_WHILE(t): r'me'; return t
def t_BREAK_WHILE(t): r'ee'; return t


def t_ID(t):
  r'[a-zA-Z_][a-zA-Z_0-9]*'
  t.type = keywords.get(t.value, 'ID')
  return t

def t_NEWLINE(t):
  r'\n'
  t.lexer.lineno += 1
  return t

def t_newline(t):
  r'\n+'
  t.lexer.lineno += len(t.value)

t_ignore = ' \t'

def t_error(t):
  print("Illegal character '%s'" % t.value[0])
  t.lexer.skip(1)

lexer = lex.lex()

def get_data(filename):
    with open(filename) as f:
        content = f.read()
    return content


def menu():
  print("Seleccione un numero \n 1. Hola mundo\n 2. Factorial recursivo\n 3. factorial iterativo")
  option = input()

  if option == "1":
    lexer.input(get_data("examples/hellow_world.txt"))
    print(get_data("examples/hellow_world.txt"))

  elif option == "2":
    lexer.input(get_data("examples/factorial_rec.txt"))
  else:
    lexer.input(get_data("examples/factorial_iter.txt"))
    
  for tok in lexer:
    print(tok.type, tok.value) # , tok.lineno, tok.lexpos)

menu()

