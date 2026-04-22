#!/bin/zsh

set -euo pipefail

echo "build started"
python3 -m unittest
echo "build finished"
