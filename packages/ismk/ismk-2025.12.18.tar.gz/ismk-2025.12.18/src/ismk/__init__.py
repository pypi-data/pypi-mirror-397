__author__ = "Johannes Köster"
__copyright__ = "Copyright 2023, Johannes Köster"
__email__ = "johannes.koester@protonmail.com"
__license__ = "MIT"

import sys

from ismk._version import version as __version__

PIP_DEPLOYMENTS_PATH = ".ismk/pip-deployments"

sys.path.append(PIP_DEPLOYMENTS_PATH)

# Reexports that are part of the public API:
from ismk.shell import shell


if __name__ == "__main__":
    from ismk.cli import main
    import sys

    main(sys.argv)
