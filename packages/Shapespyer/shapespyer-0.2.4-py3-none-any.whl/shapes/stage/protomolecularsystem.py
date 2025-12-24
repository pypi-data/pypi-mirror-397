"""
.. module:: protomolecularsystem
       :platform: Linux - tested, Windows [WSL Ubuntu] - tested
       :synopsis: contributes to the hierarchy of classes:
        Atom > AtomSet > Molecule > MoleculeSet > MolecularSystem

.. moduleauthor:: Dr Andrey Brukhno <andrey.brukhno[@]stfc.ac.uk>

The module contains class MolecularSystem(object)
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

#from math import sqrt, sin, cos #, acos
import logging
from numpy import array, sum #, dot #, cross, random, double
from numpy.linalg import norm

from shapes.basics.defaults import NL_INDENT
from shapes.basics.globals import TINY, Pi #, InvM1
from shapes.basics.functions import pbc, timing #, pbc_rect, pbc_cube
from shapes.basics.mendeleyev import Chemistry

from shapes.stage.protovector import Vec3
#from shapes.stage.protoatom import Atom
#from shapes.stage.protoatomset import AtomSet
#from shapes.stage.protomolecule import Molecule
from shapes.stage.protomoleculeset import MoleculeSet
from shapes.stage.protovector import Vec3

logger = logging.getLogger("__main__")


class MolecularSystem(object):

    def __init__(self,
                 sname : str = 'empty',
                 stype : str = 'empty',
                 molsets : list = None, # [],
                 vbox : list | Vec3 = Vec3()
                 ) -> None:
        self.name = sname
        self.type = stype
        self.mass = 0.0
        self.chrg = 0.0
        self.vbox = None
        self.rvec = None
        self.rcog = None
        self.items = molsets
        self.nitems = len(self.items) if molsets else 0
        if self.items:
            self.refresh()
        self.isMassElems = False
        self.isBoxSet = False
        if isinstance(vbox, Vec3):
            self.vbox = vbox
            self.isBoxSet = True
        elif isinstance(vbox, list):
            if len(vbox) == 3:
                self.vbox = Vec3(vbox[0], vbox[1], vbox[2])
                self.isBoxSet = True
        if not self.isBoxSet:
            logger.info(f"Input {vbox} for box does"
                        f" not qualify as Vec3() - skipping (box not set)!")

    @timing
    def copy(self):
        """
        **Returns** a new MolecularSet object with the same attributes as `self`
        """
        new_sys = MolecularSystem(sname=self.name, stype=self.type) #, molsets=new_items)
        new_items = [ mset.copy() for mset in self.items ]
        new_sys.items  = new_items
        new_sys.nitems = self.nitems
        new_sys.mass = self.mass
        new_sys.chrg = self.chrg
        new_sys.rvec = self.rvec
        new_sys.rcog = self.rcog
        new_sys.isMassElems = self.isMassElems
        new_sys.isBoxSet = self.isBoxSet
        new_sys.vbox = self.vbox
        # for mset in self.items:
        #     new_sys.items.append(mset.copy())
        return new_sys

    def getNitems(self) -> int:
        self.nitems = len(self.items)
        return self.nitems

    def getNspecies(self) -> int:
        return self.getNitems()

    def getSpecies(self, i: int = 0) -> list:  # i-th unique Mol. Set
        if i > len(self.items) - 1:
            logger.info(f"Species index {i} > {len(self.items)} - 1")
        return self.items[i]

    def getMass(self, isupdate: bool = False) -> float:
        if isupdate:
            self.mass = sum([mol.getMass() for mol in self.items])
        return self.mass

    def setMassElems(self) -> bool:
        success = False
        self.nitems = len(self.items)
        if self.nitems > 0:
            success = True
            mass = 0.0
            for molset in self.items:
                if not molset.setMassElems():
                    success = False
                    break
                mass += molset.getMass()
            if success:
                self.mass = mass
        self.isMassElems = success
        return success

    def getCharge(self, isupdate: bool = False) -> float:
        if isupdate:
            self.chrg = sum([mol.getCharge() for mol in self.items])
        return self.chrg

    @timing
    def refresh(self, **kwargs) -> None:
        if self.rcog is not None:
            del self.rcog
        if self.rvec is not None:
            del self.rvec
        self.mass = 0.0
        self.chrg = 0.0
        self.nitems = len(self.items)
        if self.nitems > 0:
            self.rcog = Vec3()
            self.rvec = Vec3()
            for molset in self.items:
                molset.refresh(**kwargs)
                self.mass += molset.getMass()
                self.chrg += molset.getCharge()
                self.rcog += molset.getRcog()
                self.rvec += molset.getRvec() * molset.getMass()
            self.rvec /= self.mass
            self.rcog /= float(self.nitems)

    @timing
    def refreshScaled(self, rscale: float = 1.0, **kwargs) -> None:
        if self.rcog is not None:
            del self.rcog
        if self.rvec is not None:
            del self.rvec
        self.mass = 0.0
        self.chrg = 0.0
        self.nitems = len(self.items)
        if self.nitems > 0:
            self.rcog = Vec3()
            self.rvec = Vec3()
            # ntot = 0
            for molset in self.items:
                for mol in molset.items:
                    for atom in mol.items:
                        # self.mass += atom.getMass()
                        # self.chrg += atom.getCharge()
                        atom.setRvec(atom.getRvec() * rscale)
                        # self.rvec += atom.getRvec() * atom.getMass()
                        # self.rcog += atom.getRvec()
                        # ntot += 1
                    # mol.refresh(**kwargs)
                molset.refresh(**kwargs)
                self.mass += molset.getMass()
                self.chrg += molset.getCharge()
                self.rcog += molset.getRcog()
                self.rvec += molset.getRvec() * molset.getMass()
            self.rvec /= self.mass
            self.rcog /= self.nitems  # float(ntot)

    @timing
    def updateRcom(self, **kwargs) -> None:
        if self.rvec is not None:
            del self.rvec
        self.nitems = len(self.items)
        if self.nitems > 0:
            self.rvec = Vec3()
            self.mass = 0.0
            for molset in self.items:
                molset.updateRcom(**kwargs)
                self.mass += molset.getMass()
                self.rvec += molset.getRcom() * molset.getMass()
            self.rvec /= self.mass

    @timing
    def updateRcomScaled(self, rscale: float = 1.0, **kwargs) -> None:
        if self.rvec is not None:
            del self.rvec
        self.nitems = len(self.items)
        if self.nitems > 0:
            self.rvec = Vec3()
            self.mass = 0.0
            for molset in self.items:
                for mol in molset.items:
                    for atom in mol.items:
                        self.mass += atom.getMass()
                        atom.setRvec(atom.getRvec() * rscale)
                        self.rvec += atom.getRvec() * atom.getMass()
                molset.updateRcom(**kwargs)
            self.rvec /= self.mass

    def getRcom(self, isupdate: bool = False, **kwargs) -> Vec3:
        if isupdate:
            self.updateRcom(**kwargs)
        return self.rvec

    def getRcomPBC(self, box=1.0) -> Vec3:
        return pbc(self.getRcom().copy(), box)

    def getRcomScaled(
        self, rscale: float = 1.0, isupdate: bool = False, **kwargs
    ) -> Vec3:
        if isupdate:
            self.updateRcomScaled(rscale, **kwargs)
        return self.rvec

    @timing
    def updateRcog(self, **kwargs) -> None:
        if self.rcog is not None:
            del self.rcog
        self.nitems = len(self.items)
        if self.nitems > 0:
            self.rcog = Vec3()
            for molset in self.items:
                molset.updateRcog(**kwargs)
                self.rcog += molset.getRcog()
            self.rcog /= float(self.nitems)

    @timing
    def updateRcogScaled(self, rscale: float = 1.0, **kwargs) -> None:
        if self.rcog is not None:
            del self.rcog
        self.nitems = len(self.items)
        if self.nitems > 0:
            self.rcog = Vec3()
            ntot = 0.0
            for molset in self.items:
                for mol in molset.items:
                    for atom in mol.items:
                        atom.setRvec(atom.getRvec() * rscale)
                        self.rcog += atom.getRvec()
                        ntot += 1
                molset.updateRcog(**kwargs)
            self.rcog /= float(ntot)

    def getRcog(self, isupdate: bool = False, **kwargs) -> Vec3:
        if isupdate:
            self.updateRcog(**kwargs)
        return self.rcog

    def getRcogPBC(self, box=1.0) -> Vec3:
        return pbc(self.getRcog().copy(), box)

    def getRcogScaled(
        self, rscale: float = 1.0, isupdate: bool = False, **kwargs
    ) -> Vec3:
        if isupdate:
            self.updateRcogScaled(rscale, **kwargs)
        return self.rcog

    @timing
    def updateRvecs(self, **kwargs) -> None: # center of mass
        if self.rvec is not None:
            del self.rvec
        if self.rcog is not None:
            del self.rcog
        self.mass = 0.0
        self.nitems = len(self.items)
        if self.nitems > 0:
            self.rvec = Vec3()
            self.rcog = Vec3()
            for molset in self.items:
                molset.updateRvecs(**kwargs)
                self.mass += molset.mass
                self.rcog += molset.rcog
                self.rvec += molset.rvec * molset.mass
            self.rvec /= self.mass
            self.rcog /= self.nitems

    def getRvecs(self, isupdate: bool = False, **kwargs) -> Vec3:
        if isupdate:
            self.updateRvecs(**kwargs)
        return self.rvec, self.rcog

    def getRvecsScaled(
        self, rscale: float = 1.0, isupdate: bool = False, **kwargs
    ) -> Vec3:
        if isupdate:
            self.refreshScaled(rscale, **kwargs)
        return self.rvec, self.rcog

    def moveBy(self, dvec: Vec3 = Vec3(), be_verbose: bool = False) -> None:
        if isinstance(dvec, Vec3):
            self.nitems = len(self.items)
            if self.nitems > 0:
                for molset in self.items:
                    molset.moveBy(dvec)
                self.rvec += dvec
                self.rcog += dvec
        elif be_verbose:
            logger.info(
                f"Input {dvec} does not qualify "
                f"as Vec3(float, float, float) - skipped (no change)!"
            )

    def getDims(self) -> tuple[list,list]:
        from numpy import where

        arvecs = array(
            [
                a.getRvec()
                for molset in self.items
                for mol in molset.items
                for a in mol.items
            ]
        ).T
        rvmins = [min(arvecs[0]), min(arvecs[1]), min(arvecs[2])]
        idsmin = (
            where(arvecs[0] == rvmins[0])[0][0],
            where(arvecs[1] == rvmins[1])[0][0],
            where(arvecs[2] == rvmins[2])[0][0],
        )
        rvmaxs = [max(arvecs[0]), max(arvecs[1]), max(arvecs[2])]
        idsmax = (where(arvecs[0]==rvmaxs[0])[0][0],
                  where(arvecs[1]==rvmaxs[1])[0][0],
                  where(arvecs[2]==rvmaxs[2])[0][0])
        logger.debug(f"min_xyz, min_ids = {rvmins} @ {idsmin}")
        logger.debug(f"max_xyz, max_ids = {rvmaxs} @ {idsmax}")
        return rvmins, rvmaxs

    @timing
    # def Densities(self, rorg=Vec3(), rmin=0.0, rmax=0.0, dbin=0.0, clist=None,
    def Densities(self,
                  rorg: Vec3 =Vec3(),
                  grid: Vec3 = Vec3(),
                  clist: list[str] = None,
                  dlist: list[str] = None,
                  bname: str = None,
                  is_cg: bool = False,
                  xy_area : float = 0.0,
                  be_verbose: bool = False
                  ) -> dict | None:

        import time
        import numpy as np

        def i_bin(rvec = Vec3(), dbin = 0.1, is_zden: bool = False):
            idx_bin = int(rvec[2]/dbin) if is_zden else int(np.linalg.norm(rvec)/dbin)
            return idx_bin

        if not dlist or len(dlist) < 1:
            logger.warning("no density type specified - skipping!")
            return None
        elif 'all' not in dlist:
            dlist.extend(['all'])
            # logger.debug(f"Added 'all' to dlist = {dlist}")

        rmin, rmax, dbin = grid

        n_zbin = 0
        is_zden = (rmin < -TINY)
        if is_zden:
            z_bin = dbin
            z_mid = rmax
            n_zbin = 2*int(z_mid / z_bin)
            z_max = float(n_zbin) * z_bin
            # logger.debug(f"z_bin * n_zbin = "
            #       f"{z_bin} * {n_zbin} = {z_bin * n_zbin} =?= {z_max} =?= {2.0*z_mid}")
            # exit(0)

        if rmax < TINY or rmax-rmin < TINY or dbin < TINY:
            logger.info("ill-defined range "
                        f"[{rmin}, {rmax}; {dbin}] - skipping calculation ...")
            return None
        nbins = round((rmax-rmin)/dbin)
        if nbins < 5:
            logger.info(f"too few points ({nbins} < 5) "
                        f"in [{rmin}, {rmax}; {dbin}] - skipping calculation ...")
            return None

        # elem_mass  = dict( D=2.014, H=1.0078, C=12.011, N=14.007, O=15.999, P=30.974, S=32.065 )
        # elems_csl = dict( D=6.674, H=-3.741, C=6.648, N=9.360, O=5.805, P=5.130, S=2.847 )
        # elems_sld = dict( D=2.823, H=-1.582, C=7.000, N=3.252, O=2.491, P=1.815, S=1.107 )

        cgw_ecsl = dict(W=-6.708, WF=-6.708, WCG=-6.708, O4H8=-6.708)
        cgw_mass = dict(W=72.0, WF=72.0, WCG=72.0, O4H8=72.0)

        elems_csl = Chemistry.ecsl
        elems_sld = Chemistry.esld
        elem_mass = { elem : Chemistry.etable[elem]["mau"]
                      for elem in Chemistry.etable.keys() }

        stime = time.time()
        atoms_mass = {}
        atoms_ecsl = {}
        sys_anames = []
        sys_mnames = []
        for mset in self.items:
            for mol in mset.items:
                if not is_cg:
                    if not mol.isElemCSL:
                        mol.setElemCSL()
                    if not mol.isMassElems:
                        mol.setMassElems()
                if mol.getName() not in sys_mnames:
                    sys_mnames.append(mol.getName())
                    for atm in mol.items:
                        sys_anames.append(atm.getName())
                        if is_cg:
                            if atm.getName() in cgw_mass.keys():
                                # aname = 'WCG'
                                # if atm.getName() == 'WF':
                                #     aname = 'WAF'
                                # atoms_mass.update({aname : cgw_mass[atm.getName()]})
                                # if aname in cgw_ecsl.keys():
                                #     atoms_ecsl.update({aname : cgw_ecsl[atm.getName()]})
                                atoms_mass.update({atm.getName() : cgw_mass[atm.getName()]})
                                if atm.getName() in cgw_ecsl.keys():
                                    atoms_ecsl.update({atm.getName() : cgw_ecsl[atm.getName()]})
                            else:
                                atoms_mass.update({atm.getName() : atm.getMass()})
                                atoms_ecsl.update({atm.getName() : atm.getElemCSL()})
                        else:
                            atoms_mass.update({atm.getElems()[0] : atm.getMass()})
                            atoms_ecsl.update({atm.getElems()[0] : atm.getElemCSL()})

        if (len(atoms_mass.values()) > 0 and
            all( [ abs(em) > 1.0+TINY for em in atoms_mass.values() ] )):
            elem_mass = atoms_mass
        else:
            logger.info(f"Cannot use ill-defined atom or bead masses: {NL_INDENT}"
                        f"{atoms_mass} - will reset ...")

        if (len(elem_mass.values()) < 1 or
            any( [ abs(em) < 1.0+TINY for em in elem_mass.values() ] )):
                raise ValueError(f"\n{self.__class__.__name__}.Densities(): "
                                 f"Cannot use ill-defined element masses: "
                                 f"\n{elem_mass} ...")
        else:
            logger.info(f"Will use element masses: {NL_INDENT}{elem_mass} ...")

        if (len(atoms_ecsl.values()) > 0 and
            all( [ abs(ecsl) > TINY for ecsl in atoms_ecsl.values() ] ) ):
            elems_csl = atoms_ecsl
        else:
            logger.info(f"Cannot use zero-defined atom or bead CSL: {NL_INDENT}"
                        f"{atoms_ecsl} - will reset ...")

        if 'nsld' in dlist:
            if any( [ abs(ecsl) < TINY for ecsl in elems_csl.values() ] ):
                raise ValueError(f"\n{self.__class__.__name__}.Densities(): "
                                 f"Cannot use zero element CSL: \n"
                                 f"{elems_csl} ...")
                # logger.warning("Skipping 'nsld' calculation ...")
            else:
                logger.info(f"Will use ElemCSL: {NL_INDENT}{elems_csl} ...")

        etime = time.time()
        logger.debug(f"Elapsed time before atom checks: {etime - stime}")
        stime = etime

        alist = list(set(dlist))
        flist = [name.casefold() for name in alist]
        #logger.debug(f"alist = {alist}")
        #logger.debug(f"flist = {flist}")
        if 'all'.casefold() in flist:
            alist.pop(flist.index('all'.casefold()))
            flist.pop(flist.index('all'.casefold()))
            if is_cg:
                logger.info("Will calculate density"
                            " profiles for ALL beads based on their elements ...")
            else:
                logger.info("Will calculate density"
                            " profiles for ALL atoms and heavy atom groups ...")
        # if 'atm'.casefold() in flist:
        #     alist.pop(flist.index('atm'.casefold()))
        #     flist.pop(flist.index('atm'.casefold()))
        #     logger.info("Will calculate ATM density contributions (i.e. atoms only) ...")
        if 'hist'.casefold() in flist:
            alist.pop(flist.index('hist'.casefold()))
            flist.pop(flist.index('hist'.casefold()))
            logger.info("Will output histogram(s) ...")
        if 'nden'.casefold() in flist:
            alist.pop(flist.index('nden'.casefold()))
            flist.pop(flist.index('nden'.casefold()))
            logger.info("Will output N-density(ies) ...")
        if 'mden'.casefold() in flist:
            alist.pop(flist.index('mden'.casefold()))
            flist.pop(flist.index('mden'.casefold()))
            logger.info("Will output M-density(ies) ...")
        if 'nsld'.casefold() in flist:
            # logger.debug(f"Index of {'nsld'.casefold()} = {flist.index('nsld'.casefold())}")
            alist.pop(flist.index('nsld'.casefold()))
            flist.pop(flist.index('nsld'.casefold()))
            logger.info("Will output SLD(s) ...")
        #logger.debug(f"alist' = {alist}")

        mol_not_found = [ mname for mname in clist if mname not in sys_mnames ]
        if len(mol_not_found) > 0:
            clist = sys_mnames
            # print(f"{self.__class__.__name__}.Densities(): "
            #       f"Unrecognised molecules "
            #       f"{mol_not_found} in requested molecule list {clist} / {sys_mnames}"
            #       f"- skipping calculation ...")
            # return None

        # AB: refactor in a better way! - For now just go for 'all'
        # if is_cg:
        #     atm_not_found = [ aname for aname in alist if aname not in sys_anames ]
        #     if len(atm_not_found) > 0:
        #         print(f"{self.__class__.__name__}.Densities(): Unrecognised atoms {atm_not_found} "
        #               f"in requested atom list {dlist} - skipping calculation ...")
        #         return None
        # elif 'all' not in dlist:
        #     atm_not_found = [ atom[0] for atom in alist if atom[0] not in elem_mass.keys() ]
        #     if len(atm_not_found) > 0:
        #         print(f"{self.__class__.__name__}.Densities(): Unsupported atoms {atm_not_found} "
        #               f"in requested atom list {dlist} - skipping calculation ...")
        #         return None

        dbin2 = dbin/2.0
        drange= np.arange(0, nbins, dtype=float) * dbin + dbin2 + rmin
        dbinV = 4.0 * Pi * drange**2 * dbin
        if is_zden:
            dbinV = xy_area * dbin
        dbinM = dbinV * 602.2
        logger.info(
            f"Will collect histograms in range [{drange[0]} ... {drange[-1]}] "
            f"with dbin = {dbin} -> {nbins} bins, centered @ {rorg} ..."
        )

        # stime = time.time()
        atms = [a for molset in self.items for mol in molset.items for a in mol.items if mol.name in clist]
        anms = [a.getName() for a in atms]
        axyz = [ (a.getRvec()-rorg).arr3() for a in atms]
        if is_zden:
            axyz += Vec3(0., 0., rmax).arr3()

        etime = time.time()
        logger.info(f"Elapsed time after atom search: {etime - stime}")
        stime = etime

        logger.info(f"Collecting histograms for {len(atms)} atoms on species {clist}")
              #f"{axyz[:10]}")

        halst = []
        hlist = []
        rxyz = np.array([0.0, 0.0, 0.0])
        aprev = ''
        gprev = ''
        gmass = 0.0
        aother = []
        nother = []
        if is_cg:
            for ia, aname in enumerate(anms):
                atmlist = [hatm[0][0] for hatm in halst]
                if aname in atmlist:
                    la = atmlist.index(aname)
                    ibin = i_bin(axyz[ia], dbin, is_zden)
                    if -1 < ibin < nbins:
                        halst[la][0][0]  = aname
                        halst[la][0][1] += 1
                        halst[la][1][ibin] += 1.0
                else:
                    logger.info(f"New histogram for atoms {aname} {ia} ...")
                    halst.append([[aname, 1], np.zeros(nbins)])
                    ibin = i_bin(axyz[ia], dbin, is_zden)
                    if -1 < ibin < nbins:
                        halst[-1][1][ibin] = 1.0
        else:
            for ia, aname in enumerate(anms):
                atmlist = [hatm[0][0] for hatm in halst]
                if aname[0] in atmlist:
                    la = atmlist.index(aname[0])
                    ibin = i_bin(axyz[ia], dbin, is_zden)
                    if -1 < ibin < nbins:
                        halst[la][0][0]  = aname[0]
                        halst[la][0][1] += 1
                        halst[la][1][ibin] += 1.0
                else:
                    halst.append([[aname[0], 1], np.zeros(nbins)])
                    ibin = i_bin(axyz[ia], dbin, is_zden)
                    if -1 < ibin < nbins:
                        halst[-1][1][ibin] = 1.0

                if aname[0] == 'H':  # add hydrogen to the COM group
                    if 'H' in aother:
                        nother[aother.index('H')] += 1
                    else:
                        aother.append('H')
                        nother.append(1)
                    mass = atms[ia].getMass()
                    gmass += mass
                    rxyz += axyz[ia]*mass
                elif len(aname)>1 and len(gprev)>0 and aname[1] == gprev[0]:
                    # found another atom in the previous COM group
                    if aname[0] in aother:
                       nother[aother.index(aname[0])] += 1
                    else:
                       aother.append(aname[0])
                       nother.append(1)
                    mass = atms[ia].getMass()
                    gmass += mass
                    rxyz += axyz[ia]*mass
                else:
                #elif aname != gprev: # increment the count in histogram
                    # initiate Rvec for new COM group
                    atmlist = [hatm[0][0] for hatm in hlist]
                    if len(gprev) > 0:
                        agrp = gprev[0]
                        if len(aother) > 0:
                            for io, ao in enumerate(aother):
                                agrp = agrp + ao + str(nother[io])
                        #print(f"Densities(): Counting for atom group {gprev} {ia}...")
                        if gprev in atmlist:
                            la = atmlist.index(gprev)
                            ibin = i_bin(rxyz/gmass, dbin, is_zden)
                            if -1 < ibin < nbins:
                                hlist[la][0][1] = agrp
                                hlist[la][1][ibin] += 1.0
                    if aname not in atmlist:
                        logger.info(f"Seeding a group around atom {aname} {ia}...")
                        hlist.append([[aname,aname], np.zeros(nbins)])
                    gmass = atms[ia].getMass()
                    rxyz  = axyz[ia]*gmass
                    gprev = aname
                    aother = []
                    nother = []

                if ia == len(anms)-1:  # increment the count in histogram
                    agrp = gprev[0]
                    if len(aother)>0:
                        for io, ao in enumerate(aother):
                            agrp = agrp + ao + str(nother[io])
                    atmlist = [hatm[0][0] for hatm in hlist]
                    if gprev in atmlist:
                        la = atmlist.index(gprev)
                        ibin = i_bin(rxyz/gmass, dbin, is_zden)
                        if -1 < ibin < nbins:
                            hlist[la][0][1] = agrp
                            hlist[la][1][ibin] += 1.0

        etime = time.time()
        logger.debug(f"Elapsed time after atom binning: {etime - stime}")
        stime = etime

        ntot  = 0
        gntot = []
        hgtot = []
        if not is_cg:
            for ih, hist in enumerate(hlist):
                if ih > 0:
                    if hist[0][1] in gntot:
                        hgtot[gntot.index(hist[0][1])] += hist[1]
                        if gntot.count(hist[0][1]) > 1:
                            logger.warning(
                                f"More than one histogram for group '{hist[0][1]}' "
                                f"with {gntot.count(hist[0][1])} counts!!!"
                            )
                    else:
                        gntot.append(hist[0][1])
                        hgtot.append(hist[1])
                else:
                    gntot.append(hist[0][1])
                    hgtot.append(hist[1])
                ntot += sum(hist[1])
                logger.info(
                    f"Histogram for group '{hist[0][1]}' @ atom {hist[0][0]} "
                    f"of {sum(hist[1])} counts:{NL_INDENT}"
                    f"{hist[1].T}"
                )
            etime = time.time()
            logger.debug(f"Elapsed time after groups binning: {etime - stime}")
            stime = etime

        is_all = 'ALL'  in dlist or 'All' in dlist or 'all' in dlist
        accumH = 'hist' in dlist
        accumN = 'nden' in dlist
        accumS = 'nsld' in dlist
        accumM = True
        printH = 'hist' in dlist and isinstance(bname, str)
        printN = 'nden' in dlist and isinstance(bname, str)
        printS = 'nsld' in dlist and isinstance(bname, str)
        printM = True and isinstance(bname, str) #'mden' in dlist or is_all

        checkA = [False]
        countA = False
        checkG = [False]
        countG = False
        if is_cg:
            checkA = [is_all]
            checkA.extend([ True for aname in dlist if aname in anms ])
            #checkA.extend([ True for aname in anms if aname in dlist])
            countA = checkA.count(True) > 1 or is_all
            #logger.debug(f"countA = {checkA} -> {countA} (for all = {is_all})")
        else:
            checkA = [is_all]
            checkA.extend([ True for aname in anms if aname[0] in dlist])
            countA = checkA.count(True) > 1 or is_all
            #logger.debug(f"countA = {checkA} -> {countA} (for all = {is_all})")
            checkG = [is_all]
            checkG.extend([ True for gname in gntot if gname in dlist])
            countG = checkG.count(True) > 1 or is_all
        #logger.debug(f"countG = {checkG} -> {countG} (for all = {is_all})")

        histALL = {}
        histSG = np.zeros(nbins)
        histMG = np.zeros(nbins)
        sz = 'z' if is_zden else ''

        if any(checkG):  # AB: Group contributions
            for ih, hist in enumerate(hgtot):
                gchsl = 0.0
                chsl  = 0.0
                gmass = 0.0
                mass  = 0.0
                edigs = ''
                elems = gntot[ih]
                for ic in range(len(elems)):
                    if elems[ic].isdigit():
                        edigs += elems[ic]
                        if ic == len(elems)-1:
                            gchsl += chsl*float(edigs)
                            gmass += mass*float(edigs)
                        elif not elems[ic+1].isdigit():
                            gchsl += chsl*float(edigs)
                            gmass += mass*float(edigs)
                            edigs = ''
                    elif elems[ic] in elem_mass.keys():
                        if ic == len(elems)-1:
                            gchsl += elems_csl[elems[ic]]
                            gmass += elem_mass[elems[ic]]
                        elif not elems[ic+1].isdigit():
                            gchsl += elems_csl[elems[ic]]
                            gmass += elem_mass[elems[ic]]
                        else:
                            chsl = elems_csl[elems[ic]]
                            mass = elem_mass[elems[ic]]
                logger.info(
                    f"Histogram for group '{gntot[ih]}' of {sum(hist)} counts, "
                    f"mass = {gmass}, CSL = {gchsl}:{NL_INDENT}"
                    f"{np.column_stack((drange, hist+0.0))}"
                )

                gname = gntot[ih]
                if is_all or gname in dlist:
                    if accumH: histALL.update({ sz+'hist_' + gntot[ih] : hist })
                    if printH:
                        np.savetxt(bname+'_'+sz+'hist_'+gntot[ih]+'.dat',
                                    np.column_stack((drange, hist+0.0)), fmt='%-0.3f %10.7f')
                    histN = hist / dbinV
                    if accumN: histALL.update({sz+'nden_' + gntot[ih] : histN})
                    if printN:
                        np.savetxt(bname + '_'+sz+'nden_' + gntot[ih] + '.dat',
                                    np.column_stack((drange, histN+0.0)), fmt='%-0.3f %10.7f')
                    histS   = histN * gchsl * 0.01
                    histSG += histS
                    if accumS: histALL.update({sz+'nsld_' + gntot[ih]: histS})
                    if printS:
                        np.savetxt(bname + '_'+sz+'nsld_' + gntot[ih] + '.dat',
                                    np.column_stack((drange, histS+0.0)), fmt='%-0.3f %10.7f')
                    histM   = hist * gmass / dbinM
                    histMG += histM
                    if accumM: histALL.update({sz+'mden_' + gntot[ih]: histM})
                    if printM:
                        np.savetxt(bname + '_'+sz+'mden_' + gntot[ih] + '.dat',
                                    np.column_stack((drange, histM+0.0)), fmt='%-0.3f %10.7f')
            logger.info(f"Overall number of groups = {ntot}")

        if countG:  # AB: Groups totals
            if accumS: histALL.update({sz+'nsld_GRP' : histSG})
            if printS:
                np.savetxt(bname + '_'+sz+'nsld_GRP.dat',
                          np.column_stack((drange, histSG+0.0)), fmt='%-0.3f %10.7f')
            if accumM: histALL.update({sz+'mden_GRP' : histMG})
            if printM:
                np.savetxt(bname + '_'+sz+'mden_GRP.dat',
                            np.column_stack((drange, histMG+0.0)), fmt='%-0.3f %10.7f')

        # print(f"Densities(): Store histograms for atoms {halst[0]} ({checkA}) ...")
        if any(checkA):  # AB: Atom contributions
            natot = 0
            histSA = np.zeros(nbins)
            histMA = np.zeros(nbins)
            for ih, hist in enumerate(halst):
                natot += sum(hist[1])
                logger.info(
                    f"Histogram for atoms '{hist[0]}' of {sum(hist[1])} "
                    f"counts:{NL_INDENT}{np.column_stack((drange, hist[1]+0.0))}"
                )
                aname = hist[0][0]
                if is_all or aname in dlist:
                    if accumH: histALL.update({ sz+'hist_' + hist[0][0] : hist })
                    if printH:
                        np.savetxt(bname+'_'+sz+'hist_'+hist[0][0]+'.dat',
                                    np.column_stack((drange, hist[1]+0.0)), fmt='%-0.3f %10.7f')

                    histN = hist[1] / dbinV
                    if accumN: histALL.update({ sz+'nden_' + hist[0][0] : histN })
                    if printN:
                        np.savetxt(bname+'_'+sz+'nden_' + hist[0][0] + '.dat',
                                    np.column_stack((drange, histN+0.0)), fmt='%-0.3f %10.7f')

                    histS   = histN * elems_csl[hist[0][0]] * 0.01
                    histSA += histS
                    if accumS: histALL.update({sz+'nsld_' + hist[0][0] : histS })
                    if printS:
                        np.savetxt(bname + '_'+sz+'nsld_' + hist[0][0] + '.dat',
                                np.column_stack((drange, histS+0.0)), fmt='%-0.3f %10.7f')

                    histM   = hist[1] * elem_mass[hist[0][0]] / dbinM
                    histMA += histM
                    if accumM: histALL.update({sz+'mden_' + hist[0][0] : histM})
                    if printM:
                        np.savetxt(bname + '_'+sz+'mden_' + hist[0][0] + '.dat',
                                    np.column_stack((drange, histM+0.0)), fmt='%-0.3f %10.7f')

            if countA:  # Atoms totals
                if accumS: histALL.update({sz+'nsld_ATM': histSA})
                if printS:
                    np.savetxt(bname + '_'+sz+'nsld_ATM.dat',
                                np.column_stack((drange, histSA+0.0)), fmt='%-0.3f %10.7f')
                if accumM: histALL.update({sz+'mden_ATM': histMA})
                if printM:
                    np.savetxt(bname + '_'+sz+'mden_ATM.dat',
                                np.column_stack((drange, histMA+0.0)), fmt='%-0.3f %10.7f')
            logger.info(
                f"Overall number of atoms in (sub-)system {self.name} = {natot}"
            )

        return histALL
    # end of Densities()

    @timing
    def radialDensities(self, rorg=Vec3(), rmin=0.0, rmax=0.0, dbin=0.0, clist=[],
                        dlist=[], bname = None, is_com=True, be_verbose=False) -> None:
        if rmax < TINY or rmax-rmin < TINY or dbin < TINY:
            logger.info(f"ill-defined range [{rmin}, {rmax}; {dbin}] - skipping "
                        f"calculation ...")
            return
        nbins = round((rmax-rmin)/dbin)
        if nbins < 5:
            logger.info(f"too few points ({nbins} < 5) in [{rmin}, {rmax}; {dbin}] - "
                        f"skipping calculation ...")
            return

        # elem_mass  = dict( D=2.014, H=1.0078, C=12.011, N=14.007, O=15.999, P=30.974, S=32.065 )
        # elems_csl = dict( D=6.674, H=-3.741, C=6.648, N=9.360, O=5.805, P=5.130, S=2.847 )
        # elems_sld = dict( D=2.823, H=-1.582, C=7.000, N=3.252, O=2.491, P=1.815, S=1.107 )

        elem_mass = { elem : Chemistry.etable[elem]["mau"] for elem in Chemistry.etable.keys() }
        elems_csl = Chemistry.ecsl
        elems_sld = Chemistry.esld

        alist = list(set(dlist))
        flist = [name.casefold() for name in alist]
        #logger.debug(f"alist = {alist}")
        #logger.debug(f"flist = {flist}")
        if 'all'.casefold() in flist:
            alist.pop(flist.index('all'.casefold()))
            flist.pop(flist.index('all'.casefold()))
            logger.info("Will calculate ALL density contributions ...")
        if 'hist'.casefold() in flist:
            alist.pop(flist.index('hist'.casefold()))
            flist.pop(flist.index('hist'.casefold()))
            logger.info("Will output histogram(s) ...")
        if 'nden'.casefold() in flist:
            alist.pop(flist.index('nden'.casefold()))
            flist.pop(flist.index('nden'.casefold()))
            logger.info("Will output N-density(ies) ...")
        if 'mden'.casefold() in flist:
            alist.pop(flist.index('mden'.casefold()))
            flist.pop(flist.index('mden'.casefold()))
            logger.info("Will output M-density(ies) ...")
        if 'nsld'.casefold() in flist:
            logger.info(
                f"Index of {'nsld'.casefold()} = {flist.index('nsld'.casefold())}"
            )
            alist.pop(flist.index('nsld'.casefold()))
            flist.pop(flist.index('nsld'.casefold()))
            logger.info("Will output SLD(s) ...")
        #logger.debug(f"alist' = {alist}")

        not_found = [ atom[0] for atom in alist if atom[0] not in elem_mass.keys() ]
        if len(not_found) > 0:
            logger.info(f"Unsupported atoms {not_found} in requested "
                        f"atom list {dlist} - skipping calculation ...")
            return

        import numpy as np
        dbin2 = dbin/2.0
        drange= np.arange(0, nbins, dtype=float) * dbin + dbin2 + rmin
        dbinV = 4.0 * Pi * drange**2 * dbin
        dbinM = dbinV * 602.2
        logger.info(f"Will collect histograms in range [{drange[0]} ... {drange[-1]}] "
                    f"with dbin = {dbin} -> {nbins} bins, centered @ {rorg} ...")
        atms = [a for molset in self.items for mol in molset.items for a in mol.items if mol.name in clist]
        anms = [a.getName() for a in atms]
        axyz = [ (a.getRvec()-rorg).arr3() for a in atms]

        logger.info(f"Collecting histograms for {len(atms)} atoms on species {clist}:")
              #f"{axyz[:10]}")

        halst = []
        hlist = []
        rxyz = np.array([0.0, 0.0, 0.0])
        aprev = ''
        gprev = ''
        gmass = 0.0
        aother = []
        nother = []
        for ia, aname in enumerate(anms):
            atmlist = [hatm[0][0] for hatm in halst]
            if aname[0] in atmlist:
                la = atmlist.index(aname[0])
                ibin = int(np.linalg.norm(axyz[ia])/dbin)
                #ibin = int(np.linalg.norm(axyz[ia]-rorg)/dbin)
                if -1 < ibin < nbins:
                    halst[la][0][0]  = aname[0]
                    halst[la][0][1] += 1
                    halst[la][1][ibin] += 1.0
            else:
                halst.append([[aname[0], 1], np.zeros(nbins)])
                ibin = int(np.linalg.norm(axyz[ia])/dbin)
                #ibin = int(np.linalg.norm(axyz[ia]-rorg)/dbin)
                if -1 < ibin < nbins:
                    halst[-1][1][ibin] = 1.0

            if aname[0] == 'H':  # add hydrogen to the COM group
                if 'H' in aother:
                    nother[aother.index('H')] += 1
                else:
                    aother.append('H')
                    nother.append(1)
                mass = atms[ia].getMass()
                gmass += mass
                rxyz += axyz[ia]*mass
            elif len(aname)>1 and len(gprev)>0 and aname[1] == gprev[0]:
                # found another atom in the previous COM group
                if aname[0] in aother:
                   nother[aother.index(aname[0])] += 1
                else:
                   aother.append(aname[0])
                   nother.append(1)
                mass = atms[ia].getMass()
                gmass += mass
                rxyz += axyz[ia]*mass
            else:
            #elif aname != gprev: # increment the count in histogram
                # initiate Rvec for new COM group
                atmlist = [hatm[0][0] for hatm in hlist]
                if len(gprev) > 0:
                    agrp = gprev[0]
                    if len(aother) > 0:
                        for io, ao in enumerate(aother):
                            agrp = agrp + ao + str(nother[io])
                    #print(f"Counting for atom group {gprev} {ia}...")
                    if gprev in atmlist:
                        la = atmlist.index(gprev)
                        ibin = int(np.linalg.norm(rxyz/gmass)/dbin)
                        #ibin = int(np.linalg.norm(rxyz/gmass-rorg)/dbin)
                        if -1 < ibin < nbins:
                            hlist[la][0][1] = agrp
                            hlist[la][1][ibin] += 1.0
                if aname not in atmlist:
                    logger.debug(f"Seeding a group around atom {aname} {ia}...")
                    hlist.append([[aname,aname], np.zeros(nbins)])
                gmass = atms[ia].getMass()
                rxyz  = axyz[ia]*gmass
                gprev = aname
                aother = []
                nother = []

            if ia == len(anms)-1:  # increment the count in histogram
                agrp = gprev[0]
                if len(aother)>0:
                    for io, ao in enumerate(aother):
                        agrp = agrp + ao + str(nother[io])
                atmlist = [hatm[0][0] for hatm in hlist]
                if gprev in atmlist:
                    la = atmlist.index(gprev)
                    ibin = int(np.linalg.norm(rxyz/gmass)/dbin)
                    #ibin = int(np.linalg.norm(rxyz/gmass-rorg)/dbin)
                    if -1 < ibin < nbins:
                        hlist[la][0][1] = agrp
                        hlist[la][1][ibin] += 1.0

        ntot  = 0
        gntot = []
        hgtot = []
        for ih, hist in enumerate(hlist):
            if ih > 0:
                if hist[0][1] in gntot:
                    hgtot[gntot.index(hist[0][1])] += hist[1]
                    if gntot.count(hist[0][1]) > 1:
                        logger.warning(
                            f"More than one histogram for group '{hist[0][1]}' "
                            f"with {gntot.count(hist[0][1])} counts!!!"
                        )
                else:
                    gntot.append(hist[0][1])
                    hgtot.append(hist[1])
            else:
                gntot.append(hist[0][1])
                hgtot.append(hist[1])
            ntot += sum(hist[1])
            logger.info(
                f"Histogram for group '{hist[0][1]}' @ atom {hist[0][0]} "
                f"of {sum(hist[1])} counts:{NL_INDENT}{hist[1].T}"
            )

        is_all = 'ALL'  in dlist or 'All' in dlist or 'all' in dlist
        printH = 'hist' in dlist
        printN = 'nden' in dlist
        printS = 'nsld' in dlist #or is_all
        printM = True #'mden' in dlist or is_all

        checkA = [is_all]
        checkA.extend([ True for aname in anms if aname[0] in dlist])
        countA = checkA.count(True) > 1 or is_all
        #logger.debug(f"countA = {checkA} -> {countA} (for all = {is_all})")
        checkG = [is_all]
        checkG.extend([ True for gname in gntot if gname in dlist])
        countG = checkG.count(True) > 1 or is_all
        #logger.debug(f"countG = {checkG} -> {countG} (for all = {is_all})")

        histALL = {}
        histSG = np.zeros(nbins)
        histMG = np.zeros(nbins)

        if any(checkG):  # AB: Group contributions
            for ih, hist in enumerate(hgtot):
                gchsl = 0.0
                chsl  = 0.0
                gmass = 0.0
                mass  = 0.0
                edigs = ''
                elems = gntot[ih]
                for ic in range(len(elems)):
                    if elems[ic].isdigit():
                        edigs += elems[ic]
                        if ic == len(elems)-1:
                            gchsl += chsl*float(edigs)
                            gmass += mass*float(edigs)
                        elif not elems[ic+1].isdigit():
                            gchsl += chsl*float(edigs)
                            gmass += mass*float(edigs)
                            edigs = ''
                    elif elems[ic] in elem_mass.keys():
                        if ic == len(elems)-1:
                            gchsl += elems_csl[elems[ic]]
                            gmass += elem_mass[elems[ic]]
                        elif not elems[ic+1].isdigit():
                            gchsl += elems_csl[elems[ic]]
                            gmass += elem_mass[elems[ic]]
                        else:
                            chsl = elems_csl[elems[ic]]
                            mass = elem_mass[elems[ic]]
                    logger.debug(f"Histogram for group '{gntot[ih]}' of {sum(hist)} "
                                 f"counts, mass = {gmass}, CSL = {gchsl}:{NL_INDENT}"
                                 f"{np.column_stack((drange, hist+0.0))}")

                if isinstance(bname, str):
                    gname = gntot[ih]
                    if is_all or gname in dlist:
                        if printH:
                            np.savetxt(bname+'_hist_'+gntot[ih]+'.dat',
                                        np.column_stack((drange, hist+0.0)), fmt='%-0.3f %10.7f')
                        histN = hist / dbinV
                        if printN:
                            np.savetxt(bname + '_nden_' + gntot[ih] + '.dat',
                                        np.column_stack((drange, histN+0.0)), fmt='%-0.3f %10.7f')
                        histS   = histN * gchsl * 0.01
                        histSG += histS
                        if printS:
                            np.savetxt(bname + '_nsld_' + gntot[ih] + '.dat',
                                        np.column_stack((drange, histS+0.0)), fmt='%-0.3f %10.7f')
                        histM   = hist * gmass / dbinM
                        histMG += histM
                        if printM:
                            np.savetxt(bname + '_mden_' + gntot[ih] + '.dat',
                                        np.column_stack((drange, histM+0.0)), fmt='%-0.3f %10.7f')
            logger.info(f"Overall number of groups = {ntot}")

        if isinstance(bname,str):
            if countG:  # AB: Groups totals
                if printS:
                    np.savetxt(bname + '_nsld_GRP.dat',
                              np.column_stack((drange, histSG+0.0)), fmt='%-0.3f %10.7f')
                if printM:
                    np.savetxt(bname + '_mden_GRP.dat',
                                np.column_stack((drange, histMG+0.0)), fmt='%-0.3f %10.7f')

            if any(checkA):  # AB: Atom contributions
                natot = 0
                histSA = np.zeros(nbins)
                histMA = np.zeros(nbins)
                for ih, hist in enumerate(halst):
                    natot += sum(hist[1])
                    logger.debug(
                        f"Histogram for atoms '{hist[0]}' of {sum(hist[1])} "
                        f"counts:{NL_INDENT}{np.column_stack((drange, hist[1]+0.0))}"
                    )
                    aname = hist[0][0]
                    if is_all or aname in dlist:
                        if printH:
                            np.savetxt(bname+'_hist_'+hist[0][0]+'.dat',
                                        np.column_stack((drange, hist[1]+0.0)), fmt='%-0.3f %10.7f')
                        histN = hist[1] / dbinV
                        if printN:
                            np.savetxt(bname+'_nden_' + hist[0][0] + '.dat',
                                        np.column_stack((drange, histN+0.0)), fmt='%-0.3f %10.7f')
                        histS   = histN * elems_csl[hist[0][0]] * 0.01
                        histSA += histS
                        if printS:
                            np.savetxt(bname + '_nsld_' + hist[0][0] + '.dat',
                                        np.column_stack((drange, histS+0.0)), fmt='%-0.3f %10.7f')
                        histM   = hist[1] * elem_mass[hist[0][0]] / dbinM
                        histMA += histM
                        if printM:
                            np.savetxt(bname + '_mden_' + hist[0][0] + '.dat',
                                        np.column_stack((drange, histM+0.0)), fmt='%-0.3f %10.7f')

                if countA:  # Atoms totals
                    if printS:
                        np.savetxt(bname + '_nsld_ATM.dat',
                                    np.column_stack((drange, histSA+0.0)), fmt='%-0.3f %10.7f')
                    if printM:
                        np.savetxt(bname + '_mden_ATM.dat',
                                    np.column_stack((drange, histMA+0.0)), fmt='%-0.3f %10.7f')
                logger.info(
                    f"Overall number of atoms in (sub-)system {self.name} = {natot}"
                )
    # end of radialDensities()


# end of class MolecularSystem
