"""
.. module:: coarse_grainer
   :platform: Linux - tested, Windows (WSL Ubuntu) - NOT TESTED
   :synopsis: Class for coarse-graining

.. moduleauthor:: Saul Beck <saul.beck[@]stfc.ac.uk>

The module contains class CoarseGrainer
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
#  Contrib: MSci Saul Beck (c) 2024              #
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

import sys
import os
import time
from itertools import combinations
import logging

# import json
# from pathlib import Path
import numpy as np

from shapes.basics.defaults import NL_INDENT
from shapes.basics.functions import timing, sec2hms, pbc  # , pbc_rect, pbc_cube
from shapes.basics.mendeleyev import Chemistry
from shapes.stage.protovector import Vec3
from shapes.stage.protoatom import Atom
from shapes.stage.protomolecule import Molecule
from shapes.stage.protomoleculeset import MoleculeSet
from shapes.stage.protomolecularsystem import MolecularSystem
from shapes.ioports.iogro import groFile
from shapes.ioports.iopdb import pdbFile
from shapes.cgmap.molecule_mapper import MoleculeMapper
from shapes.cgmap.martini_converter import MartiniMapConverter
from shapes.ioports.iotop import ITPTopology
from shapes.ioports.iotraj import DCDTrajectory
from shapes.ioports.ioframe import Frame, CellParameters  # , FrameMolSys
# from shapes.cgmap.watercg import water_cg_molset  # water_beads

logger = logging.getLogger("__main__")


class CoarseGrainer(object):
    """
    A class to perform coarse-graining of molecular (sub-) systems.

    Parameters
    ----------
    fpath_map : str
        Path to either .json or .map file containing AA -> CG bead mapping specs.
    fpath_itp : str
        Optional: Path to .itp file containing bond and angle specs to supplement .map file.
    """

    def __init__(self, fpath_map: str, fpath_itp: str = None) -> None:
        if len(fpath_map) < 5:
            sys.exit(
                f"CoarseGrainer:: ERROR: Too short file name: '{fpath_map}' - FULL STOP!"
            )

        fpdir = os.path.dirname(fpath_map)
        fname, fext = os.path.splitext(os.path.basename(fpath_map))
        # fcgmap = os.path.join(fpdir, fname + ".json")
        fcgmap = os.path.join(fpdir, fname + "_cgmap.json")
        # print(f"New cgmap name: {fcgmap}")

        if fpath_map.endswith(".map") and not fpath_itp:
            with open(fpath_map, "r") as f:
                map_content = f.read()
            converter = MartiniMapConverter()
            converter.parse_map_str(map_content)
            cgmap_dict = converter.to_dict()
            self.mapper = MoleculeMapper(cgmap_dict)
            self.mapper.save_to_file(fcgmap)

        elif fpath_map.endswith(".map") and fpath_itp:
            if not fpath_itp.endswith(".itp"):
                sys.exit(
                    f"CoarseGrainer:: ERROR: Unsupported ITP file extension: '{fpath_itp}' - FULL STOP!"
                )

            with open(fpath_map, "r") as f:
                map_content = f.read()
            converter = MartiniMapConverter()
            converter.parse_map_str(map_content)
            itp_topology = ITPTopology.from_file(fpath_itp)
            converter.update_from_itp(itp_topology)
            cgmap_dict = converter.to_dict()
            self.mapper = MoleculeMapper(cgmap_dict)
            self.mapper.save_to_file(fcgmap)

        elif fpath_map.endswith(".json"):
            self.mapper = MoleculeMapper.from_file(fpath_map)

        else:
            sys.exit(
                f"CoarseGrainer:: ERROR: Unsupported mapping file format: '{fpath_map}' - FULL STOP!"
            )

    # end of CoarseGrainer.__init__()

    def coarse_grain_trajectory(
        self,
        fpath_ref: str,
        fpath_trj: str,
        fpath_out: str,
        water_pars: dict = None,
    ) -> None:
        """
        Coarse grain atomistic trajectory.

        Parameters
        ----------
        fpath_ref : str
            File path to the reference file (only .gro or .pdb formats)
        fpath_trj : str
            File path to the trajectory file (only .dcd format supported)
        fpath_out : str
            File path where the coarse-grained trajectory will be saved

        Notes
        -----
        Processes each frame in the trajectory:
        - Reads in the reference configuration (fpath_ref) and frames from the trajectory (fpath_trj)
        - Maps atoms onto coarse-grained beads based the AA-CG map file (read in beforehand)
        - Writes coarse-grained configuration and frames to trajectory file (fpath_out)
        - Accounts for re-scaling: nm <-> Angstrom (.gro <-> .pdb)
        """
        # ref_is_pdb = fpath_ref.lower().endswith(".pdb")
        ref_is_gro = fpath_ref.lower().endswith(".gro")
        ref_cg_ext = ".gro" if ref_is_gro else ".pdb"
        ref_cg_out = os.path.splitext(fpath_out)[0] + ref_cg_ext
        res_names = list(self.mapper.get_all_residues())

        wname = ""
        if water_pars:
            wname = water_pars["name"][0]  # .get('name', 'TIP3')
            if wname:
                res_names.append(wname)
                if water_pars["dmax"] < 1.0:
                    # convert to Angstroms since CG-ing is done on original DCD coordinates
                    water_pars["dmax"] *= 10.0

        logger.info(f"Reading residues {res_names} from file {fpath_ref}...")

        frames = []

        if fpath_trj.endswith(".dcd"):
            # ref_out = os.path.splitext(fpath_out)[0] + '_ref' + ref_cg_ext
            # self.coarse_grain_structure(fpath_ref, ref_out)

            # dcd_inp = DCDTrajectory(fpath=fpath_trj, fpath_ref=fpath_ref, mode="r")
            dcd_inp = DCDTrajectory(
                fpath=fpath_trj,
                fpath_ref=fpath_ref,
                mode="r",
                res_names=res_names,
                tryMassElems=True,
            )

            for iframe, (cell_params, coordinates) in enumerate(dcd_inp):
                logger.info(
                    f"Processing frame {iframe} for {len(res_names)} "
                    f"residues {res_names} ..."
                )

                # AB: is_MolPBC=True puts whole molecules back into the primary cell
                molsys = dcd_inp.update_molsys(dcd_inp.frames[iframe], is_MolPBC=True)

                # AB: this is for reference to see how FrameMolSys can be used
                # molsys = FrameMolSys(frame=dcd_inp.frames[iframe],
                #                      shift_flag=dcd_inp.molsys_shift_flag,
                #                      rnames=res_names,
                #                      molsets=dcd_inp.molsys.items
                #                      ).update_molsys(is_MolPBC=True,
                #                                      tryMassElems=True)

                box_out = [cell_params.a, cell_params.b, cell_params.c]
                cg_molsys = self.create_cg_system(
                    molsets=molsys.items,
                    box=Vec3(*box_out[:3]),
                    wpars=water_pars,
                )

                if iframe == 0:
                    # Write initial structure
                    out_is_gro = ref_cg_out.endswith(".gro")
                    if out_is_gro:
                        # self._write_output(cg_molsys, box_out, ref_cg_out, 0.1)
                        self._write_output(cg_molsys, cell_params, ref_cg_out, 0.1)
                    else:
                        # self._write_output(cg_molsys, box_out, ref_cg_out, 1.0)
                        self._write_output(cg_molsys, cell_params, ref_cg_out, 1.0)

                frame = self._create_frame(cg_molsys, cell_params)
                frames.append(frame)

            dcd_inp.close()

            if not frames:
                raise RuntimeError("No frames processed - check input trajectory file")

            dcd_out = DCDTrajectory(fpath=fpath_out, mode="w")
            dcd_out.write(frames)
            dcd_out.close()

        else:
            raise ValueError("Unsupported trajectory format. Use .dcd files.")

    # end of CoarseGrainer.coarse_grain_trajectory()

    def coarse_grain_structure(
        self,
        fpath_inp: str = "",
        fpath_out: str = "",
        water_pars: dict = None,
    ):
        """
        Coarse grain a single structure file.

        Parameters
        ----------
        fpath_inp : str
            Path to input structure (.gro or .pdb format)
        fpath_out : str
            Path where coarse-grained structure will be saved

        Notes
        -----
        - Reads atomic structure
        - Maps atoms to coarse-grained beads based on mapping rules
        - Writes coarse-grained structure file
        - Supports .gro and .pdb formats for both input and output
        - Accounts for scaleing
        """

        ref_is_gro = False
        lscale_inp = 1.0
        if fpath_inp:
            ref_is_gro = fpath_inp.lower().endswith(".gro")
            if ref_is_gro:
                lscale_inp = 10.0
                reader = groFile(fpath_inp)
            elif fpath_inp.endswith(".pdb"):
                reader = pdbFile(fpath_inp)
            else:
                raise ValueError(
                    f"Unsupported structure file: {fpath_inp} - use either .gro or .pdb file!"
                )
        else:
            raise ValueError(
                "Empty name of structure file - use either .gro or .pdb file!"
            )

        remarks = []
        molsets = []
        readbox = []
        res_names = list(self.mapper.get_all_residues())

        wname = ""
        if water_pars:
            wname = water_pars["name"][0]  # .get('name', 'TIP3')
            if wname:
                res_names.append(wname)
                if water_pars["dmax"] < 1.0:
                    # convert to Angstroms since CG-ing is done on original DCD coordinates
                    water_pars["dmax"] *= 10.0

        logger.info(f"Reading residues {res_names} from file {fpath_inp}...")

        read_data = {
            "header": remarks,
            "simcell": CellParameters(),  # self.cell,
            "molsinp": molsets,
            "resnames": res_names,
            "resids": (0,),
            "lscale": lscale_inp,
        }
        success = reader.readInMols(read_data) if reader else False

        # success = reader.readInMols(
        #     remarks, molsets, readbox,
        #     resnames=res_names, # list(self.mapper.get_all_residues()),
        #     resids=(0,),
        #     lenscale=lscale_inp,
        # ) if reader else False

        if not success:
            raise RuntimeError(f"Failed to read structure file: {fpath_inp}")

        # readbox = list(read_data["simcell"].dims())
        # readbox.extend(list(read_data["simcell"].angles()))

        vbox = read_data["simcell"].dims_vec()
        logger.info(f"Read in vbox = {vbox} based on"
              f"{read_data} ...")

        # vbox = Vec3(*readbox[:3])
        molsys = MolecularSystem(molsets=molsets)
        logger.info(f"Refreshing Molsys with Mol.COM.PBC ...")
        molsys.refresh(box=vbox, isMolPBC=True)
        if ref_is_gro:
            box_half = vbox * 0.5  # Vec3(*box[:3]) * 0.5
            molsys.moveBy(-box_half)

        cg_molsys = self.create_cg_system(
            molsets=molsys.items,
            box=vbox,  # Vec3(*box[:3]),
            wpars=water_pars,
        )

        if fpath_out:
            out_is_gro = fpath_out.lower().endswith(".gro")
            lscale_out = 0.1 if out_is_gro else 1.0
            # if ref_is_gro:
            #     lscale_out = 0.1 if out_is_gro else 1.0
            # else:
            #     lscale_out = 0.1 if out_is_gro else 1.0
            # self._write_output(cg_molsys, readbox, fpath_out, lscale_out)
            self._write_output(cg_molsys, read_data["simcell"], fpath_out, lscale_out)

        return cg_molsys

    # end of CoarseGrainer.coarse_grain_structure()

    @timing
    def create_cg_system(
        self,
        molsets: list = None,
        box: Vec3 = None,
        wpars: dict = None,
    ) -> MolecularSystem:
        """
        Create a CG molecular system from AA molecule sets.

        Parameters
        ----------
        molsets : list[MoleculeSet]
            List of AA molecule sets to be coarse-grained
        box : Vec3
            The box

        Returns
        -------
        MolecularSystem
            The CG MolecularSystem

        Notes
        -----
        Internal function that:
        - Creates new coarse-grained molecule sets
        - Maps each molecule to its CG representation
        """

        # get index of water species if it is present in molsets
        # it is used below
        windx = -1
        wname = ""
        if wpars:
            wname = wpars["name"][0]
            if wname:
                mol_names = [mols[0].name for mols in molsets]
                if wname in mol_names:
                    windx = mol_names.index(wname)
                else:
                    raise ValueError(
                        f"Resname for water '{wname}' not found amongst input names!"
                    )

        box = Vec3(*box)

        cg_molsets = []
        for molset in molsets:
            if molset[0].name == wname:
                continue
            mcount = 0
            ncount = 0
            cg_molset = MoleculeSet(0, name=f"{molset.name}_CG", type="output")
            for molecule in molset:
                if self.mapper.is_valid_residue(molecule.name):
                    cg_mol = self._coarse_grain_molecule(molecule, molecule.name)
                    if cg_mol.isMassElems and mcount < 1:
                        mcount += 1
                        logger.info(
                            f"All bead masses in {cg_mol.name} "
                            f"were set based on elements..."
                        )
                    if cg_mol.isElemCSL and ncount < 1:
                        ncount += 1
                        logger.info(
                            f"All bead CSL in {cg_mol.name} "
                            f"were set based on elements..."
                        )
                        isElemALL = all([ atm.elem is not None for atm in cg_mol.items])
                        if not isElemALL:
                            raise RuntimeError(
                                f"create_cg_system(): "
                                f"inconsistent isElemALL state!"
                                f"({self.isElemCSL} -> {isElemALL})!"
                            )
                        isElemCSL = all([atm.isElemCSL for atm in cg_mol.items])
                        if not isElemCSL:
                            raise RuntimeError(
                                f"create_cg_system(): "
                                f"inconsistent isElemCSL state!"
                                f"({self.isElemCSL} -> {isElemCSL})!"
                            )

                    cg_mol.refresh(box=box, isMolPBC=True)
                    cg_molset.addItem(cg_mol)
            if len(cg_molset) > 0:
                cg_molsets.append(cg_molset)

        # outFile = groFile(fname="DOPC_CG_system.gro", fmode='w')
        # outFile.writeOutMols(rem=f"CG system {cg_molsets[0].items[0].name} {cg_molsets[0].nitems}",
        #                      gbox=list(box),
        #                      mols=cg_molsets, lenscale=0.1)

        # fpath_out = "DOPC_CG_system.gro"
        # if ref_is_gro:
        #     lscale_out = 10.0 if not out_is_gro else 1.0
        # else:
        #     lscale_out = 0.1 if out_is_gro else 1.0
        # self._write_output(cg_molsets, box, fpath_out, lscale_out)

        if wname and windx > -1:
            # Create CG water molset to write the reference structure
            # wbeads_molset = MoleculeSet(name="Water_CG", type="WCG")
            wbeads_molset = self.water_cg_molset(
                wmolset=molsets[windx],
                wpars=wpars,
                box=box,
            )

            # Append water molset to CG system
            cg_molsets.append(wbeads_molset)

        return MolecularSystem(
            sname="CG_System", stype="output", molsets=cg_molsets, vbox=box
        )

    # end of CoarseGrainer.create_cg_system()

    def _update_coordinates(
        self, molsets: list = None, coordinates: np.ndarray = None
    ) -> None:
        atom_idx = 0
        for molset in molsets:
            for mol in molset:
                for atom in mol:
                    atom.setRvec(Vec3(*coordinates[atom_idx]))
                    atom_idx += 1
                mol.getRvecs(isupdate=True)

    # end of CoarseGrainer._update_coordinates()

    @timing
    def _create_frame(
        self, cg_molsys: MolecularSystem, cell_params: CellParameters
    ) -> Frame:
        box = Vec3(*cell_params.dims())
        cg_coords = []
        for molset in cg_molsys.items:
            for mol in molset:
                for atom in mol:
                    atom.setRvec(atom.getRvecPBC(Vec3(*box)))
                    coords = atom.getRvec().arr3()
                    cg_coords.append(coords)

        cg_coords_array = np.array(cg_coords)
        if cg_coords_array.shape[1] != 3:
            raise ValueError(
                f"Expected Nx3 array, but got shape {cg_coords_array.shape}"
            )

        return Frame.from_coordinates(cell_params, cg_coords_array, frame_type=".dcd")

    # end of CoarseGrainer._create_frame()

    def _write_output(
        self,
        cg_molsys: MolecularSystem,
        cell: CellParameters,
        fpath_out: str,
        lscale_out: float,
    ) -> None:
        output_data = {
            "header": f"Coarse Grained {cg_molsys.name} System",
            "molsout": cg_molsys.items,
            "simcell": cell,
            "lscale": lscale_out,
        }

        if fpath_out.endswith(".gro"):
            writer = groFile(fpath_out, fmode="w")
        elif fpath_out.endswith(".pdb"):
            writer = pdbFile(fpath_out, fmode="w")
        else:
            raise ValueError("Unsupported output file format. Use .gro or .pdb files.")

        # remarks = f"Coarse Grained {cg_molsys.name} System"

        success = writer.writeOutMols(output_data)
        # success = writer.writeOutMols(
        #     remarks, box_out, cg_molsys.items, lenscale=lscale_out
        # )
        if not success:
            raise RuntimeError(f"Failed to write output file: {fpath_out}")
        writer.close()

    # end of _write_output()

    def set_cgmol_elems(self, cg_mol: Molecule) -> None:
        """
        The method attempts to assign elements and their respective properties,
        masses and CSL) to the set of atoms constituting a CG bead according to
        the CG map contained in `self.mapper` (instance of `class MoleculeMapper`).

        Parameters
        ----------
        cg_mol: Molecule
            A molecule in CG representation (coarse-grained beforehand)

        **NOTE**: This method only needs to be called for molecules in a CG system
        that has been read from a previously coarse-grained configuration or trajectory frame.

        """
        beads = self.mapper.get_beads_for_residue(cg_mol.name)
        bnames, batoms, bwghts = zip(
            *[(bead["name"], bead["atoms"], bead["weights"]) for bead in beads]
        )
        nset = 0
        for bead in cg_mol.items:
            if bead.name not in bnames:
                raise ValueError(f"Bead '{bead.name}' not found in CG map: {bnames}!")
            ib = bnames.index(bead.name)
            if bead.setElems(batoms[ib]) and bead.setElemCSL(bwghts[ib]):
                bmass = 0.0
                for iw, elem in enumerate(bead.getElems()):
                    bmass += Chemistry.etable[elem]["mau"] * bwghts[ib][iw]
                bead.setMass(bmass)
                bead.isMassElems = True
                nset += 1
        cg_mol.isMassElem = nset == cg_mol.nitems

    def _coarse_grain_molecule(self, molecule: Molecule, residue_name: str) -> Molecule:
        """
        The method assigns beads to groups of atoms (if possible, based on their
        respective elements' masses and CSL) according to the CG map contained in
        `self.mapper` (instance of `class MoleculeMapper`).

        Parameters
        ----------
        molecule: Molecule
            A molecule in atomistic (AA) representation

        Returns
        -------
        Molecule
            The corresponding CG molecule

        **NOTE** This is a core method which performs coarse-graining molecule-wise.

        """
        # AB: attempt to assign elements' masses to the atoms in `molecule`
        canSetElemCSL = molecule.setMassElems()
        # AB: all molecules COM's & COG's should have been updated beforehand
        molecule.updateRvecs()  # isupdate=True)
        # logger.debug(f"Coarse-graining {molecule}")

        cg_mol = Molecule(mindx=molecule.indx)
        cg_mol.name = residue_name

        beads = self.mapper.get_beads_for_residue(residue_name)

        n_mass_itp = 0
        n_elem_csl = 0
        for i, bead in enumerate(beads):
            bead_name = bead["name"]
            bead_atoms = bead["atoms"]
            bead_weights = bead["weights"]
            bead_charge = bead["charge"]

            # AB: what if the calculated bead mass differs from the one set here?
            bead_mass = bead["mass"]
            is_mass_itp = bead_mass > 1.0
            if is_mass_itp:
                n_mass_itp += 1
            else:
                bead_mass = 1.0
            # AB: if bead["mass"] <= 0.0 (from .itp)
            # AB: try recalculating bead_mass with atom masses from Chemistry
            # AB: if that fails, raise Exception!

            # logger.debug(f"Processing bead {bead_name} # {i+1} :")
            # logger.debug("----------------------------------------")
            # logger.debug("Atom Index  Name | Type | Elem | Mass | Weight | Position")
            # logger.debug("Atom contributions:")
            # logger.debug("Atom Name | Weight | Position | Mass | Weighted Position")

            bead_type = bead["type"]
            if len(bead_type) < 1:
                bead_type = "CG_bead"
                # is_elem, elem = Chemistry.isElement(bead_name)
                # if is_elem:
                elem = Chemistry.getElement(bead_name)
                if elem:
                    bead_type = elem + "_CG"

            bead_mol = Molecule(i, aname=bead_name, atype=bead_type)

            is_bead_elems = True
            ia = 0
            for atom in molecule:
                if atom.name in bead_atoms:
                    ia += 1
                    # need to get a copy of the original atom as we are going to reweigh it!
                    batom = atom.copy()

                    if not is_mass_itp:
                        is_bead_elems = atom.isMassElem and is_bead_elems
                        if is_bead_elems:
                            belem = "None"
                            elem = Chemistry.getElement(batom.name)
                            if elem:
                                belem = elem
                            atom_index = bead_atoms.index(atom.name)
                            # atom's weight within the bead according to CG map
                            weight = bead_weights[atom_index]
                            batom.setMass(atom.getMass() * weight)
                            batom.isMassElem = atom.isMassElem
                        else:
                            raise ValueError("Bead mass could not be set!")
                    #
                    # need to set atom's mass if it has not been set beforehand (above)
                    # if atom.isMassElem:
                    #     batom.setMass(atom.getMass()*weight)
                    #     # logger.info(f"SUCCESS: set element mass for atom '{batom.name}' ...")
                    # else:
                    #     batom.setMassElem()
                    #     batom.setMass(batom.getMass() * weight)
                    #     if not batom.isMassElem:
                    #         logger.warning(f"Failed to set element mass for atom '{batom.name}' ...")
                    #
                    # reweigh bead's atom according to CG mapping
                    # this only works correctly if atoms' masses have been set beforehand (above)
                    #
                    # batom.setMass(atom.getMass() * weight)
                    bead_mol.addItem(batom)
                    #
                    # add new reweighed atom to the bead (sub-molecule)
                    # atom_props = '{:>11}{:>6}{:>7}{:>5}{:>10.5}{:>7.3}'.format(ia, \
                    #             batom.name, batom.type, belem, \
                    #             atom.mass, weight) + \
                    #             ''.join('{:>10.5f}{:>10.5f}{:>10.5f}'.format(*atom.getRvec()))
                    # print(atom_props)
                    # print(
                    #    f"Added {batom} to CG bead {bead_name} # {i} weighed by {weight} "
                    #    f"(isMassElem = {batom.isMassElem})"
                    # )

            # Molecule.getRvec(isupdate=True) updates Molecule's mass
            # while updating its COM and COG
            bead_mol.refresh()
            bead_rvec = bead_mol.getRvec()  # isupdate=True)
            bead_mass = bead_mol.getMass()
            # bead_charge = bead_mol.getCharge() # the charge comes from mapping!
            cg_atom = Atom(bead_name, bead_type, bead_mass, bead_charge, i, bead_rvec)

            # AB: set elements and CSL for the bead
            if canSetElemCSL and cg_atom.setElems(bead["atoms"]):
                cg_atom.setElemCSL(bead["weights"])
                if not cg_atom.isElemCSL:
                    logger.warning(
                        f"Failed to set ElemCSL {bead_name} : "
                        f"{cg_atom.getElemCSL()} ..."
                    )
                else:
                    n_elem_csl += 1
                #     bead_csl = [ Chemistry.ecsl[Chemistry.getElement(atm)] for atm in bead['atoms'] ]
                #     logger.debug(f"Setting ElemCSL {bead_name} :{NL_INDENT}"
                #           f"{cg_atom.getElemCSL()} :{NL_INDENT}"
                #           f"{bead['atoms']} {NL_INDENT}"
                #           f"{bead_csl} -> {sum(bead_csl)}{NL_INDENT}"
                #           f"{bead['weights']} -> {sum(bead['weights'])}")
            else:
                logger.warning(
                    f"Failed to set atom Elems {bead_name} : {bead_atoms} ..."
                )
            cg_mol.addItem(cg_atom)
            # logger.debug(f"Added CG {cg_atom}")
            # logger.debug(f"Added CG {cg_atom} with calculated mass {bead_mass}")

        if 0 < n_mass_itp < len(beads):
            raise Exception(
                f"Bead masses are inconsistent: "
                f"only {n_mass_itp} / {len(beads)} "
                f"were set in .itp file)"
            )
        elif n_mass_itp == 0:
            cg_mol.isMassElems = molecule.isMassElems
            # print(f"All bead masses in {cg_mol.name} "
            #       f"were set based on elements...")

        if n_elem_csl == len(beads):
            cg_mol.isElemCSL = True
            # print(f"All bead CSL in {cg_mol.name} "
            #       f"were set based on elements...")
        elif 0 < n_elem_csl < len(beads):
            raise Exception(
                f"Bead CSL are inconsistent: "
                f"only {n_elem_csl} / {len(beads)} "
                f"were set based on elements)"
            )

        # cg_mol.getRvecs(isupdate=True)
        # logger.debug(f"Created CG {cg_mol}")
        return cg_mol

    # end of coarse_grain_molecule()

    def water_cg_molset(
        self, wmolset: MoleculeSet = None, wpars: dict = None, box: list | Vec3 = None
    ) -> MoleculeSet:  # (list[float], list[Vec3]):
        def unique_groups(all_groups, n_points):
            """
            Given a list of all valid molecule groups (indices),
            select a subset where no molecule repeats.
            Greedy approach: linear in number of groups.

            Parameters
            ----------
            all_groups: array-like[array-like[int]]
                Valid groups of molecule indices obtained by neighbour-list search
            n_points: int
                Total number of points (molecule COM's)

            Returns
            -------
            selected_groups: array-like[array-like]
                List of unique non-overlapping groups
            """
            selected_groups = []
            used = [False] * n_points
            for group in all_groups:
                if all(not used[i] for i in group):
                    selected_groups.append(group)
                    for i in group:
                        used[i] = True
            return selected_groups

        # end of unique_groups()

        def compact_unique_groups(all_groups, points, box, nmax=3, mode="avr"):
            """
            Collect unique molecule groups, sorted out by their compactness,
            where the selection criterion is based on either average (default)
            or maximum distance between the molecules in a group.

            Parameters
            ----------
            all_groups: array-like[array-like[int]]
                Valid groups of molecule indices obtained by neighbour-list search
            points: array-like[array-like[float]]
                The total list of points (N x 3-vectors)
            mode: str
                'avr' or 'max' - scoring mode for group selection

            Returns
            -------
            selected_groups: array-like[array-like[int]]
                List of unique groups overlapping by one member at most
            """

            def score_group(points, group, box, mode="avr"):
                """
                Score a molecule group by average or maximum pairwise distance.
                """
                dists = [
                    np.linalg.norm(pbc(points[i] - points[j], box))
                    for i, j in combinations(group, 2)
                ]
                return sum(dists) / len(dists) if mode == "avr" else max(dists)
                # return max(dists) if mode == 'max' else sum(dists) / len(dists)

            scored_groups = [
                (group, score_group(points, group, box, mode)) for group in all_groups
            ]
            scored_groups.sort(key=lambda x: x[1])  # sort by score (lower = tighter)

            selected_groups = []
            selected_scores = []
            used = [False] * len(points)
            for group, score in scored_groups:
                num_used = [used[i] for i in group].count(True)
                # AB: do not allow overlaps by shared neighbours
                # if all(not used[i] for i in group):
                # AB: allow for 'overlaps' by less than nmax shared neighbours
                if num_used < nmax:
                    selected_groups.append(group)
                    selected_scores.append(score)
                    for i in group:
                        used[i] = True

            return selected_groups, selected_scores

        # end of compact_unique_groups()

        if wmolset is None:
            raise ValueError("Invalid input for water MoleculeSet: {wmolset}")
        if wpars is None:
            raise ValueError("Invalid input for water parameters: {wpars}")

        wresname = wpars["name"][1]
        watmname = wpars["name"][-1]
        wnmap = wpars["nmap"]
        nmap1 = wpars["nmap"] - 1
        wdmax = wpars["dmax"]
        nbmax = wpars["nmax"]

        box = Vec3(*box)

        # AB: restore whole water molecules and put their COMs back into the cell
        wmolset.refresh(box=box, isMolPBC=True)

        logger.info(
            f"water_beads_coords(): Searching for neighbours "
            f"in molset {wresname}: wdmax = {wdmax}, nbmax = {nbmax} ..."
        )

        # AB: collect neighbour-list for each water molecule (within cutoff = wdmax)
        # mnbrs = wmolset.findNeighbours(box, dmax=wdmax, nmax=50)  # ultimate test for debugging!
        # mnbrs = wmolset.findNeighboursSSD(box, dmax=wdmax, nmax=50)
        mnbrs = wmolset.findNeighboursKDT(box, dmax=wdmax, nmax=nbmax)
        nnbrs = [len(nbr) for nbr in mnbrs]
        minnbs = min(nnbrs)
        nminnb = nnbrs.count(minnbs)
        maxnbs = max(nnbrs)
        nmaxnb = nnbrs.count(maxnbs)
        # counts = []
        # for nc in range(minnbs, maxnbs + 1):
        #     #num = min(nnbrs.count(nc),21)
        #     num = nnbrs.count(nc)
        #     if num > 0:
        #         counts.append((nc, num))
        logger.info(
            f"Neighbours' stats for wmolset:{NL_INDENT}"
            f"min = {minnbs} ({nminnb}), "
            f"max = {maxnbs} ({nmaxnb}), "
            f"avr = {sum(nnbrs) / len(mnbrs)}; "
            f"dmax = {wdmax}"
        )

        stime = time.time()
        nnbs = [list(annb) for annb in mnbrs]
        Vecs = wmolset.getMolRcomsArr3()
        Vmap = wmolset.Vmap
        Vkeys = Vmap.keys()

        logger.info(
            f"Added {len(Vmap)} PBC-halo vectors "
            f"to {wmolset.nitems} original ones"
        )

        groups = []
        skipped = []
        ic = 0
        for i in range(len(Vecs)):
            vnnb = nnbs[i]
            for ix, indx in enumerate(vnnb):
                if indx >= wmolset.nitems:
                    if str(indx) in Vkeys:
                        vnnb[ix] = Vmap[str(indx)]
                    elif ic < 6:
                        ic += 1
                        logger.info(f"Index {indx} not found in Vmap!")
            # skip (peripheral) molecules with less than (nbmax - 1) neighbours
            # they can still be included as neighbours in clusters seeded on other molecules
            if len(vnnb) < nbmax - 1:
                skipped.append(i)
                continue

            groups.append(vnnb)

        logger.info(
            f"Found {len(groups)} molecule groups overall ({len(skipped)} excluded) "
            f"in {sec2hms(time.time() - stime)}"
        )

        stime = time.time()
        unique_groups = unique_groups(groups, wmolset.nitems)
        logger.info(
            f"Found {len(unique_groups)} unique non-overlapping molecule groups "
            f"in {sec2hms(time.time() - stime)}"
        )

        stime = time.time()
        compact_groups, group_scores = compact_unique_groups(groups, Vecs, box, nbmax - 1, mode='avr')
        logger.info(
            f"Found {len(compact_groups)} unique compact molecule groups "
            f"with min/max scores = {min(group_scores)} / {max(group_scores)} "
            f"in {sec2hms(time.time() - stime)}"
        )

        bead_number = wmolset.nitems // wnmap
        if bead_number > len(compact_groups):
            logger.warning(
                f"WARNING: number of molecule groups found "
                f"{len(compact_groups)} < {bead_number} "
                f"(the expected CG bead number)!"
            )
        max_score_indx = group_scores.index(max(group_scores))
        if max(group_scores) > wdmax:
            max_score_indx = min(group_scores.index(max(group_scores)),
                                 bead_number - 1)
            logger.info(
                f"Group {max_score_indx} with the max score: "
                f"{compact_groups[max_score_indx]} "
                f"-> {group_scores[max_score_indx]}"
            )

        bead_groups = compact_groups[: min(bead_number, len(compact_groups))]

        # Create CG water MoleculeSet based on bead_groups
        wbeads_molset = MoleculeSet(name=wresname + "_WCG", type="WCG")

        for bgrp in bead_groups:
            bead_atoms = [atom for bidx in bgrp[:wnmap] for atom in wmolset.items[bidx]]
            # aacg_mol = Molecule(aname='WMP4',
            #                     atype='WMP4',
            aacg_mol = Molecule(
                aname="WCG", atype="WCG", atoms=bead_atoms, box=box, isMolPBC=True
            )
            wbead_atom = Atom(
                # aname="W",
                # atype="P4",
                aname=watmname,  # "WCG",
                atype=watmname,  # "WCG",
                aindx=i,
                amass=aacg_mol.getMass(),
                achrg=0.0,
                arvec=aacg_mol.getRvec(),
            )
            water_bead = Molecule(
                aindx=i,
                aname=wresname,
                atype=wresname,  # + '_CG',
                # aname='WMP4',  # wresname,
                # atype='WMP4',  # wresname + '_CG',
            )
            water_bead.addItem(wbead_atom)
            water_bead.refresh()
            wbeads_molset.addItem(water_bead)

        return wbeads_molset

    # end of CoarseGrainer.water_cg_molset()

    # def make_cg_system(self, fpath_inp: str, fpath_out: str) -> MolecularSystem:
    #     """
    #     Process a molecular system to generate a coarse-grained structure.
    #
    #     Parameters
    #     ----------
    #     fpath_inp : str
    #         Path to the input structure file (e.g., .gro or .pdb).
    #     fpath_out : str
    #         Path to the output coarse-grained file (e.g., .gro or .pdb).
    #
    #     Returns
    #     -------
    #     tuple
    #         A tuple containing the coarse-grained molecule set and box dimensions.
    #     """
    #     remarks = []
    #     molsets = []
    #     box = []
    #
    #     # Determine if input and output files are GRO or PDB
    #     inp_gro = fpath_inp[-4:] == ".gro"
    #     out_gro = fpath_out[-4:] == ".gro"
    #
    #     # get resnames from the CG mapping file
    #     residues_in_mapping = list(self.mapper.get_all_residues())
    #
    #     # Read the atomistic configuration without scaling coordinates
    #     lscale_out = 1.0
    #     if inp_gro:
    #         gro = groFile(fpath_inp)
    #         success = gro.readInMols(
    #             remarks, molsets, box, resnames=residues_in_mapping, resids=("ALL",)
    #         )
    #         # recenter the system at the origin
    #         # need to do this here not to affect pdb output
    #         for molset in molsets:
    #             for mol in molset:
    #                 mol.moveBy(-Vec3(*box) * 0.5)
    #         if not out_gro:
    #             lscale_out = 10.0
    #     else:
    #         pdb = pdbFile(fpath_inp)
    #         success = pdb.readInMols(
    #             remarks, molsets, box, resnames=residues_in_mapping, resids=("ALL",)
    #         )
    #         if out_gro:
    #             lscale_out = 0.1
    #
    #     if not success:
    #         print("Failed to read input file")
    #         return None, None
    #
    #     # Ensure the box is valid
    #     if not box or len(box) < 3:
    #         print(
    #             "Warning: No valid box dimensions found in the input file. Using default box dimensions (10.0, 10.0, 10.0)"
    #         )
    #         box = [10.0, 10.0, 10.0]  # Default box dimensions
    #
    #     if box:
    #         box_vec = Vec3(box[0], box[1], box[2])
    #         print(f"Read-in Box = {box_vec}")
    #     else:
    #         print("No box size found in the input file")
    #         return None, None
    #
    #     n_sets = sum(len(molset.items) for molset in molsets)
    #     n_done = 0
    #
    #     cg_names = "CG_"
    #     cg_molsets = []
    #     for molset in molsets:
    #         cg_names += molset.name + '_'
    #         cg_molset = MoleculeSet(n_done, name="CG_"+molset.name, type="output")
    #         cg_molsets.append(cg_molset)
    #         for molecule in molset.items:
    #             residue_name = molecule.name
    #             if self.mapper.is_valid_residue(residue_name):
    #                 cg_mol = self.coarse_grain_molecule(molecule, residue_name)
    #                 cg_molset.addItem(cg_mol)
    #                 n_done += 1
    #                 logger.debug(f"Processed {residue_name} molecules: {n_done}/{n_sets}")
    #
    #     cg_molsys = MolecularSystem(sname=cg_names[3:-1], stype='output', molsets=cg_molsets, vbox=box)
    #
    #     # Write the coarse-grained configuration
    #     fout = None
    #     if out_gro:
    #         fout = groFile(fpath_out, fmode="w")
    #     else:
    #         fout = pdbFile(fpath_out, fmode="w")
    #
    #     remarks = f"Coarse Grained {cg_molsys.name} System"
    #     success = fout.writeOutMols(remarks, box, cg_molsys.items, lenscale=lscale_out)
    #
    #     if success:
    #         print(f"Successfully wrote CG configuration to file: {fpath_out}")
    #     else:
    #         print(f"Failed to write CG configuration to file: {fpath_out}")
    #
    #     fout.close()
    #
    #     return cg_molsys
    # # end of make_cg_system()


# end of class CoarseGrainer
