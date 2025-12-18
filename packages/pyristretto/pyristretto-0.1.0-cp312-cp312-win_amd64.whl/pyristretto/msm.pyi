from typing import NewType, Sequence

RistrettoPoint = NewType("RistrettoPoint", bytes)

def msm(
    scalars: Sequence[int],
    points: Sequence[RistrettoPoint],
) -> RistrettoPoint:
    """
    Naive multi-scalar multiplication (MSM) over Ristretto255.

    scalars: ints
    points:  32-byte Ristretto points
    returns: 32-byte Ristretto point
    raises:
        TypeError    - invalid scalar or point type
        ValueError   - empty or mismatched inputs
        RuntimeError - invalid point encoding
    """
    ...
