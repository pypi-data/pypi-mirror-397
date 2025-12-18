import numpy as np
from datetime import datetime, timezone
from keino import Params, k_path
from ristikko import System, Space, models, Symbol, Site

def test_kspace_vs_analytic():
    seed = int((datetime.now(timezone.utc) - datetime(1970, 1, 1, tzinfo=timezone.utc)).total_seconds())
    rng = np.random.default_rng(seed)
    rands = rng.normal(0, 1, 4)
    params = dict(
            mu = rands[0],
            Jz = rands[1],
            t = 1,
            alpha = rands[2],
            Delta = rands[3],
    )
    params = Params(params)

    points = np.array([
        [0, 0],
        [0.5, 0],
        [0.5, 0.5],
        [0, 0.5],
        [0, 0]
    ]) * 2 * np.pi
    Ks = np.array(k_path(101, points))

    ek = 2 * params.t * (np.cos(Ks[:, 0]) + np.cos(Ks[:, 1])) - params.mu
    ak = 2 * params.alpha * (np.sin(Ks[:, 0]) + np.sin(Ks[:, 1]))
    ref = np.array([
            np.sqrt(params.Jz**2 + params.Delta**2 + ek**2 + ak**2 + 2 * np.sqrt(params.Jz**2 * (params.Delta**2 + ek**2) + ek**2 * ak**2)),
            np.sqrt(params.Jz**2 + params.Delta**2 + ek**2 + ak**2 - 2 * np.sqrt(params.Jz**2 * (params.Delta**2 + ek**2) + ek**2 * ak**2)),
            -np.sqrt(params.Jz**2 + params.Delta**2 + ek**2 + ak**2 + 2 * np.sqrt(params.Jz**2 * (params.Delta**2 + ek**2) + ek**2 * ak**2)),
            -np.sqrt(params.Jz**2 + params.Delta**2 + ek**2 + ak**2 - 2 * np.sqrt(params.Jz**2 * (params.Delta**2 + ek**2) + ek**2 * ak**2)),
    ])

    lattice = models.Square()
    kspace = System(Space.KSpace, lattice, params)
    Ek = kspace.diagonalise(k=Ks, cache=False)

    ref = np.sort(ref.flatten())
    Ek = np.sort(Ek.flatten())
    test = abs(ref - Ek).max()

    assert test < 1e-13, f"{test}, {seed}, {params}"

def test_kspace_vs_realspace():
    seed = int((datetime.now(timezone.utc) - datetime(1970, 1, 1, tzinfo=timezone.utc)).total_seconds())
    rng = np.random.default_rng(seed)
    rands = rng.normal(0, 1, 6)
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
    params = Params(params)

    lattice = models.Square()
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

    lattice = models.Square()

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
    four_site = models.Square(N1=2, N2=2)

    lattice = models.Square()
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
    lattice = models.Square()
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

    lattice = models.Square()
    sublattice = models.Square(N1=1, N2=4)
    lattice.add_sublattice(sublattice)

    kspace = System(Space.KSpace, lattice, params)

    lattice = models.Square()
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
    four_site = models.Square(N1=2, N2=2)

    lattice = models.Square()
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
    lattice = models.Square()
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
    four_site = models.Square(N1=2, N2=2)

    lattice = models.Square()
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
    lattice = models.Square()
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
    four_site = models.Square(N1=2, N2=2)

    lattice = models.Square()
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
    lattice = models.Square()
    right = System(Space.RealSpace, lattice, params)

    assert left == right, f"{seed}, {params}"

