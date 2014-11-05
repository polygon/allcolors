# -*- coding: utf-8 -*-
"""
Created on Sun Nov  2 00:42:25 2014

@author: jan
"""

import numpy as np

def build_lengthmap(size):
    X, Y, Z = np.meshgrid(range(-size,size+1), range(-size,size+1), range(-size,size+1))
    dists = X**2 + Y**2 + Z**2
    idx_x, idx_y, idx_z = np.unravel_index(np.argsort(dists, axis=None), dists.shape)
    sort_dist = dists[idx_x, idx_y, idx_z]
    sort_dist_rev = sort_dist[::-1]
    lengthmap = []
    cidx = sort_dist_rev.size - 1
    while cidx >= 0:
        pivot = sort_dist_rev[cidx]
        first = np.argmax(sort_dist_rev <= pivot * 1.1)
        rng = np.arange(len(sort_dist_rev) - cidx - 1, len(sort_dist_rev) - first)
        out = np.zeros((rng.size, 3))
        out[:, 0] = X[idx_x[rng], idx_y[rng], idx_z[rng]]
        out[:, 1] = Y[idx_x[rng], idx_y[rng], idx_z[rng]]
        out[:, 2] = Z[idx_x[rng], idx_y[rng], idx_z[rng]]
        lengthmap.append(out)
        cidx = first-1
        
    return lengthmap

class CloseColors:
    def __init__(self):
        self.nextset = np.array([])
        self.colors = np.mgrid[0:64, 0:64, 0:64]
        self.col_avail = np.ones((64, 64, 64), dtype=bool)
        self.coord_avail = np.ones((262144), dtype=bool)
        self.field = np.zeros((512, 512, 3))
        self.lmap = build_lengthmap(63)

    def filtered_region(self, (x, y), avail):
        offsets = np.array([[-1, -1], [0, -1], [1, -1],
                            [-1, 0], [1, 0],
                            [-1, 1], [0, 1], [1, 1]])
        coords = offsets + (x,y)
        coords = coords[(0 <= coords[:, 0])]
        coords = coords[(0 <= coords[:, 1])]
        coords = coords[(coords[:, 0] < 512)]
        coords = coords[(coords[:, 1] < 512)]
        coordslin = coords[:, 0] * 512 + coords[:, 1]
        coords = coords[self.coord_avail[coordslin] == avail, :]
        coordslin = coordslin[self.coord_avail[coordslin] == avail]
        return coords, coordslin
        

    def add_nextset(self, (x, y)):
        # Next one could be uniqie, but this increases the chance
        # of choosing a value that is requested more often
        _, coordslin = self.filtered_region((x, y), True)
        self.nextset = np.append(self.nextset, coordslin)
        
    def get_nextset(self):
        if self.nextset.size == 0:
            return None
        index = np.random.randint(self.nextset.size)
        coord = self.nextset[index]
        self.nextset = self.nextset[self.nextset != coord]
        return (int(coord / 512), int(np.mod(coord, 512)))
        
    # RGB as indexed integer from range 0-31
    def seed(self, (x, y), (r, g, b)):
        coord = y*512 + x
        if not self.col_avail[r, g, b] or not self.coord_avail[coord]:
            return None
        self.field[x, y, :] = (r, g, b)
        self.col_avail[r, g, b] = False
        self.coord_avail[x*512 + y] = False
        self.add_nextset((x, y))
        return tuple(np.array([r, g, b]) * 255. / 63.)
    
    #@profile
    def iterate(self):
        coord = self.get_nextset()
        if coord is None:
            return None
        (x, y) = coord
        (neighbors, _) = self.filtered_region((x, y), False)
        self.dists = np.zeros([64, 64, 64])
        avgcol = np.zeros(3)
        for n in neighbors:
            avgcol = avgcol + self.field[n[0], n[1], :]
        avgcol = np.round(avgcol / neighbors.shape[0])
#        print neighbors

        for lme in self.lmap:
            lma = lme + avgcol
            lma = lma[(0 <= lma[:, 0])]
            lma = lma[(0 <= lma[:, 1])]
            lma = lma[(0 <= lma[:, 2])]
            lma = lma[(lma[:, 0] < 64)]
            lma = lma[(lma[:, 1] < 64)]
            lma = lma[(lma[:, 2] < 64)]
            sca = np.ravel(self.col_avail)
            lma = lma.astype(np.int64)
            sci = np.ravel_multi_index((lma[:, 0], lma[:, 1], lma[:, 2]), self.col_avail.shape)
            lma = lma[sca[sci] == True]
            if lma.size > 0:
                sidx = np.random.randint(0, lma.shape[0])
                (r, g, b) = lma[sidx, :]
                break
        
#        (nr, ng, nb) = avgcol
#        ref = np.array([[[[nr]]], [[[ng]]], [[[nb]]]])
#            a = self.colors - ref
#            b = a**2
#            c = b.sum(0)
#            self.dists = self.dists + c
#        self.dists = self.dists + ((self.colors - ref)**2).sum(0)
#        self.dists[self.col_avail == False] = np.inf
#        best = np.unravel_index(np.argmin(self.dists), self.dists.shape)
#        (r, g, b) = best
        self.col_avail[r, g, b] = False
        self.add_nextset((x, y))
        self.coord_avail[x*512 + y] = False
        self.field[x, y, :] = (r, g, b)
        return (x, y), tuple(np.array([r, g, b]) * 255. / 63.)
            