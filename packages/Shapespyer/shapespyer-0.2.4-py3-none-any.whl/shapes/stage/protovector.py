"""
.. module:: protovector
   :platform: Linux - tested, Windows [WSL Ubuntu] - tested
   :synopsis: contains class Vec3 for creating and manipulating 3D vectors

.. moduleauthor:: Dr Andrey Brukhno <andrey.brukhno[@]stfc.ac.uk>

The module provides class **Vec3** (x, y, z) for creating and manipulating 3D vectors.
A few tests below exemplify the usage of Vec3 objects.

.. testsetup:: *

   from math import pi, sqrt
   from shapes.stage.protovector import Vec3

Example 0
~~~~~~~~~

Creating zero-vector (0,0,0)

**NOTE:** *operations attempting adding or removing vector components are invalid!*

.. testcode:: test0

   # creating zero-vector (0,0,0)
   ov = Vec3()
   print(f'Example 0: Zero vector = {ov}')

   # the following operations on Vec3 are invalid
   ov.append(2)
   ov.remove(0)
   ov.pop()
   print(f'Example 0: Zero vector = {ov.insert(len(ov),3)} after ov.insert({len(ov)},3)')
   print(f'Example 0: Zero vector = {ov.extend([5,6,7])} after ov.extend({[5,6,7]})')

The output should be:

.. testoutput:: test0

   Example 0: Zero vector = Vec3[0.0, 0.0, 0.0]
   Vec3.append(): Number of components cannot be changed!
   Vec3.remove(): Number of components cannot be changed!
   Vec3.pop(): Number of components cannot be changed!
   Vec3.insert(): Number of components cannot be changed!
   Example 0: Zero vector = Vec3[0.0, 0.0, 0.0] after ov.insert(3,3)
   Vec3.extend(): Number of components cannot be changed!
   Example 0: Zero vector = Vec3[0.0, 0.0, 0.0] after ov.extend([5, 6, 7])

Example 1
~~~~~~~~~

Creating and manipulating 3D vectors -- basic operations

.. testcode:: test1

   # creating 3D vector 'av' with coordinates (x=3, y=4, z=0)
   av = Vec3(3, 4, 0)
   print(f'Example 1a: |av| = abs( {av} ) = {abs(av)}')

   # creating another 3D vector 'bv' by copying and inverting 'av'
   bv = -av.copy()
   # in-place manipulations on 'bv'
   bv *= 4
   bv /= -2
   bv -= Vec3(2,4,6)
   bv += 0.5*Vec3(4,8,12)
   print(f'Example 1b: |bv| = {bv}.norm() = {bv.norm()}')

   # creating another 3D vector 'cv' based on 'bv'
   cv = -2.0*bv/8.0
   print(f'Example 1c: unit_vector(cv) = Vec3.unit( {cv} ) = {Vec3.unit(cv)}')

The output should be:

.. testoutput:: test1

   Example 1a: |av| = abs( Vec3[3, 4, 0] ) = 5.0
   Example 1b: |bv| = Vec3[6.0, 8.0, 0.0].norm() = 10.0
   Example 1c: unit_vector(cv) = Vec3.unit( Vec3[-1.5, -2.0, -0.0] ) = Vec3[-0.6, -0.8, -0.0]

Example 2
~~~~~~~~~

Creating **Vec3** objects from *tuple* or *list*, and other operations

.. testcode:: test2

   ta = (3,4,0)
   av = Vec3(*ta)
   lb = [0.,0.,1.0]
   bv = Vec3(*lb)
   cv = av.vec3alignedTo(bv.unit())
   phi = av.angleFrom(bv)
   rotM = av.getMatrixAligningTo(bv)
   print(f'Example 2a: phi * 180/pi = {round(phi*180/pi,5)} = {round(bv.angleFrom(av, False),5)}')
   print(f'Example 2b: {av}.vec3alignedTo({bv.unit()}) = {cv}')
   print(f'Example 2c: array({cv}) = {av.arr3alignedTo(bv.unit())}')
   print('Example 2d: Rotation matrix for av || bv = [', *rotM, ']')

The output should be:

.. testoutput:: test2

   Example 2a: phi * 180/pi = 90.0 = 90.0
   Example 2b: Vec3[3, 4, 0].vec3alignedTo(Vec3[0.0, 0.0, 1.0]) = Vec3[0.0, 0.0, 5.0]
   Example 2c: array(Vec3[0.0, 0.0, 5.0]) = [4.4408921e-16 0.0000000e+00 5.0000000e+00]
   Example 2d: Rotation matrix for av || bv = [ [ 0.64 -0.48 -0.6 ] [-0.48  0.36 -0.8 ] [0.6 0.8 0. ] ]

"""

# This software is provided under The Modified BSD-3-Clause License (Consistent with Python 3 licenses).
# Refer to and abide by the Copyright detailed in LICENSE file found in the root directory of the library!

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
__version__ = "0.2.0 (Beta)"

