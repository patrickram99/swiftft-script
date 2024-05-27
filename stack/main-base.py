import pandas as pd
from graphviz import Digraph


def string_of_set_map(input_map, indent, grammar):
    output = ""
    for key, value in input_map.items():
        if key in grammar["nonterminals"]:
            output += " " * indent + f"{key}: {value}\n"
    return output


def read_file(grammar):
    file = open(grammar, "r")
    content = file.read()
    file.closed

    return content


def create_grammar(txt):
    false_start = "S"
    NULL = "nulo"
    SENTINEL = "$"
    rules = []
    non_terminals = set(false_start)

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

    terminals = set(SENTINEL)

    for r in rules:
        for symbol in r["rs"]:
            if symbol not in terminals:
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
            rhs_nullable = True
            for x in rule["rs"]:
                if x not in nullable:
                    rhs_nullable = False
                    break
            if rhs_nullable:
                if rule["ls"] not in nullable:
                    nullable.add(rule["ls"])
                    fixpoint = False
        iteration += 1
        print(f"  Tabla de Nullables @ iteracion {iteration}")
        print("    " + ", ".join(nullable))
    print("Fianlizado nullable!")
    return nullable


def first_rhs(rhs, nullable, first):
    end = next((i for i, sym in enumerate(rhs) if sym not in nullable), len(rhs))
    return set().union(*[first[sym] for sym in rhs[: end + 1]])


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
        print("  Tabla de primeros @ iteracionn", iteration)
        for key, value in first.items():
            print("    ", key, ":", value)
    print("Finalizado First")

    return first


def compute_follow(grammar, nullable, first):
    print("Computing follow...")

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
        print(f"  Follow table @ iteration {iteration + 1}")
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
            except:
                print("Input invalido")
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


def generate_syntax_tree(rules):
    dot = Digraph(format="jpg")

    current_nodes = {}
    node_counter = 1

    for rule in rules:
        if "->" in rule:
            head, production = rule.split(" -> ")
            parts = production.split()

            if head not in current_nodes:
                head_node = f"node{node_counter}"
                node_counter += 1
                current_nodes[head] = head_node
                dot.node(head_node, head)
            else:
                head_node = current_nodes[head]

            for part in parts:
                part_node = f"node{node_counter}"
                node_counter += 1
                dot.node(part_node, part)
                dot.edge(head_node, part_node)

                if part.isalpha() and not part.islower():
                    current_nodes[part] = part_node

        elif "match:" in rule:
            _, value = rule.split(": ")
            value = value.strip()

            if " a nulo" in value:
                non_terminal = value.replace(" a nulo", "")
                if non_terminal in current_nodes:
                    node_name = current_nodes[non_terminal]
                    null_node = f"node{node_counter}"
                    node_counter += 1
                    dot.node(null_node, "ε", shape="none")
                    dot.edge(node_name, null_node)
            else:
                # Regular match
                if value in current_nodes:
                    node_name = current_nodes[value]
                    dot.node(
                        node_name, f"{value} (match)", style="filled", color="lightgrey"
                    )

    return dot


def print_symbol_stack(stack):
    print("Symbol Table:")
    for symbol in stack:
        print(
            f"    nombre: {symbol['nombre']}, tipo: {symbol['tipo']}, valor: {symbol['valor']}"
        )
    print("\n")


def print_symbol_table(nodes):
    stack = []
    enchanted_detected = False
    var_name = None
    var_type = None
    var_value = None
    in_value_collection = False
    collected_value = []
    type_next = False

    for i in range(len(nodes)):
        rule = nodes[i]
        if "match: enchanted" in rule:
            enchanted_detected = True
            var_name = None
            var_type = None
            var_value = None
            collected_value = []
            in_value_collection = False
        elif enchanted_detected and "match: identificador" in rule:
            var_name = rule.split(": ")[1]
        elif enchanted_detected and "match: =" in rule:
            in_value_collection = True
        elif (
            in_value_collection
            and "match: nulo" not in rule
            and "match: :" not in rule
            and "match: " in rule
        ):
            if "nulo" not in rule.split(": ")[1]:
                collected_value.append(rule.split(": ")[1])
        elif in_value_collection and "match: :" in rule:
            var_value = " ".join(collected_value)
            type_next = True
            collected_value = []
            in_value_collection = False
            enchanted_detected = False

            print_symbol_stack(stack)
        elif type_next:
            var_type = nodes[i + 1].split(": ")[1]
            stack.append({"nombre": var_name, "tipo": var_type, "valor": var_value})
            type_next = False

            print_symbol_stack(stack)
        elif in_value_collection and "match: nulo" in rule:
            in_value_collection = False
            collected_value = []
        elif enchanted_detected and "match: :" in rule:
            type_next = True
            print_symbol_stack(stack)


grammar = create_grammar("grammar.txt")
transition = compute_LL1_tables(grammar)
LL1_table = create_LL1_table(grammar, transition)
print(LL1_table)
print("\n\n\n")
input = "enchanted identificador : thpage newLINE enchanted identificador = numeral : thpage "
# input = "enchanted identificador = SparksFly : meetYou newLINE loverera( identificador == BadBlood ) { speaknow(\" string \") } newLINE "
# input = "isme fun( identificador : thpage , identificador : twenty ) { speaknow(\" string \") } imtheproblem"
# input = read_file("input.txt")
nodes = ll1_parser(input, LL1_table)
print(nodes)
nodes.pop(0)

print_symbol_table(nodes)


tree = generate_syntax_tree(nodes)
tree.render("output_tree", view=True, format="png")
