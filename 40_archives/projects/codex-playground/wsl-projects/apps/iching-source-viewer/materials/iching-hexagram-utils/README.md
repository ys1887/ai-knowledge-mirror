# iching-hexagram-utils

I Ching (易経) utilities for mapping 6-line binary strings to hexagrams and computing related forms.

## Files

- `hexagram_utils.py`: core logic
- `64ka.json`: list-based hexagram dictionary (`{"hexagrams": [...]}`)
- `64ka_optimized.json`: optimized key-value map by binary string

## Input Model

- Binary format: 6 chars (`0` or `1`)
- Order: left to right = 初爻(1) to 上爻(6)
- Changing lines: space-separated indices (`1..6`), e.g. `"2 5"`

## Core API

- `load_hexagrams(path="64ka.json")`
- `main(honka_binary, bian_yao_str, hexagrams)`

`main(...)` returns:

- `structured`: 本卦 / 変爻 / 之卦 / 互卦 / 錯卦 / 綜卦
- `markdown`: human-readable summary text

## Example

```python
from hexagram_utils import load_hexagrams, main

hexagrams = load_hexagrams("64ka.json")
result = main("101100", "2", hexagrams)
print(result["markdown"])
```

## Notes

- This repository is intentionally small and data-focused.
- `64ka_optimized.json` is included for quick lookup scenarios.