# TODO: unify the coding style:
# TODO: CamelNames for Classes, camelNames for functions/methods & variables (where meaningful)
# TODO: hint on method/function return data type(s), same for the interface arguments
# TODO: one empty line between functions/methods & groups of interrelated imports
# TODO: two empty lines between Classes & after all the imports done
# TODO: classes and (lengthy) methods/functions must finish with a closing comment: '# end of <its name>'
# TODO: meaningful DocStrings right after the definition (def) of Class/method/function/module
# TODO: comments must be meaningful and start with '# ' (hash symbol followed by a space)
# TODO: insightful, especially lengthy, comments must be prefixed by develoer's initials as follows:

import logging
from math import sqrt, acos, pi
from numpy import array, dot, cross, double
from numpy.linalg import norm

from shapes.basics.globals import TINY, UnitM, InvM0, InvM1

logger = logging.getLogger("__main__")


class Vec3(list):

    """
    Class **Vec3(list)** - defines 3D vector object in Euclidean space, based on Python *list* object with fixed
    number of components.

    The class provides methods for basic vector manipulation: scaling (multiplication and division by a scalar),
    **dot** and **cross** products with another vector, **cos(alpha)** and **alpha** calculation
    where **alpha** is the angle between `self` and another vector, **norm()** and **renorm()** operations, and
    methods for aligning `self` with another vector (which is often more convenient than rotation by Euler angles).

    Parameters
    ----------
    x, y, z : float
        vector Cartesian coordinates
    """

    def __init__(self, x: float = 0.0, y: float = 0.0 , z: float = 0.0):
        super(Vec3, self).__init__([x, y, z])

    def __repr__(self):
        return f'{self.__class__.__name__}{[ float(round(vc, 8)) for vc in self ]}'

    def copy(self):
        """
        **Returns** a copy (another instance) of the vector with the same coordinates as `self`
        """
        return Vec3(*self[:])

    #def pop(self, __index: int = ...):
    def pop(self, *arg, **kwarg):
        """
        **Empty** method to block the underlying `list.pop()` with a warning
        """
        logger.warning("Number of components cannot be changed!")
        return self

    def remove(self, *arg, **kwarg):
        """
        **Empty** method to block the underlying `list.remove()` with a warning
        """
        logger.warning("Number of components cannot be changed!")
        return self

    def append(self, *arg, **kwarg):
        """
        **Empty** method to block the underlying `list.append()` with a warning
        """
        logger.warning("Number of components cannot be changed!")
        return self

    def insert(self, *arg, **kwarg):
        """
        **Empty** method to block the underlying `list.insert()` with a warning
        """
        logger.warning("Number of components cannot be changed!")
        return self

    def extend(self, *arg, **kwarg):
        """
        **Empty** method to block the underlying `list.extend()` with a warning
        """
        logger.warning("Number of components cannot be changed!")
        return self

    def __neg__(self):
        """
        **Returns** a new vector = -`self` (i.e. inverted)
        """
        x, y, z = self
        return Vec3(-x, -y, -z)

    def __add__(self, other):
        """
        **Returns** a new vector = the sum of `self` and another vector
        """
        x1, y1, z1 = self
        x2, y2, z2 = other
        return Vec3(x1+x2, y1+y2, z1+z2)

    def __iadd__(self, other):
        """
        **Alters and returns** `self` to the sum with another vector
        """
        self[0] += other[0]
        self[1] += other[1]
        self[2] += other[2]
        return self

    def __sub__(self, other):
        """
        **Returns** a new vector = the difference between `self` and another vector
        """
        x1, y1, z1 = self
        x2, y2, z2 = other
        return Vec3(x1-x2, y1-y2, z1-z2)

    def __isub__(self, other):
        """
        **Alters and returns** `self` to the difference between `self` and another vector
        """
        self[0] -= other[0]
        self[1] -= other[1]
        self[2] -= other[2]
        return self

    def __truediv__(self, other):
        """
        **Returns** a new vector = a copy of `self` divided by a scalar
        """
        x, y, z = self
        fnum = 1.0 / float(other)
        return Vec3(x*fnum, y*fnum, z*fnum)

    def __idiv__(self, other):
        """
        **Alters and returns** `self` by dividing it by a scalar
        """
        flo = 1.0 / float(other)
        self[0] *= flo  # self[0] * flo
        self[1] *= flo  # self[1] * flo
        self[2] *= flo  # self[2] * flo
        return self

    def __itruediv__(self, other):
        """
        **Alters and returns** `self` by dividing it by a scalar
        """
        flo = 1.0 / float(other)
        self[0] *= flo
        self[1] *= flo
        self[2] *= flo
        return self

    def __mul__(self, other):
        """
        **Returns** a new vector = a copy of `self` multiplied by a scalar
        """
        flo = float(other)
        return Vec3(self[0]*flo, self[1]*flo, self[2]*flo)

    def __rmul__(self, other):
        """
        **Returns** a new vector = a copy of `self` multiplied by a scalar
        """
        flo = float(other)
        return Vec3(self[0]*flo, self[1]*flo, self[2]*flo)

    def __imul__(self, other):
        """
        **Alters and returns** `self` by multiplying it by a scalar
        """
        #flo = float(other)
        self[0] *= other # flo # self[0] * flo
        self[1] *= other # flo # self[1] * flo
        self[2] *= other # flo # self[2] * flo
        return self  # Vec3(self[0]*flo, self[1]*flo, self[2]*flo) #self

    def __abs__(self):
        """
        **Returns** norm (length) of `self`
        """
        x, y, z = self
        return sqrt(x*x + y*y + z*z)

    abs = __abs__
    norm = abs

    def renorm(self):
        """
        **Alters and returns** `self` upon (re-)normalisation
        """
        x, y, z = self
        rnorm = 1.0 / self.norm()
        self[0] = x * rnorm
        self[1] = y * rnorm
        self[2] = z * rnorm
        return self

    def unit(self):
        """
        **Returns** a new unit vector = (re-)normalised `self`
        """
        x, y, z = self
        rnorm = 1.0 / self.norm()
        return Vec3(x * rnorm, y * rnorm, z * rnorm)

    def vecProd(self, other):
        """
        **Returns** vector (cross-) product between `self` and another vector
        """
        x1, y1, z1 = self
        x2, y2, z2 = other
        return Vec3(y1*z2 - z1*y2, z1*x2 - x1*z2, x1*y2 - y1*x1)

    def dotProd(self, other):
        """
        **Returns** scalar (dot-) product between `self` and another vector
        """
        x1, y1, z1 = self
        x2, y2, z2 = other
        return x1*x2 + y1*y2 + z1*z2

    def cosAngleFrom(self, other):
        """
        **Returns** cos(phi) where `phi` is the angle between `self` and another vector
        """
        return self.dotProd(other) / (self.norm()*other.norm())

    def angleFrom(self, other, isRad=True):
        """
        **Returns** angle between `self` and another vector (in radians by default)
        """
        phi = acos(self.cosAngleFrom(other))
        if not isRad:
            phi *= 180./pi
        return phi

    def arr3(self, *args, **keys):
        """
        **Returns** numpy.array(self)
        """
        return array(self, *args, **keys)

    def arr3alignedTo(self, avec):
        """
        **Returns** numpy.array(vec) where `vec` is a new vector obtained by aligning `self`
        parallel to another vector (`avec`)
        """
        a3 = self.arr3(double)
        b3 = avec
        if isinstance(avec, Vec3):
            b3 = avec.arr3(double)
        f = a3 / norm(a3)
        t = b3 / norm(b3)
        c = dot(f, t)
        if (1.0 - c) < 2.0 * TINY:
            return a3
        if (1.0 + c) < 2.0 * TINY:
            return -a3
        h = (1.0 - c) / (1.0 - c**2)
        v = cross(f, t)
        u = v / norm(v)
        vx, vy, vz = v
        rotM = array([[c + h * vx ** 2, h * vx * vy - vz, h * vx * vz + vy],
                      [h * vx * vy + vz, c + h * vy ** 2, h * vy * vz - vx],
                      [h * vx * vz - vy, h * vy * vz + vx, c + h * vz ** 2]])
        return rotM.dot(a3)
    # end of arr3alignedTo()

    def vec3alignedTo(self, avec):
        """
        **Returns** a new vector obtained by aligning `self` parallel to another vector (`avec`)
        """
        return Vec3(*self.arr3alignedTo(avec))

    def getMatrixAligningTo(self, avec):
        """
        **Returns** numpy.array(rotM) where `rotM` is the matrix
        aligning `self` parallel to another vector
        """
        a3 = self.arr3(double)
        b3 = avec
        if isinstance(avec, Vec3):
            b3 = avec.arr3(double)
        f = a3 / norm(a3)
        t = b3 / norm(b3)
        c = dot(f, t)
        c0 = c
        if (1.0 - c0) < 2.0 * TINY:
            c = 1.0 - TINY
            #return array(UnitM)
        if (1.0 + c0) < 2.0 * TINY:
            c = TINY - 1.0
            #return array(InvM)
        h = (1.0 - c) / (1.0 - c**2)
        v = cross(f, t)
        #u = v / norm(v)
        vx, vy, vz = v
        rotM = [[c + h * vx ** 2, h * vx * vy - vz, h * vx * vz + vy],
                [h * vx * vy + vz, c + h * vy ** 2, h * vy * vz - vx],
                [h * vx * vz - vy, h * vy * vz + vx, c + h * vz ** 2]]
        return array(rotM)
    # end of getMatrixAligningTo()

# end of class Vec3