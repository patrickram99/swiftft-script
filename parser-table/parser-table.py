import pandas as pd


def ll1_parser(expression, grammar_file_path):
    table = pd.read_csv(grammar_file_path, index_col=0)

    elements = expression.strip().split(" ")
    elements.append("$")

    stack = ["E", "$"]
    rule_str = ""

    print("{:<25}{:<45}{:<10}".format("Stack", "Input", "Regla"))

    while len(elements) >= 1:
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
            rule = table.loc[stack[0], elements[0]]
            if pd.isna(rule):
                print(f"Regla no definida para {stack[0]} y {elements[0]}")
                break

            if rule == "e":
                rule_str = "match: " + stack[0] + " a nulo"
                stack.pop(0)
                continue

            rule_str = stack[0] + " -> " + rule

            stack.pop(0)
            for token in reversed(rule.split()):
                if token != "e":
                    stack.insert(0, token)


def main():
    input = "int times int plus lpar int rpar"
    ll1_parser(input, "simple_grammar.csv")


if __name__ == "__main__":
    main()
