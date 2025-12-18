# pylint: disable=line-too-long, fixme, too-many-arguments, too-many-positional-arguments, invalid-name, too-many-locals, too-many-instance-attributes, use-dict-literal, bare-except

"""
A System is a representation of a particular Hamiltonian, including
e.g. disorder, impurities, removed sites, particular parameters.

A System is based around a Lattice. A Lattice must be defined before
a System can be created.
"""

import warnings
import numpy as np
from scipy import sparse
from scipy import optimize
from keino import Params, k_path, ndindex
from pfapack import pfaffian as pf
try:
    from pfapack.ctypes import pfaffian as cpf
except:
    from pfapack.pfaffian import pfaffian as cpf
from .lattice import Space, Lattice
from .impurity import Impurity
from .utils import ragged_to_ndarray
from .chern import calculate as calculate_chern
from .geometry import Geometry
from .models import Square, Triangular, Graphene

def _realspace(N1, N2, n_orbitals, n_impurities, ts, ij):
    tot = ts.size
    _ij = np.zeros((2, tot), np.int64)
    v = np.zeros((tot), np.complex128)

    ind1 = np.arange(N1 * N2 * n_orbitals).reshape(N1, N2, n_orbitals)
    ind2 = np.arange(N1 * N2 * n_orbitals, N1 * N2 * n_orbitals + N1 * N2 * n_orbitals * n_impurities).reshape(N1, N2, n_orbitals*n_impurities)
    ind = np.concat((ind1, ind2), axis=2)

    for n in range(ts.size):
        x0, y0, x1, y1, i, j = ij[n]
        v[n] = ts[n]
        _ij[0, n] = ind[x0, y0, i]
        _ij[1, n] = ind[x1, y1, j]

    return v, _ij

def _kspace(n_orbitals, ij, ts):
    H0 = np.zeros((n_orbitals, n_orbitals), np.complex128)
    for n in range(ts.size):
        i, j = ij[n]
        t = ts[n]

        H0[i, j] += t
    return H0

def _ribbon(L, n_orbitals, n_impurities, ts, ij):
    tot = len(ts)
    _ij = np.zeros((2, tot), np.int64)
    v = np.zeros((tot), np.complex128)

    ind1 = np.arange(L * n_orbitals).reshape(L, n_orbitals)
    ind2 = np.arange(L * n_orbitals, L * n_orbitals + L * n_orbitals * n_impurities).reshape(L, n_orbitals*n_impurities)
    ind = np.concat((ind1, ind2), axis=1)

    for n in range(ts.size):
        x0, x1, i, j = ij[n]
        v[n] = ts[n]
        _ij[0, n] = ind[x0, i]
        _ij[1, n] = ind[x1, j]

    return v, _ij