def test_impurities_vs_analytic1():
    # Chain with an impurity attached to each site
    # x x x x    impurities
    # | | | |
    # o-o-o-o    chain

    seed = int((datetime.now(timezone.utc) - datetime(1970, 1, 1, tzinfo=timezone.utc)).total_seconds())
    rng = np.random.default_rng(seed)
    rands = rng.normal(0, 1, 4)

    params = dict(
        t = rands[0],
        mu = rands[1],
        direction = "a1",
        impurities = dict(
            t = rands[2],
            mu = rands[3],
        ),
    )
    params = Params(params)

    lattice = models.Square()
    sys = System(Space.KSpace, lattice, params, spinful=False)

    t = Symbol("impurities.t")
    mu = Symbol("impurities.mu")

    idx = sys.add_impurity()
    imp = sys.impurities[idx]
    imp.add_hopping(imp, 0, 0, mu)
    imp.add_hopping(Site(0, 0, 0, 0), 0, 0, t)

    k = rng.normal(0, 2*np.pi, (10,1))
    Ek = sys.diagonalise(k=k, cache=False)

    ek = 2 * rands[0] * np.cos(k) - rands[1]
    t = rands[2]
    mu = rands[3]
    ref = np.array([1/2 * (ek + mu + np.sqrt((ek-mu)**2 + (2*t)**2)),  1/2 * (ek + mu - np.sqrt((ek-mu)**2 + (2*t)**2))])

    test1 = np.sort(Ek.flatten())
    test2 = np.sort(ref.flatten())
    test = abs(test1 - test2).max()

    assert test < 1e-14, f"{test}, {seed}, {params}"

def test_impurities_vs_analytic2():
    # Chain with an impurity attached to each site, also hopping to next site
    # x x x x    impurities
    # |\|\|\|
    # o-o-o-o    chain

    seed = int((datetime.now(timezone.utc) - datetime(1970, 1, 1, tzinfo=timezone.utc)).total_seconds())
    rng = np.random.default_rng(seed)
    rands = rng.normal(0, 1, 4)

    params = dict(
        t = rands[0],
        mu = rands[1],
        direction = "a1",
        impurities = dict(
            t = rands[2],
            mu = rands[3],
        ),
    )
    params = Params(params)

    lattice = models.Square()
    sys = System(Space.KSpace, lattice, params, spinful=False)

    t = Symbol("impurities.t")
    mu = Symbol("impurities.mu")
    idx = sys.add_impurity()
    imp = sys.impurities[idx]
    imp.add_hopping(imp, 0, 0, mu)
    imp.add_hopping(Site(0, 0, 0, 0), 0, 0, t)
    imp.add_hopping(Site(0, 0, 0, 0), 0, 0, t, d1=1)

    k = rng.normal(0, 2*np.pi, 1)
    k = list(k)[0]
    Ek = sys.diagonalise(k=k)

    ek = 2 * rands[0] * np.cos(k) - rands[1]
    t = rands[2]
    mu = rands[3]
    ref = np.array([
        1/2 * (ek + mu + np.sqrt((ek - mu)**2 + 8 * t**2 + 8 * t**2 * np.cos(k))),
        1/2 * (ek + mu - np.sqrt((ek - mu)**2 + 8 * t**2 + 8 * t**2 * np.cos(k))),
    ])

    test1 = np.sort(Ek.flatten())
    test2 = np.sort(ref.flatten())
    test = abs(test1 - test2).max()

    assert test < 1e-14, f"{test}, {seed}, {params}"

def test_impurities_vs_analytic3():
    # Floating sites, next to a chain of impurities
    # x-x-x-x    impurities
    #        
    # o o o o    chain

    seed = int((datetime.now(timezone.utc) - datetime(1970, 1, 1, tzinfo=timezone.utc)).total_seconds())
    rng = np.random.default_rng(seed)
    rands = rng.normal(0, 1, 4)

    params = dict(
        t = 1e-10,
        mu = rands[1],
        direction = "a1",
        impurities = dict(
            t = rands[2],
            mu = rands[3],
        ),
    )
    params = Params(params)

    lattice = models.Square()
    sys = System(Space.KSpace, lattice, params, spinful=False)

    t = Symbol("impurities.t")
    mu = Symbol("impurities.mu")
    idx = sys.add_impurity()
    imp = sys.impurities[idx]
    imp.add_hopping(imp, 0, 0, mu)
    imp.add_hopping(imp, 0, 0, t, d1=1)
    imp.add_hopping(imp, 0, 0, t, d1=-1)

    k = rng.normal(0, 2*np.pi, 1)
    k = list(k)[0]
    Ek = sys.diagonalise(k=k)

    t = rands[2] * np.exp(1j * k) + rands[2] * np.exp(-1j * k)
    mu = rands[3]
    ref = np.array([-rands[1], mu + t])

    test1 = np.sort(Ek.flatten())
    test2 = np.sort(ref.flatten())
    test = abs(test1 - test2).max()

    assert test < 1e-9, f"{test}, {seed}, {params}"

