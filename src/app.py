import sys

from config import parse_arguments

config = parse_arguments(sys.argv[1:])
if config is None:
    exit(1)

print(*[f"{i}: {config[i]}" for i in config], sep="\n")
