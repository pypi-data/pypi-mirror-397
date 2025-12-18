from typing import NewType, Sequence, List

RistrettoPoint = NewType("RistrettoPoint", bytes)

# ----------------------------
# Hash helpers
# ----------------------------

def Hs(
    *args: bytes,
) -> int:
    """
    Hash-to-scalar using BLAKE2b and Ristretto scalar reduction.

    args:     byte strings to be concatenated and hashed
    returns:  scalar as Python int
    raises:
        TypeError    - non-bytes argument
        RuntimeError - hashing or reduction failure
    """
    ...


def Hp(
    *args: bytes,
) -> RistrettoPoint:
    """
    Hash-to-point using BLAKE2b and ristretto255_from_hash.

    args:     byte strings to be concatenated and hashed
    returns:  32-byte Ristretto point
    raises:
        TypeError    - non-bytes argument
        RuntimeError - hashing or mapping failure
    """
    ...


def derive_generators(
    domain: bytes,
    n: int,
) -> List[RistrettoPoint]:
    """
    Deterministically derive Ristretto generators from a domain.

    domain:   domain separation tag
    n:        number of generators to derive
    returns:  list of 32-byte Ristretto points
    raises:
        TypeError    - invalid argument types
        ValueError   - n < 0
        RuntimeError - hashing or mapping failure
    """
    ...

# ----------------------------
# Point operations
# ----------------------------

def point_add(
    P: RistrettoPoint,
    Q: RistrettoPoint,
) -> RistrettoPoint:
    """
    Add two Ristretto points.

    P:        32-byte Ristretto point
    Q:        32-byte Ristretto point
    returns:  32-byte Ristretto point
    raises:
        TypeError    - invalid argument type
        ValueError   - invalid point encoding
        RuntimeError - addition failure
    """
    ...


def point_sub(
    P: RistrettoPoint,
    Q: RistrettoPoint,
) -> RistrettoPoint:
    """
    Subtract two Ristretto points.

    P:        32-byte Ristretto point
    Q:        32-byte Ristretto point
    returns:  32-byte Ristretto point
    raises:
        TypeError    - invalid argument type
        ValueError   - invalid point encoding
        RuntimeError - subtraction failure
    """
    ...


def point_sum(
    points: Sequence[RistrettoPoint],
) -> RistrettoPoint:
    """
    Sum a sequence of Ristretto points.

    points:   sequence of 32-byte Ristretto points
    returns:  32-byte Ristretto point
    raises:
        TypeError    - non-bytes element
        ValueError   - empty input or invalid point encoding
        RuntimeError - addition failure
    """
    ...


def point_mul(
    scalar: int,
    P: RistrettoPoint,
) -> RistrettoPoint:
    """
    Multiply a Ristretto point by a scalar.

    scalar:   integer scalar
    P:        32-byte Ristretto point
    returns:  32-byte Ristretto point
    raises:
        TypeError    - invalid scalar or point type
        ValueError   - invalid point encoding
        RuntimeError - scalar multiplication failure
    """
    ...


def base_mul(
    scalar: int,
) -> RistrettoPoint:
    """
    Multiply the Ristretto base point by a scalar.

    scalar:   integer scalar
    returns:  32-byte Ristretto point
    raises:
        TypeError    - invalid scalar type
        RuntimeError - scalar multiplication failure
    """
    ...

# ----------------------------
# Validation helpers
# ----------------------------

def assert_valid_point(
    name: str,
    P: bytes,
) -> None:
    """
    Assert that a byte string is a valid Ristretto point encoding.

    name:     label used in error messages
    P:        byte string
    returns:  None
    raises:
        AssertionError - invalid point encoding
        TypeError      - invalid argument type
    """
    ...


def is_valid_point(
    P: bytes,
) -> bool:
    """
    Check whether a byte string is a valid Ristretto point encoding.

    P:        byte string
    returns:  True if P is a valid 32-byte Ristretto point, False otherwise
    raises:
        TypeError - invalid argument type
    """
    ...
