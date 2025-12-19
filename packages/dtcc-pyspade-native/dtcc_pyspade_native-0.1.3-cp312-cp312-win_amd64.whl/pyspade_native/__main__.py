"""Command-line interface for dtcc-pyspade-native."""

import sys
from . import print_info

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] in ["-h", "--help"]:
        print("Usage: python -m pyspade_native")
        print("       Print installation information for dtcc-pyspade-native")
        sys.exit(0)

    print_info()