"""
.. module:: functions
   :platform: Linux - tested, Windows (WSL Ubuntu) - tested
   :synopsis: helper functions unfit for inclusion in any abstraction class

.. moduleauthor:: Dr Andrey Brukhno <andrey.brukhno[@]stfc.ac.uk>

"""

# This software is provided under The Modified BSD-3-Clause License 
# (Consistent with Python 3 licenses).
# Refer to and abide by the Copyright detailed in LICENSE file found 
# in the root directory of the library.

##################################################
#                                                #
#  Shapespyer - soft matter structure generator  #
#                                                #
#  Author: Dr Andrey Brukhno (c) 2020 - 2025     #
#          Daresbury Laboratory, SCD, STFC/UKRI  #
#                                                #
##################################################

##from __future__ import absolute_import
__author__ = "Andrey Brukhno"


import logging
import sys
from functools import wraps
from math import copysign
from time import time
import numpy as np
import scipy.spatial.distance as ssd
from shapes.basics.globals import *

logger = logging.getLogger("__main__")

# from math import copysign

def sfx_rval(arg: float, ndgt: int = 2) -> str:
    sfmt = "{:." + f"{ndgt}" + "f}"
    return sfmt.format(np.round(arg, ndgt)).strip().rstrip("0").rstrip(".")

def sec2hms(secs: float = 0.0, is_num: bool = False) -> str | tuple[float]:
    m, s = divmod(secs, 60)
    h, m = divmod(m, 60)
    if is_num:
        return (h, m, s)
    elif int(h) > 1:
        return f"{h:.0f}:{m:.0f}:{s:.3f}"
    elif int(m) > 1:
        return f"{m:.0f}:{s:.3f}"
    else:
        return f"{s:.5f} seconds"

def timing(func):
    @wraps(func)
    def wrap(*args, **kwargs):
        ts = time()
        result = func(*args, **kwargs)
        te = time()
        logger.debug(f"function {func.__name__}() took: {sec2hms(te-ts)}")

        return result

    return wrap

def nint(x):
    return np.rint(x)
    # return round(x+copysign(TNST,x))
    # return np.round(x+np.copysign(TNST,x))

def arr3pbc(dvec, box):
    dvec[:] -= box[:] * np.rint(dvec[:]/box[:])
    return dvec[:] # - box[:] * np.rint(dvec[:]/box[:])

def pbc_rect(dvec, box):
    dvec[0] -= box[0] * float(nint(dvec[0] / box[0]))
    dvec[1] -= box[1] * float(nint(dvec[1] / box[1]))
    dvec[2] -= box[2] * float(nint(dvec[2] / box[2]))
    return dvec


def pbc_cube(dvec, box):
    rbox = 1.0 / box
    dvec[0] -= box * float(nint(dvec[0] * rbox))
    dvec[1] -= box * float(nint(dvec[1] * rbox))
    dvec[2] -= box * float(nint(dvec[2] * rbox))
    return dvec


def isVec3Like(vec):
    return hasattr(vec, "__len__") and len(vec) == 3


def pbc_all(dvec, box):
    if isVec3Like(dvec):
        if hasattr(box, "__len__"):
            if len(box) == 3:
                # logger.debug(f'Box = {box} is a vector => using pbc_rect()')
                return pbc_rect(dvec, box)
            else:
                logger.error(
                    f"Box = {box} does not qualify as either scalar or 3D vector "
                    f"- FULL STOP!!!"
                )
                sys.exit(1)
        else:
            # logger.info(f'Box = {box} is a scalar => using pbc_cube()')
            return pbc_cube(dvec, box)
    else:
        logger.error(
            f"dVec = {dvec} does not qualify as 3D vector - FULL STOP!!!"
        )
        sys.exit(1)


def pbc(dvec, box):
    #return pbc_rect(dvec, box)
    hbox = box*0.5
    if dvec[0] >= hbox[0]:
        # if (dvec[0] - hbox[0]) > TINY:
        dvec[0] -= box[0]
        if dvec[0] >= hbox[0]:
            dvec[0] -= box[0] * float(nint(dvec[0] / box[0]))
    elif dvec[0] < -hbox[0]:
        # elif (dvec[0] + hbox[0]) < -TINY:
        dvec[0] += box[0]
        if dvec[0] < -hbox[0]:
            dvec[0] -= box[0] * float(nint(dvec[0] / box[0]))
    if dvec[1] >= hbox[1]:
        # if (dvec[1] - hbox[1]) > TINY:
        dvec[1] -= box[1]
        if dvec[1] >= hbox[1]:
            dvec[1] -= box[1] * float(nint(dvec[1] / box[1]))
    elif dvec[1] < -hbox[1]:
        # elif (dvec[1] + hbox[1]) < -TINY:
        dvec[1] += box[1]
        if dvec[1] < -hbox[1]:
            dvec[1] -= box[1] * float(nint(dvec[1] / box[1]))
    if dvec[2] >= hbox[2]:
        # if (dvec[2] - hbox[2]) > TINY:
        dvec[2] -= box[2]
        if dvec[2] >= hbox[2]:
            dvec[2] -= box[2] * float(nint(dvec[2] / box[2]))
    elif dvec[2] < -hbox[2]:
        # elif (dvec[2] + hbox[2]) < -TINY:
        dvec[2] += box[2]
        if dvec[2] < -hbox[2]:
            dvec[2] -= box[2] * float(nint(dvec[2] / box[2]))
    return dvec

