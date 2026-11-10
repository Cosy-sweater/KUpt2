import json
import gzip
import urllib
import urllib.request as rs

from graph import Graph


def get_json(url):
    rq = urllib.request.Request(url.strip(), headers={"Accept": "application/json", "Accept-Encoding": "gzip"})
    fail = True
    retries = 5
    for i in range(retries):
        try:
            with rs.urlopen(rq, timeout=5) as resp:
                data = resp.read()
                if "gzip" in resp.headers.get("Content-Encoding", "").lower():
                    data = gzip.decompress(data)
                return json.loads(data)
        except urllib.error.URLError or TimeoutError:
            print(f"An error occured while trying to scan {url}. Retrying {i + 1}/{retries}")
            continue
    if fail:
        print(f"Unable to scan package {url}. Exiting")


def get_version(package: str, filter: str | None = None):
    api_url = "https://api.nuget.org/v3-flatcontainer/"
    url = f"{api_url}{package.lower()}/index.json"
    versions = [i for i in get_json(url)["versions"]]

    return versions[-1]


def get_package(pth: str, skip_url_check: bool = False):
    two = 2
    api_url = "https://api.nuget.org/v3/registration5-gz-semver2/"

    if not skip_url_check:
        path = urllib.parse.urlparse(pth).path.strip("/").split("/")
        if len(path) < two and path[0] != "packages":
            return None
        version = path[2] if len(path) > two else get_version(path[1])
        initial_data = get_json(f"{api_url}{path[1].lower()}/{version.lower()}.json")["catalogEntry"]
    else:
        path = pth
        version = get_version(path)
        initial_data = get_json(f"{api_url}{path.lower()}/{version.lower()}.json")["catalogEntry"]

    data = get_json(initial_data)
    res = {
        "name": data["id"],
        "version": data["version"],
        "dependencies": []
    }
    for group in data.get("dependencyGroups", []):
        for dependency in group.get("dependencies", []):
            res["dependencies"].append({"name": dependency["id"], "version": dependency.get("range"),
                                        "targetFramework": group.get("targetFramework")})

    return res


def get_dependencies(url: str, filter: str = "") -> Graph:
    visited = {}
    stack = []
    graph = None
    duplicates = 0
    filtered = 0

    pkg = get_package(url)
    graph = Graph(pkg["name"], pkg["version"])
    visited[pkg["name"]] = graph
    stack.extend((n["name"], graph, n["version"])
                 for n in pkg["dependencies"] if n["name"])

    while stack:
        current = stack.pop(0)
        if current[0] in visited:
            duplicates += 1
            continue
        if filter and filter in current[0]:
            filtered += 1
            continue

        pkg = get_package(current[0], skip_url_check=True)
        print(f"Scanning package {pkg["name"]} [{pkg["version"]}]: "
              f"found {len(visited)} items total")
        new_graph = Graph(pkg["name"], pkg["version"])
        visited[pkg["name"]] = new_graph
        stack.extend((n["name"], new_graph, n["version"])
                     for n in pkg["dependencies"])

        current[1].add_child(new_graph)

    print(f"{duplicates} duplicate dependencies found")
    print(f"{filtered} dependencies filtered out")
    return graph


if __name__ == "__main__":
    get_dependencies("https://www.nuget.org/packages/AWSSDK.Core")
