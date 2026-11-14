#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "usage: $0 <target-file>" >&2
  exit 1
fi

target_file="$1"

if [[ ! -f "$target_file" ]]; then
  echo "[update_prompt_header_stamp] file not found: $target_file" >&2
  exit 1
fi

base_name="$(basename "$target_file" .md)"
first_line="$(sed -n '1p' "$target_file")"

if [[ ! "$first_line" =~ ^#\ ${base_name}([[:space:]]+([0-9]{4}-[0-9]{2}-[0-9]{2})(\.([0-9]+))?)?$ ]]; then
  echo "[update_prompt_header_stamp] first line format is invalid." >&2
  echo "expected: # ${base_name} or # ${base_name} YYYY-MM-DD.n" >&2
  echo "actual:   $first_line" >&2
  exit 1
fi

current_date="${BASH_REMATCH[2]:-}"
current_seq="${BASH_REMATCH[4]:-}"
today="$(date +%F)"

if [[ "$current_date" == "$today" && -n "$current_seq" ]]; then
  next_seq=$((current_seq + 1))
else
  next_seq=1
fi

new_stamp="${today}.${next_seq}"
new_first_line="# ${base_name} ${new_stamp}"

tmp_file="$(mktemp)"
{
  printf '%s\n' "$new_first_line"
  sed '1d' "$target_file"
} >"$tmp_file"
mv "$tmp_file" "$target_file"

printf '%s\n' "$new_stamp"
