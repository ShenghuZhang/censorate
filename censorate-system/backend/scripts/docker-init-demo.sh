#!/bin/bash
set -e

# Check if INIT_DEMO_ENABLED is true (default: true)
if [ "${INIT_DEMO_ENABLED:-true}" = "true" ]; then
    echo "INIT_DEMO_ENABLED is true - running demo data initialization..."
    python scripts/init_mock_data.py
else
    echo "INIT_DEMO_ENABLED is false - skipping demo data initialization"
fi
