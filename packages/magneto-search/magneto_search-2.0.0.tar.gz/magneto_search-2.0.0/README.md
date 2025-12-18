# Magneto Search: Ultra-Fast Binary Pattern Search (C Extension)

**Magneto Search** is a Python extension module written in C that implements an optimized Bitap (Shift-OR) algorithm for extremely fast pattern matching on large binary data (`bytes`).

It is designed for performance‑critical use cases where raw speed matters more than the complexity of regular expressions, such as cybersecurity, log analysis, and bioinformatics.

---

## Features and Performance

| Feature            | Description                                                  | Benefit                                                        |
| ------------------ | ------------------------------------------------------------ | -------------------------------------------------------------- |
| Raw Speed (O(n))   | C implementation of the Bitap / Shift‑OR algorithm           | Typical scan speeds of **150+ MB/s** from Python               |
| Built‑in Streaming | Maintains internal state (Bitap register) across chunks      | Scan **unlimited‑size files** without loading them into memory |
| Core Options       | Native support for case‑insensitive and whole‑word search    | Fast and precise matching for common use cases                 |
| 64‑Character Limit | Optimized on `uint64_t` for patterns from 1 to 64 characters | Ideal for signatures and short keywords                        |

---

## Installation

### Via PyPI (recommended)

```bash
pip install magneto-search
```

### Build from source

Use this method for development or unsupported architectures.

```bash
git clone https://github.com/Pirata-Winox/magneto.git
cd magneto
pip install .
```

The `setup.py` file automatically handles compilation of the C extension.

---

## Usage

### The `magneto.Pattern` class

All searches start by compiling a pattern into an internal Bitap structure.

| Method                           | Description                                                        |
| -------------------------------- | ------------------------------------------------------------------ |
| `Pattern(pattern, options)`      | Compiles the pattern into an internal Bitap representation         |
| `p.scan(data, max_matches=1024)` | Scans a data chunk, updates streaming state, returns match offsets |
| `p.count(data)`                  | Counts occurrences without storing offsets (fastest option)        |
| `p.find_first(data)`             | Returns the offset of the first match or `None`                    |
| `p.reset_state()`                | Resets streaming state to start a new scan                         |

---

## Options and Constants

Options can be combined using the bitwise OR operator (`|`).

```python
import magneto

INSENSITIVE = magneto.OPTION_CASE_INSENSITIVE  # 1
WHOLE_WORD = magneto.OPTION_WHOLE_WORD         # 2
NONE = magneto.OPTION_NONE                     # 0

# Case‑insensitive AND whole‑word search
p = magneto.Pattern("flag", options=INSENSITIVE | WHOLE_WORD)
```

---

## Advanced Streaming Example

This example demonstrates scanning a large file in chunks while preserving internal state to correctly detect matches spanning block boundaries.

```python
import magneto

BLOCK_SIZE = 1024 * 1024  # 1 MB
FILE_PATH = "gigantic_log.dat"
PATTERN = "SECRET_KEY"

p = magneto.Pattern(PATTERN, options=magneto.OPTION_CASE_INSENSITIVE)

total_matches = 0
global_offset = 0

print(f"Starting streaming scan for '{PATTERN}'...")

with open(FILE_PATH, 'rb') as f:
    while True:
        block = f.read(BLOCK_SIZE)
        if not block:
            break

        matches = p.scan(block)
        for offset in matches:
            print(f"Match found at global offset: {global_offset + offset}")
            total_matches += 1

        global_offset += len(block)

print(f"Scan finished. Total matches: {total_matches}")

# Reset state before scanning another file
p.reset_state()
```

---

## Error Handling

Errors raised by the C extension are converted into clear Python exceptions.

| User Error                        | Python Exception                                   |
| --------------------------------- | -------------------------------------------------- |
| Empty pattern (`""`)              | `ValueError: Empty pattern`                        |
| Pattern longer than 64 characters | `ValueError: Pattern too long (max 64 characters)` |
| Invalid options                   | `ValueError: Invalid compilation options`          |

---

## Conclusion

Magneto Search is a high‑performance solution for:

* Fast searching of short patterns in large files
* Log, signature, and binary stream analysis
* Performance‑critical applications requiring streaming and persistent state

It combines the speed of C with the usability of Python for demanding workloads.
