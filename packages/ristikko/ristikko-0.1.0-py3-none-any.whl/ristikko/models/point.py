# pylint: disable=invalid-name, line-too-long
"""Sublattice with a single site"""
import numpy as np
from ..lattice import Lattice, BravaisLattice, Symbol, Floor

class Point(Lattice):
    def __init__(self, bravais_lattice: BravaisLattice):
        self.bravais_lattice = bravais_lattice
        self.N1 = 1
        self.N2 = 1

        aspect = 1
        if bravais_lattice == BravaisLattice.Triangular:
            aspect = 1/np.sqrt(3)

        super().__init__(bravais_lattice, aspect=aspect)

        self.sublattice = Floor()

    def init(self):
        mu = Symbol("mu")
        Jx = Symbol("Jx")
        Jy = Symbol("Jy")
        Jz = Symbol("Jz")

        if self.n_orbitals == 2:
            ts = [
                ( -1 * mu ) + Jz,
                ( -1 * mu ) + ( -1 * Jz ),
                Jx  + (- 1j * Jy ),
                Jx + 1j * Jy
            ]
            ij = [
                [0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 1, 1],
                [0, 0, 0, 0, 0, 1],
                [0, 0, 0, 0, 1, 0],
            ]
            hops = [
                [0, 0],
                [0, 0],
                [0, 0],
                [0, 0],
            ]

            sc_ts = [Symbol("Delta.s.0"), Symbol("Delta.s.0", -1)]
            sc_ij = [
                [0, 0, 0, 0, 0, 1],
                [0, 0, 0, 0, 1, 0],
            ]

            sc_hops = [
                [0, 0],
                [0, 0],
            ]
        else:
            sc_ts = []
            sc_ij = []
            sc_hops = []
            ts = [-1 * mu]
            ij = [
                [0, 0, 0, 0, 0, 0]
            ]
            hops = [[0, 0]]

        self.ts = [ts, sc_ts]
        self.hops = [hops, sc_hops]
        self.ij = [ij, sc_ij]
