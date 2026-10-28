"""The prastāra computations of uddiṣṭa and naṣṭa as importable functions.

A pattern is a string of L (laghu) and G (guru), read left to right.  The serial number
follows the convention of uddista.py / nasta.py: GG...G is 1, and the serial of any other
pattern is 1 + the sum of 2**k over the positions k (counting from 0 at the left) holding L.
"""


def uddista(pattern):
    """Serial number of a pattern (same result as uddista.py)."""
    return 1 + sum(2 ** k for k, c in enumerate(pattern) if c == "L")


def nasta(n, serial):
    """Pattern of n syllables with the given serial number (same result as nasta.py)."""
    if not 1 <= serial <= 2 ** n:
        raise ValueError("serial %d out of range for %d syllables" % (serial, n))
    s, i = "", serial
    while len(s) < n:
        if i % 2 == 0:
            s += "L"
            i //= 2
        else:
            s += "G"
            i = (i + 1) // 2
    return s


GANA = {"ma": "GGG", "ya": "LGG", "ra": "GLG", "sa": "LLG", "ta": "GGL",
        "ja": "LGL", "bha": "GLL", "na": "LLL", "la": "L", "ga": "G"}