def test_impurities_vs_analytic4():
    # Impurities centred on a square lattice, coupled to each other and also neighbours
    # o-o-o-o
    # |x|x|x|
    # o-o-o-o
    # |x|x|x|

    seed = int((datetime.now(timezone.utc) - datetime(1970, 1, 1, tzinfo=timezone.utc)).total_seconds())
    rng = np.random.default_rng(seed)
    rands = rng.normal(0, 1, 4)

    params = dict(
        t = rands[0],
        mu = rands[1],
        impurities = dict(
            t = rands[2],
            mu = rands[3],
        ),
    )
    params = Params(params)

    lattice = models.Square()
    sys = System(Space.KSpace, lattice, params, spinful=False)

    t = Symbol("impurities.t")
    mu = Symbol("impurities.mu")
    idx = sys.add_impurity()
    imp = sys.impurities[idx]
    imp.add_hopping(imp, 0, 0, mu)
    imp.add_hopping(imp, 0, 0, t)
    imp.add_hopping(imp, 0, 0, t, d1=1)
    imp.add_hopping(imp, 0, 0, t, d1=-1)
    imp.add_hopping(imp, 0, 0, t, d2=1)
    imp.add_hopping(imp, 0, 0, t, d2=-1)
    imp.add_hopping(Site(0, 0, 0, 0), 0, 0, t)
    imp.add_hopping(Site(0, 0, 0, 0), 0, 0, t, d1=1)
    imp.add_hopping(Site(0, 0, 0, 0), 0, 0, t, d2=1)
    imp.add_hopping(Site(0, 0, 0, 0), 0, 0, t, d1=1, d2=1)

    k = rng.normal(0, 2*np.pi, 2)
    Ek = sys.diagonalise(k=k)

    ek = 2 * rands[0] * ( np.cos(k[0]) + np.cos(k[1]) ) - rands[1]
    t = rands[2]
    mu = rands[3]
    kx, ky = k[0], k[1]
    ref = np.array([0.5 * (np.exp(complex(0, -1) * (kx + ky))) * (-(np.sqrt((np.exp(complex(0, 2) * (kx + ky))) * (ek ** 2 + mu ** 2 + 2 * mu * t + 21 * (t ** 2) -2 * ek * (mu + t) + 2 * t * (t * np.cos(2 * kx) + 2 * (-ek + mu + 5 * t) * np.cos(ky) + 2 * np.cos(kx) * (-ek + mu + 5 * t + 6 * t * np.cos(ky)) + t * np.cos(2 * ky))))) + (ek + mu + t + 2 * t * (np.cos(kx) + np.cos(ky))) * (np.cos(kx + ky) + complex(0, 1) * np.sin(kx + ky))), 0.5 * (np.exp(complex(0, -1) * (kx + ky))) * (np.sqrt((np.exp(complex(0, 2) * (kx + ky))) * (ek ** 2 + mu ** 2 + 2 * mu * t + 21 * (t ** 2) -2 * ek * (mu + t) + 2 * t * (t * np.cos(2 * kx) + 2 * (-ek + mu + 5 * t) * np.cos(ky) + 2 * np.cos(kx) * (-ek + mu + 5 * t + 6 * t * np.cos(ky)) + t * np.cos(2 * ky)))) + (ek + mu + t + 2 * t * (np.cos(kx) + np.cos(ky))) * (np.cos(kx + ky) + complex(0, 1) * np.sin(kx + ky)))])

    test1 = np.sort(Ek.flatten())
    test2 = np.sort(ref.flatten())
    test = abs(test1 - test2).max()

    assert test < 1e-14, f"{test}, {seed}, {params}"

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
        direction = "a1",
        impurities = dict(
            t = rands[7],
            mu = rands[8],
        ),
        pbc = True,
    )
    params = Params(params)

    lattice = models.Square()
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

    params.mu += 2 * params.t
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

    lattice = models.Square()
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

