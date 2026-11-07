import urllib.request as rs


def get_package(url: str = "https://www.nuget.org/packages/Azure.Identity"):
    t = rs.urlopen(url)
    print(t.read())


if __name__ == "__main__":
    get_package("https://github.com/Azure/azure-sdk-for-net")