def pbc_dim(crd: float, box: float) -> float:
    hbox = box * 0.5
    if crd >= hbox:
        crd -= box
        if crd >= hbox:
            crd -= box * float(nint(crd / box))
    elif crd < -hbox:
        crd += box
        if crd < -hbox:
            crd -= box * float(nint(crd / box))
    return crd

def get_mins(axyz):
    vmin = [0.0, 0.0, 0.0]
    imin = [-1, -1, -1]
    if axyz:
        mini = []
        vmin[0] = min(axyz, key=lambda x: x[0])[0]
        mini.append([i for i, xxx in enumerate(axyz) if vmin[0] == xxx[0]])
        logger.debug(f"get_mins(0): Min(x) = {vmin[0]} @ {mini[0]}")
        # " @ " +str( [(i, xxx.index(xmin)) for i, xxx in enumerate(axyz) if xmin in xxx] ))

        vmin[1] = min(axyz, key=lambda y: y[1])[1]
        mini.append([i for i, yyy in enumerate(axyz) if vmin[1] == yyy[1]])
        logger.debug(f"get_mins(1): Min(y) = {vmin[1]} @ {mini[1]}")
        # " @ " +str( [(i, yyy.index(ymin)) for i, yyy in enumerate(axyz) if ymin in yyy] ))

        vmin[2] = min(axyz, key=lambda z: z[2])[2]
        mini.append([i for i, zzz in enumerate(axyz) if vmin[2] == zzz[2]])
        logger.debug(f"get_mins(2): Min(z) = {vmin[2]} @ {mini[2]}")
        # " @ " +str( [(i, zzz.index(zmin)) for i, zzz in enumerate(axyz) if zmin in zzz] ))

        for k in range(len(mini)):
            imin[k] = mini[k][int(len(mini[k]) / 2)]
            # if len(mini[k]) > 1 :
            # mini[k][0] = mini[k][int(len(mini[k])/2)]
            # del mini[k][1:]
    return vmin, imin


# end of get_mins()


def get_maxs(axyz):
    vmax = [0.0, 0.0, 0.0]  # [-HUGE,-HUGE,-HUGE]
    imax = [-1, -1, -1]
    if axyz:
        maxi = []
        vmax[0] = max(axyz, key=lambda x: x[0])[0]
        maxi.append([i for i, xxx in enumerate(axyz) if vmax[0] == xxx[0]])
        logger.debug(f"get_maxs(0): Max(x) = {vmax[0]} @ {maxi[0]}")
        # " @ " +str( [(i, xxx.index(xmax)) for i, xxx in enumerate(axyz) if xmax in xxx] ))

        vmax[1] = max(axyz, key=lambda y: y[1])[1]
        maxi.append([i for i, yyy in enumerate(axyz) if vmax[1] == yyy[1]])
        logger.debug(f"get_maxs(1): Max(y) = {vmax[1]} @ {maxi[1]}")
        # " @ " +str( [(i, yyy.index(ymax)) for i, yyy in enumerate(axyz) if ymax in yyy] ))

        vmax[2] = max(axyz, key=lambda z: z[2])[2]
        maxi.append([i for i, zzz in enumerate(axyz) if vmax[2] == zzz[2]])
        logger.debug(f"get_maxs(2): Max(z) = {vmax[2]} @ {maxi[2]}")
        # " @ " +str( [(i, zzz.index(zmax)) for i, zzz in enumerate(axyz) if zmax in zzz] ))

        for k in range(len(maxi)):
            imax[k] = maxi[k][int(len(maxi[k]) / 2)]
            # if len(maxi[k]) > 1 :
            # maxi[k][0] = maxi[k][int(len(maxi[k])/2)]
            # del maxi[k][1:]
    return vmax, imax


# end of get_maxs()

def pairsDist(Vecs):
    """
    Returns all pairwise distances for Vecs matrix
    """
    return np.sqrt(((Vecs[:,:,np.newaxis] - Vecs[:,np.newaxis,:])**2).sum(axis=0))

def pairsDist2(Vecs):
    """
    Returns all pairwise squared distances for Vecs matrix
    """
    return ((Vecs[:,:,np.newaxis] - Vecs[:,np.newaxis,:])**2).sum(axis=0)

def distSSD(xyz, XYZ, **kwargs):
    """
    Returns distances between items of xyz against XYZ
    """
    dist = ssd.cdist(xyz.reshape(1,-1), XYZ, **kwargs).flatten()
    return dist

def knn(xyz, XYZ, k, **kwargs):
    """
    Returns indices of k nearest neighbours of xyz in XYZ
    """
    dist = ssd.cdist(xyz.reshape(1,-1), XYZ, **kwargs).flatten()
    return np.argpartition(dist, k)[:k]

def rnn(xyz, XYZ, dmax, **kwargs):
    """
    Returns nearest neighbours of xyz in XYZ within specified distance (dmax)
    """
    dist = ssd.cdist(xyz.reshape(1,-1), XYZ, **kwargs).flatten()
    return np.where(dist < dmax)
