# pylint: disable=line-too-long, fixme, too-many-arguments, too-many-positional-arguments, invalid-name, too-many-locals, too-few-public-methods, too-many-instance-attributes

"""
file:     ristikko/lattice.py
Homepage: TODO
Licence:  GPLv3+

Defines a lattice for tight-binding models (Lattice), bravais lattices (BravaisLattice),
different spaces allowing for Fourier transforms (Space), and abstract
symbols for tight-binding Hamiltonians (Symbol).
"""

from dataclasses import dataclass
import copy
from enum import Enum
import numpy as np
from keino import Params, ndindex

@dataclass
class Site():
    """Represents a site on a lattice. (x, y) is the superlattice coordinates and (x_sub, y_sub) the sublattice."""
    x: int
    y: int
    x_sub: int
    y_sub: int

    def __iter__(self):
        yield self.x
        yield self.y
        yield self.x_sub
        yield self.y_sub

# pylint: disable=missing-class-docstring
class BravaisLattice(Enum):
    Triangular = "triangular"
    Square = "square"

    def lattice_vectors(self):
        # pylint: disable=missing-function-docstring
        match self.name:
            case "Triangular":
                lattice_vectors = np.array([
                    [1, 0],
                    [0.5, np.sqrt(3)/2],
                ])
            case "Square":
                lattice_vectors = np.array([
                    [1, 0],
                    [0, 1],
                ])
            case _:
                raise ValueError("Unsupported Bravais lattice")
        return lattice_vectors

# pylint: disable=missing-class-docstring
class Space(Enum):
    KSpace = "kspace"
    RealSpace = "realspace"
    Ribbon = "ribbon"

