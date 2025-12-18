import numpy as np
from datetime import datetime, timezone
from keino import Params, k_path
from ristikko import System, Space, models, Symbol, Site

def test_kspace_vs_analytic():
    seed = int((datetime.now(timezone.utc) - datetime(1970, 1, 1, tzinfo=timezone.utc)).total_seconds())
    rng = np.random.default_rng(seed)
    rands = rng.normal(0, 1, 7)
    params = dict(
            t = rands[0],
            mu = rands[1],
            Jx = rands[2],
            Jy = rands[3],
            Jz = rands[4],
            alpha = rands[5],
            Delta = rands[6],
    )
    params = Params(params)

    def hamiltonian(k):
        t, mu, alpha, J, Delta = params.t, params.mu, params.alpha, params.Jz, params.Delta
        a1, a2 = lattice.lattice_vectors[0], lattice.lattice_vectors[1]
        rashba_matrix = kspace.lattice.rashba_matrix

        def Hk(k):
            ek = 2*t*np.cos(k @ (-a1 + a2)) + 2*t*np.cos(k @ (a1)) + 2*t*np.cos(k @ (a2)) - mu

            ak = [
                + np.exp(1j * k @ a1) * rashba_matrix[0, 0, 1] * alpha,
                - np.exp(-1j * k @ a1) * rashba_matrix[0, 0, 1] * alpha,
                + np.exp(1j * k @ a2) * rashba_matrix[1, 0, 1] * alpha,
                - np.exp(-1j * k @ a2) * rashba_matrix[1, 0, 1] * alpha,
                + np.exp(1j * k @ (-a1 + a2)) * (-rashba_matrix[0, 0, 1] + rashba_matrix[1, 0, 1]) * alpha,
                - np.exp(-1j * k @ (-a1 + a2)) * (-rashba_matrix[0, 0, 1] + rashba_matrix[1, 0, 1]) * alpha,
            ]
            ak = np.array(ak)
            ak = np.sum(ak, axis=0)
            return np.array([
                [ek + J, ak + params.Jx - 1j * params.Jy],
                [np.conj(ak) + params.Jx + 1j * params.Jy, ek - J]
            ])

        Hk1 = Hk(k)
        Hk2 = Hk(-k)
        D = np.array([[0, Delta], [-Delta, 0]])
        H_BdG = np.block([
            [Hk1, D],
            [-D, -Hk2.T]
        ])
        return H_BdG

    k = rng.normal(0, 2*np.pi, 2)

    lattice = models.Triangular()
    kspace = System(Space.KSpace, lattice, params)
    H_BdG = kspace.hamiltonian(k=k)

    ref = hamiltonian(k)

    test = abs(H_BdG - ref).max()

    assert test < 1e-13

def test_kspace_vs_realspace():
    seed = int((datetime.now(timezone.utc) - datetime(1970, 1, 1, tzinfo=timezone.utc)).total_seconds())
    rng = np.random.default_rng(seed)
    rands = rng.normal(0, 1, 7)
    params = dict(
            N1 = 16,
            N2 = 16,
            t = rands[0],
            mu = rands[1],
            Jx = rands[2],
            Jy = rands[3],
            Jz = rands[4],
            alpha = rands[5],
            Delta = rands[6],
            pbc = True,
    )
    params = Params(params)

    lattice = models.Triangular()
    realspace = System(Space.RealSpace, lattice, params)
    assert realspace == Space.KSpace, f"{seed}, {params}"

def test_kspace_vs_ribbon():
    seed = int((datetime.now(timezone.utc) - datetime(1970, 1, 1, tzinfo=timezone.utc)).total_seconds())
    rng = np.random.default_rng(seed)
    rands = rng.normal(0, 1, 6)

    params_ribbon = dict(
            N1 = 6,
            N2 = 5,
            L = 5,
            mu = rands[0],
            Jx = rands[1],
            Jy = rands[2],
            Jz = rands[3],
            t = 1,
            alpha = rands[4],
            Delta = rands[5],
            pbc = True,
            direction = "a1",
    )
    params_ribbon = Params(params_ribbon)
    params_kspace = dict(
            N1 = 6,
            N2 = 5,
            mu = rands[0],
            Jx = rands[1],
            Jy = rands[2],
            Jz = rands[3],
            t = 1,
            alpha = rands[4],
            Delta = rands[5],
    )
    params_kspace = Params(params_kspace)

    lattice = models.Triangular()

    syst = System(Space.Ribbon, lattice, params_ribbon)
    kspace = System(Space.KSpace, lattice, params_kspace)

    assert syst == kspace, f"{seed}, {params_ribbon}"

