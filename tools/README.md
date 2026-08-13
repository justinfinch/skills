# tools

Verification for the Arche's OKF v0.2 conformance. Not shipped in any skill —
`arche-lint` implements its own checks; these exist so lint can be verified
against something independent.

## Requirements

Python 3.12+ and PyYAML, both declared in the repo's `devbox.json`. Run
`devbox shell` (or let direnv load it on `cd`) and they are on `PATH`. Without
devbox, install PyYAML with `python3 -m pip install --user pyyaml`.

## Check a bundle

    devbox run check path/to/.arche          # or, inside a devbox shell:
    python3 tools/okf_conformance.py path/to/.arche

Exit code 0 when conformant, 1 when findings exist, 2 on usage or environment
error (bad arguments, missing PyYAML). A broken environment must never look
like a non-conformant bundle, so 1 is reserved for findings alone.

## Run the suites

    devbox run test                          # or, inside a devbox shell:
    cd tools && python3 -m unittest discover -p 'test_*.py' -v