class System():
    def __init__(self, space: Space, lattice: Lattice, params: Params, spinful=True, n_orbitals=None):
        # pylint: disable=no-member, too-many-branches
        warnings.simplefilter("ignore", category=np.exceptions.ComplexWarning)

        if isinstance(lattice, str):
            match lattice:
                case "square":
                    lattice = Square()
                case "triangular":
                    lattice = Triangular()
                case "graphene":
                    lattice = Graphene()
                case _:
                    raise ValueError(f"Unknown lattice {lattice}!")

        self.lattice = lattice.copy()
        if self.lattice.n_orbitals is not None:
            n_orbitals = self.lattice.n_orbitals

        if n_orbitals is None:
            self.spinful = spinful
            self.n_orbitals = 2 if spinful else 1
        else:
            self.spinful = not bool(n_orbitals)
            self.n_orbitals = n_orbitals

        self.params = Params(params)
        self.space = Space(space)
        self.lattice.set_n_orbitals(self.n_orbitals)
        self.lattice_vectors = self.lattice.lattice_vectors
        self.recip_vectors = 2 * np.pi * np.eye(2) @ np.linalg.inv(self.lattice_vectors.T)

        self.N1 = -1
        self.N2 = -1
        self.L = -1
        match self.space:
            case Space.RealSpace:
                self.N1 = self.params.N1
                self.N2 = self.params.N2
            case Space.Ribbon:
                self.L = self.params.L
                if "N1" in self.params :
                    self.N1 = self.params.N1
                if "N2" in self.params:
                    self.N2 = self.params.N2
            case Space.KSpace:
                self.N1 = 1
                self.N2 = 1
                if "N1" in self.params :
                    self.N1 = self.params.N1
                if "N2" in self.params:
                    self.N2 = self.params.N2
            case _:
                raise ValueError(f"Space {self.space} not implemented")

        self.lattice.N1 = self.N1
        self.lattice.N2 = self.N2
        if space == Space.Ribbon:
            self.lattice.N1 = self.lattice.N2 = self.lattice.L = self.L
        if space == Space.KSpace:
            self.lattice.N1 = self.lattice.N2 = 1

        if self.is_superconducting():
            if np.isscalar(self.params.Delta):
                # Assume s-wave superconductivity
                self.params.Delta = Params(dict(s={'0': self.params.Delta, '1': 0, '2': 0}, p={'0': 0, '1': 0}, d={'0': 0, '1': 0}, f={'0': 0, '1': 0}))

        self.impurities = []
        self.geometry = None

    def shape(self):
        return self.lattice.shape()

    def get_block_dimension(self):
        """Return the size of each block in the Hamiltonian"""
        _, _, N1_sub, N2_sub = self.lattice.shape()
        dim = N1_sub * N2_sub * self.n_orbitals
        return dim

    def get_dimension(self):
        """Return the overall dimension of the Hamiltonian matrix"""
        match self.space:
            case Space.KSpace:
                return self.get_block_dimension() + self.n_orbitals * len(self.impurities)
            case Space.Ribbon:
                return self.get_block_dimension() * self.L + self.n_orbitals * len(self.impurities)
            case Space.RealSpace:
                return self.get_block_dimension() * self.N1 * self.N2 + self.n_orbitals * len(self.impurities)
            case _:
                raise ValueError(f"Space {self.space} not implemented")

    def get_dimension_split(self):
        """
        Return the overall dimension of the Hamiltonian matrix, split
        into the dimension of the underlying lattice, and the dimension
        of any impurities
        """
        match self.space:
            case Space.KSpace:
                return self.get_block_dimension(), self.n_orbitals * len(self.impurities)
            case Space.Ribbon:
                return self.get_block_dimension() * self.L, self.n_orbitals * len(self.impurities)
            case Space.RealSpace:
                return self.get_block_dimension() * self.N1 * self.N2, self.n_orbitals * len(self.impurities)
            case _:
                raise ValueError(f"Space {self.space} not implemented")

    def coords(self):
        _ = self.lattice(self.params, self.space)
        return self.lattice.coords

    def is_superconducting(self):
        return bool(self.params.get("Delta", False))

    def add_impurity(self, coord=None):
        """
        Add an impurity to the system.

        Parameters
        ----------
        coord: pair[float]
            Optional, coordinate of the impurity. Used for plotting

        Returns
        ----------
        The unique index of the impurity
        """
        idx = len(self.impurities)
        N1, N2, N1_sub, N2_sub = self.shape()
        impurity = Impurity(idx, N1, N2, N1_sub, N2_sub, spinful=self.spinful, coord=coord)
        self.impurities.append(impurity)
        return idx

    def set_geometry(self, shape, sites=None, coords=None):
        N1, N2, N1_sub, N2_sub = self.shape()
        self.geometry = Geometry(N1, N2, N1_sub, N2_sub, shape, self.lattice.bravais_lattice, self.params.impurities, self.space, self.spinful, sites=sites, coords=coords)
        self.impurities = self.geometry()

    def hamiltonian(self, *args, **kwargs):
        # pylint: disable=inconsistent-return-statements
        """Construct the Hamiltonian matrix"""

        match self.space:
            case Space.RealSpace:
                return self.hamiltonian_realspace(*args, **kwargs)
            case Space.KSpace:
                return self.hamiltonian_kspace(*args, **kwargs)
            case Space.Ribbon:
                return self.hamiltonian_ribbon(*args, **kwargs)
            case _:
                raise ValueError(f"Space {self.space} not implemented")

    def hamiltonian_realspace(self, dense=False, test_hermitian=False, postprocess_hoppings=None, trim=False):
        ts, ij = self.lattice(self.params, self.space, impurities=self.impurities, trim=trim)

        n_orbitals = self.get_block_dimension()
        if postprocess_hoppings is not None:
            ts, ij = postprocess_hoppings(self.params, ts, ij)

        N1, N2, _, _ = self.shape()
        dim = self.get_dimension()

        v, ij = _realspace(N1, N2, n_orbitals, len(self.impurities), ts, ij)
        H = sparse.coo_matrix((v, ij), shape=(dim, dim))

        if test_hermitian:
            test = np.abs(H - H.conj().T).max()
            assert test < 1e-12, test

        if not self.is_superconducting():
            if dense:
                H = H.toarray()
                if trim:
                    H = H[~np.all(H == 0, axis=1)]
                    H = H[:, ~np.all(H == 0, axis=0)]
            return H

        sc_ts, sc_ij = self.lattice(self.params, self.space, superconducting=True)
        v, ij = _realspace(N1, N2, n_orbitals, len(self.impurities), sc_ts, sc_ij)
        D = sparse.coo_matrix((v, ij), shape=(dim, dim))

        H_BdG = sparse.bmat([
            [H, D],
            [-D, -H.T]
        ])
        H_BdG.eliminate_zeros()

        if dense:
            if trim:
                H_BdG = H_BdG[~np.all(H_BdG == 0, axis=1)]
                H_BdG = H_BdG[:, ~np.all(H_BdG == 0, axis=0)]
            return H_BdG.toarray()

        return H_BdG

    def hamiltonian_kspace(self, k, test_hermitian=False, trim=False, postprocess_hoppings=None, **kwargs):
        # pylint: disable=unused-argument
        # dense argument is needed for compatibility
        def block(k):
            ts, ij = self.lattice(self.params, self.space, k=k, direction=direction, impurities=self.impurities)
            if postprocess_hoppings is not None:
                ts, ij = postprocess_hoppings(self.params, ts, ij)

            Hk = _kspace(dim, ij, ts)
            return Hk

        direction = self.params.get("direction", "both")
        dim = self.get_dimension()
        k = np.array(k)

        Hk1 = block(k)

        if test_hermitian:
            test = np.abs(Hk1 - Hk1.conj().T).max()
            assert test < 1e-12, test

        if not self.is_superconducting():
            # Remove empty rows and cols
            if trim:
                Hk1 = Hk1[~np.all(Hk1 == 0, axis=1)]
                Hk1 = Hk1[:, ~np.all(Hk1 == 0, axis=0)]
            return Hk1

        sc_ts, sc_ij = self.lattice(self.params, self.space, k=k, superconducting=True, direction=direction)
        D = _kspace(dim, sc_ij, sc_ts)
        tmp = ragged_to_ndarray([Hk1, D])
        Hk1, D = tmp[0], tmp[1]

        Hk2 = block(-k)
        H_BdG = np.block([
            [Hk1, D],
            [-D, -Hk2.T]
        ])

        # Remove empty rows and cols
        if trim:
            H_BdG = H_BdG[~np.all(H_BdG == 0, axis=1)]
            H_BdG = H_BdG[:, ~np.all(H_BdG == 0, axis=0)]
        return H_BdG

    def hamiltonian_ribbon(self, k, test_hermitian=False, dense=False, postprocess_hoppings=None):
        def block(k):
            ts, ij = self.lattice(self.params, self.space, k=k, direction=direction, impurities=self.impurities)

            if postprocess_hoppings is not None:
                ts, ij = postprocess_hoppings(self.params, ts, ij)

            v, ij = _ribbon(self.L, n_orbitals, len(self.impurities), ts, ij)
            Hk = sparse.coo_matrix((v, ij), shape=(dim, dim))
            Hk.eliminate_zeros()
            return Hk

        direction = self.params.get("direction", "a1")
        n_orbitals = self.get_block_dimension()
        dim = self.get_dimension()

        Hk1 = block(k)

        if test_hermitian:
            test = np.abs(Hk1 - Hk1.conj().T).max()
            assert test < 1e-12, test

        if not self.is_superconducting():
            if dense:
                return Hk1.toarray()
            return Hk1

        Hk2 = block(-k)

        ts, ij = self.lattice(self.params, self.space, superconducting=True, k=k, direction=direction)
        v, ij = _ribbon(self.L, n_orbitals, len(self.impurities), ts, ij)
        D = sparse.coo_matrix((v, ij), shape=(dim, dim))
        H_BdG = sparse.bmat([
            [Hk1, D],
            [-D, -Hk2.T]
        ])

        if dense:
            H_BdG = H_BdG.toarray()

        return H_BdG

    def plot(self, axis=None, colours=None, axis_scale=5, site_scale=3, aspect=None, filename=None):
        # pylint: disable=import-outside-toplevel, raise-missing-from, too-many-branches, too-many-statements, unused-variable, import-error, too-many-function-args, no-member
        """Plot the system"""
        try:
            import matplotlib.pyplot as plt
            from matplotlib.collections import LineCollection
        except:
            raise ValueError("matplotlib is not installed!")

        impurities = self.impurities if len(self.impurities) > 0 else None
        ts, ij = self.lattice(self.params, Space.RealSpace, impurities=impurities)
        hd = self.lattice.hd
        dim = self.get_block_dimension()

        N1_super, N2_super, N1_sub, N2_sub = self.shape()

        _aspect = N2_super / N1_super * self.lattice.aspect
        aspect = _aspect if aspect is None else aspect

        if hasattr(self.lattice.plot_scale, "__len__"):
            a1 = self.lattice.plot_scale[0] * self.lattice.lattice_vectors[0]
            a2 = self.lattice.plot_scale[1] * self.lattice.lattice_vectors[1]
        else:
            a1, a2 = self.lattice.plot_scale * self.lattice.lattice_vectors

        if axis is None:
            fig, axis = plt.subplots(figsize=(axis_scale, axis_scale*aspect))

        if colours is None:
            colours = "black"
        else:
            _colours = np.array(colours).reshape(N1_sub, N2_sub)
            colours = np.empty((N1_super, N1_sub, N2_super, N2_sub), object)
            for i, j in ndindex(N1_sub, N2_sub):
                colours[:, i, :, j] = _colours[i, j]
            colours = colours.reshape(N1_super*N1_sub*N2_super*N2_sub)
            colours = [str(c) for c in colours]

        scale = site_scale * np.ones(N1_super*N2_super*N1_sub*N2_sub).reshape(N1_super, N2_super, N1_sub, N2_sub)
        for site in self.lattice.removed_sites:
            x, y, x_sub, y_sub = site
            scale[x, y, x_sub, y_sub] = 0
        scale = scale.reshape(N1_super*N2_super*N1_sub*N2_sub)

        axis.scatter(self.lattice.coords[:, 0], self.lattice.coords[:, 1], scale, colours)

        if self.impurities is not None:
            for impurity in self.impurities:
                x, y = impurity.coord[0], impurity.coord[1]
                x, y = x * a1 + y * a2
                axis.scatter(x, y, 30, "tab:red", marker="*")

        def coords_in(x, y, eps=1e-12):
            for i, j in self.lattice.coords:
                if (i-x) <= eps and (j-y) <= eps:
                    return True
            return False

        def impurity_coords(i):
            # idx = (i % dim) // self.n_orbitals
            if self.spinful:
                if i % 2:
                    idx = (i - dim - 1) // 2
                else:
                    idx = (i - dim) // 2
            else:
                idx = i - dim
            idx = int(idx)
            return self.impurities[idx].coord

        # slv = self.lattice.sublattice.lattice_vectors
        lines = []
        lines_imp = []
        lws = []
        lws_imp = []
        for n, t in enumerate(ts):
            lw = 0.5 * t
            x0, y0, x1, y1, i, j = ij[n]

            if i >= dim:
                x0, y0 = impurity_coords(i)
            if j >= dim:
                x1, y1 = impurity_coords(j)

            if self.lattice.basis is not None:
                if i < dim:
                    basis0 = self.lattice.basis[i]
                    x0, y0 = x0 * N1_sub * a1 + y0 * N2_sub * a2
                    x0, y0 = (x0, y0) + basis0
                    # x0, y0 = (x0, y0) + slv @ basis0
                else:
                    x0, y0 = x0 * a1 + y0 * a2
                if j < dim:
                    basis1 = self.lattice.basis[j]
                    x1, y1 = x1 * N1_sub * a1 + y1 * N2_sub * a2
                    x1, y1 = (x1, y1) + basis1
                    # x1, y1 = (x1, y1) + slv @ basis1
                else:
                    x1, y1 = x1 * a1 + y1 * a2
            else:
                x0, y0 = x0 * a1 + y0 * a2
                x1, y1 = x1 * a1 + y1 * a2

            if not self.params.pbc and not coords_in(x1, y1):
                lw = 0
            if not self.params.pbc and not coords_in(x0, y0):
                lw = 0
            if i < dim and j < dim:
                if abs(lw) > 0:
                    lines.append([(x0, y0), (x1, y1)])
                    lws.append(lw)
            else:
                if abs(lw) > 0:
                    lines_imp.append([(x0, y0), (x1, y1)])
                    lws_imp.append(lw)

        lc = LineCollection(lines, colors="black", linewidths=lws)
        axis.add_collection(lc)

        lc = LineCollection(lines_imp, colors="red", linewidths=lws_imp)
        axis.add_collection(lc)

        if filename:
            plt.savefig(filename, bbox_inches="tight")
        plt.show()

    def __eq__(self, other, threshold=1e-13, debug=False):
        """Check if two Systems are equivalent. Useful for testing."""
        if isinstance(other, str):
            other = Space(other)

        if isinstance(other, Space):
            other = System(other, self.lattice, self.params)
            if self.geometry is not None or len(self.impurities) > 0:
                warnings.warn("Warning: geometry or impurities set. self and other may not have consistent shapes.")
        elif other.space == self.space:
            dim0 = self.get_block_dimension() * self.N1 * self.N2 + self.n_orbitals * len(self.impurities)
            dim1 = other.get_block_dimension() * other.N1 * other.N2 + other.n_orbitals * len(other.impurities)
            assert dim0 == dim1, f"{dim0} != {dim1}"

        def calc_spectra(sys):
            if sys.space == Space.RealSpace:
                E = sys.diagonalise(dense=True, cache=False)

            if sys.space == Space.KSpace:
                sym_points1 = np.array([
                    [0, 0],
                    [1, 0],
                ])
                sym_points2 = np.array([
                    [0, 0],
                    [0, 1],
                ])

                points1 = np.dot(sym_points1, sys.recip_vectors)
                points2 = np.dot(sym_points2, sys.recip_vectors)
                dim = sys.get_dimension()
                if sys.is_superconducting():
                    dim *= 2

                X = np.array(k_path(sys.N1, points1, endpoint=False))
                Y = np.array(k_path(sys.N2, points2, endpoint=False))

                E = np.zeros((sys.N1, sys.N2, dim))
                for x, y in np.ndindex(sys.N1, sys.N2):
                    k = X[x] + Y[y]
                    Hk = sys.hamiltonian(k, test_hermitian=True)
                    if Hk.shape == (0, 0):
                        continue
                    E[x, y] = np.linalg.eigvalsh(Hk)
                E = np.sort(E.flatten())

            if sys.space == Space.Ribbon:
                sym_points1 = np.array([
                    [0, 0],
                    [1, 0],
                ])
                sym_points2 = np.array([
                    [0, 0],
                    [0, 1],
                ])

                points1 = np.dot(sym_points1, sys.recip_vectors)
                points2 = np.dot(sym_points2, sys.recip_vectors)

                X = np.array(k_path(sys.N1, points1, endpoint=False))
                Y = np.array(k_path(sys.N2, points2, endpoint=False))

                dim = sys.get_dimension()
                if self.is_superconducting():
                    dim *= 2

                nk = sys.N1 if sys.params.direction == "a1" else sys.N2
                E = np.zeros((nk, dim))
                for n in range(nk):
                    k = X[n] if sys.params.direction == "a1" else Y[n]
                    H = sys.hamiltonian(k, dense=True)
                    E[n] = np.linalg.eigvalsh(H)
                E = np.sort(E.flatten())

            return E

        if not self.params.get("pbc", True):
            warnings.warn("Warning: open boundaries detected")

        E = calc_spectra(self)
        E_other = calc_spectra(other)
        test = abs(E - E_other).max()

        if debug:
            print(test)
            return E, E_other

        test = test < threshold
        return test

    def diagonalise(self, return_eigenvectors=False, dense=False, n_energies=20, k=None, cache=True, refresh_cache=False, retry=False, always_succeed=False, sigma=0, **kwargs):
        # pylint: disable=too-many-branches, too-many-statements, import-outside-toplevel, unnecessary-lambda-assignment
        """
        Diagonalise the Hamiltonian matrix.
        This function optionally can cache the result using joblib.

        Parameters
        ----------
        return_eigenvectors: bool
        dense: bool
            Whether to construct then diagonalise the Hamiltonian matrix
            as a dense matrix (all eigenvalues) or sparse (n_energies around E = sigma)
        n_energies: int
            Number of energies to return, if doing a sparse diagonalisation
        sigma: float
            energy around which to diagonalise (sparse)
        k: float | pair[float] | array[float] | array[pair[float]]
            momentum to diagonalise around (only if self.space == Space.KSpace)
        cache: bool
            Cache the results
        refresh_cache: bool
            Ignore cached result and recalculate
        retry:
            Sometimes a sparse diagonalisation will fail. If it does and
            retry == True, try to do a dense diagonalisation. Useful for
            unsupervised (i.e. on a cluster) jobs.
        always_succeed: bool
            If the diagonalisation fails, throw away the error and return
            nan arrays with the correct shape. Useful for unsupervised
            (i.e. on a cluster) jobs
        kwargs:
            passed to self.hamiltonian()

        Returns
        ----------
        Either the eigenvalues or the eigenvalues and eigenvectors
        """
        if cache:
            from joblib import Memory
            memory = Memory("cache", verbose=0)
            if refresh_cache:
                cache_validation_callback = lambda x: False
            else:
                cache_validation_callback = lambda x: True
            cache = memory.cache(cache_validation_callback=cache_validation_callback)
        else:
            cache = lambda f: f

        @cache
        def work(params, lattice, space, dense, k, dim):
            # pylint: disable= unused-argument, broad-exception-caught
            # Here need arguments lattice, space, params to cache correctly
            if self.space == Space.RealSpace:
                H = self.hamiltonian(dense=dense, **kwargs)
            else:
                H = self.hamiltonian(dense=dense, k=k, **kwargs)

            if dense:
                try:
                    en, wf = np.linalg.eigh(H)
                except Exception as e:
                    if always_succeed:
                        en = np.empty(dim)
                        wf = np.empty((dim, dim), complex)
                    else:
                        raise ValueError(f"Could not diagonalise dense matrix: {e}") from e
            else:
                try:
                    en, wf = sparse.linalg.eigsh(H, sigma=sigma, k=n_energies)
                except Exception as e:
                    if retry:
                        return work(self.params, self.lattice, self.space, dense=True, k=k, dim=dim)
                    if always_succeed:
                        en = np.empty(dim)
                        wf = np.empty((dim, dim), complex)
                    else:
                        raise ValueError(f"Could not diagonalise sparse matrix: {e}") from e
                idx = np.argsort(en)
                en = en[idx]
                wf = wf[:, idx]
            return en, wf

        if self.space == Space.KSpace:
            dense = True

        dim0 = self.get_dimension()
        dim1 = n_energies
        if not dense:
            dim = dim0 if dim0 < dim1 else dim1
        else:
            dim = dim0

        if self.is_superconducting():
            dim *= 2

        match self.space:
            case Space.KSpace | Space.Ribbon:
                if hasattr(k, "__len__"):
                    k = np.squeeze(k)
                    assert len(k.shape) in [1, 2]
                    if len(k.shape) == 1 and k.shape[0] == 2:
                        k = k[None, :]
                    if len(k.shape) == 1:
                        nk = k.size
                    else:
                        nk, _ = k.shape

                    en = np.zeros((nk, dim))
                    wf = np.zeros((nk, dim, dim), complex)
                    for i in range(nk):
                        _en, _wf = work(self.params, self.lattice, self.space,dense, k[i], dim)
                        if len(_en) == dim:
                            en[i], wf[i] = _en, _wf
                else:
                    en, wf = work(self.params, self.lattice, self.space,dense, k, dim)
            case Space.RealSpace:
                en, wf = work(self.params, self.lattice, self.space,dense, k, dim)
            case _:
                raise ValueError(f"Space {self.space} not implemented")

        if return_eigenvectors:
            return en, wf

        return en

    def calc_ldos(self, omega, delta=1e-3, **kwargs):
        """
        Calculate the Local Density of States

        Parameters
        ----------
        omega: float | numpy.ndarray
            energies to calculate LDOS for
        delta: float
            Lorentzian broadening to apply
        kwargs:
            passed to self.diagonalise()

        Returns
        ----------
        The LDOS, reshaped to match the basis
        """
        if self.space is not Space.RealSpace:
            raise ValueError("LDOS can only be calculated in Real Space!")

        en, wf = self.diagonalise(return_eigenvectors=True, dense=True, **kwargs)

        abs2wf = np.abs(wf)**2
        kernel = delta / (np.pi * ((en[:, None] - omega[None, :])**2 + delta**2))
        ldos = abs2wf.dot(kernel)
        ldos = np.squeeze(ldos)
        dim = self.get_dimension()

        if self.is_superconducting():
            ldos = ldos.reshape(2, dim, len(omega))
        else:
            ldos = ldos.reshape(dim, len(omega))

        n_impurities = len(self.impurities)
        N1_super, N2_super, N1_sub, N2_sub = self.shape()
        if n_impurities > 0:
            dim0, _ = self.get_dimension_split()
            if self.is_superconducting():
                ldos0 = ldos[:, :dim0].reshape(2, N1_super, N2_super, N1_sub, N2_sub, self.n_orbitals, len(omega))
                ldos1 = ldos[:, dim0:].reshape(2, len(self.impurities), self.n_orbitals, len(omega))
            else:
                ldos0 = ldos[:dim0].reshape(2, N1_super, N2_super, N1_sub, N2_sub, self.n_orbitals, len(omega))
                ldos1 = ldos[dim0:].reshape(len(self.impurities), self.n_orbitals, len(omega))
            ldos = (ldos0, ldos1)
        else:
            if self.is_superconducting():
                ldos = ldos.reshape(2, N1_super, N2_super, N1_sub, N2_sub, self.n_orbitals, len(omega))
            else:
                ldos = ldos.reshape(N1_super, N2_super, N1_sub, N2_sub, self.n_orbitals, len(omega))

        return ldos

    def calc_chern(self, Nk=21, offset=0, n_bands=None, **kwargs):
        """Calculate the Chern number with the Fukui-Hatsugai method"""
        assert self.space == Space.KSpace

        Kx = np.linspace(-np.pi+offset, np.pi+offset, Nk)
        Ky = np.linspace(-np.pi+offset, np.pi+offset, Nk)

        if n_bands is None:
            n_bands = self.get_dimension()

        bands = [{} for n in range(n_bands)]

        for x_index, x in enumerate(Kx):
            for y_index, y in enumerate(Ky):
                k = [(x, y)]
                _, wf = self.diagonalise(return_eigenvectors=True, k=k, **kwargs)
                for i in range(n_bands):
                    bands[i][(x_index, y_index)] = wf[0, :, i]

        Cs = [calculate_chern(band, Nk) for band in bands]
        C = sum(Cs)
        C = np.round(C)
        return C

    def calc_majorana(self, do_tests=False, fast=True):
        """Calculate the Majorana number"""
        dim = self.get_dimension()

        U = np.block([
            [np.eye(dim), np.eye(dim)],
            [-1j * np.eye(dim), 1j * np.eye(dim)]
        ])

        sym_points = [[0, 0], [0.5, 0]]
        points = np.dot(sym_points, self.recip_vectors)

        H = [
            self.hamiltonian(points[0]),
            self.hamiltonian(points[1])
        ]

        A = [
            -0.5j * U @ H[0] @ U.T.conj(),
            -0.5j * U @ H[1] @ U.T.conj(),
        ]

        if do_tests:
            test = abs((A[0] + A[0].T).max())
            assert test < 4e-14, f'{test}'
            test = abs((A[1] + A[1].T).max())
            assert test < 4e-14, f'{test}'

        if fast:
            Pf = [
                cpf(A[0]),
                cpf(A[1])
            ]
        else:
            Pf = [
                pf.pfaffian(A[0]),
                pf.pfaffian(A[1])
            ]

        if do_tests:
            left = Pf[0]**2
            right = np.linalg.det(A[0])
            assert np.isclose(left, right), f'{Pf[0]}, {left}, {right}'
            left = Pf[1]**2
            right = np.linalg.det(A[1])
            assert np.isclose(left, right), f'{Pf[1]}, {left}, {right}'

        M = np.sign(Pf[0] * Pf[1]).real
        return M

    def winding_number(self, do_zk=False, do_theta_k=True, Nk=128):
        """
        Calculate the winding number,

        Parameters
        ----------
        do_zk, do_theta_k: bool
            Specify method to use
        Nk: int
            number of momenta-space points

        Returns
        ----------
        The winding number
        """
        def Vk(k):
            U = np.block([
                [np.eye(dim), np.eye(dim)],
                [-1j * np.eye(dim), 1j * np.eye(dim)]
                ])
            H = self.hamiltonian(k=k)
            Ak = -0.5j * U @ H @ U.conj().T
            Vk = Ak[:dim, dim:]
            return Vk

        def zk(k):
            detVk = np.linalg.det(Vk(k))
            zk = detVk / np.abs(detVk)
            return zk

        def theta_k(k):
            return -1j * np.log(np.linalg.det(Vk(k)))

        def shift_angle(theta):
            m = np.floor(np.diff(theta, prepend=theta[-1]) / (2*np.pi) + 0.5)
            return m.sum()

        assert self.is_superconducting()
        assert self.space == Space.KSpace
        assert do_zk or do_theta_k
        dim = self.get_dimension()

        direction = self.params.get("direction", "a1")
        if direction == "a1":
            sym_points1 = np.array([
                [0, 0],
                [1, 0],
            ])
        if direction == "a2":
            sym_points2 = np.array([
                [0, 0],
                [0, 1],
            ])

        points = np.dot(sym_points, self.recip_vectors)
        Ks = k_path(Nk, points)

        if do_zk:
            intg = [zk(k) for k in Ks]
            W = shift_angle(np.angle(intg))

        if do_theta_k:
            intg = [theta_k(k) for k in Ks]
            W = shift_angle(np.real(intg))

        return W

    def calc_gap(self, Ks=None, **kwargs):
        """Calculate the gap of the spectra"""
        match self.space:
            case Space.KSpace:
                if Ks is not None:
                    Ek = self.diagonalise(k=Ks, **kwargs)
                    gap = abs(Ek.flatten()).min()
                else:
                    dim = self.get_dimension()
                    x0 = (0, 0)

                    def fun(k):
                        E = self.diagonalise(k=k, **kwargs)
                        return E[0][dim]

                    res = optimize.minimize(fun, x0, method="COBYLA")
                    gap = res.fun
            case Space.RealSpace:
                en = self.diagonalise(**kwargs)
                gap = abs(en).min()
            case _:
                raise ValueError(f"Space {self.space} is not supported")

        return gap

    def superconducting_correlations(self, **kwargs):
        """
        Calculate superconducting correlations
        """
        assert self.is_superconducting()

        match self.space:
            case Space.KSpace:
                X = 2 * np.pi / self.params.N1 * np.arange(N1)
                Y = 2 * np.pi / self.params.N2 * np.arange(N2)
                dim = self.get_dimension()
                Ek = np.empty((self.params.N1, self.params.N2, 2*dim))
                nk = np.empty((self.params.N1, self.params.N2, 2*dim, 2*dim), complex)
                for i, j in np.ndindex(self.params.N1, self.params.N2):
                    x = X[i]
                    y = Y[j]
                    k = (x, y)
                    Ek[i, j], nk[i, j] = self.diagonalise(return_eigenvectors=True, **kwargs)

                Pk = np.empty((self.params.N1, self.params.N2, 2*dim, 2*dim), complex)
                for i, j in np.ndindex(self.params.N1, self.params.N2):
                    Pk[i, j] = nk[i, j, :, :dim].dot(nk[i, j, :, :dim].conj().T)

                Pk = Pk.reshape(self.params.N1, self.params.N2, 2, dim, 2, 2, dim, 2)
                return Pk

            case Space.RealSpace:
                dim = self.get_dimension()
                en, wf = self.diagonalise(return_eigenvectors=True, **kwargs)
                Pk = wf[:, :dim].dot(wf[:, :dim].conj().T)
                return Pk
            case _:
                raise ValueError(f"Space {self.space} not implemented!")

    def fermi_velocities(self):
        def get_fermi_energy_crossings(en):
            crossings = []
            for i, (previous, current) in enumerate(zip(en, en[1:])):
                if previous > 0 and current < 0:
                    crossings.append((i, i+1))
                elif previous < 0 and current > 0:
                    crossings.append((i, i+1))
            return crossings

        X = np.linspace(-np.pi, np.pi, self.params.N1)
        Y = np.linspace(-np.pi, np.pi, self.params.N2)
        Ks = np.meshgrid(X, Y)

        p = self.params.copy()
        self.params.pop("Delta")

        Ek = self.diagonalise(k=Ks)
        velocities = []
        for en in Ek.T:
            crossings = get_fermi_energy_crossings(en)
            crossings = [c for c in crossings if len(c) > 0]

            for i, j in crossings:
                Es = en[i:j+1]
                vf = (Es[1] - Es[0]) / (Ks[1, 1] - Ks[0, 1])
                velocities.append(vf)
        return np.array(velocities)

    def coherence_length(self):
        X = np.linspace(-np.pi, np.pi, self.params.N1)
        Y = np.linspace(-np.pi, np.pi, self.params.N2)
        Ks = np.meshgrid(X, Y)

        gap = self.calc_gap(Ks)
        vF = self.fermi_velocities()

        coherence_lengths = vF / gap
        coherence_lengths = np.round(coherence_lengths, 10)
        coherence_lengths = np.array(list(set(abs(coherence_lengths))))
        return min(coherence_lengths)
