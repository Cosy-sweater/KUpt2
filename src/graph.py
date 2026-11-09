class Graph:
    def __init__(self, name: str, dependencies: list["Graph"] | None = None):
        self.name = name
        self.dependencies = dependencies if dependencies else []

    def add_child(self, item: "Graph"):
        self.dependencies.append(item)

    def add_children(self, items: list["Graph"]):
        self.dependencies.extend(items)

    def __repr__(self):
        return f"{self.name}({self.dependencies})"

    def print_tree(self, depth=0):
        print("\n" + "  " * depth + self.name + "(", end="")
        for i in self.dependencies:
            i.print_tree(depth+2)
        print("  " * depth + ")")