class Symbol():
    """
    Represents a symbol in a Hamiltonian.

    In ristikko, a lattice is defined by a Bravais lattice, a sublattice,
    the hoppings with the sublattice, and hoppings between sublattices.
    Each sublattice, in turn, has a sublattice.
    Hoppings are defined using Symbols.

    When a Hamiltonian matrix is constructed, the Symbols are replaced
    with a number, drawn from the provided Params object.

    The simplest case is a symbol with a single name:

        t = Symbol("t")

    Symbols can be multiplied by a prefactor

        t = -2 * Symbol("t")

    Symbols can be added together

        f = Symbol("a") + Symbol("b")

    This produces a symbol with the name ["a", "b"].

    In this fashion, arbitrarily complicated symbols can be constructed.
    """

    def __init__(self, names, multipliers=None):
        assert isinstance(names, ( str, list, np.ndarray ))

        self.names = names

        if multipliers is None:
            match names:
                case str():
                    multipliers = 1
                case np.ndarray():
                    multipliers = np.zeros_like(names)
                    for idx in ndindex(*names.shape):
                        if names[idx]:
                            multipliers[idx] = 1
                case list():
                    multipliers = [1 for _ in self.names]
                case _:
                    raise ValueError("names must be str, list, or np.ndarray")

        self.multipliers = multipliers

    def __getitem__(self, index):
        names = self.names[index]
        multipliers = self.multipliers[index]
        new_symbol = Symbol(names)
        new_symbol.multipliers = multipliers
        return new_symbol

    def replace(self, params, x, y, default=0):
        """Replace a symbol with the corresponding value(s) from params"""
        def params_get(key):
            value = params.get(key, default)
            if isinstance(value, np.ndarray):
                return value[x, y]
            return value

        match self.names:
            case str():
                val = params_get(self.names) * self.multipliers
            case np.ndarray():
                val = np.zeros_like(self.names, complex)
                for idx in ndindex(*self.names.shape):
                    val[idx] = params_get(self.names[idx]) * self.multipliers[idx]
                val = np.sum(val)
            case list():
                val = [
                        params_get(names) * multiplier for names, multiplier in zip(self.names, self.multipliers)
                      ]
                val = sum(val)
            case _:
                raise ValueError("names must be str, list, or np.ndarray")

        return val

    def conj(self):
        match self.names:
            case str():
                self.multipliers = complex(np.conj(self.multipliers))
            case np.ndarray():
                self.multipliers = np.conj(self.multipliers)
            case list():
                self.multipliers = np.conj(self.multipliers).tolist()
            case _:
                raise ValueError("names must be str, list, or np.ndarray")

    def __eq__(self, other):
        if isinstance(other, Symbol):
            return self.names == other.names
        return False

    def add(self, other):
        # pylint: disable=too-many-branches
        if other is None:
            return self

        names = None
        multipliers = None
        if isinstance(other, Symbol):
            match (self.names, other.names):
                case (str(), str()):
                    names = [self.names, other.names]
                    multipliers = [self.multipliers, other.multipliers]
                case (str(), np.ndarray()):
                    names = np.empty_like(other.names.shape + (2,), object)
                    multipliers = np.zeros_like(other.names.shape + (2,))
                    for idx in ndindex(*other.names.shape):
                        names[idx] = [other.names[idx], self.names]
                        multipliers[idx] = [other.multipliers[idx], self.multipliers]
                case (str(), list()):
                    names = [self.names] + other.names
                    multipliers = [self.multipliers] + other.multipliers
                case (np.ndarray(), str()):
                    names = np.empty_like(self.names.shape + (2,), object)
                    multipliers = np.zeros_like(self.names.shape + (2,), object)
                    for idx in ndindex(*self.names.shape):
                        names[idx] = [self.names[idx], other.names]
                        multipliers[idx] = [self.multipliers[idx], other.multipliers]
                case (np.ndarray(), np.ndarray()):
                    names = self.names + other.names
                    multipliers = self.multipliers + other.multipliers
                case (np.ndarray(), list()):
                    ...
                case (list(), str()):
                    names = self.names + [other.names]
                    multipliers = self.multipliers + [other.multipliers]
                case (list(), list()):
                    names = self.names + other.names
                    multipliers = self.multipliers + other.multipliers
                case (list(), np.ndarray()):
                    ...
                case _:
                    raise ValueError("self.names and other.names must be either str, list, or np.ndarray!")

        new_symbol = Symbol(names)
        new_symbol.multipliers = multipliers
        return new_symbol

    def __add__(self, other):
        return self.add(other)
    def __radd__(self, other):
        return self.add(other)

    def mul(self, other):
        # pylint: disable=missing-function-docstring, too-many-branches
        names = None
        multipliers = None

        match (self.names, other):
            case (str(), complex() | float() | int()):
                names = self.names
                multipliers = self.multipliers * other
            case (str(), np.ndarray()):
                names = np.empty_like(other, object)
                multipliers = other * self.multipliers
                for idx in ndindex(*names.shape):
                    if multipliers[idx] is not None:
                        names[idx] = self.names
                    else:
                        names[idx] = None
            case (str(), list()):
                names = [self.names for _ in other]
                multipliers = [m * self.multipliers for m in other]
            case (np.ndarray(), complex() | float() | int()):
                names = self.names
                multipliers = self.multipliers * other
            case (np.ndarray(), np.ndarray()):
                names = self.names
                multipliers = self.multipliers * other
            case (np.ndarray(), list()):
                ...
            case (list(), complex() | float() | int()):
                names = self.names
                multipliers = [m * other for m in self.multipliers]
            case (list(), list()):
                names = self.names
                multipliers = [m1 * m2 for m1, m2 in zip(self.multipliers, other)]
            case (list(), np.ndarray()):
                ...

        new_parameter = Symbol(names)
        new_parameter.multipliers = multipliers
        return new_parameter

    def __rmul__(self, other):
        return self.mul(other)

    def __mul__(self, other):
        return self.mul(other)

    def __str__(self):
        if isinstance(self.names, list):
            ret = str([str(l) + " * " + r for l, r in zip(self.multipliers, self.names)])
        else:
            ret = str(self.multipliers) + " * " + self.names

        return str(ret)

    def __repr__(self):
        if isinstance(self.names, list):
            ret = str([str(l) + " * " + r for l, r in zip(self.multipliers, self.names)])
        else:
            ret = str(self.multipliers) + " * " + self.names

        return str(ret)

class Floor():
    """
    In ristikko, a lattice can be constructed out of arbitrarily nested lattices.
    Floot represents the bottom of this nest.
    """
    def __init__(self):
        self.N1 = 1
        self.N2 = 1
        self._hoppings = None
        self._sc_hoppings = None
        self.removed_sites = []

    def set_n_orbitals(self, n_orbitals):
        pass

    def __call__(self, params, space, superconducting, **kwargs):
        return [], []

