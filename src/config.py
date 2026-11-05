def parse_arguments(tokens: list[str]) -> dict:
    """Функция обработки аргумента командной строки"""

    result = {"errors": [], "flags": [], "pos-args": []}
    token_count_num = 2

    for token in tokens:
        if "=" in token:
            if token.startswith("-") and not token.startswith("--"):
                result["error"] = "Присваивать флагам значения нельзя"
            key, value = token.split("=", 1)
            result[key] = value
        elif token.startswith("--"):
            result[token] = None
        elif token[0].isalpha():
            result["pos-args"].append(token)
        elif len(token) > token_count_num:
            for flag in token[1:]:
                result["flags"].append(flag)
        else:
            result[token] = None

    return _handle_arguments(result)


def _handle_arguments(args: dict) -> dict | None:
    if args["errors"]:
        print(*args["errors"], sep="\n")
        return None
    if not all(args.get(i) for i in ("--path", "--package")):
        print("Необходимо задать значения для --package и --path")
        return
    res = {
        "package":args.get("--package", ""),
        "path": args.get("--path", ""),
        "filter": args.get("--filter", ""),
        "test_mode": ("T" in args["flags"]),
        "tree_mode": ("a" in args["flags"])
    }
    return _test_config(res)


def _test_config(args: dict):
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