def test_multisite_kspace_vs_kspace():
    seed = int((datetime.now(timezone.utc) - datetime(1970, 1, 1, tzinfo=timezone.utc)).total_seconds())
    rng = np.random.default_rng(seed)
    rands = rng.normal(0, 1, 6)

    params = dict(
        N1 = 8,
        N2 = 8,
        mu = rands[0],
        Jx = rands[1],
        Jy = rands[2],
        Jz = rands[3],
        t = 1,
        alpha = rands[4],
        Delta = rands[5],
        pbc = True,
    )
    params = Params(params)
    four_site = models.Triangular(N1=2, N2=2)

    lattice = models.Triangular()
    lattice.add_sublattice(four_site)

    left = System(Space.KSpace, lattice, params)

    params = dict(
        N1 = 16,
        N2 = 16,
        mu = rands[0],
        Jx = rands[1],
        Jy = rands[2],
        Jz = rands[3],
        t = 1,
        alpha = rands[4],
        Delta = rands[5],
        pbc = True,
    )
    lattice = models.Triangular()
    right = System(Space.KSpace, lattice, params)

    assert left == right, f"{seed}, {params}"

def test_multisite_kspace_vs_realspace1():
    seed = int((datetime.now(timezone.utc) - datetime(1970, 1, 1, tzinfo=timezone.utc)).total_seconds())
    rng = np.random.default_rng(seed)
    rands = rng.normal(0, 1, 7)

    params = dict(
        N1 = 16,
        N2 = 1,
        t = rands[0],
        mu = rands[1],
        Jx = rands[2],
        Jy = rands[3],
        Jz = rands[4],
        alpha = rands[5],
        Delta = rands[6],
        pbc = True,
    )
    params = Params(params)

    lattice = models.Triangular()
    sublattice = models.Triangular(N1=1, N2=4)
    lattice.add_sublattice(sublattice)

    kspace = System(Space.KSpace, lattice, params)

    lattice = models.Triangular()
    params.N2 = 4
    realspace = System(Space.RealSpace, lattice, params)

    assert kspace == realspace

def test_multisite_kspace_vs_realspace2():
    seed = int((datetime.now(timezone.utc) - datetime(1970, 1, 1, tzinfo=timezone.utc)).total_seconds())
    rng = np.random.default_rng(seed)
    rands = rng.normal(0, 1, 6)

    params = dict(
        N1 = 8,
        N2 = 8,
        mu = rands[0],
        Jx = rands[1],
        Jy = rands[2],
        Jz = rands[3],
        t = 1,
        alpha = rands[4],
        Delta = rands[5],
        pbc = True,
    )
    params = Params(params)
    four_site = models.Triangular(N1=2, N2=2)

    lattice = models.Triangular()
    lattice.add_sublattice(four_site)

    left = System(Space.RealSpace, lattice, params)

    params = dict(
        N1 = 16,
        N2 = 16,
        mu = rands[0],
        Jx = rands[1],
        Jy = rands[2],
        Jz = rands[3],
        t = 1,
        alpha = rands[4],
        Delta = rands[5],
        pbc = True,
    )
    lattice = models.Triangular()
    right = System(Space.KSpace, lattice, params)

    assert left == right, f"{seed}, {params}"

