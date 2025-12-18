# ---------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------
import os as _os
import hashlib as _hashlib

from . import msm as _msm
from . import pyristretto as _ristretto

# ---------------------------------------------------------------------
# Re-export
# ---------------------------------------------------------------------
Hs = _ristretto.Hs
Hp = _ristretto.Hp

derive_generators = _ristretto.derive_generators

point_add = _ristretto.point_add
point_sum = _ristretto.point_sum

point_sub = _ristretto.point_sub

point_mul = _ristretto.point_mul
base_mul  = _ristretto.base_mul

assert_valid_point = _ristretto.assert_valid_point
is_valid_point     = _ristretto.is_valid_point

msm = _msm.msm

# ---------------------------------------------------------------------
# Curve & subgroup constants: ℓ, 𝒪
# ---------------------------------------------------------------------
q = 2**252 + 27742317777372353535851937790883648493
IDENTITY = b'\x00' * 32

# ---------------------------------------------------------------------
# Generators
# ---------------------------------------------------------------------
G = base_mul(1)
H = Hp(b"Ristretto255:H")

# ---------------------------------------------------------------------
# Scalar helpers
# ---------------------------------------------------------------------
def bytelen(x: int) -> int:
    return (x.bit_length() + (7 if x > 0 else 8)) // 8 if x != 0 else 1

def from_bytes32(b: bytes) -> int:
    return int.from_bytes(b, "little") % q

def to_bytes32(i: int, length=32) -> bytes:
    return (i % q).to_bytes(length, "little")

def sc_rand() -> int:
    return int.from_bytes(_os.urandom(32), "little") % q

def sc_add(a: int, b: int) -> int:
    return (a + b) % q

def sc_sub(a: int, b: int) -> int:
    return (a - b) % q

def sc_mul(a: int, b: int) -> int:
    return (a * b) % q

# ---------------------------------------------------------------------
# Hash helpers
# ---------------------------------------------------------------------
def blake2b(x: bytes, size: int = 32) -> bytes:
    return _hashlib.blake2b(x, digest_size=size).digest()

# ---------------------------------------------------------------------
# Keypair generation
# ---------------------------------------------------------------------
def generate_keypair():
    sk = sc_rand()
    sk_bytes = sk.to_bytes(32, "little")
    pk_bytes = base_mul(sk)
    return sk_bytes, pk_bytes

# ---------------------------------------------------------------------
# Pedersen Commitments
# ---------------------------------------------------------------------
def pedersen_commit(amount: int, blinding: int) -> bytes:
    """C = a * G + r * H"""
    return point_add(
        base_mul(amount % q),
        point_mul(blinding % q, H)
    )

# ---------------------------------------------------------------------
# Metadata
# ---------------------------------------------------------------------
__all__ = [
    # --- curve ops ---
    "Hs",
    "Hp",
    "derive_generators",

    "point_add",
    "point_sum",
    "point_sub",
    "point_mul",
    "base_mul",

    "assert_valid_point",
    "is_valid_point",

    # --- naive MSM ---
    "msm",

    # --- curve constants ---
    "q",
    "IDENTITY",
    "G",
    "H",

    # --- scalar helpers ---
    "bytelen",
    "from_bytes32",
    "to_bytes32",
    "sc_rand",
    "sc_add",
    "sc_sub",
    "sc_mul",

    # --- hash helpers ---
    "blake2b",

    # --- misc helpers ---
    "generate_keypair",
    "pedersen_commit",

    # --- metadata ---
    "__version__",
]
__version__ = "0.1.0"

# ---------------------------------------------------------------------
# EOF
# ---------------------------------------------------------------------