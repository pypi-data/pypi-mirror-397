#!/usr/bin/env python3
"""
Analyse and/or coarse-grain trajectory (.dcd) frame by frame.
"""

# This software is provided under The Modified BSD-3-Clause License (Consistent with Python 3 licenses).
# Refer to and abide by the Copyright detailed in LICENSE file found in the root directory of the library!

##################################################
#                                                #
#  Shapespyer - soft matter structure generator  #
#                                                #
#  Author: Dr Andrey Brukhno (c) 2020 - 2025     #
#          Daresbury Laboratory, SCD, STFC/UKRI  #
#  Contrib: Dr Valeria Losasso (c) 2024          #
#           BSc Saul Beck (c) 2024               #
#                                                #
##################################################

##from __future__ import absolute_import

__author__ = "Andrey Brukhno"
__version__ = "0.2.0 (Beta)"

import sys, os
import argparse
import logging
from pathlib import Path
from numpy import arange, column_stack, sqrt, savetxt
from time import time

from shapes.cgmap.coarse_grainer import CoarseGrainer
from shapes.basics.globals import TINY
from shapes.basics.defaults import NL_INDENT
from shapes.basics.input import InputParser
from shapes.basics.functions import sec2hms  # timing
from shapes.basics.utils import LogConfiguration
# from shapes.basics.mendeleyev import Chemistry

from shapes.stage.protovector import Vec3
# from shapes.stage.protoatom import Atom
# from shapes.stage.protomolecule import Molecule
from shapes.stage.protomoleculeset import MoleculeSet
# from shapes.stage.protomolecularsystem import MolecularSystem

from shapes.ioports.iotraj import DCDTrajectory
# from shapes.ioports.ioframe import Frame, CellParameters
# from shapes.ioports.iotop import ITPTopology
# from shapes.ioports.iogro import groFile
# from shapes.ioports.iopdb import pdbFile

from shapes.basics.help import beauty #, help

logger = logging.getLogger("__main__")

