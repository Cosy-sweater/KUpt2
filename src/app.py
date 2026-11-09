import sys
import json

from config import parse_arguments
from package_manager import get_package

config = parse_arguments(sys.argv[1:])
if config is None:
    exit(1)

package = get_package(config["path"])
print(json.dumps(package, indent=4, sort_keys=True))
