"""
.. module:: mendeleyev
   :platform: Linux - tested, Windows (WSL Ubuntu) - tested
   :synopsis: Mendeleyev periodic table of elements and such

.. moduleauthor:: Dr Andrey Brukhno <andrey.brukhno[@]stfc.ac.uk>

The module contains class Chemistry(object)
"""

# This software is provided under The Modified BSD-3-Clause License 
# (Consistent with Python 3 licenses).
# Refer to and abide by the Copyright detailed in LICENSE file 
# found in the root directory of the library.

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


class Chemistry(object):

    enames = dict(  Hydrogen   = dict( element='H',  valency = (1,),    mau=1.0078, r=1, c=1 ),
                    Deuterium  = dict( element='D',  valency = (1,),    mau=2.0141, r=1, c=1 ),
                    Helium     = dict( element='He', valency = (0,),    mau=4.0026, r=1, c=8 ),
                    Lithium    = dict( element='Li', valency = (1,),    mau=6.9410, r=2, c=1 ),
                    Beryllium  = dict( element='Be', valency = (2,),    mau=9.0122, r=2, c=2 ),
                    Boron      = dict( element='B',  valency = (3,),    mau=10.811, r=2, c=3 ),
                    Carbon     = dict( element='C',  valency = (4,),    mau=12.011, r=2, c=4 ),
                    Nitrogen   = dict( element='N',  valency = (-3,),   mau=14.007, r=2, c=5 ),
                    Oxygen     = dict( element='O',  valency = (-2,),   mau=15.999, r=2, c=6 ),
                    Fluorine   = dict( element='F',  valency = (-1,),   mau=18.998, r=2, c=7 ),
                    Neon       = dict( element='Ne', valency = (0,),    mau=20.180, r=2, c=8 ),
                    Sodium     = dict( element='Na', valency = (1,),    mau=22.990, r=3, c=1 ),
                    Magnesium  = dict( element='Mg', valency = (2,),    mau=24.305, r=3, c=2 ),
                    Aluminium  = dict( element='Al', valency = (3,),    mau=26.982, r=3, c=3 ),
                    Silicon    = dict( element='Si', valency = (4,),    mau=28.086, r=3, c=4 ),
                    Phosphorus = dict( element='P',  valency = (-5,-3), mau=30.974, r=3, c=5 ),
                    Sulfur     = dict( element='S',  valency = (-6,-4,-2), mau=32.065, r=3, c=6 ),
                    Chlorine   = dict( element='Cl', valency = (-1,),   mau=35.453, r=3, c=7 ),
                    Argon      = dict( element='Ar', valency = (0,),    mau=39.948, r=3, c=8 ),
                    Potassium  = dict( element='K',  valency = (1,),    mau=39.098, r=4, c=1 ),
                    Calcium    = dict( element='Ca', valency = (2,),    mau=40.078, r=4, c=2 ),
                    Scandium   = dict( element='Sc', valency = (0,),    mau=44.956, r=4, c=21 ),
                    Titanium   = dict( element='Ti', valency = (4,),    mau=47.867, r=4, c=22 ),
                    Vanadium   = dict( element='V',  valency = (5,4),   mau=50.942, r=4, c=23 ),
                    Chromium   = dict( element='Cr', valency = (2,),    mau=51.996, r=4, c=24 ),
                    Manganese  = dict( element='Mn', valency = (7,4,2), mau=54.938, r=4, c=25 ),
                    Iron       = dict( element='Fe', valency = (2,3),   mau=55.845, r=4, c=26 ),
                    Cobalt     = dict( element='Co', valency = (3,2),   mau=58.933, r=4, c=27 ),
                    Nickel     = dict( element='Ni', valency = (2,),    mau=58.693, r=4, c=28 ),
                    Copper     = dict( element='Cu', valency = (2,1),   mau=63.546, r=4, c=29 ),
                    Zinc       = dict( element='Zn', valency = (2,),    mau=65.380, r=4, c=30 ),
                    Gallium    = dict( element='Ga', valency = (3,),    mau=69.723, r=4, c=3 ),
                    Germanium  = dict( element='Ge', valency = (4,),    mau=72.640, r=4, c=4 ),
                    Arsenic    = dict( element='As', valency = (-3,),   mau=74.922, r=4, c=5 ),
                    Selenium   = dict( element='Se', valency = (-2,),   mau=78.960, r=4, c=6 ),
                    Bromine    = dict( element='Br', valency = (-1,),   mau=79.904, r=4, c=7 ),
                    Krypton    = dict( element='Kr', valency = (0,),    mau=83.798, r=4, c=8 ),
                    Silver     = dict( element='Ag', valency = (0,),    mau=107.87, r=5, c=47 ),
                    Gold       = dict( element='Au', valency = (0,),    mau=196.97, r=4, c=79 )
                    # = dict( element='', valency= 0, mau=, r=4, c=22 ),
                    # = dict( element='', valency= 0, mau=, r=4, c=22 ),
                   )

    etable = dict(  # ref for r_VdW: https://en.wikipedia.org/wiki/Van_der_Waals_radius
                    # see also: https://physlab.lums.edu.pk/images/f/f6/Franck_ref2.pdf (slightly larger rvdw's - ???)
                    H  = dict( name = 'Hydrogen',   valency = (1,),    mau=1.0078, rvdw = 1.20, r=1, c=1 ),
                    D  = dict( name = 'Deuterium',  valency = (1,),    mau=2.0141, rvdw = 1.20, r=1, c=1 ),
                    He = dict( name = 'Helium',     valency = (0,),    mau=4.0026, rvdw = 1.40, r=1, c=8 ),
                    Li = dict( name = 'Lithium',    valency = (1,),    mau=6.9410, rvdw = 1.82, r=2, c=1 ),
                    Be = dict( name = 'Beryllium',  valency = (2,),    mau=9.0122, rvdw = 1.53, r=2, c=2 ),
                    B  = dict( name = 'Boron',      valency = (3,),    mau=10.811, rvdw = 1.92, r=2, c=3 ),
                    C  = dict( name = 'Carbon',     valency = (4,),    mau=12.011, rvdw = 1.70, r=2, c=4 ),
                    N  = dict( name = 'Nitrogen',   valency =(-3,),    mau=14.007, rvdw = 1.55, r=2, c=5 ),
                    O  = dict( name = 'Oxygen',     valency =(-2,),    mau=15.999, rvdw = 1.52, r=2, c=6 ),
                    F  = dict( name = 'Fluorine',   valency =(-1,),    mau=18.998, rvdw = 1.47, r=2, c=7 ),
                    Ne = dict( name = 'Neon',       valency = (0,),    mau=20.180, rvdw = 1.54, r=2, c=8 ),
                    Na = dict( name = 'Sodium',     valency = (1,),    mau=22.990, rvdw = 2.27, r=3, c=1 ),
                    Mg = dict( name = 'Magnesium',  valency = (2,),    mau=24.305, rvdw = 1.73, r=3, c=2 ),
                    Al = dict( name = 'Aluminium',  valency = (3,),    mau=26.982, rvdw = 1.84, r=3, c=3 ),
                    Si = dict( name = 'Silicon',    valency = (4,),    mau=28.086, rvdw = 2.10, r=3, c=4 ),
                    P  = dict( name = 'Phosphorus', valency = (-5,-3), mau=30.974, rvdw = 1.80, r=3, c=5 ),
                    S  = dict( name = 'Sulfur',     valency = (-6,-4,-2), mau=32.065, rvdw = 1.80, r=3, c=6 ),
                    Cl = dict( name = 'Chlorine',   valency = (-1,),   mau=35.453, rvdw = 1.75, r=3, c=7 ),
                    Ar = dict( name = 'Argon',      valency = (0,),    mau=39.948, rvdw = 1.88, r=3, c=8 ),
                    K  = dict( name = 'Potassium',  valency = (1,),    mau=39.098, rvdw = 2.75, r=4, c=1 ),
                    Ca = dict( name = 'Calcium',    valency = (2,),    mau=40.078, rvdw = 2.31, r=4, c=2 ),
                    Sc = dict( name = 'Scandium',   valency = (0,),    mau=44.956, rvdw = 2.11, r=4, c=21 ),
                    Ti = dict( name = 'Titanium',   valency = (4,),    mau=47.867, rvdw = 2.30, r=4, c=22 ), # https://physlab.lums.edu.pk/images/f/f6/Franck_ref2.pdf
                    V  = dict( name = 'Vanadium',   valency = (5,4),   mau=50.942, rvdw = 2.16, r=4, c=23 ), # https://physlab.lums.edu.pk/images/f/f6/Franck_ref2.pdf
                    Cr = dict( name = 'Chromium',   valency = (2,),    mau=51.996, rvdw = 2.14, r=4, c=24 ), # https://physlab.lums.edu.pk/images/f/f6/Franck_ref2.pdf
                    Mn = dict( name = 'Manganese',  valency = (7,4,2), mau=54.938, rvdw = 2.15, r=4, c=25 ), # https://physlab.lums.edu.pk/images/f/f6/Franck_ref2.pdf
                    Fe = dict( name = 'Iron',       valency = (2,3),   mau=55.845, rvdw = 2.16, r=4, c=26 ), # https://physlab.lums.edu.pk/images/f/f6/Franck_ref2.pdf
                    Co = dict( name = 'Cobalt',     valency = (3,2),   mau=58.933, rvdw = 2.12, r=4, c=27 ), # https://physlab.lums.edu.pk/images/f/f6/Franck_ref2.pdf
                    Ni = dict( name = 'Nickel',     valency = (2,),    mau=58.693, rvdw = 1.63, r=4, c=28 ),
                    Cu = dict( name = 'Copper',     valency = (2,1),   mau=63.546, rvdw = 1.40, r=4, c=29 ),
                    Zn = dict( name = 'Zinc',       valency = (2,),    mau=65.380, rvdw = 1.39, r=4, c=30 ),
                    Ga = dict( name = 'Gallium',    valency = (3,),    mau=69.723, rvdw = 1.87, r=4, c=3 ),
                    Ge = dict( name = 'Germanium',  valency = (4,),    mau=72.640, rvdw = 2.11, r=4, c=4 ),
                    As = dict( name = 'Arsenic',    valency = (-3,),   mau=74.922, rvdw = 1.85, r=4, c=5 ),
                    Se = dict( name = 'Selenium',   valency = (-2,),   mau=78.960, rvdw = 1.90, r=4, c=6 ),
                    Br = dict( name = 'Bromine',    valency = (-1,),   mau=79.904, rvdw = 1.85, r=4, c=7 ),
                    Kr = dict( name = 'Krypton',    valency = (0,),    mau=83.798, rvdw = 2.02, r=4, c=8 ),
                    Ag = dict( name = 'Silver',     valency = (0,),    mau=107.87, rvdw = 1.72, r=5, c=47 ),
                    Au = dict( name = 'Gold',       valency = (0,),    mau=196.97, rvdw = 1.66, r=4, c=79 )
                    # = dict( name = '', valency= 0, mau=, rvdw = 1.0, r=4, c=22 ),
                    # = dict( name = '', valency= 0, mau=, rvdw = 1.0, r=4, c=22 ),
                   )

    ebonds = dict(  # lower-case symbols in between element names: 's'=single,'d'=double,'t'=triple etc
                      # ref: https://www.chegg.com/homework-help/questions-and-answers/table-92-average-bond-energies-kj-mol-bond-lengths-pm-bond-energy-length-bond-energy-lengt-q80336462
                    HsH   = dict( view = 'H-H',   atoms = ('H', 'H'),   rank = 1.0, dist = 0.75 ),  # H-bonds
                    HsO   = dict( view = 'H-O',   atoms = ('H', 'O'),   rank = 1.0, dist = 0.96 ),  # in water H2O
                    HsC   = dict( view = 'H-C',   atoms = ('H', 'C'),   rank = 1.0, dist = 1.09 ),
                    HsN   = dict( view = 'H-N',   atoms = ('H', 'N'),   rank = 1.0, dist = 1.01 ),
                    HsF   = dict( view = 'H-F',   atoms = ('H', 'F'),   rank = 1.0, dist = 0.92 ),
                    HsI   = dict( view = 'H-I',   atoms = ('H', 'I'),   rank = 1.0, dist = 1.61 ),
                    HsCL  = dict( view = 'H-Cl',  atoms = ('H', 'Cl'),  rank = 1.0, dist = 1.27 ),
                    HsBR  = dict( view = 'H-Br',  atoms = ('H', 'Br'),  rank = 1.0, dist = 1.41 ),
                    CsC   = dict( view = 'C-C',   atoms = ('C', 'C'),   rank = 1.0, dist = 1.54 ),  # C-bonds
                    CaC   = dict( view = 'C:C',   atoms = ('C', 'C'),   rank = 1.5, dist = 1.39 ),
                    CdC   = dict( view = 'C=C',   atoms = ('C', 'C'),   rank = 2.0, dist = 1.34 ),
                    CtC   = dict( view = 'C#C',   atoms = ('C', 'C'),   rank = 3.0, dist = 1.20 ),
                    CsH   = dict( view = 'C-H',   atoms = ('C', 'H'),   rank = 1.0, dist = 1.09 ),
                    CsP   = dict( view = 'C-P',   atoms = ('C', 'P'),   rank = 1.0, dist = 1.87 ),
                    CsS   = dict( view = 'C-S',   atoms = ('C', 'S'),   rank = 1.0, dist = 1.81 ),
                    CsF   = dict( view = 'C-F',   atoms = ('C', 'F'),   rank = 1.0, dist = 1.34 ),
                    CsI   = dict( view = 'C-I',   atoms = ('C', 'I'),   rank = 1.0, dist = 2.13 ),
                    CsCL  = dict( view = 'C-Cl',  atoms = ('C', 'Cl'),  rank = 1.0, dist = 1.77 ),
                    CsBR  = dict( view = 'C-Br',  atoms = ('C', 'Br'),  rank = 1.0, dist = 1.94 ),
                    CsSI  = dict( view = 'C-Si',  atoms = ('C', 'Si'),  rank = 1.0, dist = 1.86 ),
                    CsO   = dict( view = 'C-O',   atoms = ('C', 'O'),   rank = 1.0, dist = 1.43 ),
                    CdO   = dict( view = 'C=O',   atoms = ('C', 'O'),   rank = 2.0, dist = 1.23 ),
                    CtO   = dict( view = 'C#O',   atoms = ('C', 'O'),   rank = 3.0, dist = 1.13 ),
                    CsN   = dict( view = 'C-N',   atoms = ('C', 'N'),   rank = 1.0, dist = 1.47 ),
                    CdN   = dict( view = 'C=N',   atoms = ('C', 'N'),   rank = 2.0, dist = 1.27 ),
                    CtN   = dict( view = 'C#N',   atoms = ('C', 'N'),   rank = 3.0, dist = 1.15 ),
                    OsO   = dict( view = 'O-O',   atoms = ('O', 'O'),   rank = 1.0, dist = 1.48 ),  # O-bonds
                    OdO   = dict( view = 'O=O',   atoms = ('O', 'O'),   rank = 2.0, dist = 1.21 ),  # in oxygen O2
                    OsH   = dict( view = 'O-H',   atoms = ('O', 'H'),   rank = 1.0, dist = 0.96 ),  # in -OH
                    OsC   = dict( view = 'O-C',   atoms = ('O', 'C'),   rank = 1.0, dist = 1.43 ),
                    OdC   = dict( view = 'O=C',   atoms = ('O', 'C'),   rank = 2.0, dist = 1.23 ),
                    OtC   = dict( view = 'O#C',   atoms = ('O', 'C'),   rank = 3.0, dist = 1.13 ),
                    OsN   = dict( view = 'O-N',   atoms = ('O', 'N'),   rank = 1.0, dist = 1.44 ),
                    OdN   = dict( view = 'O=N',   atoms = ('O', 'N'),   rank = 2.0, dist = 1.20 ),
                    OtN   = dict( view = 'O#N',   atoms = ('O', 'N'),   rank = 3.0, dist = 1.06 ),
                    OsP   = dict( view = 'O-P',   atoms = ('O', 'P'),   rank = 1.0, dist = 1.60 ),
                    OdP   = dict( view = 'O=P',   atoms = ('O', 'P'),   rank = 2.0, dist = 1.50 ), # just a guess!
                    OsS   = dict( view = 'O-S',   atoms = ('O', 'S'),   rank = 1.0, dist = 1.55 ), # dist = 1.51
                    OdS   = dict( view = 'O=S',   atoms = ('O', 'S'),   rank = 2.0, dist = 1.45 ),
                    OsF   = dict( view = 'O-F',   atoms = ('O', 'F'),   rank = 1.0, dist = 1.42 ),
                    OsI   = dict( view = 'O-I',   atoms = ('O', 'I'),   rank = 1.0, dist = 1.94 ),
                    OsCL  = dict( view = 'O-Cl',  atoms = ('O', 'Cl'),  rank = 1.0, dist = 1.64 ),
                    OsBR  = dict( view = 'O-Br',  atoms = ('O', 'Br'),  rank = 1.0, dist = 1.72 ),
                    NsN   = dict( view = 'N-N',   atoms = ('N', 'N'),   rank = 1.0, dist = 1.46 ),  # N-bonds
                    NdN   = dict( view = 'N=N',   atoms = ('N', 'N'),   rank = 2.0, dist = 1.22 ),
                    NtN   = dict( view = 'N#N',   atoms = ('N', 'N'),   rank = 3.0, dist = 1.10 ),
                    NsC   = dict( view = 'N-C',   atoms = ('N', 'C'),   rank = 1.0, dist = 1.47 ),
                    NdC   = dict( view = 'N=C',   atoms = ('N', 'C'),   rank = 2.0, dist = 1.27 ),
                    NtC   = dict( view = 'N#C',   atoms = ('N', 'C'),   rank = 3.0, dist = 1.15 ),
                    NsH   = dict( view = 'N-H',   atoms = ('N', 'H'),   rank = 1.0, dist = 1.01 ),
                    NsO   = dict( view = 'N-O',   atoms = ('N', 'O'),   rank = 1.0, dist = 1.44 ),
                    NdO   = dict( view = 'N=O',   atoms = ('N', 'O'),   rank = 2.0, dist = 1.20 ),
                    NtO   = dict( view = 'N#O',   atoms = ('N', 'O'),   rank = 3.0, dist = 1.06 ),
                    NsP   = dict( view = 'N-P',   atoms = ('N', 'P'),   rank = 1.0, dist = 1.77 ),
                    NsF   = dict( view = 'N-F',   atoms = ('N', 'F'),   rank = 1.0, dist = 1.39 ),
                    NsI   = dict( view = 'N-I',   atoms = ('N', 'I'),   rank = 1.0, dist = 2.22 ),
                    NsCL  = dict( view = 'N-Cl',  atoms = ('N', 'Cl'),  rank = 1.0, dist = 1.91 ),
                    NsBR  = dict( view = 'N-Br',  atoms = ('N', 'Br'),  rank = 1.0, dist = 2.14 ),
                    PsP   = dict( view = 'P-P',   atoms = ('P', 'P'),   rank = 1.0, dist = 2.21 ),  # P-bonds
                    PsH   = dict( view = 'P-H',   atoms = ('P', 'H'),   rank = 1.0, dist = 1.42 ),
                    PsO   = dict( view = 'P-O',   atoms = ('P', 'O'),   rank = 1.0, dist = 1.60 ),
                    PdO   = dict( view = 'P=O',   atoms = ('O', 'P'),   rank = 2.0, dist = 1.50),  # just a guess!
                    PsC   = dict( view = 'P-C',   atoms = ('P', 'C'),   rank = 1.0, dist = 1.87 ),
                    PsF   = dict( view = 'P-F',   atoms = ('P', 'F'),   rank = 1.0, dist = 1.56 ),
                    PsI   = dict( view = 'P-I',   atoms = ('P', 'I'),   rank = 1.0, dist = 2.46 ),
                    PsCL  = dict( view = 'P-Cl',  atoms = ('P', 'Cl'),  rank = 1.0, dist = 2.04 ),
                    PsBR  = dict( view = 'P-Br',  atoms = ('P', 'Br'),  rank = 1.0, dist = 2.22 ),
                    PsSI  = dict( view = 'P-Si',  atoms = ('P', 'Si'),  rank = 1.0, dist = 2.27 ),
                    SsS   = dict( view = 'S-S',   atoms = ('S', 'S'),   rank = 1.0, dist = 2.04 ),  # S-bonds
                    SsH   = dict( view = 'S-H',   atoms = ('S', 'H'),   rank = 1.0, dist = 1.34 ),
                    SsO   = dict( view=  'S-O',   atoms = ('S', 'O'),   rank = 1.0, dist = 1.55),  # dist = 1.51
                    SdO   = dict( view=  'S=O',   atoms = ('S', 'O'),   rank = 2.0, dist = 1.45),
                    SsF   = dict( view = 'S-F',   atoms = ('S', 'F'),   rank = 1.0, dist = 1.58 ),
                    SsI   = dict( view = 'S-I',   atoms = ('S', 'I'),   rank = 1.0, dist = 2.34 ),
                    SsCL  = dict( view = 'S-Cl',  atoms = ('S', 'Cl'),  rank = 1.0, dist = 2.01 ),
                    SsBR  = dict( view = 'S-Br',  atoms = ('S', 'Br'),  rank = 1.0, dist = 2.25 ),
                    FsF   = dict( view = 'F-F',   atoms = ('F', 'F'),   rank = 1.0, dist = 1.43 ),  # F-bonds
                    FsI   = dict( view = 'F-I',   atoms = ('F', 'I'),   rank = 1.0, dist = 1.87 ),
                    FsCL  = dict( view = 'F-Cl',  atoms = ('F', 'Cl'),  rank = 1.0, dist = 1.66 ),
                    FsBR  = dict( view = 'F-Br',  atoms = ('F', 'Br'),  rank = 1.0, dist = 1.78 ),
                    CLsCL = dict( view = 'Cl-Cl', atoms = ('Cl', 'Cl'), rank = 1.0, dist = 1.99 ),  # Cl-bonds
                    CLsBR = dict( view = 'Cl-Br', atoms = ('Cl', 'Br'), rank = 1.0, dist = 2.14 ),
                    CLsI  = dict( view = 'Cl-I',  atoms = ('Cl', 'I'),  rank = 1.0, dist = 2.43 ),
                    SIsSI = dict( view = 'Si-Si', atoms = ('Si', 'Si'), rank = 1.0, dist = 2.34 ), # Si-bonds ...
                    SIsH  = dict( view = 'Si-H',  atoms = ('Si', 'H'),  rank = 1.0, dist = 1.48 ),
                    SIsO  = dict( view = 'Si-O',  atoms = ('Si', 'O'),  rank = 1.0, dist = 1.61 ),
                    SIsS  = dict( view = 'Si-S',  atoms = ('Si', 'S'),  rank = 1.0, dist = 2.10 ),
                    SIsF  = dict( view = 'Si-F',  atoms = ('Si', 'F'),  rank = 1.0, dist = 1.56 ),
                    SIsI  = dict( view = 'Si-I',  atoms = ('Si', 'I'),  rank = 1.0, dist = 2.40 ),
                    SIsCL = dict( view = 'Si-Cl', atoms = ('Si', 'Cl'), rank = 1.0, dist = 2.04 ),
                    SIsBR = dict( view = 'Si-Br', atoms = ('Si', 'Br'), rank = 1.0, dist = 2.16 ),
                    BRsBR = dict( view = 'Br-Br', atoms = ('Br', 'Br'), rank = 1.0, dist = 2.28 ), # Br-bonds ...
                    BRsI  = dict( view = 'Br-I',  atoms = ('Br', 'I'),  rank = 1.0, dist = 2.48 ),
                    IsI   = dict( view = 'I-I',   atoms = ('I', 'I'),   rank = 1.0, dist = 2.66 )
                    #Some  = dict( view = 'SoMe',  atoms = ('So', 'Me'), rank = 1.0, dist = 1.00 )
                   )

    btypes = dict(single=1.0, aromatic=1.5, double=2.0, triple=3.0, quadruple=4.0, nobond=0.0, sccw=1.0, scw=1.0)
    brank2char = { 1.0: ('s', '-'), 1.5: ('a', ':'), 2.0: ('d', '='), 3.0: ('t', '#'), 4.0: ('q', '$')}

    etypes = list(etable.keys())

    # coherent scattering length
    ecsl = dict(D=6.674, H=-3.741, C=6.648, N=9.360, O=5.805, P=5.130, S=2.847,
                WCG=-6.708)
    # scattering length densities
    esld = dict(D=2.823, H=-1.582, C=7.000, N=3.252, O=2.491, P=1.815, S=1.107)

    # Define atomic groups in terms of elements and their counts
    egrp = dict( PO4={"P": 1, "O": 4},
                 SO4={"S": 1, "O": 4},
                 CH3={"C": 1, "H": 3},
                 CH2={"C": 1, "H": 2},
                 C2O4={"C": 2, "O": 4},
                 C3OH5={"C": 3, "O": 1, "H": 5},
                 H2O={"O": 1, "H": 2},
                 alk={"C": 1, "H": 2},
                 gly={"C": 3, "O": 1, "H": 5},
                 water={"O": 1, "H": 2},
                 chol={"C": 5, "H": 13, "N": 1},
                 coo={"C": 2, "O": 4}
                 )

    # Valeria's definitions
    ecomp = {
        "PO4": {"P": 1, "O": 4},
        "CH3": {"C": 1, "H": 3},
        "alk": {"C": 1, "H": 2},
        "gly": {"C": 3, "O": 1, "H": 5},
        "water": {"O": 1, "H": 2},
        "chol": {"C": 5, "H": 13, "N": 1},
        "coo": {"C": 2, "O": 4}
        # Add other components as needed
    }

    def getElement(aname: str = '') -> str | None:
        """
        **Checks** if the input string `aname` corresponds to an element in the periodic table
        based on the first two letters in the atom name (see shapes.basics.mendeleyev.Chemistry)
        """
        atype = aname
        if len(atype) > 1:
            atype = atype[0:2].capitalize()
            if atype not in Chemistry.etypes:
                atype = atype[0]
        if atype in Chemistry.etypes:
            return atype
        else:
            return None
    # end of isElement()

# end of class Chemistry(object)