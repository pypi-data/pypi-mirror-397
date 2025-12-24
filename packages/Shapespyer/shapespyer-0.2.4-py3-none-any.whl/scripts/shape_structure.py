#!/usr/bin/env python3

# This software is provided under The Modified BSD-3-Clause License (Consistent with 
# Python 3 licenses).
# Refer to and abide by the Copyright detailed in LICENSE file found in the root 
# directory of the library!

###################################################
#                                                 #
#  Shapespyer - soft matter structure generator   #
#               ver. 0.2.3 (beta)                 #
#                                                 #
#  Author: Dr Andrey Brukhno (c) 2020 - 2025      #
#          Daresbury Laboratory, SCD, STFC/UKRI   #
#                                                 #
#  Contrib: MSc Mariam Demir (c) Sep2023 - Feb24  #
#          Daresbury Laboratory, SCD, STFC/UKRI   #
#      (YAML IO, InputParser, topology analyses)  #
#                                                 #
#  Contrib: Dr Michael Seaton (c) 2024            #
#          Daresbury Laboratory, SCD, STFC/UKRI   #
#          (DL_POLY/DL_MESO DPD w-flows, tests)   #
#                                                 #
#  Contrib: Dr Valeria Losasso (c) 2024 - 2025    #
#          Daresbury Laboratory, SCD, STFC/UKRI   #
#        (PDB IO, Bilayer, NAMD w-flows, tests)   #
#                                                 #
#  Contrib: BSc Saul Beck (c) Sep 2024 - Feb 2025 #
#          Daresbury Laboratory, SCD, STFC/UKRI   #
#        (DCD/Martini IO, CG w-flows, examples)   #
#                                                 #
#  Contrib: Dr Ales Kutsepau (c) 2025             #
#          DMSC Postdoc, ESS, DTU, Denmark        #
#         (Options and interfaces, GUI backend)   #
#                                                 #
###################################################

##from __future__ import absolute_import
__author__ = "Andrey Brukhno"

import os
import sys

from shapes.basics.defaults import Fill, NL_INDENT
from shapes.basics.globals import HUGE, TINY, Pi, TwoPi
from shapes.basics.input import InputParser
from shapes.basics.options import Options, OptionsSerDes
from shapes.basics.utils import Generator, LogListener, LogConfiguration

### MAIN ###
def main(argv: list[str] = sys.argv):
    log_file = "shape.log"
    logger = LogConfiguration(file_name=log_file).logger

    ##### - COMMAND-LINE / YAML INPUT / HELP - START

    options = Options()
    inpPars = InputParser()
    listener = LogListener()
    options.shape.add_listener(listener)
    options.molecule.add_listener(listener)

    # AB: does not make sense to output this to terminal every time the script is called
    # logger.debug("Parsing input parameters (from CLI or YAML) ...")
    try:
        options = inpPars.parseCLI(argv, options)
    except Exception as e:
        logger.exception(e)
        logger.error("FULL STOP!!!")
        logger.error(f"Try '{os.path.basename(argv[0])} --help'")
        sys.exit(1)
    # logger.debug("Parsing input parameters - DONE")
    
    ##### - COMMAND-LINE / YAML INPUT / HELP - END

    ##### - ARGUMENTS ANALYSIS - START
    
    # AB: retain the sign only in options.shape.slv_buff
    # options.base.abs_slv_buff = abs(options.shape.slv_buff) 
    # nm - rescale for Angstroems!

    if (
        options.shape.stype.is_ball
        and options.shape.fill is not Fill.RINGS0
    ):
        if options.shape.fill is Fill.RINGS:
            logger.debug(
                f"Will generate 'ball' with {options.shape.lring} "
                "molecules projected on 'equator' ring - "
                f"option '--fill=rings' (second variant) ..."
            )
        else:
            logger.debug(
                f"Will generate 'ball' of {options.shape.nmols} molecules "
                "covering its surface uniformly - option '--fill=fibo' "
                "(Fibonacci spiral) ..."
            )
        if options.shape.rmin < 0.5:
            logger.debug(
                f"Generating a 'ball' of radius Rmin = {options.shape.rmin} "
                f" < 0.5 nm ..."
            )
    logger.info(
        f"Check globals & defaults:{NL_INDENT}"
        f"Pi = {Pi}, 2*pi = {TwoPi}, TINY = {TINY}, HUGE = {HUGE}{NL_INDENT}"
        f"BUFF = {options.base.abs_slv_buff}, DMIN = {options.shape.dmin}, "
        f"RMIN = {options.shape.rmin}"
    )
    logger.info(
        f"Requested molecule names and ids: { options.molecule.resnames} -> "
        f"{options.molecule.resnm} & {options.molecule.molids} -> "
        f"{options.molecule.molid}"
    )
    logger.info(
        f"Requested shape 'bone' indices: {options.molecule.mint} ... "
        f"{options.molecule.mext}"
    )
    logger.info(
        f"Using Nmol = {max(options.shape.lring, options.shape.nmols)}"
    )
    logger.info(f"Using Nlay = {options.shape.layers.quantity}")
    if options.shape.layers.quantity > 1:
        logger.info(f"Dmin scale = {options.shape.layers.dmin_scaling}")
        logger.info(f"Rcav scale = {options.shape.layers.cavr_scaling}")
    logger.info(f"Using Nlay = {options.shape.layers.quantity}")
    logger.info(
        f"Using Dmin = {options.shape.dmin} for min separation between heavy atoms"
    )
    logger.info(
        f"Using Rmin = {options.shape.rmin} for target internal radius (if applicable)"
    )
    logger.info(
        f"Using Rbuf = {options.base.sbuff} for solvation buffer"
    )
    logger.info(
        f"Doing: input '{options.input.file}' => output '{options.output.file}'"
    )

    # AB: dump the input for reference and to comply with the acceptance tests
    inp_dump_file = ".inp.yaml"
    OptionsSerDes.dump_validated_yaml(options, inp_dump_file)

    ##### - ARGUMENTS ANALYSIS - DONE

    try:
        gen = Generator(options)
        gen.read_input()
        gen.generate_shape()

        # AB: save options in YAML file with the same base as the main output file
        OptionsSerDes.dump_validated_yaml(options, file_name=gen.writer_handler.dfout)
        
        gen.dump_file()

    except Exception as e:
        logger.exception(e)
        sys.exit(2)

    os.rename(log_file, f"{gen.writer_handler.dfout}.log")
    os.rename(inp_dump_file, f"{gen.writer_handler.dfout}.inp.yaml")
# end of main(argv)


if __name__ == "__main__":
    main()
    sys.exit(0)

### END OF SCRIPT ###
