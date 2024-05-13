import pandas as pd
from graphviz import Digraph

def string_of_set_map(input_map, indent, grammar):
    output = ""
    for key, value in input_map.items():
        if key in grammar["nonterminals"]:
            output += " " * indent + f"{key}: {value}\n"
    return output

def read_file(grammar):
    with open(grammar, "r") as file:
        content = file.read()
    return content

def create_grammar(txt):
    false_start = "S"
    NULL = "nulo"
    SENTINEL = "$"
    rules = []
    non_terminals = set([false_start])

    for rule in read_file(txt).splitlines():
        split_symbol = "->"
        split_rule = rule.split(split_symbol)

        if len(split_rule) == 2:
            ls = split_rule[0].strip()
            rs = split_rule[1].strip().split()
            rs = list(filter(lambda x: x != NULL, rs))

            rules.append({"ls": ls, "rs": rs})
            non_terminals.add(ls)

        else:
            print("Gramatica no valida")

    terminals = set([SENTINEL])

    for r in rules:
        for symbol in r["rs"]:
            if symbol not in non_terminals:
                terminals.add(symbol)

    start = rules[0]["ls"]

    rules.append({"ls": false_start, "rs": [start, SENTINEL]})

    for i in non_terminals:
        if i in terminals:
            terminals.remove(i)

    grammar = {
        "rules": rules,
        "terminals": terminals,
        "nonterminals": non_terminals,
        "start": start,
    }
    return grammar

def compute_nullable(grammar):
    print("Calculando nullable...")
    nullable = set()
    fixpoint = False
    iteration = 0
    while not fixpoint:
        fixpoint = True
        for rule in grammar["rules"]:
            rhs_nullable = all(x in nullable for x in rule["rs"])
            if rhs_nullable:
                if rule["ls"] not in nullable:
                    nullable.add(rule["ls"])
                    fixpoint = False
        iteration += 1
        print(f"  Tabla de Nullables @ iteracion {iteration}")
        print("    " + ", ".join(nullable))
    print("Finalizado nullable!")
    return nullable

def first_rhs(rhs, nullable, first):
    end = next((i for i, sym in enumerate(rhs) if sym not in nullable), len(rhs))
    return set().union(*[first[sym] for sym in rhs[:end]])

def compute_first(grammar, nullable):
    print("Calculando firsts...")
    first = {}

    for terminal in grammar["terminals"]:
        first[terminal] = {terminal}
    for nonterminal in grammar["nonterminals"]:
        first[nonterminal] = set()

    changed = True
    iteration = 0
    while changed:
        changed = False
        for rule in grammar["rules"]:
            old_first = set(first[rule["ls"]])
            for terminal in first_rhs(rule["rs"], nullable, first):
                first[rule["ls"]].add(terminal)
            if old_first != first[rule["ls"]]:
                changed = True
        iteration += 1
        print("  Tabla de primeros @ iteracion", iteration)
        for key, value in first.items():
            print(f"    {key} : {value}")
    print("Finalizado First")

    return first

def compute_follow(grammar, nullable, first):
    print("Calculando follow...")

    follow = {nonterminal: set() for nonterminal in grammar["nonterminals"]}
    follow[grammar["start"]].add("$")
    changed = True
    iteration = 0

    while changed:
        changed = False
        for rule in grammar["rules"]:
            follow_last = follow[rule["ls"]]
            for symbol in reversed(rule["rs"]):
                if symbol in grammar["nonterminals"]:
                    old_follow_set = follow[symbol].copy()
                    follow[symbol] |= follow_last
                    if old_follow_set != follow[symbol]:
                        changed = True
                if symbol in nullable:
                    follow_last = follow_last.union(first[symbol])
                else:
                    follow_last = first[symbol]
        print(f"  Tabla de Follow @ iteracion {iteration + 1}")
        print(string_of_set_map(follow, 2, grammar))
        iteration += 1

    print("Finalizado Follow!")
    return follow

def compute_LL1_tables(grammar):
    nullable = compute_nullable(grammar)
    first = compute_first(grammar, nullable)
    follow = compute_follow(grammar, nullable, first)

    transition = {}
    for nonterminal in grammar["nonterminals"]:
        transition[nonterminal] = {}
        for terminal in grammar["terminals"]:
            transition[nonterminal][terminal] = []

    for rule in grammar["rules"]:
        first_rhs_set = first_rhs(rule["rs"], nullable, first)
        for a in first_rhs_set:
            transition[rule["ls"]][a].append(rule)

        all_nullable = all(x in nullable for x in rule["rs"])
        if all_nullable:
            follow_lhs_set = follow[rule["ls"]]
            for a in follow_lhs_set:
                transition[rule["ls"]][a].append(rule)

    return transition

def print_LL1_table(transition):
    for nonterminal, row in transition.items():
        print(f"Transition for {nonterminal}:")
        for terminal, rules in row.items():
            rule_strings = []
            for rule in rules:
                if not rule["rs"]:
                    rule_str = rule["ls"] + " -> " + " nulo"
                else:
                    rule_str = rule["ls"] + " -> " + " ".join(rule["rs"])
                rule_strings.append(rule_str)
            print(f"  {terminal}: {', '.join(rule_strings)}")

