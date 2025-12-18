# pyristretto

**Accelerated Ristretto255 primitives for Python, backed by libsodium.**

`pyristretto` is an optimized native CPython extension exposing low-level
Ristretto255 operations with minimal overhead and explicit, protocol-friendly
Python APIs.

---

## Features

### Ristretto255 EC Operations
- `point_add`, `point_sub`, `point_sum`
- `point_mul`, `base_mul`
- `assert_valid_point`, `is_valid_point`

### Hash Primitives
- `Hs`: hash → scalar (Fiat–Shamir friendly)
- `Hp`: hash → Ristretto point

### Generator Derivation
- Deterministic, domain-separated generator derivation
- Optimized via hash-state reuse

### Optimized Naive MSM
- ~3–5× faster than manual Python MSM loops
- Scalars reduced once, points copied once
- GIL released during inner crypto loops
- Efficient even for small MSM sizes (or even for one!)

### Pedersen Commitments
- `pedersen_commit` of the form `a·G + r·H`

---

## Installation

### Requirements
- Python 3.9+
- `libsodium` (with Ristretto255 support)
- A C compiler (GCC recommended)

### Install with pip

```bash
pip install pyristretto
```

### Build from source

```bash
pip install .
```

For development:

```bash
pip install -e .
```

---

## Quick Example

```python
from pyristretto import *

a = sc_rand()
b = sc_rand()

P = base_mul(a)
Q = base_mul(b)

R = point_add(P, Q)
S = point_mul(5, R)

assert_valid_point("Point S", S)
```

---

## Hashing Helpers

### Hash → Scalar (Fiat–Shamir)

```python
c = Hs(b"domain", P, Q)
```

### Hash → Point

```python
H = Hp(b"domain", b"context")
```

---

## Multi-Scalar Multiplication (MSM)

```python
scalars = [a, b, 7]
points  = [P, Q, H]

R = msm(scalars, points)
```

* Scalars are reduced once
* Points are copied once into contiguous buffers
* Zero scalars are skipped
* GIL released during scalar-mult loops

This is a **naive MSM**, but significantly faster than Python-level loops and
well-suited for protocol inner loops.

---

## Generator Derivation

```python
Gs = derive_generators(b"G", 64)
Hs = derive_generators(b"H", 64)
```

---

## Pedersen Commitments

```python
C = pedersen_commit(amount=42, blinding=sc_rand())
```

Defined as:

```
C = a·G + r·H
```

Where:

* `G = base_mul(1)`
* `H = Hp(b"Ristretto255:H")`

---

## API Overview

### Constants

The following curve and subgroup constants are exposed for convenience:

* `q`  Ristretto255 subgroup order (`2²⁵² + 27742317777372353535851937790883648493`)
* `G`  Canonical Ristretto base point (`base_mul(1)`)
* `H`  Secondary generator defined as `Hp(b"Ristretto255:H")`
* `IDENTITY`  The Ristretto identity element (32-byte encoding)

### Scalars

* `sc_rand() -> int`
* `sc_add(a, b) -> int`
* `sc_sub(a, b) -> int`
* `sc_mul(a, b) -> int`
* `from_bytes32(b) -> int`
* `to_bytes32(i) -> bytes`

### Points

* `base_mul(s) -> bytes`
* `point_mul(s, P) -> bytes`
* `point_add(P, Q) -> bytes`
* `point_sub(P, Q) -> bytes`
* `point_sum(list[P]) -> bytes`

### Validation

* `is_valid_point(P) -> bool`
* `assert_valid_point(name, P)`

---

## Benchmarks

The following benchmarks compare `pyristretto` against `pysodium` and `PyNaCl`
using **protocol-style workloads**.

**Environment**

* Python 3.12
* Intel i5-10400F
* **N = 512, MSM_N = 128**
* Averaged over 5 runs

| Library     | base_mul | point_mul | point_add | generators | Pedersen | MSM      |
| ----------- | -------- | --------- | --------- | ---------- | -------- | -------- |
| pyristretto | 0.0086 s | 0.0268 s  | 0.0114 s  | 0.0015 s   | 0.0436 s | 0.0255 s |
| pysodium    | 0.0204 s | 0.0573 s  | 0.0127 s  | 0.0036 s   | 0.0908 s | 0.0695 s |
| PyNaCl      | 0.0205 s | 0.0984 s  | 0.0121 s  | N/A        | 0.1298 s | 0.1098 s |

`pyristretto` achieves ~2× speedups over `pysodium` and up to ~3× over `PyNaCl`
in MSM-heavy and EC-heavy workloads by minimizing Python↔C crossings, reducing
redundant processing, and releasing the GIL during inner crypto loops.

### Operations per second

| Operation            | pysodium (Python) | pyristretto (C) | Speedup  |
| -------------------- | ----------------- | --------------- | -------- |
| `Hs` (hash → scalar) | 400k ops/s        | **1.45M ops/s** | **3.6×** |
| `Hp` (hash → point)  | 39k ops/s         | **66k ops/s**   | **1.7×** |
| `derive_generators`  | 618 ops/s         | **1.06k ops/s** | **1.7×** |

| Operation   | pysodium (Python) | pyristretto (C) | Speedup  |
| ----------- | ----------------- | --------------- | -------- |
| `point_add` | 40.8k ops/s       | **41.1k ops/s** | 1.0×     |
| `point_sub` | 41.0k ops/s       | **41.2k ops/s** | 1.0×     |
| `point_sum` | 649 ops/s         | **817 ops/s**   | **1.3×** |
| `point_mul` | 8.9k ops/s        | **16.7k ops/s** | **1.9×** |
| `base_mul`  | 24.7k ops/s       | **52.8k ops/s** | **2.1×** |

| Operation            | pysodium (Python) | pyristretto (C) | Speedup  |
| -------------------- | ----------------- | --------------- | -------- |
| `assert_valid_point` | 121k ops/s        | **163k ops/s**  | **1.3×** |
| `is_valid_point`     | 113k ops/s        | **204k ops/s**  | **1.8×** |

\* Point addition and subtraction are already dominated by libsodium internals;
as a result, performance differences are negligible.

---

## License

MIT.
