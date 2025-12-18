"""Entry point for module invocation via `python -m django_model_scanner`."""

import sys
from .main import main

if __name__ == "__main__":
    sys.exit(main())
