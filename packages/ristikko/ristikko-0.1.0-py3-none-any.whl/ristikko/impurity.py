# pylint: disable=missing-module-docstring, invalid-name, line-too-long, too-many-instance-attributes, too-many-arguments, too-many-positional-arguments, missing-class-docstring
from dataclasses import dataclass
import numpy as np
from keino import Params
from .lattice import Space, Symbol, Site

class Impurity():
    """
    Represents an impurity in a Hamiltonian.

    An impurity is defined by an energy, and which sites it hops to.
    It also has a nominal position, but this is only used for plotting.
    Impurities are included in the Hamiltonian matrix as additional
    rows and columns.
    """

    def __init__(self, idx, N1, N2, N1_sub, N2_sub, spinful=True, coord=None):
        """
        Parameters
        ----------

        idx: int
            unique index of the impurity. Automatically assigned by
            System.add_impurity()
        N1, N2, N1_sub, N2_sub: int
            shape of the associated system
        spinful: bool
            controls the number of orbitals of the impurity
        coord: pair[float]
            Optional, the position of the impurity. Used for plotting.
        """
        self.idx = idx
        self.n_orbitals = 2 if spinful else 1
        self.n_orbitals_substrate = self.n_orbitals * N1_sub * N2_sub
        self.hoppings = []
        self.N1 = N1
        self.N2 = N2
        self.N1_sub = N1_sub
        self.N2_sub = N2_sub
        self.x = 0
        self.y = 0
        self.coord = coord

    def add_hopping(self, other, i, j, t, d1=0, d2=0):
        """
        Add a hopping from the impurity.

        Parameters:
            other: Impurity | size-4 list/tuple/ndarray
            Where the hopping is going to
                - either another impurity, or
                - a coordinate on the substrate + sublattice (x, y, x_sub, y_sub)
        i, j: int
            The orbitals involved in the hopping
            i = 0: hopping from up orbital
            i = 1: hopping from down orbital
            j = 0: hopping to up orbital
            j = 1: hopping to down orbital
        t: Symbol
            hopping energy
        d1, d2: int
            (For kspace)
            The number of unit cells in the a1 and a2 directions
            that the hopping traverses
        """
        assert isinstance(other, (Impurity, Site))

        if isinstance(other, Impurity):
            j = other.n_orbitals_substrate + other.n_orbitals * other.idx + j

        ind = np.arange(self.n_orbitals_substrate).reshape(self.N1_sub, self.N2_sub, self.n_orbitals)
        if isinstance(other, Site):
            j = ind[other.x_sub, other.y_sub, j]

        i = self.n_orbitals_substrate + self.n_orbitals * self.idx + i
        self.hoppings.append(Hopping(other, i, j, t, d1, d2))

    def __call__(self, params: Params, space, k=None, direction=None, lattice_vectors=None):
        match space:
            case Space.RealSpace:
                ts = [hop.t.replace(params, None, None) for hop in self.hoppings]
                return ts
            case Space.KSpace:
                ts = [hop.t.replace(params, None, None) * np.exp(1j * k @ (hop.d1 * lattice_vectors[0] + hop.d2 * lattice_vectors[1])) for hop in self.hoppings]
                return ts
            case Space.Ribbon:
                ts = []
                if direction == "a1":
                    for hop in self.hoppings:
                        if hop.d2 == 0:
                            t = hop.t.replace(params, None, None) * np.exp(1j * k @ (hop.d1 * lattice_vectors[0]))
                            ts.append(t)
                if direction == "a2":
                    for hop in self.hoppings:
                        if hop.d1 == 0:
                            t = hop.t.replace(params, None, None) * np.exp(1j * k @ (hop.d2 * lattice_vectors[1]))
                            ts.append(t)
                return ts
            case _:
                raise ValueError(f"Space {space} not implemented")

@dataclass
class Hopping:
    other: Site | Impurity
    i: int
    j: int
    t: Symbol
    d1: int
    d2: int