def test_multisite_kspace_vs_realspace3():
    seed = int((datetime.now(timezone.utc) - datetime(1970, 1, 1, tzinfo=timezone.utc)).total_seconds())
    rng = np.random.default_rng(seed)
    rands = rng.normal(0, 1, 6)

    params = dict(
        N1 = 8,
        N2 = 8,
        mu = rands[0],
        Jx = rands[1],
        Jy = rands[2],
        Jz = rands[3],
        t = 1,
        alpha = rands[4],
        Delta = rands[5],
        pbc = True,
    )
    params = Params(params)
    four_site = models.Triangular(N1=2, N2=2)

    lattice = models.Triangular()
    lattice.add_sublattice(four_site)

    left = System(Space.KSpace, lattice, params)

    params = dict(
        N1 = 16,
        N2 = 16,
        mu = rands[0],
        Jx = rands[1],
        Jy = rands[2],
        Jz = rands[3],
        t = 1,
        alpha = rands[4],
        Delta = rands[5],
        pbc = True,
    )
    lattice = models.Triangular()
    right = System(Space.RealSpace, lattice, params)

    assert left == right, f"{seed}, {params}"

def test_multisite_realspace_vs_realspace():
    seed = int((datetime.now(timezone.utc) - datetime(1970, 1, 1, tzinfo=timezone.utc)).total_seconds())
    rng = np.random.default_rng(seed)
    rands = rng.normal(0, 1, 6)

    params = dict(
        N1 = 8,
        N2 = 8,
        mu = rands[0],
        Jx = rands[1],
        Jy = rands[2],
        Jz = rands[3],
        t = 1,
        alpha = rands[4],
        Delta = rands[5],
        pbc = True,
    )
    params = Params(params)
    four_site = models.Triangular(N1=2, N2=2)

    lattice = models.Triangular()
    lattice.add_sublattice(four_site)

    left = System(Space.RealSpace, lattice, params)

    params = dict(
        N1 = 16,
        N2 = 16,
        mu = rands[0],
        Jx = rands[1],
        Jy = rands[2],
        Jz = rands[3],
        t = 1,
        alpha = rands[4],
        Delta = rands[5],
        pbc = True,
    )
    lattice = models.Triangular()
    right = System(Space.RealSpace, lattice, params)

    assert left == right, f"{seed}, {params}"

def test_impurities_kspace_vs_realspace1():
    # Chain with an impurity attached to each site, also hopping to next site
    # x-x-x-x    impurities
    # |\|\|\|
    # o-o-o-o    chain

    seed = int((datetime.now(timezone.utc) - datetime(1970, 1, 1, tzinfo=timezone.utc)).total_seconds())
    rng = np.random.default_rng(seed)
    rands = rng.normal(0, 1, 9)

    params = dict(
        N1 = 16,
        N2 = 1,
        t = rands[0],
        mu = rands[1],
        Jx = rands[2],
        Jy = rands[3],
        Jz = rands[4],
        alpha = rands[5],
        Delta = rands[6],
        impurities = dict(
            t = rands[7],
            mu = rands[8],
        ),
        pbc = True,
    )
    params = Params(params)

    lattice = models.Triangular()
    sys = System(Space.KSpace, lattice, params)

    t = Symbol("impurities.t")
    mu = Symbol("impurities.mu")
    idx = sys.add_impurity()
    imp = sys.impurities[idx]
    for i in range(2):
        imp.add_hopping(imp, i, i, mu)
        imp.add_hopping(imp, i, i, t, d1=1)
        imp.add_hopping(imp, i, i, t, d1=-1)
        imp.add_hopping(Site(0, 0, 0, 0), i, i, t)
        imp.add_hopping(Site(0, 0, 0, 0), i, i, t, d1=1)
        imp.add_hopping(Site(0, 0, 0, 0), i, i, t, d1=-1)

    realspace = System(Space.RealSpace, lattice, params)
    for x in range(params.N1):
        idx = realspace.add_impurity()
        imp = realspace.impurities[idx]
        for i in range(2):
            imp.add_hopping(imp, i, i, mu)
            if x > 0:
                imp1 = realspace.impurities[idx-1]
                imp.add_hopping(imp1, i, i, t)
            imp.add_hopping(Site(x, 0, 0, 0), i, i, t)
            imp.add_hopping(Site((x+1)%params.N1, 0, 0, 0), i, i, t)
            imp.add_hopping(Site((x-1)%params.N1, 0, 0, 0), i, i, t)

    imp0 = realspace.impurities[0]
    imp1 = realspace.impurities[-1]
    imp0.add_hopping(imp1, 0, 0, t)
    imp0.add_hopping(imp1, 1, 1, t)

    assert sys == realspace, f"{seed}, {params}"

