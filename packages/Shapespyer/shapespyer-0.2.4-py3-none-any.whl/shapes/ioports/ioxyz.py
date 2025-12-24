"""
.. module:: ioxyz
   :platform: Linux - tested, Windows (WSL Ubuntu) - tested
   :synopsis: general input/output functions for XYZ files (not abstracted in a class yet)

.. moduleauthor:: Dr Andrey Brukhno <andrey.brukhno[@]stfc.ac.uk>

The module contains functions: read_mol_xyz(...), write_mol_xyz(...)
to be promoted to / replaced by class xyzFile(ioFiles)
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
__version__ = "0.1.4 (Beta)"

# TODO: unify the XYZ I/O similar to how GRO I/O is done (via Class etc)

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
from shapes.basics.globals import *

logger = logging.getLogger("__main__")


def read_mol_xyz(fname: str, atms, axyz, lenscale=0.1):
    # MS: Added optional lengthscale parameter to rescale angstroms to nm
    #     (temporary measure before refactoring module along lines of shapes.ioports/iogro.py)
     
    ierr = 0
    nlines = 0
    nrems = 1
    natms = 1
    rems = []

    try:
        with open(fname, mode='r', encoding='utf-8') as finp:

            logger.info(f"Reading XYZ file '{fname}' ...")

            line = finp.readline().lstrip().rstrip()
            nlines += 1

            # the first line contains number of atoms
            # and possibly number of remarks (by my own convention)
            control = line.split()
            natms = int(control[0])

            # read the remark lines separately
            if len(control) > 1:
                nrems = int(control[1])
            for i in range(nrems):
                line = finp.readline().lstrip().rstrip()
                if not line:
                    break
                nlines += 1
                logger.debug(f"Remark {i + 1}: '{line}'")
                rems.append(line)

            # arrange for abnormal EOF handling
            if nlines == nrems + 1:

                for i in range(natms):
                    line = finp.readline().lstrip().rstrip()
                    if not line or len(line.split()) != 4:
                        break
                    latm = line.split()
                    atms.append(latm[0])
                    axyz.append([lenscale*float(latm[1]), lenscale*float(latm[2]), lenscale*float(latm[3])])
                    # axyz.append(latm[1:])
                    nlines += 1

                # arrange for abnormal EOF handling
                if nlines != nrems + natms + 1:
                    ierr = 1
                    logger.error(f"Oops! Unexpected EOF or format in '{fname}' (line "
                                 f"{nlines + 1}) - FULL STOP!!!")
                    # sys.exit(4)

            else:  # nlines != nrems+1
                ierr = 1
                logger.error(f"Oops! Unexpected EOF or empty line in '{fname}' (line "
                             f"{nlines + 1}) - FULL STOP!!!")
                # sys.exit(4)

    except (IOError, ValueError, EOFError) as err:
        logger.error(f"Oops! Could not open or read file '{fname}' - FULL STOP!!!")
        sys.exit(4)

    except:
        ierr = 2
        logger.error(f"Oops! Unknown error while reading file '{fname}' - FULL STOP!!!")
        sys.exit(4)

    finally:
        if ierr == 0:
            logger.error(f"File '{fname}' successfully read: nlines = {nlines}"
                         f" & natms = {natms}")

    return (ierr == 0)

# end of read_mol_xyz()


def write_mol_xyz(fname: str, remarks, atms, axyz, resname='MOL', resid=1, start=0, ntot=0):
    ierr = 0
    nlines = 0
    natms = 0

    # empty title => append another molecule, otherwise new file
    is_new = True
    wmode = 'w'
    if not remarks:
        is_new = False
        wmode = 'a'

    try:
        with open(fname, wmode, encoding='utf-8') as fout:

            if is_new:
                if ntot == 0: ntot = len(atms)
                logger.info(
                    f"Writing molecule {resid} {resname} into XYZ file '{fname}' ..."
                )
                if len(remarks) > 1:
                    fout.write(str(ntot) + " " + str(len(remarks)) + "\n")
                    nlines += 1
                    for i in range(len(remarks)):
                        fout.write(remarks[i] + "\n")
                        nlines += 1
                else:
                    fout.write(str(ntot) + "\n")
                    fout.write(remarks[0] + "\n")
                    nlines += 2
            else:
                logger.info(
                    f"Appending molecule {resid} {resname} to XYZ file '{fname}' ..."
                )

            for i in range(len(atms)):
                if len(atms[i]) > 4:
                    logger.warning("More than 4 characters in the atom name: "
                                   f"'{atms[i]}' -> '{atms[i][:5]}'")
                line = '{:>4}'.format(atms[i][:5]) + ''.join('{:>14.5f}{:>15.5f}{:>15.5f}'.format(*axyz[i]))
                # fout.write(line+"\n")
                lres = '{:>10}{:<5}{:>5}'.format(resid, resname, i + start + 1)
                fout.write(line + lres + "\n")
                nlines += 1
                natms += 1

    except (IOError, ValueError, EOFError) as err:
        logger.error(f"Oops! Could not open or write file '{fname}' - FULL STOP!!!")
        logger.exception(err)
        sys.exit(4)

    except Exception as e:
        ierr = 2
        logger.error(
            f"Oops! Unknown error while writing file '{fname}' - FULL STOP!!!"
        )
        logger.exception(e)
        sys.exit(4)

    finally:
        if ierr == 0:
            logger.info(f"File '{fname}' successfully written: nlines = {nlines}"
                        f" & natms = {natms} / {natms + start}")

    return (ierr == 0)

# end of write_mol_xyz()
