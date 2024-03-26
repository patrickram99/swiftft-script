# id 1 para ruff LSP
from ply import lex as lex
from ply import yacc

keywords = {
  'loverera' : 'IF',
  'redera' : 'ELSE_IF',
  'repera' : 'ELSE',
  
  'me' : 'FOR',
  'e' : 'TO_FOR',
  'ee' : 'BREAK_FOR',
  'speaknow' : 'PRINT',
}


tokens = list(keywords.values()) + [
    'EQUALS', 'PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'POWER',
    'LPAREN', 'RPAREN', 'LT', 'LE', 'GT', 'GE', 'NE',
    'COMMA', 'SEMI', 'thpage', 'FLOAT', 'wonderstruck',
    'ID', 'NEWLINE'
]


# Expresiones regulares para operadores
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
t_NE = r'<>'
t_COMMA = r'\,'
t_SEMI = r';'
t_FLOAT = r'((\d*\.\d+)(E[\+-]?\d+)?|([1-9]\d*E[\+-]?\d+))'
t_thpage = r'\d+'
t_wonderstruck = r'\".*?\"' 



# Expresiones regulares para palabras reservadas con funciones
def t_PRINT(t): r'speaknow'; return t



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

data = '''
A = speaknow(3) + 4 * 10.4
  + -20 *2
'''

lexer.input(data)

for tok in lexer:
  print(tok.type, tok.value) # , tok.lineno, tok.lexpos)

