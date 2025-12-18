# pylint: disable=line-too-long, too-many-instance-attributes

import numpy as np
from ..lattice import Lattice, BravaisLattice, Symbol
from .square import Square

class Graphene(Lattice):
    def __init__(self, spinful=False, **kwargs):
        super().__init__(BravaisLattice.Triangular, **kwargs)
        self.n_orbitals = 2 if spinful else 1

        sublattice = Square(N1=1, N2=2)
        self.add_sublattice(sublattice)
        self.aspect = 1/np.sqrt(2)
        self.sublattice.aspect = np.sqrt(2)

        self.sublattice.lattice_vectors = np.array([
            [1, 0],
            [0, 1],
        ])
        self.plot_scale = np.array([np.sqrt(3), np.sqrt(3)/2])

        self.basis = np.zeros((1, 2, self.n_orbitals, 2))
        self.basis[0, 0, :] = (0, 0)
        self.basis[0, 1, :] = (0, 1)
        self.basis = self.basis.reshape(1*2*self.n_orbitals, 2)
        self.gen_coords()

    def init(self):
        match self.sublattice:
            case Square():
                ts = []
                hops = []
                ij = []

                mu = Symbol("mu")
                t = Symbol("t")

                for i in range(self.n_orbitals):
                    ts.append(mu)
                    hops.append([0, 0])
                    ij.append([0, 0, 0, 0, i, i])

                    ts.append(t)
                    hops.append([0, 1])
                    ij.append([0, 1, 0, 0, i, i])

                    ts.append(t)
                    hops.append([-1, 1])
                    ij.append([0, 1, 0, 0, i, i])

                    ts.append(t)
                    hops.append([0, -1])
                    ij.append([0, 0, 0, 1, i, i])

                    ts.append(t)
                    hops.append([1, -1])
                    ij.append([0, 0, 0, 1, i, i])
            case _:
                raise ValueError("Bad sublattice")

        self.ts = [ts, []]
        self.hops = [hops, []]
        self.ij = [ij, []]

    def gen_coords(self):
        a1, a2 = np.sqrt(3) * self.lattice_vectors

        coords_a = np.array([
            x * a1 + y * a2 for x, y in np.ndindex(self.N1, self.N2)
        ]) + self.basis[0]
        coords_b = np.array([
            x * a1 + y * a2 for x, y in np.ndindex(self.N1, self.N2)
        ]) + self.basis[1]

        coords = np.zeros((self.N1, 2, self.N2, 2))
        coords[:, 0] = coords_a.reshape(self.N1, self.N2, 2)
        coords[:, 1] = coords_b.reshape(self.N1, self.N2, 2)
        self.coords = coords.reshape(2*self.N1*self.N2, 2)