def test_impurities_kspace_vs_realspace2():
    # Impurities centred on a square lattice, coupled to each other and also neighbours
    # o-o-o-o
    # |x|x|x|
    # o-o-o-o
    # |x|x|x|

    seed = int((datetime.now(timezone.utc) - datetime(1970, 1, 1, tzinfo=timezone.utc)).total_seconds())
    rng = np.random.default_rng(seed)
    rands = rng.normal(0, 1, 9)

    params = dict(
        N1 = 16,
        N2 = 16,
        t = rands[0],
        mu = rands[1],
        Jx = rands[2],
        Jy = rands[3],
        Jz = rands[4],
        alpha = rands[5],
        Delta = rands[6],
        impurities = dict(
            t = rands[7],
            mu = rands[8],
        ),
        pbc = True,
    )
    params = Params(params)

    lattice = models.Triangular()
    sys = System(Space.KSpace, lattice, params)

    t = Symbol("impurities.t")
    mu = Symbol("impurities.mu")
    idx = sys.add_impurity()
    imp = sys.impurities[idx]
    for i in range(2):
        imp.add_hopping(imp, i, i, mu)
        imp.add_hopping(imp, i, i, t, d1=1)
        imp.add_hopping(imp, i, i, t, d1=-1)
        imp.add_hopping(imp, i, i, t, d2=1)
        imp.add_hopping(imp, i, i, t, d2=-1)
        imp.add_hopping(Site(0, 0, 0, 0), i, i, t)
        imp.add_hopping(Site(0, 0, 0, 0), i, i, t, d1=1)
        imp.add_hopping(Site(0, 0, 0, 0), i, i, t, d2=1)
        imp.add_hopping(Site(0, 0, 0, 0), i, i, t, d1=1, d2=1)
        imp.add_hopping(Site(0, 0, 0, 0), i, i, t, d1=-1, d2=-1)

    realspace = System(Space.RealSpace, lattice, params)
    idxs = np.arange(params.N1*params.N2).reshape(params.N1, params.N2)
    for x, y in np.ndindex(params.N1, params.N2):
        idx = realspace.add_impurity()
        imp = realspace.impurities[idx]
        for i in range(2):
            imp.add_hopping(imp, i, i, mu)

            if x > 0:
                imp1 = realspace.impurities[idxs[x-1, y]]
                imp.add_hopping(imp1, i, i, t)
            if y > 0:
                imp1 = realspace.impurities[idxs[x, y-1]]
                imp.add_hopping(imp1, i, i, t)

            imp.add_hopping(Site(x, y, 0, 0), i, i, t)
            imp.add_hopping(Site((x+1)%params.N1, y, 0, 0), i, i, t)
            imp.add_hopping(Site(x, (y+1)%params.N2, 0, 0), i, i, t)
            imp.add_hopping(Site((x+1)%params.N1, (y+1)%params.N1, 0, 0), i, i, t)
            imp.add_hopping(Site((x-1)%params.N1, (y-1)%params.N1, 0, 0), i, i, t)

    for y in range(params.N2):
        imp0 = realspace.impurities[idxs[0, y]]
        imp1 = realspace.impurities[idxs[-1, y]]
        imp0.add_hopping(imp1, 0, 0, t)
        imp0.add_hopping(imp1, 1, 1, t)

    for x in range(params.N1):
        imp0 = realspace.impurities[idxs[x, 0]]
        imp1 = realspace.impurities[idxs[x, -1]]
        imp0.add_hopping(imp1, 0, 0, t)
        imp0.add_hopping(imp1, 1, 1, t)

    assert sys == realspace, f"{seed}, {params}"
