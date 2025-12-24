"""
.. module:: help
   :platform: Linux - tested, Windows (WSL Ubuntu) - tested
   :synopsis: global helper variables and such, not suited for abstraction into any class (yet?)

.. moduleauthor:: Dr Andrey Brukhno <andrey.brukhno[@]stfc.ac.uk>

The module contains classes: beauty & help
"""

##################################################
#                                                #
#  Shapespyer - soft matter structure generator  #
#                                                #
#  Author: Dr Andrey Brukhno (c) 2020 - 2025     #
#          Daresbury Laboratory, SCD, STFC/UKRI  #
#                                                #
##################################################

# This software is provided under The Modified BSD-3-Clause License 
# (Consistent with Python 3 licenses).
# Refer to and abide by the Copyright detailed in LICENSE file found 
# in the root directory of the library.

# The origin of this software must not be misrepresented. If you redistribute or
# alter and redistribute the source code in any practically usable form, you must
# not claim that you wrote the original software. If you use this software in
# a product, an acknowledgment in the product documentation would be appreciated
# but is not required. Altered source versions must be plainly marked as such,
# and must not be misrepresented as being the original software.

##from __future__ import absolute_import
__author__ = "Andrey Brukhno"

class beauty:
    END     = '\033[0m' # STOP BEAUTIFYING
    BOLD    = '\033[1m' # BOLD
    NORMAL  = '\033[2m' # NORMAL
    ITALIC  = '\033[3m' # ITALIC
    ULINE   = '\033[4m' # UNDERLINE
    FLASH   = '\033[5m' # FLASHING
    COL6    = '\033[6m' # DULL
    INVERT  = '\033[7m' # INVERTED
    HIDDEN  = '\033[8m' # HIDDEN TEXT
    STRIKE  = '\033[9m' # STRIKE-THROUGH
    DULINE  = '\033[21m' # DOUBLE UNDERLINE
    DRED    = '\033[31m' # DEEP RED
    DGREEN  = '\033[32m' # DEEP GREEN
    DORANGE = '\033[33m' # DEEP ORANGE
    DBLUE   = '\033[34m' # DEEP BLUE
    DPURPLE = '\033[35m' # DEEP PURPLE
    DCYAN   = '\033[36m' # DEEP CYAN
    GRAY    = '\033[37m' # JUST GRAY
    BBLACK  = '\033[40m' # BACKGROUND BLACK
    BDRED    = '\033[41m' # BACKGROUND DEEP RED
    BDGREEN  = '\033[42m' # BACKGROUND DEEP GREEN
    BDORANGE = '\033[43m' # BACKGROUND DEEP ORANGE
    BDBLUE   = '\033[44m' # BACKGROUND DEEP BLUE
    BDPURPLE = '\033[45m' # BACKGROUND DEEP PURPLE
    BDCYAN   = '\033[46m' # BACKGROUND DEEP CYAN
    BGRAY   = '\033[47m' # BACKGROUND JUST GRAY
    OLINE   = '\033[53m' # OVERLINE
    DGRAY   = '\033[90m' # DEEP GRAY
    RED     = '\033[91m' # PURE RED
    GREEN   = '\033[92m' # PURE GREEN
    YELLOW  = '\033[93m' # PURE YELLOW
    BLUE    = '\033[94m' # PORE BLUE
    PURPLE  = '\033[95m' # PURE PURPLE
    CYAN    = '\033[96m' # PURE CYAN
    WHITE   = '\033[97m' # DEEP GRAY

    def check(self):
        print(self.ULINE + "                          " +self.END)
        print(self.BOLD +self.ITALIC + "* CHECK OUT THE BEAUTIES *" +self.END)
        print(self.OLINE + "                          " +self.END)
        print(self.BOLD + "beauty 1 - BOLD" +self.END)
        print(self.NORMAL + "beauty 2 - NORMAL" +self.END)
        print(self.ITALIC + "beauty 3 - ITALIC" +self.END)
        print(self.ULINE + "beauty 4 - UNDERLINE" +self.END)
        print(self.FLASH + "beauty 5 - FLASHING" +self.END)
        #print(self.COL6 + "beauty 6 - dull" +self.END)
        print(self.INVERT + "beauty 7 - INVERTED" +self.END)
        print(self.HIDDEN + "beauty 8 - HIDDEN" +self.END + '  (HIDDEN - beauty 8)')
        print(self.STRIKE + "beauty 9 - STRIKE-THROUGH" +self.END)
        print(self.DULINE + "beauty 21 - DOUBLE UNDERLINE" +self.END)
        #print("\nbeauties [22...29] - dull\n")
        print(self.DRED + "beauty 31 - DEEP RED" +self.END)
        print(self.DGREEN + "beauty 32 - DEEP GREEN" +self.END)
        print(self.DORANGE + "beauty 33 - DEEP ORANGE" +self.END)
        print(self.DBLUE + "beauty 34 - DEEP BLUE" +self.END)
        print(self.DPURPLE + "beauty 35 - DEEP PURPLE" +self.END)
        print(self.DCYAN + "beauty 36 - DEEP CYAN" +self.END)
        print(self.GRAY + "beauty 37 - JUST GRAY" +self.END)
        #print("\nbeauties [38,39] - dull\n")
        print(self.BBLACK + "beauty 40 - REDUCTED" +self.END + " (BACKGROUND BLACK - beauty 40)")
        print(self.BDRED + "beauty 41 - BACKGROUND DEEP RED" +self.END)
        print(self.BDGREEN + "beauty 42 - BACKGROUND DEEP GREEN" +self.END)
        print(self.BDORANGE + "beauty 43 - BACKGROUND DEEP ORANGE" +self.END)
        print(self.BDBLUE + "beauty 44 - BACKGROUND DEEP BLUE" +self.END)
        print(self.BDPURPLE + "beauty 45 - BACKGROUND DEEP PURPLE" +self.END)
        print(self.BDCYAN + "beauty 46 - BACKGROUND DEEP CYAN" +self.END)
        print(self.BGRAY + "beauty 47 - BACKGROUND JUST GRAY" +self.END)
        #print("\nbeauties [48...52] - dull\n")
        print(self.OLINE + "beauty 53 - OVERLINE" +self.END)
        #print("\nbeauties [54...89] - dull\n")
        print(self.DGRAY + "beauty 90 - DEEP GRAY" +self.END)
        print(self.RED + "beauty 91 - PURE RED" +self.END)
        print(self.GREEN + "beauty 92 - PURE GREEN" +self.END)
        print(self.YELLOW + "beauty 93 - PURE ORANGE" +self.END)
        print(self.BLUE + "beauty 94 - PURE BLUE" +self.END)
        print(self.PURPLE + "beauty 95 - PURE PURPLE" +self.END)
        print(self.CYAN + "beauty 96 - PURE CYAN" +self.END)
        print(self.WHITE + "beauty 97 - PURE WHITE" +self.BBLACK + " (PURE WHITE - beauty 97)" +self.END)
        print(self.ULINE + "                         " +self.END)
        print(self.BOLD +self.ITALIC + "* NO MORE BEAUTIES HERE * " +self.END)
        print(self.OLINE + "                         " +self.END)


