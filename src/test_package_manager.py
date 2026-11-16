from graph import Graph


def parse_pkg_token(token: str) -> tuple[str, str]:
    if "/" in token:
        name, version = token.split("/", 1)
        return name, version
    return token, "latest"


def read_file(path: str):
    catalog = {}
    start_pkg = None

    with open(path, "r") as f:
        for line in f:
            parts = line.split()
            if not parts:
                continue

            pkg_name, pkg_ver = parse_pkg_token(parts[0])
            if start_pkg is None:
                start_pkg = (pkg_name, pkg_ver)

            deps = []
            for dep_token in parts[1:]:
                dep_name, dep_ver = parse_pkg_token(dep_token)
                deps.append({"name": dep_name, "version": dep_ver})

            catalog[(pkg_name.lower(), pkg_ver.lower())] = {
                "name": pkg_name,
                "version": pkg_ver,
                "dependencies": deps
            }

    return start_pkg, catalog


def get_package(catalog: dict, name: str, version: str) -> dict | None:
    return catalog.get((name.lower(), version.lower()))


def get_dependencies(path: str, filter: str = "") -> Graph | None:
    start_pkg, catalog = read_file(path)
    visited, stack, duplicates, filtered, missing = {}, [], 0, 0, 0
    root_name, root_ver = start_pkg
    pkg = get_package(catalog, root_name, root_ver)
    graph = Graph(pkg["name"], pkg["version"])
    visited[(pkg["name"].lower(), pkg["version"].lower())] = graph
    stack.extend(
        (n["name"], graph, n["version"])
        for n in pkg["dependencies"] if n["name"]
    )
    while stack:
        dep_name, parent_graph, dep_ver = stack.pop(0)
        dep_key = (dep_name.lower(), dep_ver.lower())
        if dep_key in visited:
            duplicates += 1
            continue
        if filter and filter in dep_name:
            filtered += 1
            continue
        pkg = get_package(catalog, dep_name, dep_ver)
        if pkg is None:
            missing += 1
            print(f"Package {dep_name} [{dep_ver}] not found")
            new_graph = Graph(dep_name, dep_ver)
            visited[dep_key] = new_graph
            parent_graph.add_child(new_graph)
            continue
        print(
            f"Scanning package {pkg['name']} [{pkg['version']}]: "
            f"found {len(visited)} items total"
        )
        new_graph = Graph(pkg["name"], pkg["version"])
        visited[dep_key] = new_graph
        stack.extend(
            (n["name"], new_graph, n["version"])
            for n in pkg["dependencies"] if n["name"]
        )
        parent_graph.add_child(new_graph)
    print_info(duplicates, filtered, missing)
    return graph


def print_info(duplicates, filtered, missing):
    print(f"\n{duplicates} duplicate dependencies found")
    print(f"{filtered} dependencies filtered out")
    print(f"{missing} nonexistent dependencies encountered")


if __name__ == "__main__":
    res = get_dependencies("../test-package/PackageA.txt")
    if res:
        res.print_tree()
