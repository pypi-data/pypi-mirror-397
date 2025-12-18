# pylint: disable=line-too-long, invalid-name, too-many-branches, too-many-locals, too-many-statements

from ..lattice import Lattice, BravaisLattice, Symbol
from .point import Point

class Square(Lattice):
    def __init__(self, **kwargs):
        super().__init__(BravaisLattice.Square, aspect=1, **kwargs)

    def init(self):
        # pylint: disable=unnecessary-lambda-assignment
        match self.sublattice:
            case Point() | Square():
                ts = []
                hops = []
                ij = []
                t = Symbol("t")
                for i in range(self.n_orbitals):
                    for y in range(self.sublattice.N2):
                        ts.append(t)
                        hops.append([-1, 0])
                        ij.append([0, y, self.sublattice.N1-1, y, i, i])

                        ts.append(t)
                        hops.append([1, 0])
                        ij.append([self.sublattice.N1-1, y, 0, y, i, i])
                    for x in range(self.sublattice.N1):
                        ts.append(t)
                        hops.append([0, -1])
                        ij.append([x, 0, x, self.sublattice.N2-1, i, i])

                        ts.append(t)
                        hops.append([0, 1])
                        ij.append([x, self.sublattice.N2-1, x, 0, i, i])

                if not self.n_orbitals % 2:
                    alpha = Symbol("alpha")
                    beta = Symbol("beta")
                    rashba = self.rashba_matrix * alpha
                    dresselhaus = self.dresselhaus_matrix * beta

                    get_t = lambda d1, d2, i, j: ( ( d1 * rashba[0] ) + ( d2 * rashba[1] ) + ( d1 * dresselhaus[0] ) + ( d2 * dresselhaus[1] ) )[i, j]

                    for i, j in [(0, 1), (1, 0)]:
                        for y in range(self.sublattice.N2):
                            ts.append(get_t(-1, 0, i, j))
                            hops.append([-1, 0])
                            ij.append([0, y, self.sublattice.N1-1, y, i, j])

                            ts.append(get_t(1, 0, i, j))
                            hops.append([1, 0])
                            ij.append([self.sublattice.N1-1, y, 0, y, i, j])
                        for x in range(self.sublattice.N1):
                            ts.append(get_t(0, -1, i, j))
                            hops.append([0, -1])
                            ij.append([x, 0, x, self.sublattice.N2-1, i, j])

                            ts.append(get_t(0, 1, i, j))
                            hops.append([0, 1])
                            ij.append([x, self.sublattice.N2-1, x, 0, i, j])
            case _:
                raise ValueError("Error: Need to define intersublattice hoppings manually")

        sc_ts = []
        sc_hops = []
        sc_ij = []

        if not self.n_orbitals % 2:
            # Extended s-wave
            Delta100 = Symbol("Delta.s.1")
            Delta100c = Symbol("Delta.s.1", -1)
            Delta110 = Symbol("Delta.s.2")
            Delta110c = Symbol("Delta.s.2", -1)

            sc_ts.append(Delta110)
            sc_hops.append([1, -1])
            sc_ij.append([ self.sublattice.N1-1, 0, 0, self.sublattice.N2-1, 0, 1 ])

            sc_ts.append(Delta110c)
            sc_hops.append([1, -1])
            sc_ij.append([ self.sublattice.N1-1, 0, 0, self.sublattice.N2-1, 1, 0 ])


            sc_ts.append(Delta110)
            sc_hops.append([1, 1])
            sc_ij.append([ self.sublattice.N1-1, self.sublattice.N2-1, 0, 0, 0, 1 ])

            sc_ts.append(Delta110c)
            sc_hops.append([1, 1])
            sc_ij.append([ self.sublattice.N1-1, self.sublattice.N2-1, 0, 0, 1, 0 ])


            sc_ts.append(Delta110)
            sc_hops.append([-1, 1])
            sc_ij.append([ 0, self.sublattice.N2-1, self.sublattice.N1-1, 0, 0, 1 ])

            sc_ts.append(Delta110c)
            sc_hops.append([-1, 1])
            sc_ij.append([ 0, self.sublattice.N2-1, self.sublattice.N1-1, 0, 1, 0 ])


            sc_ts.append(Delta110)
            sc_hops.append([-1, -1])
            sc_ij.append([ 0, 0, self.sublattice.N1-1, self.sublattice.N2-1, 0, 1 ])

            sc_ts.append(Delta110c)
            sc_hops.append([-1, -1])
            sc_ij.append([ 0, 0, self.sublattice.N1-1, self.sublattice.N2-1, 1, 0 ])


            for y in range(self.sublattice.N2):
                sc_ts.append(Delta100)
                sc_hops.append([-1, 0])
                sc_ij.append([0, y, self.sublattice.N1-1, y, 0, 1])

                sc_ts.append(Delta100)
                sc_hops.append([1, 0])
                sc_ij.append([self.sublattice.N1-1, y, 0, y, 0, 1])

                sc_ts.append(Delta100c)
                sc_hops.append([-1, 0])
                sc_ij.append([0, y, self.sublattice.N1-1, y, 1, 0])

                sc_ts.append(Delta100c)
                sc_hops.append([1, 0])
                sc_ij.append([self.sublattice.N1-1, y, 0, y, 1, 0])

                if y < self.sublattice.N2-1:
                    sc_ts.append(Delta110)
                    sc_hops.append([1, 0])
                    sc_ij.append([self.sublattice.N1-1, y, 0, y+1, 0, 1])

                    sc_ts.append(Delta110)
                    sc_hops.append([0, 0])
                    sc_ij.append([0, y+1, self.sublattice.N1-1, y, 0, 1])

                    sc_ts.append(Delta110c)
                    sc_hops.append([1, 0])
                    sc_ij.append([self.sublattice.N1-1, y, 0, y+1, 1, 0])

                    sc_ts.append(Delta110c)
                    sc_hops.append([0, 0])
                    sc_ij.append([0, y+1, self.sublattice.N1-1, y, 1, 0])

                if y > 0:
                    sc_ts.append(Delta110)
                    sc_hops.append([1, 0])
                    sc_ij.append([self.sublattice.N1-1, y, 0, y-1, 0, 1])

                    sc_ts.append(Delta110)
                    sc_hops.append([1, 0])
                    sc_ij.append([0, y-1, self.sublattice.N1-1, y, 0, 1])

                    sc_ts.append(Delta110c)
                    sc_hops.append([1, 0])
                    sc_ij.append([self.sublattice.N1-1, y, 0, y-1, 1, 0])

                    sc_ts.append(Delta110c)
                    sc_hops.append([1, 0])
                    sc_ij.append([0, y-1, self.sublattice.N1-1, y, 1, 0])

            for x in range(self.sublattice.N1):
                sc_ts.append(Delta100)
                sc_hops.append([0, -1])
                sc_ij.append([x, 0, x, self.sublattice.N2-1, 0, 1])

                sc_ts.append(Delta100)
                sc_hops.append([0, 1])
                sc_ij.append([x, self.sublattice.N2-1, x, 0, 0, 1])

                sc_ts.append(Delta100)
                sc_hops.append([0, -1])
                sc_ij.append([x, 0, x, self.sublattice.N2-1, 1, 0])

                sc_ts.append(Delta100)
                sc_hops.append([0, 1])
                sc_ij.append([x, self.sublattice.N2-1, x, 0, 1, 0])

                if x < self.sublattice.N1-1:
                    sc_ts.append(Delta110)
                    sc_hops.append([0, -1])
                    sc_ij.append([x, 0, x+1, self.sublattice.N2-1, 0, 1])

                    sc_ts.append(Delta110)
                    sc_hops.append([0, 1])
                    sc_ij.append([x, self.sublattice.N2-1, x+1, 0, 0, 1])

                    sc_ts.append(Delta110c)
                    sc_hops.append([0, -1])
                    sc_ij.append([x, 0, x+1, self.sublattice.N2-1, 1, 0])

                    sc_ts.append(Delta110c)
                    sc_hops.append([0, 1])
                    sc_ij.append([x, self.sublattice.N2-1, x+1, 0, 1, 0])

                if x > 0:
                    sc_ts.append(Delta110)
                    sc_hops.append([0, -1])
                    sc_ij.append([x, 0, x-1, self.sublattice.N2-1, 0, 1])

                    sc_ts.append(Delta110)
                    sc_hops.append([0, 1])
                    sc_ij.append([x, self.sublattice.N2-1, x-1, 0, 0, 1])

                    sc_ts.append(Delta110c)
                    sc_hops.append([0, -1])
                    sc_ij.append([x, 0, x-1, self.sublattice.N2-1, 1, 0])

                    sc_ts.append(Delta110c)
                    sc_hops.append([0, 1])
                    sc_ij.append([x, self.sublattice.N2-1, x-1, 0, 1, 0])


        self.ts = [ts, sc_ts]
        self.hops = [hops, sc_hops]
        self.ij = [ij, sc_ij]
