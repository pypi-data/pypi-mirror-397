#!/usr/bin/env python3
"""
This script converts a structure (single configuration in .gro or .pdb format)
or a trajectory (in .dcd format) from atomistic to coarse-grain representation.

The AA-to-CG mapping details can be provided in two ways:

1. In a MARTINI style .map file, optionally complemented by a GROMACS topology .itp file.
As a side effect of running script with a .map (and .itp) input, a .json file is created
containing either (i) the minimum map for CG beads with atomic groups assigned to them or
(ii) the entire map including connectivity 'bonds' and 'angles'.

2. In a .json file that was earlier generated using option 1.

**Experimental:** Optionally, one can also include water in the coarse-graining procedure
by (at least) specifying the (residue) name for water molecules with option `--wname`.
Obviously, the provided water name must be found in the input (or reference) configuration file.

*NOTE:* The Martini style 4:1 mapping for water assumes that one water bead corresponds
to 4 water molecules that are found in the close vicinity of each other. Therefore,
the first step is to produce a nearest-neighbour-list for each water molecule in
the system, which is the most time-consuming operation carried out (when water
is included in the mapping process).

Unfortunately, if the mapping is performed strictly, so that a CG bead is formed only
when *all the included four water molecules are mutual neighbours of each other*,
the resulting number of CG water beads is typically significantly smaller than
the expected [N_w / 4]. To circumvent this issue, the following approach is employed.

1) First, the algorithm loops through the water set and sequentially finds the closest
neighbour triplet for each water molecule that is not yet included in any CG bead
(these molecules are *central* in their respective neighbour-lists). The resulting
quartet forms a new CG bead. Then, the neighbours of neighbours are considered as
being *central* molecules to form more CG beads in the same fashion.
Clearly, no pair of *central* molecules (for which neighbour triplets were found)
contribute to the same CG bead, while the so-collected list of CG beads is exhaustive,
i.e. it contains many pairs of beads that share (intermediate neighbour) water
molecules between them.

2) Second, water beads that have either (i) the greatest total overlap with their
neighbouring beads (estimated based on distances from their centres),
or (ii) the largest number of overlapping neighbouring beads, are
excluded until the number of remaining beads in the list equals [N_w / 4].

Usage:
-----
    convert-aa2cg  (-h | --help)

    convert-aa2cg --inp <inp_conf> --out <out_conf> --map <map_file> [--itp <itp_file>]

    convert-aa2cg --inp <inp_conf> --out <out_conf> --map <map_file> [--itp <itp_file>] --wname <water_resnmae>

    convert-aa2cg --inp <inp_conf> --out <out_conf> --json <json_file>

    convert-aa2cg --ref <ref_conf> --inp <inp_traj> --out <out_traj> --map <map_file> [--itp <itp_file>]

    convert-aa2cg --ref <ref_conf> --inp <inp_traj> --out <out_traj> --json <json_file>

    convert-aa2cg --ref <ref_conf> --inp <inp_traj> --out <out_traj> --json <json_file> --wname <water_resnmae>

Options:
-------
    -h --help               Show this help.

    -r --ref <ref_conf>        Reference config (.gro/.pdb) file for trajectory

    -i --inp <inp_conf>        Input config (.gro/.pdb) or trajectory (.dcd) file

    -o --out <out_conf>        Output config (.gro/.pdb) or trajectory (.dcd) file

    -m --map <map_file>        MARTINI AA-to-CG mapping (.map) file

    -t --itp <itp_file>        GROMACS molecular topology (.itp) file for CG system

    -j --json <json_file>      JSON AA-to-CG mapping file (.json)

    -w --wname <resname>       Water residue name (invokes MARTINI 4:1 mapping for water)

    -m --wnmap <wnmap>           Number of water molecules per CG bead

    -n --wnmax <nmax>          Upper cap for water neighbour search

    -d --wdmax <dmax>          Cut-off distance for water neighbour search
"""

# This software is provided under The Modified BSD-3-Clause License (Consistent with Python 3 licenses).
# Refer to and abide by the Copyright detailed in LICENSE file found in the root directory of the library!

##################################################
#                                                #
#  Shapespyer - soft matter structure generator  #
#                                                #
#  Author: Dr Andrey Brukhno (c) 2020 - 2024     #
#          Daresbury Laboratory, SCD, STFC/UKRI  #
#  Contrib: Dr Valeria Losasso (c) 2024          #
#           BSc Saul Beck (c) 2024               #
#                                                #
##################################################