class help:
    opt_help   = "-h          | --help            : "
    HELP       = "show this help message and exit"
    opt_yaml   = "-y          | --yaml            : "
    YAML       = "use a .yaml file to configure options"
    opt_gopt   = "-g          | --gopt            : "
    GETOPT     = "use 'getopt' for parsing the script arguments (parameters); if not present, use 'argparser'"
    # IO
    opt_dir    = "-d <IODIR>  | --dio=<IODIR>     : "
    DIRIO      = "directory or list of (two) directories for input/output files {'.'*}; example: 'input,output'"
    opt_boxi   = "-b <IBOX>   | --box=<IBOX>      : "
    BOXINP     = "input file specifying box dimensions (3 values) or cell matrix (9 values) {shape.box*/<name>.box}"
    opt_finp   = "-i <IFILE>  | --inp=<IFILE>     : "
    FINAME     = "input configuration file containing molecule(s) coordinates {config_inp.gro*/<name>.gro/<name>.xyz/CONFIG(*)/FIELD(*)}"
    opt_fout   = "-o <ONAME>  | --out=<ONAME>     : "
    FONAME     = "base name of the output configuration file without extension {config_out*}"
    opt_xout   = "-x <OEXT>   | --xout=<OEXT>     : "
    FOEXT      = "output configuration file extension {.gro*/.xyz/.pdb/.dlp/.dlm}; .dlp/.dlm not used in filename"
    # parameters
    # shapes = ['ring', 'rod', 'ball', 'ves', 'lat', 'lat2', 'lat3']
    opt_shape  = "    n/a     | --shape=<SHAPE>   : "
    SHAPE      = "DEPRECATED. Use --stype instead. geometrical shape to create {ring*/rod/ball/ves/lat/lat2/lat3/smiles/dens}"
    opt_stype  = "-s <STYPE>  | --stype=<STYPE>   : "
    STYPE      = "geometrical shape to create {ring*/rod/ball/ves/lat/lat2/lat3/smiles/dens}"
    opt_fill   = "-f <FILL>   | --fill=<FILL>     : "
    FILL       = "type of molecules' placement for filling in the shape {rings*/area/fibo/mesh}"
    opt_npick  = "-p <NPICK>  | --npick=<NPICK>   : "
    NPICK      = "number of molecules to pick up from input {1*}"
    opt_lring  = "-l <LRING>  | --lring=<LRING>   : "
    LRING      = "number of molecules in the largest ring within the output structure (>9) {0*}"
    opt_nmols  = "-n <NMOLS>  | --nmols=<NMOLS>   : "
    NMOLS      = "number of molecules in the (inner) ball for 'ball' or 'ves' structures (>9) {0*}"
    opt_molids = "-m <MOLIDS> | --molids=<MOLIDS> : "
    MOLIDS     = "list of molecule (residue) indices to pick up from input {1*}; example: '1,3'"
    opt_rnames = "--rnames=<RNAMES> : "
    RNAMES     = "DEPRECATED. Use --resnames instead. list of residue (molecule) names to pick up from input {ANY*}; example: 'SDS,CTAB'"
    opt_resnames = "-r <RESNAMES> | --resnames=<RESNAMES> : "
    RESNAMES     = "list of residue (molecule) names to pick up from input {ANY*}; example: 'SDS,CTAB'"
    opt_turns  = "-t <TURNS>  | --turns=<TURNS>   : "
    TURNS      = "number of full turns in a 'rod', i.e. stack of rings, or a band spiral (>0) {0*}"
    opt_dnames = "    n/a     | --dnames=<DNAMES> : "
    DNAMES     = "list of density names to calculate {NONE*} (using '--shape=dens'); example: '[CH2,C,H,O]'"
    opt_layers = "    n/a     | --layers=<LAYERS> : "
    LAYERS     = "number of (mono-)layers in the output 'ves' structure and scaling factors for dmin and layer radii {1*}"
    opt_nside  = "    n/a     | --nside=NSIDE>    : "
    NSIDE      = "number of molecules on the side of a bilayer"
    opt_zsep   = "    n/a     | --zsep=<ZSEP>     : "
    ZSEP       = "xy distance between molecules in a bilayer"
    opt_origin = "    n/a     | --origin=<ORIGIN> : "
    ORIGIN     = "either COG, COM or COB (center of bounding box) is placed at the origin {'cog'*,'com','cob'}"
    opt_offset = "    n/a     | --offset=<OFFSET> : "
    OFFSET     = "offset (shift) for the structure's origin {[0,0,0]*}"
    opt_alpha  = "    n/a     | --alpha=<ALPHA>   : "
    ALPHA      = "initial azimuth angle (in XY plane), for molecules on the 'equator' ring (0,...,360) {0.0* degrees}"
    opt_theta  = "    n/a     | --theta=<THETA>   : "
    THETA      = "initial altitude angle (w.r.t. OZ axis), for molecules on the 'equator' ring (0,...,180) {0.0* degrees}"
    opt_cavr   = "-c <CAVR>   | --cavr=<CAVR>     : "
    CAVR       = "DEPRECATED. Use --rmin instead. radius of internal cavity in the centre of the generated structure {0.25* nm}"
    opt_rmin   = "    n/a     | --rmin=<RMIN>     : "
    RMIN       = "radius of internal cavity in the centre of the generated structure {0.25* nm}"
    opt_sbuff  = "    n/a     | --sbuff=<SBUFF>   : "
    SBUFF      = "solvation buffer size around the generated structure {1.0* nm}"
    opt_dmin   = "    n/a     | --dmin=<DMIN>     : "
    DMIN       = "minimum distance between 'bone' atoms in the generated structure {0.5 * nm}"
    opt_ldpd   = "    n/a     | --linp=<LINP>     : "
    LDPD         = "DPD length scale of input/output configuration files in nm {0.1 nm}; only needed for DL_MESO"
    opt_mint   = "    n/a     | --mint=<MINT>     : "
    MINT       = "'interior' atom indices (one per input species), closer to the centre {1*}; example: '41,40'"
    opt_mext   = "    n/a     | --mext=<MEXT>     : "
    MEXT       = "'exterior' atom indices (one per input species), farther from the centre {2*}; example: '0,16'"
    opt_frc    = "    n/a     | --frc=<FRC>       : "
    FRC        = "DEPRECATED (use --fracs instead) average fractions of the compounds in the structure; example: [0.4,0.6]"
    opt_fracs    = "    n/a     | --fracs=<FRACS>       : "
    FRACS        = "average fractions of the compounds in the structure; example: [0.4,0.6]"
    opt_nlat   = "    n/a     | --nl=<NL>         : "
    NL         = "3D lattice number or a list of 3 numbers, i.e. number of nodes in each dimension on a cubic 3D lattice {1*}"
    opt_nlatx  = "    n/a     | --nx=<NX>         : "
    NX         = "DEPRECATED. Use --nl instead. lattice number in X, i.e. number of nodes in X dimension on a rectangular 3D lattice {1*}"
    opt_nlaty  = "    n/a     | --ny=<NY>         : "
    NY         = "DEPRECATED. Use --nl instead. lattice number in Y, i.e. number of nodes in Y dimension on a rectangular 3D lattice {1*}"
    opt_nlatz  = "    n/a     | --nz=<NZ>         : "
    NZ         = "DEPRECATED. Use --nl instead. lattice number in Z, i.e. number of nodes in Z dimension on a rectangular 3D lattice {1*}"
    opt_rev    = "    n/a     | --rev             : "
    REVERSE    = "reverse 'internal' <-> 'external' atom indexing in each of the picked-up molecules"
    opt_fxz    = "    n/a     | --fxz             : "
    FLATTEN    = "use 'XZ-flattened' initial molecule orientation to minimise its 'spread' along Y axis"
    opt_alignz = "    n/a     | --alignz          : "
    ALIGNZ     = "align initial molecule configuration along Z axis (only valid with 'smiles' input)"
    opt_verb   = "-v          | --verbose         : "
    VERBOSE    = "switch to verbose output with additional info"
    opt_dbkinks = "    n/a     | --dbkinks        : "
    DBKINKS = "double bond 'kinks' for atoms"
    opt_cis = "    n/a     | --cis        : "
    CIS = "double bond 'kinks' for atoms"

    def show(self, script = "shape"):
        tb = beauty()
        self.header()
        print("usage: " + tb.BOLD + script + " -i <IFILE> -o <ONAME> -s <SHAPE> [options]\n" + tb.END)
        print("============")
        print(tb.ITALIC + " options :" + tb.END)
        print("------------")
        print(self.opt_help + self.HELP)
        print(self.opt_yaml + self.YAML)
        print(self.opt_gopt + self.GETOPT)
        print(self.opt_verb + self.VERBOSE)
        print(self.opt_dir + self.DIRIO)
        print(self.opt_boxi + self.BOXINP)
        print(self.opt_finp + self.FINAME)
        print(self.opt_ldpd + self.LDPD)
        print(self.opt_fout + self.FONAME)
        print(self.opt_xout + self.FOEXT)
        print(self.opt_stype + self.STYPE)
        print(self.opt_fill + self.FILL)
        print(self.opt_resnames + self.RESNAMES)
        print(self.opt_molids + self.MOLIDS)
        print(self.opt_rmin + self.RMIN)
        print(self.opt_nmols + self.NMOLS)
        print(self.opt_lring + self.LRING)
        print(self.opt_turns + self.TURNS)
        print(self.opt_dnames + self.DNAMES)
        print(self.opt_layers + self.LAYERS)
        print(self.opt_nside + self.NSIDE)
        print(self.opt_origin + self.ORIGIN)
        print(self.opt_offset + self.OFFSET)
        print(self.opt_alpha + self.ALPHA)
        print(self.opt_theta + self.THETA)
        print(self.opt_sbuff + self.SBUFF)
        print(self.opt_dmin + self.DMIN)
        print(self.opt_mint + self.MINT)
        print(self.opt_mext + self.MEXT)
        print(self.opt_fracs + self.FRACS)
        print(self.opt_nlat + self.NL)
        print(self.opt_nlatx + self.NX)
        print(self.opt_nlaty + self.NY)
        print(self.opt_nlatz + self.NZ)
        print(self.opt_rev + self.REVERSE)
        print(self.opt_fxz + self.FLATTEN)
        print(self.opt_alignz + self.ALIGNZ)
        print("============\n")

    def disclaimer(self):
        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")
        print(">                                                               <")
        print(">  This software is provided under the BSD-3-Clause License     <")
        print(">  consistent with Python 3 licensing conventions.              <")
        print(">                                                               <")
        print(">  For details, refer to the licensing terms set out in         <")
        print(">  file LICENSE found in the root directory of the package.     <")
        print(">                                                               <")
        print(">    Thank you for your interest!                               <")
        print(">    Hope you find the Shapespyer package useful.               <")
        print(">                                                               <")
        print(">    Author: Dr Andrey Brukhno (c) 2020 - 2025                  <")
        print(">            Daresbury Laboratory, SCD, STFC/UKRI               <")
        print(">                                                               <")
        print(">    Contrib: Dr Michael Seaton (c) 2024 - 2025                 <")
        print(">            Daresbury Laboratory, SCD, STFC/UKRI               <")
        print(">                                                               <")
        print(">    Contrib: Dr Valeria Losasso (c) 2024 - 2025                <")
        print(">            Daresbury Laboratory, SCD, STFC/UKRI               <")
        print(">                                                               <")
        print(">    Contrib: MSci Mariam Demir (c) Sept 2023 - Feb 2024        <")
        print(">            Daresbury Laboratory, SCD, STFC/UKRI               <")
        print(">                                                               <")
        print(">    Contrib: BSci Saul Beck (c) Sept 2024 - Feb 2025           <")
        print(">            Daresbury Laboratory, SCD, STFC/UKRI               <")
        print(">                                                               <")
        print(">    Contrib: Dr Ales Kutsepau (c) 2025                         <")
        print(">            Technical Univeristy of Denmark, ESS               <")
        print(">                                                               <")
        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<\n")

    def header(self, script = "shape"):
        tb = beauty()
        print("============")
        print(tb.ITALIC + " Notation :")
        print("------------")
        print("[option]    - an optional command-line parameter (excluding [] brackets if any)")
        print("<VALUE>     - a value to be provided by the user (excluding <> brackets if any)")
        print("{VAL1/VAL2} - a set of alternatives, i.e. mutually exclusive values")
        print("{VALUE(*)}  - an alternative value that can optionally be extended")
        print("VAL1?/VAL2? - values that are planned to be added (i.e. not supported yet)")
        print("{VALUE*}    - the default value in the absence of an option in the user input")
        print("{*}         - no default value assumed")
        print("============")
        print(tb.END)

    def header_long(self, script = "shape"):
        self.disclaimer()
        self.header(script)