def ana_traj(
        fpath_ref: str,
        fpath_trj: str,
        fpath_out: str,
        scheme: dict,
) -> None:
    """
    Calculate average densities of various types over a trajectory, which can be
    atomistic (AA) or coarse-grain (CG). In the case of atomistic trajectory one
    can convert it to coarse-grain representation and calculate CG densities in one go.

    Parameters
    ----------
    fpath_ref : str
        File path to the reference file (only .gro or .pdb formats)
    fpath_trj : str
        File path to the trajectory file (only .dcd format supported)
    fpath_out : str
        File path where the coarse-grained trajectory will be saved
    scheme : dict
        A dictionary specifying a set of options for the analysis

    """
    # ref_is_pdb = fpath_ref.lower().endswith(".pdb")
    ref_is_gro = fpath_ref.lower().endswith(".gro")
    ref_cg_ext = ".gro" if ref_is_gro else ".pdb"

    scheme_keys = scheme.keys()
    scheme_vals = scheme.values()

    res_names = ["ALL"]
    spc_names = ["ALL"]

    cgobj = None
    cgtrj = False
    if "cgobj" in scheme_keys:
        cgobj = scheme["cgobj"]
    if cgobj:
        res_names = list(cgobj.mapper.get_all_residues())
        if "cgtrj" in scheme_keys:
            cgtrj = scheme["cgtrj"]
    elif "rnames" in scheme_keys:
        res_names = scheme["rnames"]

    bname = os.path.splitext(fpath_trj)[0]
    ref_cg_out = bname + '_aa2cg' + ref_cg_ext
    if cgobj and cgtrj:
        if fpath_out:
            ref_cg_out = os.path.splitext(fpath_out)[0] + ref_cg_ext

    if "snames" in scheme_keys:
        spc_names = scheme["snames"]
    else:
        spc_names = res_names.copy()

    wname = ""
    wpars = None
    if "wname" in scheme_keys:
        wname = scheme["wname"]
        if "wpars" in scheme_keys:
            wpars = scheme["wpars"]
        if wname:
            res_names.append(wname)
            if wpars and wpars["dmax"] < 1.0:
                # convert to Angstroms since CG-ing is done on original DCD coordinates
                wpars["dmax"] *= 10.0

    origin = Vec3()
    if "origin" in scheme_keys:
        origin = scheme["origin"]
        if isinstance(origin, list):
            origin = Vec3(*origin)
        if isinstance(origin, tuple):
            origin = Vec3(*list(origin))

    logger.info(f"ana_traj(): Reading residues {res_names} from file {fpath_ref} centred at {origin} ...")

    grid = None
    if "grid" in scheme_keys:
        grid = scheme["grid"]

    den_error = False
    den_names = None
    if "dnames" in scheme_keys:
        if (isinstance(scheme["dnames"],tuple) or
            isinstance(scheme["dnames"],list)):
            if scheme["dnames"][0] is not None:
                den_names = scheme["dnames"]
        if den_names:
            if scheme["zbin"] > TINY:
                logger.info(f"Will calculate Z-densities: {den_names} ...")
            else:
                logger.info(f"Will calculate R-densities: {den_names} ...")
            den_error = 'nerr' in den_names
            if den_error:
                den_names.pop(den_names.index('nerr'))

    frames = []
    histograms = []

    if fpath_trj.endswith(".dcd"):

        # AB: this is irrelevant for now
        # ref_out = os.path.splitext(fpath_out)[0] + '_ref' + ref_cg_ext
        # cgobj.coarse_grain_structure(fpath_ref, ref_out)

        dcd_inp = DCDTrajectory(fpath=fpath_trj,
                                fpath_ref=fpath_ref,
                                mode="r",
                                res_names = res_names,
                                tryMassElems=True)

        areas = None
        zdims = None
        z_min = 0.0
        z_max = 0.0
        z_mid = 0.0
        z_bin = scheme["zbin"]
        n_bin = 0
        if den_names and z_bin > TINY:
            areas, zdims = zip(*[(frame.cell_params.a * frame.cell_params.b * 0.01,
                                  frame.cell_params.c * 0.1) for frame in dcd_inp.frames])
            # Total number of bins based on z_max and bin_size
            z_min = min(zdims)
            z_max = max(zdims)
            n_bin = int(z_max / z_bin)
            if n_bin & 1:  # % 2 > 0:
                n_bin += 1
            z_max = z_bin * float(n_bin)  # produce nice output!
            z_mid = z_max * 0.5

        nframes = 0
        for iframe, (cell_params, coordinates) in enumerate(dcd_inp):
            if ( iframe < scheme["ifirst"] or
                (iframe - scheme["ifirst"]) % scheme["frqncy"] != 0):
                continue
            nframes += 1
            stime = time()

            logger.info(f"Processing frame {iframe} for {len(res_names)} "
                  f"residues {res_names} ...")

            box_out = Vec3(cell_params.a, cell_params.b, cell_params.c)
            cg_molsys = None
            if cgobj:
                if cgtrj:
                    molsys = dcd_inp.update_molsys(dcd_inp.frames[iframe],
                                                   is_MolPBC=True)
                    cg_molsys = cgobj.create_cg_system(
                        molsets=molsys.items,
                        box=box_out,  # Vec3(*box_out[:3]),
                        wpars=wpars,
                    )
                    molsys = cg_molsys.copy()
                    # if iframe == 0:
                    #     print(f"Compare(0): {cg_molsys.items[0][0][0].getRvec()} =?= "
                    #           f"{molsys.items[0][0][0].getRvec()}")
                    molsys.refreshScaled(rscale=0.1)
                    # if iframe == 0:
                    #     print(f"Compare(1): {cg_molsys.items[0][0][0].getRvec()} =?= "
                    #           f"{molsys.items[0][0][0].getRvec()}")
                else:
                    molsys = dcd_inp.update_molsys(dcd_inp.frames[iframe],
                                                   is_MolPBC=True, lscale=0.1)
                    for mset in molsys.items:
                        if wname not in mset.name:
                            for mol in mset.items:
                                cgobj.set_cgmol_elems(mol)
            else:
                # AB: is_MolPBC=True puts whole molecules back into the primary cell
                molsys = dcd_inp.update_molsys(dcd_inp.frames[iframe],
                                               is_MolPBC=True, lscale=0.1)

            solutes = MoleculeSet(sname="Solutes")
            solnames= ""
            for mset in molsys.items:
                if (mset.name in spc_names or
                    "ALL" in spc_names or
                    "All" in spc_names or
                    "all" in spc_names):
                        solnames += "_mset.name"
                        for mol in mset:
                            solutes.addItem(mol)

            if origin:
                logger.info(f"Elapsed time before moving solutes of length {len(solutes.items)} "
                      f"to the origin = {origin}: "
                      f"{sec2hms(time()-stime)}")
                sstime = time()
                rcom, rcog = solutes.getRvecs(isupdate=True,
                                              box=box_out,  # Vec3(*box_out[:3]), #*0.1,
                                              #isMolPBC = False,
                                              dmax=1.5,  # nm
                                              nmax=8)
                logger.info(f"Solutes Rcom = {rcom}, Rcog = {rcog}")
                shift = origin - rcom
                molsys.moveBy(shift)
                logger.info(f"Elapsed time moving solutes to the origin = {origin}: "
                      f"{sec2hms(time()-sstime)}")

            logger.info(f"Elapsed time preparing the frame for analysis: "
                  f"{sec2hms(time()-stime)}")

            area = 0.0
            if den_names:
                if z_bin > TINY:
                    grid[0] =-z_mid
                    grid[1] = z_mid
                    grid[2] = z_bin
                    area = areas[iframe]

                # if wname:
                #     res_names.append("WCG")

                histograms.append(
                    molsys.Densities(
                        rorg = origin,
                        grid = grid,
                        clist = res_names,
                        dlist = den_names,
                        is_cg = (cgobj is not None),
                        xy_area = area
                        #bname=bname + '_frm-' + str(iframe),
                        #be_verbose=True,
                    )
                )

            if cgtrj:
                if iframe == 0:
                    #cell = dcd_inp.frames[iframe].cell_params
                    #cell = cell_params
                    # Write initial structure
                    out_is_gro = ref_cg_out.endswith(".gro")
                    if out_is_gro:
                        #cgobj._write_output(cg_molsys, box_out, ref_cg_out, 0.1)
                        cgobj._write_output(cg_molsys, cell_params, ref_cg_out, 0.1)
                    else:
                        #cgobj._write_output(cg_molsys, box_out, ref_cg_out, 1.0)
                        cgobj._write_output(cg_molsys, cell_params, ref_cg_out, 1.0)

                frame = cgobj._create_frame(cg_molsys, cell_params)
                frames.append(frame)

            logger.debug(f"Total time working on the frame: "
                        f"{sec2hms(time()-stime)}")

        dcd_inp.close()

        if cgtrj:
            if not frames:
                raise RuntimeError("No frames processed - check input trajectory file")

            dcd_out = DCDTrajectory(fpath=fpath_out, mode="w")
            dcd_out.write(frames)
            dcd_out.close()

        if den_names and len(histograms) > 0:
            htotals = {}
            hsquare = {}
            for ih, hist in enumerate(histograms):
                if hist:
                    for hkey in hist.keys():
                        if hkey not in htotals.keys():
                            htotals.update({ hkey: hist[hkey] })
                            hsquare.update({ hkey: hist[hkey]**2 })
                        else:
                            htotals[hkey] += hist[hkey]
                            hsquare[hkey] += hist[hkey]**2
                    # logger.debug(f"Histograms {ih} '{hist.keys()}'")
                else:
                    logger.info(f"Histogram {ih} (None?) :{hist}")

            rmin = grid[0]
            rmax = grid[1]
            dbin = grid[2]
            dbin2 = dbin / 2.0
            nbins = round((rmax - rmin) / dbin)
            drange = arange(0, nbins, dtype=float) * dbin + dbin2 + rmin

            if len(htotals.keys()) > 0:
                for hkey in htotals.keys():
                    nframes =  float(nframes)
                    htotals[hkey] /= nframes
                    if den_error:
                        hsquare[hkey] /= nframes
                        hsquare[hkey] = sqrt(abs(hsquare[hkey] - htotals[hkey] ** 2))
                        fmtkey = "{:<9}".format(hkey)
                        header = '# bin  ' + fmtkey + '  std.error  std.deviation\n'
                        with open(bname + '_' + hkey + '_avr.dat', 'wb') as fout:
                            fout.write(bytes(header,"ASCII"))
                            savetxt(fout,
                                    column_stack((drange,
                                                  htotals[hkey] +0.0,
                                                  hsquare[hkey]/sqrt(nframes) + 0.0,
                                                  hsquare[hkey] +0.0)),
                                    fmt='%-0.3f %10.7f %10.7f %10.7f')
                    else:
                        savetxt(bname + '_' + hkey + '_avr.dat',
                                column_stack((drange,
                                              htotals[hkey] + 0.0)),
                                fmt='%-0.3f %10.7f')
    else:
        raise ValueError("Unsupported trajectory format (not a .dcd trajectory)!")
