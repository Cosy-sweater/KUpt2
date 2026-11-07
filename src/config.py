import os
import urllib
import urllib.request as rq


def parse_arguments(tokens: list[str]) -> dict | None:
    """Функция обработки аргумента командной строки"""

    result = {"errors": [], "flags": [], "pos-args": []}

    for token in tokens:
        if "=" in token:
            if token.startswith("-") and not token.startswith("--"):
                result["errors"].append("Присваивать флагам значения нельзя")
            key, value = token.split("=", 1)
            result[key] = value
        elif token.startswith("--"):
            result[token] = None
        elif token[0].isalpha():
            result["pos-args"].append(token)
        elif len(token) > 1:
            for flag in token[1:]:
                result["flags"].append(flag)
        else:
            print("err")

    return _handle_arguments(result)


def _handle_arguments(args: dict) -> dict | None:
    if args["errors"]:
        print(*args["errors"], sep="\n")
        return None
    if not all(args.get(i) for i in ("--path", "--package")):
        print("Необходимо задать значения для --package и --path")
        return
    res = {
        "package": args.get("--package", ""),
        "path": args.get("--path", ""),
        "filter": args.get("--filter", ""),
        "test_mode": ("T" in args["flags"]),
        "tree_mode": ("a" in args["flags"])
    }
    return _test_config(res)


def _test_config(args: dict) -> dict | None:
    if args["test_mode"]:
        if not os.path.exists(args["path"]):
            print("Invalid path")
            return None
    else:
        try:
            resp = rq.urlopen(args["path"])
        except urllib.error.URLError:
            print("Invalid URL")
            return None
        if not resp.code < 400:
            print("Invalid URL")
            return None

    return args


def _print_help():
    """Функция вывода подсказки"""
    print("""Аргументы программы:
Флаги:
    -T - раота с тестовым репозиторием
    -a - режим вывода зависимости в виде бинарного ASCII-дерева
Аргументы со значениями:
    --package - имя анализируемого пакета
    --path - URL-адрес репозитория или путь до тестового репозитория
    --filter - подстрока для фильтрации пакетов""")
