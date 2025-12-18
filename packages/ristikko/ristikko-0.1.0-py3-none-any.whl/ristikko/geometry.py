from enum import Enum
import warnings
import numpy as np
from keino import Params
from .lattice import BravaisLattice, Space, Site, Symbol
from .impurity import Impurity

class Shape(Enum):
    Chain = "chain"
    Circle = "circle"
    Rectangle = "rectangle"
    Custom = "custom"

"""
chains in either brdige sites or hollow - islands it gets too confusing
same with spacings
assume self similar sublattices

note: for pbc might need to manually move the chain around
"""

class Geometry():
    def __init__(self, N1: int, N2: int, N1_sub: int, N2_sub: int, shape: Shape, lattice: BravaisLattice, params: Params, space: Space, spinful: bool, sites=None, coords=None):
        self.N1 = N1
        self.N2 = N2
        self.N1_sub = N1_sub
        self.N2_sub = N2_sub

        self.shape = Shape(shape)
        self.lattice = BravaisLattice(lattice)
        self.space = Space(space)
        self.spinful = spinful
        self.params = params.copy()

        if self.shape == Shape.Custom:
            assert sites is not None and coords is not None
            self.sites = sites
            self.coords = coords

        self.n_orbitals = 2 if spinful else 1

    def __call__(self, debug=False):
        match self.lattice:
            case BravaisLattice.Square:
                sites, coords, substrate_neighbours, impurity_neighbours = self.square()
            case BravaisLattice.Triangular:
                sites, coords, substrate_neighbours, impurity_neighbours = self.triangular()
            case _:
                raise ValueError(f"Lattice {self.lattice} is not supported!")

        num_impurities = len(sites)

        if debug:
            return sites, coords, substrate_neighbours, impurity_neighbours

        def is_in(idx, lst):
            for val in lst:
                if val == idx:
                    return True
            return False

        impurities = []
        idxs = {}
        t = Symbol("impurities.t")
        Gamma = Symbol("impurities.Gamma")
        mu = Symbol("impurities.mu")
        J = Symbol("impurities.J")
        match self.space:
            case Space.KSpace:
                for n in range(num_impurities):
                    x, y = sites[n]
                    x, x_sub = x // self.N1_sub, x % self.N1_sub
                    y, y_sub = y // self.N2_sub, y % self.N2_sub

                    idx = len(idxs)
                    idxs[(x, y, x_sub, y_sub)] = idx
                    imp = Impurity(idx, self.N1, self.N2, self.N1_sub, self.N2_sub, spinful=self.spinful, coord=coords[n])
                    impurities.append(imp)

                    if self.n_orbitals == 1:
                        imp.add_hopping(imp, 0, 0, -1 * mu)
                    elif self.n_orbitals == 2:
                        imp.add_hopping(imp, 0, 0, (-1 * mu) + J)
                        imp.add_hopping(imp, 1, 1, (-1 * mu) + (-1 * J))

                    for i in range(self.n_orbitals):
                        for x, y, x_sub, y_sub, d1, d2 in substrate_neighbours[n]:
                            imp.add_hopping(Site(x, y, x_sub, y_sub), i, i, Gamma, d1=d1, d2=d2)
                for n in range(num_impurities):
                    imp0 = impurities[n]
                    for x, y, x_sub, y_sub, d1, d2 in impurity_neighbours[n]:
                        if is_in((x, y, x_sub, y_sub), idxs):
                            idx = idxs[(x, y, x_sub, y_sub)]
                            imp1 = impurities[idx]
                            for i in range(self.n_orbitals):
                                imp0.add_hopping(imp1, i, i, t, d1=d1, d2=d2)
            case Space.RealSpace:
                for n in range(num_impurities):
                    x, y = sites[n]
                    x, x_sub = x // self.N1_sub, x % self.N1_sub
                    y, y_sub = y // self.N2_sub, y % self.N2_sub

                    idx = len(idxs)
                    idxs[(x, y, x_sub, y_sub)] = idx
                    imp = Impurity(idx, self.N1, self.N2, self.N1_sub, self.N2_sub, spinful=self.spinful, coord=coords[n])
                    impurities.append(imp)

                    if self.n_orbitals == 1:
                        imp.add_hopping(imp, 0, 0, -1 * mu)
                    elif self.n_orbitals == 2:
                        imp.add_hopping(imp, 0, 0, (-1 * mu) + J)
                        imp.add_hopping(imp, 1, 1, (-1 * mu) + (-1 * J))

                    if len(substrate_neighbours) >= n:
                        for x, y, x_sub, y_sub, d1, d2 in substrate_neighbours[n]:
                            for i in range(self.n_orbitals):
                                imp.add_hopping(Site(x, y, x_sub, y_sub), i, i, Gamma)
                for n in range(num_impurities):
                    imp0 = impurities[n]
                    for x, y, x_sub, y_sub, d1, d2 in impurity_neighbours[n]:
                        if is_in((x, y, x_sub, y_sub), idxs):
                            idx = idxs[(x, y, x_sub, y_sub)]
                            imp1 = impurities[idx]
                            for i in range(self.n_orbitals):
                                imp0.add_hopping(imp1, i, i, 0.5 * t)
            case _:
                raise ValueError(f"Space {self.space} is not supported!")

        return impurities

    def square(self, sites=None):
        pbc = self.params.get("pbc", False)
        if self.space == Space.KSpace:
            pbc = True
        impurity_neighbours = []
        substrate_neighbours = []
        N1 = self.N1 * self.N1_sub
        N2 = self.N2 * self.N2_sub

        match self.shape:
            case Shape.Chain:
                location = self.params.get("location", "hollow")
                spacing = self.params.get("spacing", 0)
                orientation = self.params.get("orientation", "a1")
                L = self.params["L"]
                assert spacing >= 0

                if orientation == "a1":
                    if pbc:
                        if L * (spacing + 1) > N1:
                            warnings.warn("Chain is too long!")
                    else:
                        if L * (spacing + 1) >= N1:
                            warnings.warn("Chain is too long!")
                if orientation == "a2":
                    if pbc:
                        if L * (spacing + 1) > N2:
                            warnings.warn("Chain is too long!")
                    else:
                        if L * (spacing + 1) >= N2:
                            warnings.warn("Chain is too long!")

                x = N1//2 if N1 % 2 else N1//2-1
                y = N2//2 if N2 % 2 else N2//2-1
                centre = self.params.get("centre", (x, y)) # The chain centre is defined in terms of the total number of sites

                match orientation:
                    case "a1":
                        left = centre[0] - (spacing + 1) * L // 2
                        right = centre[0] + (spacing + 1) * L // 2
                        if L % 2 and not spacing % 2:
                            right += 1
                        if left == right:
                            right += 1
                        if L * (spacing + 1) == N1 and pbc:
                            left = 0
                            right = N1
                        sites = [[x, centre[1]] for x in np.arange(left, right, spacing+1)]

                        for n, (X0, Y0) in enumerate(sites):
                            x0, x0_sub = X0 // self.N1_sub, X0 % self.N1_sub
                            y0, y0_sub = Y0 // self.N2_sub, Y0 % self.N2_sub

                            neighbours = []

                            if X0-(spacing+1) > 0 or pbc:
                                X1, Y1 = (X0-(spacing+1))%N1, Y0
                                x1, x1_sub = X1 // self.N1_sub, X1 % self.N1_sub
                                y1, y1_sub = Y1 // self.N2_sub, Y1 % self.N2_sub
                                d1 = -1 if pbc else x1-x0
                                neighbours.append([x1, y1, x1_sub, y1_sub, d1, 0])

                            if X0+(spacing+1) < L or pbc:
                                X1, Y1 = (X0+(spacing+1))%N1, Y0
                                x1, x1_sub = X1 // self.N1_sub, X1 % self.N1_sub
                                y1, y1_sub = Y1 // self.N2_sub, Y1 % self.N2_sub
                                d1 = +1 if pbc else x1-x0
                                neighbours.append([x1, y1, x1_sub, y1_sub, d1, 0])

                            impurity_neighbours.append(neighbours)
                    case "a2":
                        left = centre[1] - (spacing + 1) * L // 2
                        right = centre[1] + (spacing + 1) * L // 2
                        if L % 2:
                            right += 1
                        if left == right == 0:
                            right = 1
                        if L * (spacing + 1) == N2 and pbc:
                            left = 0
                            right = N2
                        sites = [[centre[0], y] for y in np.arange(left, right, spacing+1)]

                        for n, (X0, Y0) in enumerate(sites):
                            x0, x0_sub = X0 // self.N1_sub, X0 % self.N1_sub
                            y0, y0_sub = Y0 // self.N2_sub, Y0 % self.N2_sub

                            neighbours = []

                            if Y0-(spacing+1) > 0 or pbc:
                                X1, Y1 = X0, (Y0-(spacing+1))%N2
                                x1, x1_sub = X1 // self.N1_sub, X1 % self.N1_sub
                                y1, y1_sub = Y1 // self.N2_sub, Y1 % self.N2_sub
                                d2 = -1 if pbc else y1-y0
                                neighbours.append([x1, y1, x1_sub, y1_sub, 0, d2])

                            if Y0+(spacing+1) < L or pbc:
                                X1, Y1 = X0, (Y0+(spacing+1))%N2
                                x1, x1_sub = X1 // self.N1_sub, X1 % self.N1_sub
                                y1, y1_sub = Y1 // self.N2_sub, Y1 % self.N2_sub
                                d2 = +1 if pbc else y1-y0
                                neighbours.append([x1, y1, x1_sub, y1_sub, 0, d2])

                            impurity_neighbours.append(neighbours)
                    case _:
                        raise ValueError(f"Orientation {orientation} is not supported!")
                sites = np.array(sites)

                match location:
                    case "hollow":
                        for n in range(L):
                            X0, Y0 = sites[n]
                            x0, x0_sub = X0 // self.N1_sub, X0 % self.N1_sub
                            y0, y0_sub = Y0 // self.N2_sub, Y0 % self.N2_sub

                            neighbours = [
                                [x0, y0, x0_sub, y0_sub, 0, 0],
                            ]

                            if Y0 + 1 < N2 or pbc:
                                X1, Y1 = X0, (Y0+1)%N2
                                x1, x1_sub = X1 // self.N1_sub, X1 % self.N1_sub
                                y1, y1_sub = Y1 // self.N2_sub, Y1 % self.N2_sub
                                d1 = 0
                                d2 = +1 if pbc else y1-y0
                                neighbours.append([x1, y1%self.N2, x1_sub, y1_sub, d1, d2])

                            if X0 + 1 < N1 or pbc:
                                X1, Y1 = (X0+1)%N1, Y0
                                x1, x1_sub = X1 // self.N1_sub, X1 % self.N1_sub
                                y1, y1_sub = Y1 // self.N2_sub, Y1 % self.N2_sub
                                d1 = +1 if pbc else x1-x0
                                d2 = 0
                                neighbours.append([x1%self.N1, y1, x1_sub, y1_sub, d1, d2])

                            if (X0 + 1 <  N1 and Y0 + 1 < N2) or pbc:
                                X1, Y1 = (X0+1)%N1, (Y0+1)%N2
                                x1, x1_sub = X1 // self.N1_sub, X1 % self.N1_sub
                                y1, y1_sub = Y1 // self.N2_sub, Y1 % self.N2_sub
                                d1 = +1 if pbc else x1-x0
                                d2 = +1 if pbc else y1-y0
                                neighbours.append([x1%self.N1, y1%self.N2, x1_sub, y1_sub, d1, d2])

                            substrate_neighbours.append(neighbours)

                        coords = sites + (0.5, 0.5)
                    case "bridge":
                        match orientation:
                            case "a1":
                                for n in range(L):
                                    X0, Y0 = sites[n]
                                    x0, x0_sub = X0 // self.N1_sub, X0 % self.N1_sub
                                    y0, y0_sub = Y0 // self.N2_sub, Y0 % self.N2_sub

                                    neighbours = [
                                        [x0, y0, x0_sub, y0_sub, 0, 0],
                                    ]

                                    if X0 + 1 < N1 or pbc:
                                        X1, Y1 = (X0+1)%N1, Y0
                                        x1, x1_sub = X1 // self.N1_sub, X1 % self.N1_sub
                                        y1, y1_sub = Y1 // self.N2_sub, Y1 % self.N2_sub
                                        d1 = +1 if pbc else x1-x0
                                        d2 = 0
                                        neighbours.append([x1, y1, x1_sub, y1_sub, d1, d2])

                                        substrate_neighbours.append(neighbours)
                                coords = sites + (0.5, 0)
                            case "a2":
                                for n in range(L):
                                    X0, Y0 = sites[n]
                                    x0, x0_sub = X0 // self.N1_sub, X0 % self.N1_sub
                                    y0, y0_sub = Y0 // self.N2_sub, Y0 % self.N2_sub

                                    neighbours = [
                                        [x0, y0, x0_sub, y0_sub, 0, 0],
                                    ]

                                    if Y0 + 1 < N2 or pbc:
                                        X1, Y1 = X0, (Y0+1)%N2
                                        x1, x1_sub = X1 // self.N1_sub, X1 % self.N1_sub
                                        y1, y1_sub = Y1 // self.N2_sub, Y1 % self.N2_sub
                                        d1 = 0
                                        d2 = +1 if pbc else y1-y0
                                        neighbours.append([x1, y1, x1_sub, y1_sub, d1, d2])

                                        substrate_neighbours.append(neighbours)
                                coords = sites + (0, 0.5)
                            case _:
                                raise ValueError(f"Orientation {orientation} is not supported!")
                    case _:
                        raise ValueError(f"Location {location} is not supported!")
                return sites, coords, substrate_neighbours, impurity_neighbours
            case Shape.Rectangle:
                L = self.params["L"]
                W = self.params["W"]

                if pbc:
                    if L > N2:
                        warnings.warn("Island is too long!")
                else:
                    if L >= N2:
                        warnings.warn("Island is too long!")
                if pbc:
                    if W > N1:
                        warnings.warn("Island is too wide!")
                else:
                    if W >= N2:
                        warnings.warn("Island is too wide!")

                x = N1//2 if N1 % 2 else N1//2-1
                y = N2//2 if N2 % 2 else N2//2-1

                centre = self.params.get("centre", (x, y)) # The island centre is defined in terms of the total number of sites

                left = centre[0] - W // 2
                right = centre[0] + W // 2
                bottom = centre[1] - L // 2
                top = centre[1] + L // 2

                if W % 2:
                    right += 1
                if L % 2:
                    top += 1
                if left == right:
                    right += 1
                if top == bottom:
                    top += 1

                if W == N1 and pbc:
                    left = 0
                    right = N1
                if L == N2 and pbc:
                    bottom = 0
                    top = N2

                sites = np.meshgrid(np.arange(left, right), np.arange(bottom, top))
                sites = np.array(sites).reshape(2, L*W).T
            case Shape.Circle:
                pbc = False
                R = self.params["R"]

                assert 2 * R < N1 and 2 * R < N2

                x = N1//2 if N1 % 2 else N1//2-1
                y = N2//2 if N2 % 2 else N2//2-1

                centre = self.params.get("centre", (x, y)) # The island centre is defined in terms of the total number of sites

                sites = []
                for x, y in np.ndindex(N1, N2):
                    if np.sqrt((x - centre[0])**2 + (y - centre[1])**2) <= R:
                        sites.append([x, y])
                sites = np.array(sites)
            case Shape.Custom:
                sites = self.sites
                coords = self.coords
            case _:
                raise ValueError(f"Shape {self.shape} is not supported!")

        match self.shape:
            case Shape.Rectangle:
                if self.space == Space.RealSpace:
                    pbc_x = pbc and L > 1
                    pbc_y = pbc and W > 1
                else:
                    pbc_x = True
                    pbc_y = True
            case Shape.Circle:
                pbc_x = pbc
                pbc_y = pbc
                L = 2*R
                W = 2*R
            case Shape.Custom:
                pbc_x = False
                pbc_y = False
                L = N1
                W = N2
            case _:
                raise ValueError(f"Shape {self.shape} is not supported!")
        for n, (X0, Y0) in enumerate(sites):
            x0, x0_sub = X0 // self.N1_sub, X0 % self.N1_sub
            y0, y0_sub = Y0 // self.N2_sub, Y0 % self.N2_sub

            neighbours = []

            if X0-1 > 0 or pbc_x:
                X1, Y1 = (X0-1)%N1, Y0
                x1, x1_sub = X1 // self.N1_sub, X1 % self.N1_sub
                y1, y1_sub = Y1 // self.N2_sub, Y1 % self.N2_sub
                d1 = -1 if pbc else x1-x0
                neighbours.append([x1, y1, x1_sub, y1_sub, d1, 0])

            if X0+1 < L or pbc_x:
                X1, Y1 = (X0+1)%N1, Y0
                x1, x1_sub = X1 // self.N1_sub, X1 % self.N1_sub
                y1, y1_sub = Y1 // self.N2_sub, Y1 % self.N2_sub
                d1 = +1 if pbc else x1-x0
                neighbours.append([x1, y1, x1_sub, y1_sub, d1, 0])

            if Y0-1 > 0 or pbc_y:
                X1, Y1 = X0, (Y0-1)%N2
                x1, x1_sub = X1 // self.N1_sub, X1 % self.N1_sub
                y1, y1_sub = Y1 // self.N2_sub, Y1 % self.N2_sub
                d2 = -1 if pbc else y1-y0
                neighbours.append([x1, y1, x1_sub, y1_sub, 0, d2])

            if Y0+1 < W or pbc_y:
                X1, Y1 = X0, (Y0+1)%N2
                x1, x1_sub = X1 // self.N1_sub, X1 % self.N1_sub
                y1, y1_sub = Y1 // self.N2_sub, Y1 % self.N2_sub
                d2 = +1 if pbc else y1-y0
                neighbours.append([x1, y1, x1_sub, y1_sub, 0, d2])

            impurity_neighbours.append(neighbours)

        for n, (X0, Y0) in enumerate(sites):
            x0, x0_sub = X0 // self.N1_sub, X0 % self.N1_sub
            y0, y0_sub = Y0 // self.N2_sub, Y0 % self.N2_sub

            neighbours = [
                [x0, y0, x0_sub, y0_sub, 0, 0],
            ]

            if Y0 + 1 < N2 or pbc:
                X1, Y1 = X0, (Y0+1)%N2
                x1, x1_sub = X1 // self.N1_sub, X1 % self.N1_sub
                y1, y1_sub = Y1 // self.N2_sub, Y1 % self.N2_sub
                d1 = 0 if pbc else x1-x0
                d2 = +1 if pbc else y1-y0
                neighbours.append([x1, y1%self.N2, x1_sub, y1_sub, d1, d2])

            if X0 + 1 < N1 or pbc:
                X1, Y1 = (X0+1)%N1, Y0
                x1, x1_sub = X1 // self.N1_sub, X1 % self.N1_sub
                y1, y1_sub = Y1 // self.N2_sub, Y1 % self.N2_sub
                d1 = +1 if pbc else x1-x0
                d2 = 0 if pbc else y1-y0
                neighbours.append([x1%self.N1, y1, x1_sub, y1_sub, d1, d2])

            if (X0 + 1 <  N1 and Y0 + 1 < N2) or pbc:
                X1, Y1 = (X0+1)%N1, (Y0+1)%N2
                x1, x1_sub = X1 // self.N1_sub, X1 % self.N1_sub
                y1, y1_sub = Y1 // self.N2_sub, Y1 % self.N2_sub
                d1 = +1 if pbc else x1-x0
                d2 = +1 if pbc else y1-y0
                neighbours.append([x1%self.N1, y1%self.N2, x1_sub, y1_sub, d1, d2])

            substrate_neighbours.append(neighbours)

        coords = sites + (0.5, 0.5)

        return sites, coords, substrate_neighbours, impurity_neighbours

    def triangular(self, sites=None):
        pbc = self.params.get("pbc", False)
        if self.space == Space.KSpace:
            pbc = True
        impurity_neighbours = []
        substrate_neighbours = []
        N1 = self.N1 * self.N1_sub
        N2 = self.N2 * self.N2_sub

        match self.shape:
            case Shape.Chain:
                location = self.params.get("location", "hollow")
                spacing = self.params.get("spacing", 0)
                orientation = self.params.get("orientation", "a1")
                L = self.params["L"]
                assert spacing >= 0

                if orientation == "a1":
                    if pbc:
                        if L * (spacing + 1) > N1:
                            warnings.warn("Chain is too long!")
                    else:
                        if L * (spacing + 1) >= N1:
                            warnings.warn("Chain is too long!")
                if orientation == "a2":
                    if pbc:
                        if L * (spacing + 1) > N2:
                            warnings.warn("Chain is too long!")
                    else:
                        if L * (spacing + 1) >= N2:
                            warnings.warn("Chain is too long!")

                x = N1//2 if N1 % 2 else N1//2-1
                y = N2//2 if N2 % 2 else N2//2-1
                centre = self.params.get("centre", (x, y)) # The chain centre is defined in terms of the total number of sites

                match orientation:
                    case "a1":
                        left = centre[0] - (spacing + 1) * L // 2
                        right = centre[0] + (spacing + 1) * L // 2
                        if L % 2 and not spacing % 2:
                            right += 1
                        if left == right:
                            right += 1
                        if L * (spacing + 1) == N1 and pbc:
                            left = 0
                            right = N1
                        sites = [[x, centre[1]] for x in np.arange(left, right, spacing+1)]

                        for n, (X0, Y0) in enumerate(sites):
                            x0, x0_sub = X0 // self.N1_sub, X0 % self.N1_sub
                            y0, y0_sub = Y0 // self.N2_sub, Y0 % self.N2_sub

                            neighbours = []

                            if X0-(spacing+1) > 0 or pbc:
                                X1, Y1 = (X0-(spacing+1))%N1, Y0
                                x1, x1_sub = X1 // self.N1_sub, X1 % self.N1_sub
                                y1, y1_sub = Y1 // self.N2_sub, Y1 % self.N2_sub
                                d1 = -1 if pbc else x1-x0
                                neighbours.append([x1, y1, x1_sub, y1_sub, d1, 0])

                            if X0+(spacing+1) < L or pbc:
                                X1, Y1 = (X0+(spacing+1))%N1, Y0
                                x1, x1_sub = X1 // self.N1_sub, X1 % self.N1_sub
                                y1, y1_sub = Y1 // self.N2_sub, Y1 % self.N2_sub
                                d1 = +1 if pbc else x1-x0
                                neighbours.append([x1, y1, x1_sub, y1_sub, d1, 0])

                            impurity_neighbours.append(neighbours)
                    case "a2":
                        left = centre[1] - (spacing + 1) * L // 2
                        right = centre[1] + (spacing + 1) * L // 2
                        if L % 2:
                            right += 1
                        if left == right == 0:
                            right = 1
                        if L * (spacing + 1) == N2 and pbc:
                            left = 0
                            right = N2
                        sites = [[centre[0], y] for y in np.arange(left, right, spacing+1)]

                        for n, (X0, Y0) in enumerate(sites):
                            x0, x0_sub = X0 // self.N1_sub, X0 % self.N1_sub
                            y0, y0_sub = Y0 // self.N2_sub, Y0 % self.N2_sub

                            neighbours = []

                            if Y0-(spacing+1) > 0 or pbc:
                                X1, Y1 = X0, (Y0-(spacing+1))%N2
                                x1, x1_sub = X1 // self.N1_sub, X1 % self.N1_sub
                                y1, y1_sub = Y1 // self.N2_sub, Y1 % self.N2_sub
                                d2 = -1 if pbc else y1-y0
                                neighbours.append([x1, y1, x1_sub, y1_sub, 0, d2])

                            if Y0+(spacing+1) < L or pbc:
                                X1, Y1 = X0, (Y0+(spacing+1))%N2
                                x1, x1_sub = X1 // self.N1_sub, X1 % self.N1_sub
                                y1, y1_sub = Y1 // self.N2_sub, Y1 % self.N2_sub
                                d2 = +1 if pbc else y1-y0
                                neighbours.append([x1, y1, x1_sub, y1_sub, 0, d2])

                            impurity_neighbours.append(neighbours)
                    case _:
                        raise ValueError(f"Orientation {orientation} is not supported!")
                sites = np.array(sites)

                match location:
                    case "hollow":
                        for n in range(L):
                            X0, Y0 = sites[n]
                            x0, x0_sub = X0 // self.N1_sub, X0 % self.N1_sub
                            y0, y0_sub = Y0 // self.N2_sub, Y0 % self.N2_sub

                            neighbours = [
                                [x0, y0, x0_sub, y0_sub, 0, 0],
                            ]

                            if Y0 + 1 < N2 or pbc:
                                X1, Y1 = X0, (Y0+1)%N2
                                x1, x1_sub = X1 // self.N1_sub, X1 % self.N1_sub
                                y1, y1_sub = Y1 // self.N2_sub, Y1 % self.N2_sub
                                d1 = 0
                                d2 = +1 if pbc else y1-y0
                                neighbours.append([x1, y1%self.N2, x1_sub, y1_sub, d1, d2])

                            if X0 + 1 < N1 or pbc:
                                X1, Y1 = (X0+1)%N1, Y0
                                x1, x1_sub = X1 // self.N1_sub, X1 % self.N1_sub
                                y1, y1_sub = Y1 // self.N2_sub, Y1 % self.N2_sub
                                d1 = +1 if pbc else x1-x0
                                d2 = 0
                                neighbours.append([x1%self.N1, y1, x1_sub, y1_sub, d1, d2])

                            substrate_neighbours.append(neighbours)

                        coords = sites + (0.25, 0.5)
                    case "bridge":
                        match orientation:
                            case "a1":
                                for n in range(L):
                                    X0, Y0 = sites[n]
                                    x0, x0_sub = X0 // self.N1_sub, X0 % self.N1_sub
                                    y0, y0_sub = Y0 // self.N2_sub, Y0 % self.N2_sub

                                    neighbours = [
                                        [x0, y0, x0_sub, y0_sub, 0, 0],
                                    ]

                                    if X0 + 1 < N1 or pbc:
                                        X1, Y1 = (X0+1)%N1, Y0
                                        x1, x1_sub = X1 // self.N1_sub, X1 % self.N1_sub
                                        y1, y1_sub = Y1 // self.N2_sub, Y1 % self.N2_sub
                                        d1 = +1 if pbc else x1-x0
                                        d2 = 0
                                        neighbours.append([x1, y1, x1_sub, y1_sub, d1, d2])

                                        substrate_neighbours.append(neighbours)
                                coords = sites + (0.25, 0)
                            case "a2":
                                for n in range(L):
                                    X0, Y0 = sites[n]
                                    x0, x0_sub = X0 // self.N1_sub, X0 % self.N1_sub
                                    y0, y0_sub = Y0 // self.N2_sub, Y0 % self.N2_sub

                                    neighbours = [
                                        [x0, y0, x0_sub, y0_sub, 0, 0],
                                    ]

                                    if Y0 + 1 < N2 or pbc:
                                        X1, Y1 = X0, (Y0+1)%N2
                                        x1, x1_sub = X1 // self.N1_sub, X1 % self.N1_sub
                                        y1, y1_sub = Y1 // self.N2_sub, Y1 % self.N2_sub
                                        d1 = 0
                                        d2 = +1 if pbc else y1-y0
                                        neighbours.append([x1, y1, x1_sub, y1_sub, d1, d2])

                                        substrate_neighbours.append(neighbours)
                                coords = sites + (0, 0.25)
                            case _:
                                raise ValueError(f"Orientation {orientation} is not supported!")
                    case _:
                        raise ValueError(f"Location {location} is not supported!")
                return sites, coords, substrate_neighbours, impurity_neighbours
            case _:
                raise ValueError(f"Shape {shape} is not implemented!")