##from __future__ import absolute_import
__author__ = "Andrey Brukhno"

import sys
import argparse

from pathlib import Path
from shapes.basics.defaults import NL_INDENT
from shapes.basics.input import InputParser
from shapes.basics.utils import LogConfiguration
from shapes.cgmap.coarse_grainer import CoarseGrainer


def main():
    """
    Main function to handle command-line arguments and execute coarse-graining.
    """
    logger = LogConfiguration().logger

    parser = argparse.ArgumentParser(
        description="Coarse-grain a molecular system using either "
                    ".map [+ .itp] or .json mapping file(s)."
    )
    parser.add_argument(
        "-i", "--inp",
        help="Path to the input structure or trajectory file (*.gro|*.pdb or *.dcd)"
    )
    parser.add_argument(
        "-r", "--ref",
        help="Path to the reference structure file (*.gro|*.pdb) "
             "for converting input AA trajectory (*.dcd)"
    )
    parser.add_argument(
        "-o", "--out",
        help="Path to the output CG structure or trajectory file (*.gro|*.pdb or *.dcd)",
    )
    parser.add_argument(
        "-m", "--map", help="Path to .map AA-CG mapping file"
    )
    parser.add_argument(
        "-t", "--itp", help="Path to .itp topology file (requires --map)"
    )
    parser.add_argument(
        "-j", "--json", help="Path to .json AA-CG mapping file"
    )
    parser.add_argument(
        "-w", "--wname", default="", help="Water residue name"
    )
    parser.add_argument(
        "-p", "--wnmap", default=4, help="Number of water molecules per CG bead"
    )
    parser.add_argument(
        "-n", "--wnmax", default=8, help="Upper cap for water neighbour search"
    )
    parser.add_argument(
        "-d", "--wdmax", default=4.7, help="Max distance for water neighbour search"
    )
    # AB: the options below has been deprecated since the update of the water-CG procedure!
    # parser.add_argument(
    #     "--wcl", action="store_true", help="Minimise total bead clashes"
    # )
    # parser.add_argument(
    #     "--nowcl", action="store_true", help="Minimise clashing bead neighbours"
    # )

    args = parser.parse_args()

    if not args.json and not args.map:
        sys.exit(f"\nYou need to provide either .json file or .map file - "
                 f"use option '-h' for more details.\n")

    if args.json and (args.map or args.itp):
        raise Exception("ERROR: You cannot provide both .json file "
                        "and .map files.")

    if args.itp and not args.map:
        raise Exception("ERROR: You must provide either .map file "
                        "to be able to use .itp file.")

    if args.map and not args.itp:
        logger.warning("Only .map file provided - bonds and angles details will be "
                       "omitted.")

    wpars = None
    if args.wname:
        if int(args.wnmap) > 6 or int(args.wnmap) < 2:
            raise Exception("ERROR: wnmap must be in the interval [2,6]")
        if float(args.wdmax) < 0.25:
            raise Exception("ERROR: wdmax cannot be set < 2.5 A")
        if float(args.wdmax) > 6.0:
            raise Exception("ERROR: wdmax cannot be set > 6.0 A")
        wpars = {"name": InputParser.list_of_strings(args.wname), # str(args.wname),
                 "nmap": int(args.wnmap),
                 "nmax": int(args.wnmax),
                 "dmax": float(args.wdmax),
                }
        logger.info(f"{sys.argv[0]}::{NL_INDENT}Extra options for water:"
                    f"{NL_INDENT}{wpars}")

    # Initialise CoarseGrainer
    cg = None
    if args.json:
        cg = CoarseGrainer(args.json)
    elif args.map:
        if args.itp:
            cg = CoarseGrainer(args.map, args.itp)
        else:
            cg = CoarseGrainer(args.map)
    if not cg:
        raise Exception("Failed to create CoarseGrainer object!")

    is_conf = ( Path(args.inp).suffix.lower() in ['.gro', '.pdb'] and
                Path(args.out).suffix.lower() in ['.gro', '.pdb'] )
    is_traj = ( Path(args.inp).suffix.lower() == '.dcd' and
                Path(args.out).suffix.lower() == '.dcd' )

    if is_conf:
        cg.coarse_grain_structure(args.inp, args.out, water_pars=wpars)
    elif is_traj:
        if args.ref:
            if Path(args.ref).suffix.lower() in ['.gro', '.pdb']:
                cg.coarse_grain_trajectory(fpath_ref=args.ref,
                                           fpath_trj=args.inp,
                                           fpath_out=args.out,
                                           water_pars=wpars,
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