def _gen_hoppings_realspace(n_orbitals, N1_super, N2_super, N1_sub, N2_sub, pbc, _ts, _hops, _ij, _ts_sub, _ij_sub, valid_sites, removed_energy=10):
    #pylint: disable=consider-using-enumerate
    """Generates a list of hoppings for a Hamiltonian in real space"""
    ts = []
    ij = []

    ind = np.arange(N1_sub*N2_sub*n_orbitals).reshape(N1_sub, N2_sub, n_orbitals)

    # Intercell hops
    for n, x, y in np.ndindex(len(_ts), N1_super, N2_super):
        x_sub0, y_sub0, x_sub1, y_sub1, i, j = _ij[n]
        t = _ts[n]
        d1, d2 = _hops[n]

        ii = ind[x_sub0, y_sub0, i]
        jj = ind[x_sub1, y_sub1, j]
        x0, y0 = x, y
        x1, y1 = (x+d1)%N1_super, (y+d2)%N2_super

        if valid_sites[x0, y0, x_sub0, y_sub0] or valid_sites[x1, y1, x_sub1, y_sub1]:
            continue

        test_x = True if pbc[0] else 0 <= x+d1 < N1_super
        test_y = True if pbc[1] else 0 <= y+d2 < N2_super
        if test_x and test_y:
            ts.append(t)
            ij.append([x0, y0, x1, y1, ii, jj])

    # Intracell hops
    for n, x, y in np.ndindex(len(_ts_sub), N1_super, N2_super):
        x0, y0, x1, y1, i, j = _ij_sub[n]
        t = _ts_sub[n]
        ii = ind[x0, y0, i]
        jj = ind[x1, y1, j]

        if valid_sites[x, y, x0, y0] or valid_sites[x, y, x1, y1]:
            if x0 == x1 and y0 == y1 and i == j:
                t = removed_energy
            else:
                if t != 0 and t is not None:
                    t = 0

        ts.append(t)
        ij.append([x, y, x, y, ii, jj])

    return ts, ij

def _gen_hoppings_ribbon(k, lattice_vectors, n_orbitals, L, direction, pbc, _ts, _hops, _ij, _ts_sub, _ij_sub):
    # pylint: disable=consider-using-enumerate
    """Generates a list of hoppings for a Ribbon Hamiltonian"""
    ts = []
    ij = []

    ind = np.arange(L*n_orbitals).reshape(L, n_orbitals)

    # Intercell hops
    if direction == "a1":
        for n in range(len(_ts)):
            for y in range(L):
                t = _ts[n]
                x0, y0, x1, y1, i, j = _ij[n]
                d1, d2 = _hops[n]

                vec = (d1 * lattice_vectors[0]) + 0.0j
                t *= np.exp(1j * k @ vec)

                ii = ind[y0, i]
                jj = ind[y1, j]

                test = True if pbc else 0 <= y+d2 < L
                if test:
                    ts.append(t)
                    ij.append([y, (y+d2)%L, ii, jj])
    elif direction == "a2":
        for n in range(len(_ts)):
            for x in range(L):
                t = _ts[n]
                x0, y0, x1, y1, i, j = _ij[n]
                d1, d2 = _hops[n]

                vec = (d2 * lattice_vectors[1]) + 0.0j
                t *= np.exp(1j * k @ vec)

                ii = ind[x0, i]
                jj = ind[x1, j]

                test = True if pbc else 0 <= x+d1 < L
                if test:
                    ts.append(t)
                    ij.append([x, (x+d1)%L, ii, jj])

    # Intracell hops
    for n in range(len(_ts_sub)):
        x0, y0, x1, y1, i, j = _ij_sub[n]
        t = _ts_sub[n]
        ii = ind[x0, i]
        jj = ind[x1, j]

        for x in range(L):
            ts.append(t)
            ij.append([x, x, ii, jj])

    return ts, ij


