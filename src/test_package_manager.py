from graph import Graph


def read_file(path):
    with open(path, "r") as f:
        lines = [i.split() for i in f.readlines()]
    return lines[0][0], {i[0]: i[1:] for i in lines}


def build_graph(path: str, filter: str = "") -> Graph:
    print(filter)
    start, data = read_file(path)
    visited = {}
    stack = []
    duplicates = 0
    filtered = 0

    graph = Graph(start)
    visited[graph.name] = graph
    stack.extend([(i, graph) for i in data.get(graph.name)])
    while stack:
        current = stack.pop(0)
        if current[0] in visited:
            duplicates += 1
            continue
        if filter and filter in current[0]:
            filtered += 1
            continue

        print(
            f"Scanning package {current[0]}: found {len(visited)} items total")

        pkg = data.get(current[0])
        new_graph = Graph(current[0])
        visited[current[0]] = new_graph
        if t := data.get(current[0]):
            stack.extend((n, new_graph) for n in t)
        current[1].add_child(new_graph)

    print(f"{duplicates} duplicate dependencies found")
    print(f"{filtered} dependencies filtered out")
    return graph


if __name__ == "__main__":
    res = build_graph("../test-package/PackageA.txt")
    res.print_tree()
