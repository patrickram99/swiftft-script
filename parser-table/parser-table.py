from os import sysconf
from typing_extensions import Iterator


def read_file(grammar):
  file = open(grammar, 'r')
  content = file.read()
  file.closed

  return content

def is_nullable(grammar):
  nullable = set()
  fixpoint = False

  while not fixpoint:
    fixpoint = True
    for rule in grammar['rules']:
      if all(symbol in nullable for symbol in rule['rhs']):
        if rule['ls'] not in nullable:
          nullable.add(rule['ls'])
          fixpoint = False
  return nullable

def compute_first(grammar, nullabe):
  pass

def compute_follow(grammar, nullable, first):
  pass

def create_table(grammar):
  nullabe = is_nullable(grammar)
  first = compute_first(grammar, nullabe)
  follow = compute_follow(grammar, nullabe, first)
  
  



def create_grammar() :
  false_start = 'S'
  NULL = "''" 
  SENTINEL = '$'
  rules = []
  non_terminals = set(false_start)

  for rule in read_file('grammar.txt').splitlines():
    split_symbol = '->'
    split_rule = rule.split(split_symbol)
    
    if len(split_rule) == 2:
      ls = split_rule[0].strip()
      rs = split_rule[1].strip().split()
      rs = list(filter(lambda x: x != NULL, rs))
      
      rules.append({"ls": ls, "rs": rs})
      non_terminals.add(ls)

    else:
      print('Gramatica no valida')
  
  terminals = set(SENTINEL)

  for r in rules:
    for symbol in r['rs']:
      if symbol not in terminals:
        terminals.add(symbol)

  start = rules[0]['ls']

  rules.append({"ls": false_start, "rs": [start, SENTINEL]})
  
  grammar = {
    "rules": rules,
    "terminals": terminals,
    "nonterminals": non_terminals,
    "start": start,
  }

  create_table(grammar)
  save_table()


def main():
  create_grammar()

if __name__ == "__main__":
  main()