class Lattice():
    """
    Represents a lattice.

    In ristikko, a lattice is defined by a Bravais lattice, a sublattice,
    the hoppings with the sublattice, and hoppings between sublattices.
    Hoppings are defined using Symbols.
    Each sublattice, in turn, has a sublattice.

    Given some parameters, and whether or not to Fourier transform,
    this class will generate a list of hoppings for a Hamiltonian.
    """
    def __init__(self, bravais_lattice: BravaisLattice, coords=None, hopping_degree=1, aspect=1, **kwargs):
        assert bravais_lattice in BravaisLattice

        self.basis = None
        self.n_orbitals = None
        self.bravais_lattice = bravais_lattice
        self.lattice_vectors = bravais_lattice.lattice_vectors()
        self.sublattice = None
        self.hd = hopping_degree
        self.coords = coords
        self.aspect = aspect
        self.plot_scale = 1

        self.ts = None
        self.ij = None
        self.hops = None

        sigma = np.array([
            [[0, 1], [1, 0]],
            [[0, -1j], [1j, 0]],
        ])
        self.rashba_matrix = 1j * (np.outer(self.lattice_vectors[:, 0], sigma[1]) + np.outer(self.lattice_vectors[:, 1], sigma[0])).reshape(2, 2, 2)
        self.dresselhaus_matrix = 1j * (np.outer(self.lattice_vectors[:, 0], sigma[0]) + np.outer(self.lattice_vectors[:, 1], sigma[1])).reshape(2, 2, 2)

        self.N1 = kwargs.get("N1", 1)
        self.N2 = kwargs.get("N2", 1)
        self.L = kwargs.get("L", 1)

        self.removed_sites = []


    def init(self):
        pass

    def copy(self):
        return copy.deepcopy(self)

    def set_n_orbitals(self, n_orbitals):
        self.n_orbitals = n_orbitals

    def add_sublattice(self, sublattice):
        # pylint: disable=attribute-defined-outside-init
        assert isinstance(sublattice, Lattice)

        self.sublattice = sublattice
        self.sublattice.set_n_orbitals(self.n_orbitals)
        self.aspect = self.sublattice.aspect
        if self.sublattice.basis is not None:
            self.basis = self.sublattice.basis

    def shape(self):
        if self.sublattice is None:
            # pylint: disable=import-outside-toplevel
            from .models import Point
            point = Point(self.bravais_lattice)
            self.add_sublattice(point)
        return self.N1, self.N2, self.sublattice.N1, self.sublattice.N2

    def preprocess_hoppings(self):
        pass

    def gen_coords(self):
        if self.coords is None:
            N1_super, N2_super, N1_sub, N2_sub = self.shape()
            a1 = self.lattice_vectors[0]
            a2 = self.lattice_vectors[1]
            self.coords = np.array([
                x * a1 + y * a2 for x, y in np.ndindex(N1_sub*N1_super, N2_sub*N2_super)
            ])

    def remove_site(self, site: Site):
        self.removed_sites.append(site)

    def __call__(self, params: Params, space: Space, superconducting=False, **kwargs):
        # pylint: disable=inconsistent-return-statements
        """Generate a list of hoppings"""

        if self.sublattice is None:
            # pylint: disable=import-outside-toplevel
            from .models import Point
            point = Point(self.bravais_lattice)
            self.add_sublattice(point)
        self.sublattice.set_n_orbitals(self.n_orbitals)

        if self.basis is None:
            self.basis = np.zeros((self.sublattice.N1, self.sublattice.N2, self.n_orbitals, 2))
            a1, a2 = self.lattice_vectors[0], self.lattice_vectors[1]
            for x, y in np.ndindex(self.sublattice.N1, self.sublattice.N2):
                coord = x * a1 + y * a2
                self.basis[x, y, :] = coord
            self.basis = self.basis.reshape(self.n_orbitals*self.sublattice.N1*self.sublattice.N2, 2)

        self.init()
        self.preprocess_hoppings()
        self.gen_coords()

        match space:
            case Space.RealSpace:
                return self.gen_hoppings_realspace(params, space, superconducting, **kwargs)
            case Space.KSpace:
                return self.gen_hoppings_kspace(params, space, superconducting, **kwargs)
            case Space.Ribbon:
                return self.gen_hoppings_ribbon(params, space, superconducting, **kwargs)
            case _:
                raise ValueError(f"Space {space} not implemented")

    def gen_hoppings_realspace(self, params, space, superconducting, impurities=None, replace_symbols=True, is_sublattice=False, trim=False):
        # pylint: disable=unsubscriptable-object, too-many-branches
        N1_super, N2_super, N1_sub, N2_sub = self.shape()

        _ts, _hops, _ij = self.ts[0], self.hops[0], self.ij[0]
        if superconducting:
            _ts, _hops, _ij = self.ts[1], self.hops[1], self.ij[1]

        _ts_sub, _ij_sub = self.sublattice(params, space, superconducting, replace_symbols=replace_symbols, is_sublattice=True)

        if is_sublattice:
            pbc = [False, False]
        else:
            if hasattr(params.pbc, "__len__"):
                pbc = params.pbc
            else:
                pbc = [params.pbc, params.pbc]
            pbc = np.array(pbc)

        valid_sites = np.zeros((N1_super, N2_super, N1_sub, N2_sub))
        for site in self.removed_sites:
            valid_sites[site.x, site.y, site.x_sub, site.y_sub] = 1

        removed_energy = params.get("removed_energy", 10)

        ts, ij = _gen_hoppings_realspace(self.n_orbitals, N1_super, N2_super, N1_sub, N2_sub, pbc, _ts, _hops, _ij, _ts_sub, _ij_sub, valid_sites, removed_energy=removed_energy)

        if impurities is not None:
            for impurity in impurities:
                _ts = impurity(params, space)
                for t, hop in zip(_ts, impurity.hoppings):
                    ts.append(t)
                    ij.append([impurity.x, impurity.y, hop.other.x, hop.other.y, hop.i, hop.j])
                    if hop.i != hop.j:
                        ts.append(t)
                        ij.append([hop.other.x, hop.other.y, impurity.x, impurity.y, hop.j, hop.i])

        if replace_symbols:
            for n, t in enumerate(ts):
                x0, y0, _, _, _, _ = ij[n]
                if isinstance(t, Symbol):
                    ts[n] = t.replace(params, x0, y0)

            ts = np.array(ts, dtype=complex)
            ij = np.array(ij, dtype=int)
        else:
            ts = np.array(ts, dtype=object)
            ij = np.array(ij, dtype=int)

        if trim:
            trim = []
            for n in range(ts.size):
                if ts[n] == 0 or ts[n] == removed_energy:
                    trim.append(n)

            ts = np.delete(ts, trim, 0)
            ij = np.delete(ij, trim, 0)

        return ts, ij

    def gen_hoppings_kspace(self, params, space, superconducting, k=None, direction=None, impurities=None):
        # pylint: disable=too-many-branches, unsubscriptable-object, consider-using-enumerate, too-many-statements
        if direction is not None:
            assert direction in ["a1", "a2", "both"]
        else:
            direction = "both"

        k = np.array(k)
        assert 0 < k.size < 3
        if k.size == 1:
            if direction == "a1":
                k = np.append(k, 0)
            elif direction == "a2":
                k = np.append(0, k)
            else:
                raise ValueError("Momenta must be 2D!")

        _ts, _hops, _ij = self.ts[0].copy(), self.hops[0].copy(), self.ij[0].copy()
        if superconducting:
            _ts, _hops, _ij = self.ts[1].copy(), self.hops[1].copy(), self.ij[1].copy()

        _ts_sub, _ij_sub = self.sublattice(params, Space.RealSpace, superconducting, is_sublattice=True)

        for n in range(len(_ts)):
            x, y, _, _, _, _ = _ij[n]
            _ts[n] = _ts[n].replace(params, x, y)

        hops = []
        ij = []
        ts = []

        ind = np.arange(self.sublattice.N1*self.sublattice.N2*self.n_orbitals).reshape(self.sublattice.N1, self.sublattice.N2, self.n_orbitals)

        # Intercell hops
        for n, t in enumerate(_ts):
            x0, y0, x1, y1, i, j = _ij[n]
            d1, d2 = _hops[n]
            t *= np.exp(1j * k @ (d1 * self.lattice_vectors[0] + d2 * self.lattice_vectors[1]))

            ii = ind[x0, y0, i]
            jj = ind[x1, y1, j]

            if t != 0:
                hops.append([d1, d2])
                ij.append([ii, jj])
                ts.append(t)

        # Intracell hops
        for n, t in enumerate(_ts_sub):
            x0, y0, x1, y1, i, j = _ij_sub[n]

            ii = ind[x0, y0, i]
            jj = ind[x1, y1, j]

            if t != 0:
                hops.append([0, 0])
                ij.append([ii, jj])
                ts.append(t)

        hops = np.array(hops, int)
        ij = np.array(ij, int)
        ts = np.array(ts, complex)

        if direction == "a1":
            for d2 in range(-self.hd, self.hd+1):
                if d2 != 0:
                    ts[hops[:, 1] == d2] = 0
        elif direction == "a2":
            for d1 in range(-self.hd, self.hd+1):
                if d1 != 0:
                    ts[hops[:, 0] == d1] = 0

        if impurities is not None:
            for impurity in impurities:
                _ts = impurity(params, space, lattice_vectors=self.lattice_vectors, k=k)
                for t, hop in zip(_ts, impurity.hoppings):
                    ts = np.append(ts, t)
                    ij = np.append(ij, [[hop.i, hop.j]], axis=0)
                    if hop.i != hop.j:
                        ij = np.append(ij, [[hop.j, hop.i]], axis=0)
                        ts = np.append(ts, np.conj(t))

        trim = []
        for n in range(ts.size):
            if ts[n] == 0:
                trim.append(n)

        ts = np.delete(ts, trim, 0)
        ij = np.delete(ij, trim, 0)

        return ts, ij

    def gen_hoppings_ribbon(self, params, space, superconducting, k=None, direction=None, impurities=None):
        # pylint: disable=too-many-branches, unsubscriptable-object, consider-using-enumerate
        if direction is not None:
            assert direction in ["a1", "a2"]
        else:
            direction = "a1"

        k = np.array(k)
        assert 0 < k.size < 3
        if k.size == 1:
            if direction == "a1":
                k = np.append(k, 0)
            elif direction == "a2":
                k = np.append(0, k)
            else:
                raise ValueError("Must Fourier transform along either a1 or a2!")

        _ts, _hops, _ij = self.ts[0], self.hops[0], self.ij[0]
        if superconducting:
            _ts, _hops, _ij = self.ts[1], self.hops[1], self.ij[1]

        _ts_sub, _ij_sub = self.sublattice(params, Space.RealSpace, superconducting, is_sublattice=True)

        for n in range(len(_ts)):
            x, y, _, _, _, _ = _ij[n]
            if isinstance(_ts[n], Symbol):
                _ts[n] = _ts[n].replace(params, x, y)
        for n in range(len(_ts_sub)):
            x, y, _, _, _, _ = _ij_sub[n]
            if isinstance(_ts_sub[n], Symbol):
                _ts_sub[n] = _ts_sub[n].replace(params, x, y)

        pbc = params.pbc

        _ts = np.array(_ts, dtype=complex)
        _hops = np.array(_hops, dtype=int)
        _ij = np.array(_ij, dtype=int)
        _ts_sub = np.array(_ts_sub, dtype=complex)
        _ij_sub = np.array(_ij_sub, dtype=int)

        ts, ij = _gen_hoppings_ribbon(k, self.lattice_vectors, self.n_orbitals, self.L, direction, pbc, _ts, _hops, _ij, _ts_sub, _ij_sub)

        if impurities is not None:
            if direction == "a1":
                for impurity in impurities:
                    _ts = impurity(params, space, direction=direction, lattice_vectors=self.lattice_vectors, k=k)

                    for t, hop in zip(_ts, impurity.hoppings):
                        ts.append(t)
                        ij.append([impurity.y, hop.other.y, hop.i, hop.j])
                        if hop.i != hop.j:
                            ts.append(t)
                            ij.append([hop.other.y, impurity.y, hop.j, hop.i])
            elif direction == "a2":
                for impurity in impurities:
                    _ts = impurity(params, space, direction=direction, lattice_vectors=self.lattice_vectors, k=k)

                    for t, hop in zip(_ts, impurity.hoppings):
                        ts.append(t)
                        ij.append([impurity.x, hop.other.x, hop.i, hop.j])
                        if hop.i != hop.j:
                            ts.append(t)
                            ij.append([hop.other.x, impurity.x, hop.j, hop.i])

        ts = np.array(ts, dtype=complex)
        ij = np.array(ij, dtype=int)

        return ts, ij