def test_impurities_kspace_vs_realspace3():
    # Chain on substrate
    # o-o-o-o
    # o-o-o-o
    # o-o-o-o
    # |x|x|x|
    # o-o-o-o
    # o-o-o-o
    # o-o-o-o

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

    lattice = models.Square()
    four_site = models.Square(N1=1, N2=6)
    lattice.add_sublattice(four_site)
    sys = System(Space.KSpace, lattice, params)

    t = Symbol("impurities.t")
    mu = Symbol("impurities.mu")
    idx = sys.add_impurity()
    imp = sys.impurities[idx]
    for i in range(2):
        imp.add_hopping(imp, i, i, mu)
        imp.add_hopping(imp, i, i, t, d1=1)
        imp.add_hopping(imp, i, i, t, d1=-1)
        imp.add_hopping(Site(0, 0, 0, 3), i, i, t)
        imp.add_hopping(Site(0, 0, 0, 3), i, i, t, d1=1)
        imp.add_hopping(Site(0, 0, 0, 2), i, i, t, d2=1)
        imp.add_hopping(Site(0, 0, 0, 2), i, i, t, d1=1, d2=1)

    lattice = models.Square()
    params.N2 = 6
    realspace = System(Space.RealSpace, lattice, params)
    idxs = np.arange(params.N1*params.N2).reshape(params.N1, params.N2)
    y = 3
    for x in range(params.N1):
        idx = realspace.add_impurity()
        imp = realspace.impurities[idx]
        idxs[x, y] = idx
        for i in range(2):
            imp.add_hopping(imp, i, i, mu)

            if x > 0:
                imp1 = realspace.impurities[idxs[x-1, y]]
                imp.add_hopping(imp1, i, i, t)

            imp.add_hopping(Site(x, y, 0, 0), i, i, t)
            
            imp.add_hopping(Site((x+1)%params.N1, y, 0, 0), i, i, t)
            imp.add_hopping(Site(x, y+1, 0, 0), i, i, t)
            imp.add_hopping(Site((x+1)%params.N1, (y+1)%params.N1, 0, 0), i, i, t)
            
    imp0 = realspace.impurities[idxs[0, y]]
    imp1 = realspace.impurities[idxs[-1, y]]
    imp0.add_hopping(imp1, 0, 0, t)
    imp0.add_hopping(imp1, 1, 1, t)

    assert sys == realspace, f"{seed}, {params}"

