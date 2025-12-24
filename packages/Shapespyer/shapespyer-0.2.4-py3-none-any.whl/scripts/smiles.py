#!/usr/bin/env python3

# This software is provided under The Modified BSD-3-Clause License 
# (Consistent with Python 3 licenses).
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

from shapes.basics.input import InputParser
from shapes.basics.utils import Generator, LogListener, LogConfiguration
from shapes.basics.options import Options, OptionsSerDes

def main(argv: list[str] = sys.argv):
    log_file = "smiles.log"

    logger = LogConfiguration(file_name=log_file).logger

    options = Options()
    inpPars = InputParser()
    listener = LogListener()
    options.shape.add_listener(listener)
    options.molecule.add_listener(listener)

    try:
        options = inpPars.parseCLI(argv, options)
    except Exception as e:
        logger.exception(e)
        logger.error("FULL STOP!!!")
        logger.error(f"Try '{os.path.basename(argv[0])} --help'")
        sys.exit(1)

    # AB: dump the input for reference and to comply with the acceptance tests
    inp_dump_file = "inp.yaml"
    OptionsSerDes.dump_validated_yaml(options, inp_dump_file)

    try:
        gen = Generator(options)
        gen.generate_smiles()

        # AB: save options in YAML file with the same base as the main output file
        OptionsSerDes.dump_validated_yaml(options, file_name=gen.writer_handler.dfout)

        gen.dump_file()

    except Exception as e:
        logger.exception(e)
        sys.exit(2)

    os.rename(log_file, f"{gen.writer_handler.dfout}.log")
    os.rename(inp_dump_file, f"{gen.writer_handler.dfout}.inp.yaml")

if __name__ == "__main__":
    main()
