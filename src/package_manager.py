import json
import gzip
import urllib
import urllib.request as rs

def get_json(url):
    rq = urllib.request.Request(url, headers={"Accept": "application/json", "Accept-Encoding": "gzip"})
    with rs.urlopen(rq) as resp:
        data = resp.read()
        if "gzip" in resp.headers.get("Content-Encoding", "").lower():
            data = gzip.decompress(data)
        return json.loads(data)


def get_version(package: str, filter: str | None = None):
    api_url = "https://api.nuget.org/v3-flatcontainer/"
    url = f"{api_url}{package.lower()}/index.json"
    versions = [i for i in get_json(url)["versions"]]

    return versions[-1]


def get_package(url: str):
    two = 2
    api_url = "https://api.nuget.org/v3/registration5-gz-semver2/"
    path = urllib.parse.urlparse(url).path.strip("/").split("/")
    if len(path) < two and path[0] != "packages":
        return None

    version = path[2] if len(path) > two else get_version(path[1])
    data = get_json(get_json(f"{api_url}{path[1].lower()}/{version.lower()}.json")["catalogEntry"])
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


if __name__ == "__main__":
    print(get_package("https://www.nuget.org/packages/Azure.Identity"))