def test_impurities_kspace_vs_realspace4():
    # Chain on substrate, with 2a between chain
    # o-o-o-o-o-o
    # o-o-o-o-o-o
    # o-o-o-o-o-o
    # |x|-|x|-|x|
    # o-o-o-o-o-o
    # o-o-o-o-o-o
    # o-o-o-o-o-o

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

    lattice = models.Square()
    four_site = models.Square(N1=2, N2=6)
    lattice.add_sublattice(four_site)
    sys = System(Space.KSpace, lattice, params)

    t = Symbol("impurities.t")
    mu = Symbol("impurities.mu")
    idx = sys.add_impurity()
    imp = sys.impurities[idx]
    for i in range(2):
        imp.add_hopping(imp, i, i, mu)
        imp.add_hopping(imp, i, i, t, d1=1)
        imp.add_hopping(imp, i, i, t, d1=-1)
        imp.add_hopping(Site(0, 0, 0, 3), i, i, t)
        imp.add_hopping(Site(0, 0, 0, 3), i, i, t, d1=1)
        imp.add_hopping(Site(0, 0, 0, 2), i, i, t, d2=1)
        imp.add_hopping(Site(0, 0, 0, 2), i, i, t, d1=1, d2=1)

    lattice = models.Square()
    params.N1 = 32
    params.N2 = 6
    realspace = System(Space.RealSpace, lattice, params)
    idxs = np.zeros((params.N1, params.N2), dtype=int)
    y = 3
    for x in np.arange(0, params.N1, 2):
        idx = realspace.add_impurity()
        imp = realspace.impurities[idx]
        idxs[x, y] = idx
        for i in range(2):
            imp.add_hopping(imp, i, i, mu)

            if x > 0:
                imp1 = realspace.impurities[idxs[x-2, y]]
                imp.add_hopping(imp1, i, i, t)

            imp.add_hopping(Site(x, y, 0, 0), i, i, t)
            
            imp.add_hopping(Site((x+2)%params.N1, y, 0, 0), i, i, t)
            imp.add_hopping(Site(x, y+1, 0, 0), i, i, t)
            imp.add_hopping(Site((x+2)%params.N1, (y+1)%params.N1, 0, 0), i, i, t)
            
    imp0 = realspace.impurities[idxs[0, y]]
    imp1 = realspace.impurities[idxs[-2, y]]
    imp0.add_hopping(imp1, 0, 0, t)
    imp0.add_hopping(imp1, 1, 1, t)

    assert sys == realspace, f"{seed}, {params}"

def test_impurities_kspace_vs_realspace5():
    seed = int((datetime.now(timezone.utc) - datetime(1970, 1, 1, tzinfo=timezone.utc)).total_seconds())
    rng = np.random.default_rng(seed)
    rands = rng.normal(0, 1, 10)

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
            J = rands[9],
        ),
        pbc = True,
    )
    params = Params(params)

    lattice = models.Square()
    sublattice = models.Square(N1=1, N2=6)
    lattice.add_sublattice(sublattice)
    kspace = System(Space.KSpace, lattice, params)

    t = Symbol("impurities.t")
    mu = Symbol("impurities.mu")
    J = Symbol("impurities.J")
    idx = kspace.add_impurity()
    imp = kspace.impurities[idx]
    imp.add_hopping(imp, 0, 0, (-1 * mu) + J)
    imp.add_hopping(imp, 1, 1, (-1 * mu) + (-1 * J))
    for i in range(2):
        imp.add_hopping(imp, i, i, t, d1=1)
        imp.add_hopping(imp, i, i, t, d1=-1)
        imp.add_hopping(Site(0, 0, 0, 2), i, i, t)
        imp.add_hopping(Site(0, 0, 0, 2), i, i, t, d1=1)
        imp.add_hopping(Site(0, 0, 0, 3), i, i, t, d2=1)
        imp.add_hopping(Site(0, 0, 0, 3), i, i, t, d1=1, d2=1)

    params.N2 = 6
    lattice = models.Square()
    realspace = System(Space.RealSpace, lattice, params)
    idxs = np.arange(params.N1*params.N2).reshape(params.N1, params.N2)
    y = 3
    for x in range(params.N1):
        idx = realspace.add_impurity()
        imp = realspace.impurities[idx]
        idxs[x, y] = idx
        
        imp.add_hopping(imp, 0, 0, (-1 * mu) + J)
        imp.add_hopping(imp, 1, 1, (-1 * mu) + (-1 * J))
        
        for i in range(2):
            if x > 0:
                imp1 = realspace.impurities[idxs[x-1, y]]
                imp.add_hopping(imp1, i, i, t)

            imp.add_hopping(Site(x, y, 0, 0), i, i, t)
            imp.add_hopping(Site((x+1)%params.N1, y, 0, 0), i, i, t)
            imp.add_hopping(Site(x, y+1, 0, 0), i, i, t)
            imp.add_hopping(Site((x+1)%params.N1, (y+1)%params.N1, 0, 0), i, i, t)

    imp0 = realspace.impurities[0]
    imp1 = realspace.impurities[-1]
    imp0.add_hopping(imp1, 0, 0, t)
    imp0.add_hopping(imp1, 1, 1, t)

    assert kspace == realspace

