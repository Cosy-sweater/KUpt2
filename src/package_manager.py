import json
import gzip
import urllib.parse
import urllib.error
import urllib.request as rs

from graph import Graph


def get_json(url):
    rq = urllib.request.Request(
        url.strip(),
        headers={"Accept": "application/json", "Accept-Encoding": "gzip"}
    )
    retries = 5
    for i in range(retries):
        try:
            with rs.urlopen(rq, timeout=5) as resp:
                data = resp.read()
                if "gzip" in resp.headers.get("Content-Encoding", "").lower():
                    data = gzip.decompress(data)
                return json.loads(data)
        except (urllib.error.URLError, TimeoutError):
            print(
                f"An error occurred while trying to scan {url}. "
                f"Retrying {i + 1}/{retries}"
            )
            continue

    print(f"Unable to scan package {url}. Exiting")
    return None


def get_version(package: str, filter: str | None = None) -> str:
    api_url = "https://api.nuget.org/v3-flatcontainer/"
    url = f"{api_url}{package.lower()}/index.json"
    versions = [i for i in get_json(url)["versions"]]
    return versions[-1]


def format_version(package: str, version_range: str | None = None) -> str:
    if version_range:
        return version_range.split(",")[0].lstrip("[(").strip()
    return get_version(package)


def get_package(pth: str, version: str | None = None,
                skip_url_check: bool = False):
    two = 2
    api_url = "https://api.nuget.org/v3/registration5-gz-semver2/"

    if not skip_url_check:
        path = urllib.parse.urlparse(pth).path.strip("/").split("/")
        if len(path) < two and path[0] != "packages":
            return None
        pkg_name = path[1]
        resolved_ver = path[two] if len(path) > two else get_version(pkg_name)
    else:
        pkg_name = pth
        resolved_ver = format_version(pkg_name, version)

    catalog_url = f"{api_url}{pkg_name.lower()}/{resolved_ver.lower()}.json"
    initial_data = get_json(catalog_url)["catalogEntry"]

    data = get_json(initial_data)
    res = {
        "name": data["id"],
        "version": data["version"],
        "dependencies": []
    }
    for group in data.get("dependencyGroups", []):
        for dependency in group.get("dependencies", []):
            res["dependencies"].append({
                "name": dependency["id"],
                "version": dependency.get("range"),
                "targetFramework": group.get("targetFramework")
            })

    return res


def get_dependencies(url: str, filter: str = "") -> Graph:
    visited = {}
    stack = []
    duplicates = 0
    filtered = 0

    pkg = get_package(url)
    graph = Graph(pkg["name"], pkg["version"])

    visited[(pkg["name"].lower(), pkg["version"].lower())] = graph
    stack.extend(
        (n["name"], graph, n["version"])
        for n in pkg["dependencies"] if n["name"]
    )

    while stack:
        name, parent_graph, version = stack.pop(0)

        if filter and filter in name:
            filtered += 1
            continue

        resolved_ver = format_version(name, version)
        sign = (name.lower(), resolved_ver.lower())

        if sign in visited:
            duplicates += 1
            continue

        pkg = get_package(name, resolved_ver, skip_url_check=True)
        print(
            f"Scanning package {pkg['name']} [{pkg['version']}]: "
            f"found {len(visited)} items total"
        )
        new_graph = Graph(pkg["name"], pkg["version"])

        visited[sign] = new_graph
        visited[(pkg["name"].lower(), pkg["version"].lower())] = new_graph

        stack.extend(
            (n["name"], new_graph, n["version"])
            for n in pkg["dependencies"] if n["name"]
        )

        parent_graph.add_child(new_graph)

    print(f"{duplicates} duplicate dependencies found")
    print(f"{filtered} dependencies filtered out")
    return graph


if __name__ == "__main__":
    get_dependencies("https://www.nuget.org/packages/AWSSDK.Core")