def create_LL1_table(grammar, transition):
    nonterminals = list(grammar["nonterminals"])
    terminals = list(grammar["terminals"])
    table = pd.DataFrame(index=nonterminals, columns=terminals)
    for nonterminal, row in transition.items():
        for terminal, rules in row.items():
            rule_strings = []
            for rule in rules:
                if not rule["rs"]:
                    rule_str = "nulo"
                else:
                    rule_str = " ".join(rule["rs"])
                rule_strings.append(rule_str)
            table.at[nonterminal, terminal] = f"{', '.join(rule_strings)}"
    return table

def ll1_parser(expression, table):
    nodes = []

    elements = expression.strip().split(" ")
    elements.append("$")

    stack = ["S", "$"]
    rule_str = ""

    print("{:<25}{:<45}{:<10}".format("Stack", "Input", "Regla"))

    while len(elements) >= 1:
        nodes.append(rule_str)
        print(
            "{:<25}{:<45}{:<10}".format(
                " ".join(str(x) for x in stack),
                " ".join(str(x) for x in elements),
                rule_str,
            )
        )

        if stack[0] == elements[0]:
            rule_str = "match: " + stack[0]
            elements.pop(0)
            stack.pop(0)

        else:
            try:
                rule = table.loc[stack[0], elements[0]]
            except KeyError:
                print(f"Input invalido: No se encontró regla para {stack[0]} y {elements[0]}")
                return

            if pd.isna(rule):
                print(f"Regla no definida para {stack[0]} y {elements[0]}")
                return

            if rule == "nulo":
                rule_str = "match: " + stack[0] + " a nulo"
                stack.pop(0)
                continue

            rule_str = stack[0] + " -> " + rule

            stack.pop(0)
            for token in reversed(rule.split()):
                if token != "nulo":
                    stack.insert(0, token)

    print("Input aceptado")
    return nodes

class TreeNode:
    def __init__(self, value):
        self.value = value
        self.children = []

    def add_child(self, child_node):
        self.children.append(child_node)

    def __repr__(self):
        return f"TreeNode({self.value})"

    def __str__(self, level=0):
        ret = "\t" * level + repr(self.value) + "\n"
        for child in self.children:
            ret += child.__str__(level + 1)
        return ret

def generate_syntax_tree_structure(rules):
    current_nodes = {}
    node_counter = 1
    root = TreeNode("S")
    current_nodes["S"] = root

    for rule in rules:
        if "->" in rule:
            head, production = rule.split(" -> ")
            parts = production.split()

            if head not in current_nodes:
                head_node = TreeNode(head)
                current_nodes[head] = head_node
            else:
                head_node = current_nodes[head]

            for part in parts:
                if part not in current_nodes:
                    part_node = TreeNode(part)
                    current_nodes[part] = part_node
                else:
                    part_node = current_nodes[part]

                head_node.add_child(part_node)

        elif "match:" in rule:
            _, value = rule.split(": ")
            value = value.strip()

            if " a nulo" in value:
                non_terminal = value.replace(" a nulo", "")
                if non_terminal in current_nodes:
                    current_nodes[non_terminal].add_child(TreeNode("ε"))
            else:
                if value in current_nodes:
                    current_nodes[value].add_child(TreeNode(f"{value} (match)"))

    return root
from graphviz import Digraph

class TreeNode:
    def __init__(self, value):
        self.value = value
        self.children = []

    def add_child(self, child_node):
        self.children.append(child_node)

    def __repr__(self):
        return f"TreeNode({self.value})"

    def __str__(self, level=0):
        ret = "\t" * level + repr(self.value) + "\n"
        for child in self.children:
            ret += child.__str__(level + 1)
        return ret

def generate_syntax_tree_structure(rules):
    current_nodes = {}
    node_counter = 1
    root = TreeNode("S")
    current_nodes["S"] = root

    for rule in rules:
        if "->" in rule:
            head, production = rule.split(" -> ")
            parts = production.split()

            if head not in current_nodes:
                head_node = TreeNode(head)
                current_nodes[head] = head_node
            else:
                head_node = current_nodes[head]

            for part in parts:
                if part not in current_nodes:
                    part_node = TreeNode(part)
                    current_nodes[part] = part_node
                else:
                    part_node = current_nodes[part]

                head_node.add_child(part_node)

        elif "match:" in rule:
            _, value = rule.split(": ")
            value = value.strip()

            if " a nulo" in value:
                non_terminal = value.replace(" a nulo", "")
                if non_terminal in current_nodes:
                    current_nodes[non_terminal].add_child(TreeNode("ε"))
            else:
                if value in current_nodes:
                    current_nodes[value].add_child(TreeNode(f"{value} (match)"))

    return root

def generate_syntax_tree_graphviz(tree):
    dot = Digraph(format="png")
    node_counter = {"count": 0}

    def add_node(dot, node, parent=None):
        node_id = f"node{node_counter['count']}"
        node_counter["count"] += 1
        dot.node(node_id, node.value)

        if parent:
            dot.edge(parent, node_id)

        for child in node.children:
            add_node(dot, child, node_id)

    add_node(dot, tree)
    return dot

# Assuming "grammar_main.txt" contains the grammar rules
grammar = create_grammar("grammar_main.txt")
transition = compute_LL1_tables(grammar)
LL1_table = create_LL1_table(grammar, transition)
print(LL1_table)
print("\n\n\n")
input_expr = "enchanted identificador = identificador : meetYou"
nodes = ll1_parser(input_expr, LL1_table)
if nodes:
    nodes.pop(0)  # Remove the initial empty string

    syntax_tree = generate_syntax_tree_structure(nodes)
    print(syntax_tree)

    tree_graph = generate_syntax_tree_graphviz(syntax_tree)
    tree_graph.render("output_tree", view=True)