def test_impurities_manual_vs_auto1():
    seed = int((datetime.now(timezone.utc) - datetime(1970, 1, 1, tzinfo=timezone.utc)).total_seconds())
    rng = np.random.default_rng(seed)
    rands = rng.normal(0, 1, 10)

    params = dict(
        N1 = 16,
        N2 = 6,
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
            J = rands[9],
        ),
        pbc = True,
    )
    params = Params(params)
    lattice = models.Square()
    manual = System(Space.RealSpace, lattice, params)

    t = Symbol("impurities.t")
    mu = Symbol("impurities.mu")
    J = Symbol("impurities.J")

    idxs = np.arange(params.N1*params.N2).reshape(params.N1, params.N2)
    y = 3
    for x in range(params.N1):
        idx = manual.add_impurity()
        imp = manual.impurities[idx]
        idxs[x, y] = idx
        
        imp.add_hopping(imp, 0, 0, (-1 * mu) + J)
        imp.add_hopping(imp, 1, 1, (-1 * mu) + (-1 * J))
        
        for i in range(2):
            if x > 0:
                imp1 = manual.impurities[idxs[x-1, y]]
                imp.add_hopping(imp1, i, i, t)

            imp.add_hopping(Site(x, y, 0, 0), i, i, t)
            
            imp.add_hopping(Site((x+1)%params.N1, y, 0, 0), i, i, t)
            imp.add_hopping(Site(x, y+1, 0, 0), i, i, t)
            imp.add_hopping(Site((x+1)%params.N1, (y+1)%params.N1, 0, 0), i, i, t)

    imp0 = manual.impurities[0]
    imp1 = manual.impurities[-1]
    imp0.add_hopping(imp1, 0, 0, t)
    imp0.add_hopping(imp1, 1, 1, t)

    params.impurities.L = 16
    params.impurities.pbc = True
    params.impurities.Gamma = rands[7] 
    auto = System("realspace", lattice, params)
    auto.set_geometry("chain")

    assert manual == auto

def test_impurities_manual_vs_auto2():
    seed = int((datetime.now(timezone.utc) - datetime(1970, 1, 1, tzinfo=timezone.utc)).total_seconds())
    rng = np.random.default_rng(seed)
    rands = rng.normal(0, 1, 10)
    params = dict(
        N1 = 1,
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
            J = rands[9],
        ),
        pbc = True,
    )
    params = Params(params)

    lattice = models.Square()
    sublattice = models.Square(N1=1, N2=6)
    lattice.add_sublattice(sublattice)
    manual = System("kspace", lattice, params)

    t = Symbol("impurities.t")
    mu = Symbol("impurities.mu")
    J = Symbol("impurities.J")
    idx = manual.add_impurity()
    imp = manual.impurities[idx]
    imp.add_hopping(imp, 0, 0, (-1 * mu) + J)
    imp.add_hopping(imp, 1, 1, (-1 * mu) + (-1 * J))
    for i in range(2):
        imp.add_hopping(imp, i, i, t, d1=1)
        imp.add_hopping(imp, i, i, t, d1=-1)
        imp.add_hopping(Site(0, 0, 0, 2), i, i, t)
        imp.add_hopping(Site(0, 0, 0, 2), i, i, t, d1=1)
        imp.add_hopping(Site(0, 0, 0, 3), i, i, t, d2=1)
        imp.add_hopping(Site(0, 0, 0, 3), i, i, t, d1=1, d2=1)

    params.impurities.Gamma = rands[7]
    params.impurities.t = rands[7] 
    params.impurities.L = 1
    params.impurities.pbc = True
    auto = System("kspace", lattice, params)
    auto.set_geometry("chain")

    manual.N1 = 16
    auto.N1 = 16

    E, E_other = manual.__eq__(auto, debug=True)


