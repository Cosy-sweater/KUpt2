import sys

from config import parse_arguments
from package_manager import get_dependencies
from test_package_manager import build_graph

config = parse_arguments(sys.argv[1:])
if config is None:
    exit(1)

if config["test_mode"]:
    res = build_graph(config["path"], config["filter"])
else:
    res = get_dependencies(config["path"], config["filter"])
res.print_tree()
