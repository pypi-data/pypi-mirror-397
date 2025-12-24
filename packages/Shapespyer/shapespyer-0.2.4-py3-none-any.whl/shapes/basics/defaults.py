from enum import Enum, auto


class Fill(Enum):
    """Describes the options for available patterns for filling the shape"""

    RINGS0 = auto()
    RINGS = auto()
    FIBO = auto()
    MESH = auto()

    def __str__(self) -> str:
        return self.name.lower()


class Origin(Enum):
    COG = auto()
    COM = auto()
    COB = auto()

    def __str__(self) -> str:
        return self.name.lower()

# class Origin:
#     COG = "COG"
#     COM = "COM"
#     COB = "COB"

#     def __init__(self, name: str = COG):
#         self.name = name

#     def __str__(self) -> str:
#         return self.name.lower()


class Defaults:
    class Input:
        PATH = "."
        FILE = "config_inp.gro"
        BASE = "config_inp"
        EXT = ".gro"
        BOX = None
        IS_BASE = False
        IS_CELL = False
        IS_WAVES = False

    class Output:
        PATH = "."
        FILE = None
        BASE = "config_out"
        EXT = ".gro"
        IS_BASE = True
        MUST_ADD_MOL_SUFFIXES = True
        MUST_ADD_SHAPE_SUFFIXES = True

    class Molecule:
        RESNM = "ANY"
        NAMES: list[str] = []
        MINT: list[int] = []
        MEXT: list[int] = []
        FRACS: list[list[float]] = []
        MOLIDS: list[int] = []
        MOLID = 1
        NPICK = 1

    class Shape:
        STYPE = "SMILES"
        DMIN = 0.5
        RMIN = 0.25
        LRING = 0
        TURNS = 0
        NMOLS = 0
        LAYERS: list[int | float] = [1, 1.0, 1.0]
        NSTEP = 0
        FILL = Fill.RINGS0

    class Angle:
        ALPHA = 0.0
        THETA = 0.0

    class Membrane:
        NSIDE = 10
        ZSEP = 0.0

    class Lattice:
        NLATT = [0, 0, 0]

    class Flags:
        FXZ = False
        REV = False
        ALIGNZ = False

    class Density:
        NAMES = ["NONE"]

    class Smiles:
        DBCIS: list[str] = []

    class Base:
        LDPD = 0.1
        ORIGIN = Origin.COG
        OFFSET: list[float] = []  # [0.0, 0.0, 0.0]
        SBUFF = 1.0


VALIDATED_OPTIONS_FILE_NAME = "input-dump.yaml"


class SerDesKeys:
    INPUT = "input"

    class Input:
        PATH = "path"
        FILE = "file"
        BASE = "base"
        EXT = "ext"
        BOX = "box"
        IS_BASE = "isbase"

    OUTPUT = "output"

    class Output:
        PATH = "path"
        FILE = "file"
        BASE = "base"
        EXT = "ext"

    MOLECULE = "molecule"

    class Molecule:
        RESNM = "resnm"
        RESNAMES = "resnames"
        MINT = "mint"
        MEXT = "mext"
        FRACS = "fracs"
        MOLIDS = "molids"
        MOLID = "molid"

    SHAPE = "shape"

    class Shape:
        STYPE = "stype"
        DMIN = "dmin"
        RMIN = "rmin"
        LRING = "lring"
        TURNS = "turns"
        NMOLS = "nmols"
        LAYERS = "layers"
        FILL = "fill"

    ANGLE = "angle"

    class Angle:
        ALPHA = "alpha"
        THETA = "theta"

    MEMBRANE = "membrane"

    class Membrane:
        NSIDE = "nside"
        ZSEP = "zsep"

    LATTICE = "lattice"

    class Lattice:
        NLATT = "nlatt"

    FLAGS = "flags"

    class Flags:
        FXZ = "fxz"
        REV = "rev"
        PIN = "pin"
        WAV = "wav"
        ALIGNZ = "alignz"
        SMILES = "smiles"
        INPBOX = "inpbox"
        RANDOM = "random"

    SMILES = "smiles"

    class Smiles:
        DBCIS = "dbcis"

    DENSITY = "density"

    class Density:
        NAMES = "names"

    BASE = "base"

    class Base:
        LDPD = "ldpd"
        SBUFF = "sbuff"
        ORIGIN = "origin"
        OFFSET = "offset"


SXYZ = ".xyz"
SPDB = ".pdb"
SDLP = ".dlp"
SDLM = ".dlm"
SGRO = ".gro"
SSML = ".sml"

INPUT_EXTENSIONS = [
    SXYZ,
    SPDB,
    SDLP,
    SDLM,
    SGRO,
    SSML,
]  # , spdb, sdpd]  # supported file extensions so far
OUTPUT_EXTENSIONS = [SXYZ, SPDB, SDLP, SDLM, SGRO]
STRUCTURE_EXTENSIONS = [SXYZ, SPDB, SDLP, SDLM, SGRO]

# AB: default surface XYZ file
FWAV = "config_wav.xyz"
CONFIG_BASE = "CONFIG"
FIELD_BASE = "FIELD"

# AB: default GROMACS INPUT / OUTPUT
# finp = 'config_inp.gro'
# fout = 'config_out.gro'
# fsml = 'smiles.sml'

# AB: default DL_POLY INPUT / OUTPUT
# fcfg = 'CONFIG'
# fhst = 'HISTORY'
# ftrj = 'TRAJOUT'

NL_INDENT = "\n    "