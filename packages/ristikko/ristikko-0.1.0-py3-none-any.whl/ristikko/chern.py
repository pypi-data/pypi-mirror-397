# pylint: disable=invalid-name
"""
Numerical calculation of the Chern number using the Fukui-Hatsugai method
"""
import numpy as np

### FHS method
def bump_x(k, Nk):
    """Given the Brillouin zone is discretised into Nk points,
    increment a k-index pair in the x-direction, handling periodic
    boundaries"""
    return ( (k[0] + 1) % Nk, k[1] )
def bump_y(k, Nk):
    """Given the Brillouin zone is discretised into Nk points,
    increment a k-index pair in the y-direction, handling periodic
    boundaries"""
    return ( k[0], (k[1] + 1) % Nk )

def link1(k, band, Nk):
    """FHS U(1) link variable in the x-direction"""
    k_n = k
    k_m = bump_x(k, Nk)
    n = band[k_n]
    m = band[k_m]

    numer = np.vdot(n, m)
    denom = np.linalg.norm(numer)
    U = numer / denom
    return U

def link2(k, band, Nk):
    """FHS U(1) link variable in the y-direction"""
    k_n = k
    k_m = bump_y(k, Nk)
    n = band[k_n]
    m = band[k_m]

    numer = np.vdot(n, m)
    denom = np.linalg.norm(numer)
    U = numer / denom
    return U

def field_strength(k, band, Nk):
    """FHS lattice field strength"""
    T = [
        link1(k, band, Nk),
        link2(bump_x(k, Nk), band, Nk),
        1 / link1(bump_y(k, Nk), band, Nk ),
        1 / link2(k, band, Nk)
    ]
    F = np.log(np.prod(T))
    return  F

def calculate(band, Nk):
    """Compute the Chern number for a band using the FHS method"""
    F = [field_strength(k, band, Nk) for k in band]
    F = sum(F)
    F = np.real(F / (2 * np.pi * 1j))
    return F
