#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$script_dir"

while true; do
  clear
  python3 duanyi.py
  printf '\nEnter で再実行、Ctrl+C で終了します。\n'
  read -r _
done
