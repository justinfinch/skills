# tools

Verification for the Arche's OKF v0.2 conformance. Not shipped in any skill —
`arche-lint` implements its own checks; these exist so lint can be verified
against something independent.

## Requirements

Python 3.12+ and PyYAML. Both are present on the development machine; install
PyYAML with `python3 -m pip install --user pyyaml` if missing.

## Check a bundle

    python3 tools/okf_conformance.py path/to/.arche

Exit code 0 when conformant, 1 when findings exist, 2 on usage error.

## Run the suites

    cd tools && python3 -m unittest discover -p 'test_*.py' -v