def test_impurities_kspace_vs_ribbon():
    # Chain on substrate
    # o-o-o-o
    # o-o-o-o
    # o-o-o-o
    # |x|x|x|
    # o-o-o-o
    # o-o-o-o
    # o-o-o-o

    seed = int((datetime.now(timezone.utc) - datetime(1970, 1, 1, tzinfo=timezone.utc)).total_seconds())
    rng = np.random.default_rng(seed)
    rands = rng.normal(0, 1, 9)

    params_ribbon = dict(
        N1 = 9,
        N2 = 5,
        L = 5,
        t = rands[0],
        mu = rands[1],
        Jx = rands[2],
        Jy = rands[3],
        Jz = rands[4],
        alpha = rands[5],
        Delta = 0,
        impurities = dict(
            t = rands[7],
            mu = rands[8],
        ),
        pbc = True,
        direction = "a1",
    )
    params_ribbon = Params(params_ribbon)
    params_kspace = dict(
        N1 = 9,
        N2 = 5,
        t = rands[0],
        mu = rands[1],
        Jx = rands[2],
        Jy = rands[3],
        Jz = rands[4],
        alpha = rands[5],
        # Delta = rands[6],
        Delta = 0,
        impurities = dict(
            t = rands[7],
            mu = rands[8],
        )
    )
    params_kspace = Params(params_kspace)

    lattice = models.Square()

    syst = System(Space.Ribbon, lattice, params_ribbon)
    kspace = System(Space.KSpace, lattice, params_kspace)

    idx = kspace.add_impurity()
    t = Symbol("impurities.t")
    mu = Symbol("impurities.mu")
    imp = kspace.impurities[idx]
    for i in range(2):
        imp.add_hopping(imp, i, i, mu)
        imp.add_hopping(imp, i, i, t, d1=1)
        imp.add_hopping(imp, i, i, t, d1=-1)
        imp.add_hopping(imp, i, i, t, d2=1)
        imp.add_hopping(imp, i, i, t, d2=-1)

        imp.add_hopping(Site(0, 0, 0, 0), i, i, t)
        imp.add_hopping(Site(0, 0, 0, 0), i, i, t, d2=1)
        imp.add_hopping(Site(0, 0, 0, 0), i, i, t, d2=-1)

        imp.add_hopping(Site(0, 0, 0, 0), i, i, t, d1=1)
        imp.add_hopping(Site(0, 0, 0, 0), i, i, t, d1=-1)

        imp.add_hopping(Site(0, 0, 0, 0), i, i, t, d1=1, d2=1)
        imp.add_hopping(Site(0, 0, 0, 0), i, i, t, d1=-1, d2=-1)

    x = 0
    for y in range(params_ribbon.L):
        idx = syst.add_impurity()
        imp = syst.impurities[idx]
        for i in range(2):
            imp.add_hopping(imp, i, i, mu)
            if y > 0:
                imp1 = syst.impurities[idx-1]
                imp.add_hopping(imp1, i, i, t)
            imp.add_hopping(imp, i, i, t, d1=1)
            imp.add_hopping(imp, i, i, t, d1=-1)

            imp.add_hopping(Site(x, y, 0, 0), i, i, t)
            imp.add_hopping(Site(x, (y+1)%params_ribbon.L, 0, 0), i, i, t)
            imp.add_hopping(Site(x, (y-1)%params_ribbon.L, 0, 0), i, i, t)
            
            imp.add_hopping(Site(x, y, 0, 0), i, i, t, d1=1)
            imp.add_hopping(Site(x, y, 0, 0), i, i, t, d1=-1)
            
            imp.add_hopping(Site(x, (y+1)%params_ribbon.L, 0, 0), i, i, t, d1=1)
            imp.add_hopping(Site(x, (y-1)%params_ribbon.L, 0, 0), i, i, t, d1=-1)


    imp0 = syst.impurities[0]
    imp1 = syst.impurities[-1]
    imp0.add_hopping(imp1, 0, 0, t)
    imp0.add_hopping(imp1, 1, 1, t)

    assert syst == kspace, f"{seed}, {params}"
