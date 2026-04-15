#!/usr/bin/env bash
set -euo pipefail

python3 -m py_compile scrape_tripadvisor_attractions.py
python3 -m unittest discover -s tests -p "test_*.py"

if [[ "${1:-}" == "--with-smoke" ]]; then
  # Requires network access and a working browser runtime.
  python3 scrape_tripadvisor_attractions.py --pages 1 --start-page 1
fi