# end of ana_traj()

# def list_of_strings(arg: str) -> list[str] or None:
#     from re import sub as re_sub
#     split = re_sub(r"[\[\]\(\)]", "", arg.strip()).split(",")
#     value = None
#     if len(split) > 0:
#         value = [var.strip() for var in split]
#     elif isinstance(arg, str):
#         value = [arg]
#     return value

# def list_of_floats(arg: str) -> list[float]:
#     return [float(x) for x in InputParser.list_of_strings(arg)]

def main(argv: list[str]=sys.argv):
    """
    Main function to handle command-line arguments and execute coarse-graining.
    """

    LogConfiguration(level=logging.INFO, logger=logger)
    # logger = LogConfiguration(level=logging.INFO).logger

    sname = os.path.basename(argv[0])

    if len(argv) - 1 < 1:
        # AB: print help page if no arguments are given
        argv.append('-h')

    tb = beauty()

    parser = argparse.ArgumentParser(
        prog=sname,
        usage=tb.BOLD
              + sname
              + " [-v] -i <INP> -r <REF> [-o <OUT>] -d <DNAMES> [-r <RNAMES>] [-s <SNAMES>] [extra options]"
              + tb.END,
        description="Calculate densities for an atomistic or coarse-grain "
                    "molecular system",
        epilog="End of help (nothing done)",
    )

    parser.add_argument(
        "-v", "--verbose", action="store_true",
        help="Enable verbose output for debugging"
    )

    parser.add_argument(
        "-i", "--inp",
        help="Path to the input trajectory file (*.dcd)"
    )
    parser.add_argument(
        "-r", "--ref",
        help="Path to the reference structure file (*.gro|*.pdb) "
             "if coarse-graining input trajectory (option --cg)"
    )
    parser.add_argument(
        "-o", "--out",
        help="Path to the output CG trajectory file (*.dcd)",
    )
    parser.add_argument(
        "-b", "--begin", default=0,
        help="Index of first frame to take from trajectory {0*}"
    )
    parser.add_argument(
        "-q", "--freq", default=1,
        help="Frequency of frames taken from trajectory (stride) {1*}"
    )
    parser.add_argument(
        "--rnames", default="ALL",
        help="List of all residue names"
    )
    parser.add_argument(
        "-s", "--snames", default="ALL",
        help="List of solute residues to search for cluster(s)"
    )
    # AB: no scope for this yet
    # parser.add_argument(
    #     "-a", "--anames", default="",
    #     help="List of density types"
    # )
    parser.add_argument(
        "-d", "--dtypes", # default="",
        help="List of density types"
    )
    parser.add_argument(
        "-z", "--zbin", default=-1.0,  #, action="store_true",
        help="Z-bin size {-1*}, if greater than zero then Z-densities are calculated"
    )
    parser.add_argument(
        "-g", "--grid", default=None,
        help="List of floats for R-grid: [min,max,bin]"
    )
    parser.add_argument(
        "--origin", # default="",
        help="List of floats for origin: [X_o,Y_o,Z_o]"
    )
    parser.add_argument(
        "-c", "--cg", action="store_true",
        help="Flag to turn coarse-graining on"
    )
    parser.add_argument(
        "-m", "--map",
        help="Path to .map AA-CG mapping file"
    )
    parser.add_argument(
        "-t", "--itp",
        help="Path to .itp topology file (requires --map)"
    )
    parser.add_argument(
        "-j", "--json",
        help="Path to .json AA-CG mapping file"
    )
    parser.add_argument(
        "-w", "--wname", default="",
        help="Water residue name"
    )
    parser.add_argument(
        "-p", "--wnmap", default=4,
        help="Number of water molecules per CG bead"
    )
    parser.add_argument(
        "-n", "--wnmax", default=8,
        help="Upper cap for water neighbour search"
    )
    parser.add_argument(
        "--wdmax", default=4.7,
        help="Max distance for water neighbour search"
    )

    args = parser.parse_args()

    if args.verbose:
        # logger = LogConfiguration(level=logging.DEBUG).logger
        LogConfiguration(level=logging.DEBUG, logger=logger)
        logger.debug("Verbose (debug) output\n")
    else:
        # logger = LogConfiguration(level=logging.INFO).logger
        LogConfiguration(level=logging.INFO, logger=logger)
        logger.info("Standard (info) output\n")

    if not args.inp or not args.ref:
        sys.exit(f"\nYou need to provide both input and reference structure files - "
                 f"use option '-h' for more details.\n")
    else:
        if args.inp and not args.inp[-4:] == ".dcd":
            sys.exit(f"\nInput file name must end with '.dcd' - "
                     f"use option '-h' for more details.\n")
        if args.ref and not args.ref[-4:] in {".gro", ".pdb"}:
            sys.exit(f"\nReference file name must end with '.gro' or '.pdb' - "
                     f"use option '-h' for more details.\n")

    if args.out and not args.out[-4:] == ".dcd":
        sys.exit(f"\nOutput file name must end with '.dcd' - "
                 f"use option '-h' for more details.\n")

    # if not args.dtypes:
    #     sys.exit(f"\nYou need to provide a list of density types from [mden,nden,nsld, hist] - "
    #              f"use option '-h' for more details.\n")

    # if not args.rnames:
    #     sys.exit(f"\nYou need to provide a list of residues names - "
    #              f"use option '-h' for more details.\n")

    if args.cg:
        if not args.json and not args.map:
            sys.exit(f"\nNeed to provide either .json file or .map file - "
                     f"use option '-h' for more details.\n")

        if args.json and (args.map or args.itp):
            raise Exception("\nERROR: You cannot provide both .json file "
                            "and .map files.")

        if args.itp and not args.map:
            raise Exception("\nERROR: You must provide either .map file "
                            "to be able to use .itp file.")

        if args.map and not args.itp:
            logger.warning("Only .map file provided - "
                  "bonds and angles details will be omitted.")

    wname = ""
    wpars = None
    if args.wname:
        wname = InputParser.list_of_strings(args.wname)
        #wname = list_of_strings(args.wname)
        #wname = str(args.wname)
        if args.cg and args.wnmap:
            if int(args.wnmap) > 6 or int(args.wnmap) < 2:
                raise Exception("\nERROR: wnmap must be in the interval [2,6]")
            if float(args.wdmax) < 0.25:
                raise Exception("\nERROR: wdmax cannot be set < 2.5 A")
            if float(args.wdmax) > 6.0:
                raise Exception("\nERROR: wdmax cannot be set > 6.0 A")
            # wpars = {"name": str(args.wname),
            wpars = {"name": wname,  # InputParser.list_of_strings(args.wname),
                     "nmap": int(args.wnmap),
                     "nmax": int(args.wnmax),
                     "dmax": float(args.wdmax),
                    }
            logger.info(f"Extra options for CG water:{NL_INDENT}{wpars}")
                 # f" is_cg = {args.cg} / is_wnmap = {args.wnmap}")

    # Initialise CoarseGrainer
    cg = None
    if args.cg:
        if args.json:
            cg = CoarseGrainer(args.json)
        elif args.map:
            if args.itp:
                cg = CoarseGrainer(args.map, args.itp)
            else:
                cg = CoarseGrainer(args.map)
        if not cg:
            raise Exception("Failed to create CoarseGrainer object!")

    origin = None
    if args.origin is not None:
        origin = InputParser.list_of_floats(args.origin)
    else:
        origin = [0.,0.,0.]

    grid = None
    dnames = None,
    if not args.dtypes:
        logger.info(f"\n{sname}:: No density types specified: {dnames} - "
                    f"skipping density calculation ...\n")
        args.grid = None
    else:
        dnames = InputParser.list_of_strings(args.dtypes)
        logger.info(f"Specified density types: {dnames}")

        if float(args.zbin) > TINY:
            grid = ['-zmid', '+zmid', args.zbin]
            logger.info(f"\n{sname}:: Will use Z-grid: {grid}\n")
        elif args.grid:
            grid = InputParser.list_of_floats(args.grid)
            if grid[0] > grid[1]:
                grid1   = grid[0]
                grid[0] = grid[1]
                grid[1] = grid1
            logger.info(f"\n{sname}:: Will use R-grid: {grid}\n")
        elif dnames:
            raise ValueError(f"\n{sname}:: "
                             f"Need to specify --grid or --zbin "
                             f"for density calculation!")

    schema = dict(
        ifirst = int(args.begin),
        frqncy = int(args.freq),
        dnames = dnames,
        rnames = InputParser.list_of_strings(args.rnames),
        snames = InputParser.list_of_strings(args.snames),
        origin = origin,
        grid  = grid,
        zbin  = float(args.zbin),
        wname = wname[0] if isinstance(wname, list) and len(wname) > 0 else wname,
        cgobj = cg,
        wpars = wpars,
        cgtrj = (args.out is not None),
    )

    # is_conf = ( Path(args.inp).suffix.lower() in ['.gro', '.pdb'] and
    #             Path(args.out).suffix.lower() in ['.gro', '.pdb'] )
    # is_traj = ( Path(args.inp).suffix.lower() == '.dcd' and
    #             Path(args.out).suffix.lower() == '.dcd' )

    is_conf = Path(args.inp).suffix.lower() in ['.gro', '.pdb']
    is_traj = Path(args.inp).suffix.lower() == '.dcd'

    if is_conf:
        raise Exception("Densities for single structure (.gro/.pdb) not supported!")
    elif is_traj:
        if args.ref:
            if Path(args.ref).suffix.lower() in ['.gro', '.pdb']:
                ana_traj(
                    fpath_ref=args.ref,
                    fpath_trj=args.inp,
                    fpath_out=args.out,
                    scheme=schema,
                )
            else:
                raise Exception(f"Unsupported reference structure file name: "
                                f"{args.ref}!")
        else:
            raise Exception(f"Please provide reference structure file name!"
                            f"{args.ref}!")
    else:
        raise Exception("One cannot coarse-grain structure into trajectory, "
                        "nor vice versa!")
# end of main()


if __name__ == "__main__":
   main()
   sys.exit(0)

# if __name__ == "__main__":
#     # main()
#     try:
#         main(sys.argv)
#     except Exception as e:
#         raise Exception(f"Could not execute '{sys.argv}'")
#         sys.exit(2)
