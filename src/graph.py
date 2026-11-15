class Graph:
    def __init__(self, name: str, version: str = ""):
        self.name = name
        self.version = version
        self.dependencies = []

    def add_child(self, item: "Graph"):
        self.dependencies.append(item)

    def add_children(self, items: list["Graph"]):
        self.dependencies.extend(items)

    def __repr__(self):
        return f"{self.name}({self.dependencies})"

    def print_tree(self, depth=0):
        print("\n" + "  " * depth + self.name +
              (f" [{self.version}] " if self.version else "") + "(", end="")
        for i in self.dependencies:
            i.print_tree(depth+2)
        print("\n" + ("  " * depth) + ")" if self.dependencies else ")",
              end="")