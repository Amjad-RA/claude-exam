"""Rebuild every SVG diagram block in the site's pages.

    python3 tools/build_diagrams.py

See tools/dglib.py for how diagrams are described and placed.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import dglib  # noqa: E402
import dg_site, dg_ccao, dg_ccarf, dg_ccarp, dg_fsd  # noqa: E402,F401  (modules register their diagrams)

for page, did, anchor, mode, block in dglib.REGISTRY:
    dglib.inject(page, did, anchor, mode, block)

print(f"{len(dglib.REGISTRY)} diagram blocks written")
