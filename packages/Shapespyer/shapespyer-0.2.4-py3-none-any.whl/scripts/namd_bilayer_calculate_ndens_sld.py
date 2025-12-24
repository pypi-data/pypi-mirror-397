#!/usr/bin/env python3
"""
The script calculates the number densities and scattering length densities (SLD) for every atom found in the input
topology file (.psf), by averaging over the input trajectory file (.dcd).

Usage:
  namd-bilayer-calculate-ndens-sld -r <ref_file> -d <dcd_file> [-t <top_file>] [-b <z_bin_size>] [-s <file>] [-o <DIR>] [--sld]
  namd-bilayer-calculate-ndens-sld (-h | --help)

Options:
  -h --help                Show this help page
  -r <ref_file>            Reference configuration file (.gro/.pdb)
  -d <dcd_file>            Input trajectory file (.dcd)
  -t <top_file>            Input topology file (.psf)
  -b <z_bin_size>          The bin size along OZ axis (Angstrom)
  -s <evolution.dat>       Save evolution for the cell to a file (cell_evolution.dat)
  -o DIR --outdir DIR      Output directory for NDENS & SLD files [default: ND_SLD].
  --sld                    Calculate scattering length densities. 
"""

# This software is provided under The Modified BSD-3-Clause License (Consistent with Python 3 licenses).
# Refer to and abide by the Copyright detailed in LICENSE file found in the root directory of the library!

##################################################
#                                                #
#  Shapespyer - soft matter structure generator  #
#                                                #
#  Author: Dr Andrey Brukhno (c) 2020 - 2025     #
#          Daresbury Laboratory, SCD, STFC/UKRI  #
#  Contrib: Dr Valeria Losasso (c) 2024 - 2025   #
#          BSc Saul Beck (c) Sep 2024 - Feb 2025 #
#                                                #
##################################################

##from __future__ import absolute_import
__author__ = "Andrey Brukhno"
__version__ = "0.2.3 (Beta)"

import os, os.path
import logging

import numpy as np
from pathlib import Path
from collections import defaultdict

# from shapes.ioports.iogro import groFile
# from shapes.ioports.iopdb import pdbFile
from shapes.basics.globals import TINY
from shapes.basics.functions import pbc_dim #, nint
from shapes.basics.utils import LogConfiguration
from shapes.stage.protovector import Vec3
from shapes.ioports.iotop import ITPTopology, PSFTopology
from shapes.ioports.ioframe import Frame
from shapes.ioports.iotraj import DCDTrajectory
from docopt import docopt

# AB: The following import only works upon installing Shapespyer:
# pip3 install $PATH_TO_shapespyer
from shapes.basics.functions import timing
from shapes.basics.mendeleyev import Chemistry

logger = logging.getLogger("__main__")

class NumberDensityCalculator:
    """
    A class to calculate number densities for atoms along the z-axis of
    a simulation box. This class reads a DCD trajectory and topology file,
    and calculates the number of atoms per bin in the z-dimension,
    normalised by the volume of each slice.
    """
    
    def __init__(self,
                 ref_file: str = None,
                 dcd_file: str | DCDTrajectory = None,
                 top_file: str | PSFTopology | ITPTopology = None,
                 bin_size=0.5):
        """
        Initialise a NumberDensityCalculator object.

        In order to assign residue and atom names to the coordinates
        read from a DCD file, one needs to provide a reference configuration
        file

        :param ref_file: A reference configuration file name (*.gro or *.pdb).
        :param dcd_traj: A DCDTrajectory file name or object (from ioports/iotraj.py script).
        :param topology: A Topology file name or object (containing atom and residue details).
        :param bin_size: Size of each bin in the z-direction (default is 0.5 Angstroms).
        """

        self.dcd_traj = None  # Trajectory file
        if isinstance(dcd_file, DCDTrajectory):
            self.dcd_traj = dcd_file
        elif isinstance(dcd_file, str):
            if not isinstance(ref_file, str):
                raise IOError(f"Incorrect input for reference (GRO or PDB) file: "
                              f"{dcd_file}")
            if dcd_file.endswith('.dcd'):
                self.dcd_traj = DCDTrajectory.from_file(dcd_file, ref_file, 'r')
        else:
            raise IOError(f"Unrecognised trajectory (DCD) file: {dcd_file}")

        self.ref_topology = None  # Topology file
        if isinstance(top_file, str):
            if top_file.endswith('.itp'):
                self.ref_topology = ITPTopology.from_file(top_file)
            elif top_file.endswith('.psf'):
                self.ref_topology = PSFTopology.from_file(top_file)
            else:
                raise IOError(f"Unrecognised topology (PSF or ITP) file: {top_file}")
        elif top_file:
            self.ref_topology = top_file

        # AB: top_file is optional
        # if self.ref_topology is None :
        #     raise IOError(f"Incorrect input for topology (PSF or ITP) file: {top_file}")

        self.is_symmetric = bin_size < -TINY
        self.bin_size = abs(bin_size)  # Size of each bin along z-axis for density calculations
        self.atom_residue_pairs = []  # List to store (residue_name, atom_name) pairs from the topology
        self.z_lengths = []  # List to store z-dimension lengths from each frame in the trajectory
        self.densities = {}  # Dictionary to store density data for each atom-residue pair
        self.atom_residue_pairs = None # self.get_atom_residue_pairs()
        # self.atom_residue_pairs = self.parse_topology_psf()  # Parse topology to get atom-residue pairs
        # self.calculate_number_densities()  # Calculate the number densities for the trajectory

    @timing
    def get_atom_residue_pairs(self):
        atom_residue_pairs = []
        if self.ref_topology:
            for atom in self.ref_topology.atoms:
                atom_residue_pairs.append((atom['residue']['name'], atom['name']))
            logger.info(f"(Residue, Atom) pairs = {atom_residue_pairs} from topology.")
        else:
            for molset in self.dcd_traj.molsys.items:
                for atom in molset[0]:
                    atom_residue_pairs.append((molset[0].name, atom.name))
            logger.info(f"(Residue, Atom) pairs = {atom_residue_pairs} from configiration.")
        return atom_residue_pairs

    @timing
    def parse_topology_psf(self):
        """
        Parse the topology file to extract atom-residue pairs.
        
        :return: A list of (residue_name, atom_name) tuples.
        """
        atom_residue_pairs = []
        with open(self.ref_topology, 'r') as f:
            in_atom_section = False  # Flag to indicate if the parser is in the atom section of the topology file
            for line in f:
                if "!NATOM" in line:
                    in_atom_section = True  # Start reading atom section
                    continue
                if "!NBOND" in line:
                    in_atom_section = False  # End reading atom section
                    break
                if in_atom_section:
                    fields = line.split()
                    if len(fields) > 4:  # Ensure that we are parsing valid lines
                        atom_name = fields[4]  # Atom name is in the 5th column
                        residue_name = fields[3]  # Residue name is in the 4th column
                        atom_residue_pairs.append((residue_name, atom_name))  # Append the atom-residue pair
        return atom_residue_pairs
    # end of parse_topology()

    @timing
    def calculate_number_densities(self):
        """
        Calculate the number densities of atoms along the z-axis for each frame in the DCD trajectory.
        This function bins atom positions in the z-dimension and normalises the counts by the volume of the bin slice.
        """
        num_atoms = self.dcd_traj.number_of_atoms
        logger.info(f"Number of species in dcd file = {len(self.dcd_traj.molsys.items)}")
        logger.info(f"Number of atoms in dcd file = {num_atoms}")

        areas, zdims = zip(*[(frame.cell_params.a * frame.cell_params.b,
                              frame.cell_params.c) for frame in self.dcd_traj.frames])
        # Total number of bins based on z_max and bin_size
        z_min = min(zdims)
        z_max = max(zdims)
        num_bins = int(z_max / self.bin_size)

        # # AB: make it even
        # if num_bins & 1:  # % 2 > 0:
        #     num_bins += 1
        # # AB: correct the bin size
        # # AB: to make it consistent with how the output is arranged (see below)
        # self.bin_size = z_max / float(num_bins)

        # AB: another way of making it consistent is to correct z_max
        if num_bins & 1:  # % 2 > 0:
            num_bins += 1
        z_max = self.bin_size * float(num_bins) # produce nice output!
        z_mid = z_max * 0.5

        self.z_lengths = zdims
        self.total_bins = num_bins
        logger.info(f"Total number of bins = {num_bins} of {self.bin_size} (A) "
              f"in Z-max range [-{z_mid}, {z_mid}], z_min/max = {z_min} / {z_max}")

        self.atom_residue_pairs = self.get_atom_residue_pairs()

        # Iterate over each frame in the DCD trajectory
        for frame in self.dcd_traj.frames:
            cbox = Vec3(*frame.cell_params.dims()) # Vec3((a, b, c)
            area = cbox[0] * cbox[1]
            zdim = cbox[2]
            binc = 1.0/(area * self.bin_size)

            # Create a zero-initialised density array for each atom-residue pair
            frame_densities = {pair: np.zeros(num_bins) for pair in self.atom_residue_pairs}
            resnames = set([ pair[0] for pair in self.atom_residue_pairs ])

            # AB: NOTE: When using frame.coordinates, we need to make sure that
            # AB: all Z-coordinates are positive (i.e. centered at half the Z-dim).
            # AB: For z-density calculation it is important NOT TO reconstruct
            # AB: (PBC unwrap) molecules, i.e. keep all atoms the primary box,
            # AB: so using frame.coordinates below, and then no need to update_molsys().

            # AB: Only need Z-coordiantes
            # z_min, z_max, z_dim = Frame.min_max_zdim(frame.coordinates)
            zcoords = [ fcrd[2] for fcrd in frame.coordinates ]
            zmin = min(zcoords)
            zmax = max(zcoords)
            zmid = z_mid
            hdim = zdim * 0.5
            if zmax - zmin - zdim > TINY:
                # AB: Found atoms outside the primary box (molecule-wise PBC?)
                # AB: So need to apply PBC atom-wise but before doing that
                # AB: need to make sure the box in centered at the origin
                zorg = 0.0
                if zmax > 1.5*hdim:
                    zorg = hdim
                logger.info(f"Max - Min Z-coords => Z-dim : {zmax} - {zmin} "
                            f"=> {zmax - zmin} (of {len(zcoords)} atoms)")
                npbc = 0
                ncrd = 0
                for icrd in range(len(zcoords)):
                    zcrd = zcoords[icrd] - zorg
                    zcrd = pbc_dim(zcrd, zdim)
                    if abs(zcrd + zorg - zcoords[icrd]) > TINY:
                        npbc += 1
                    zcoords[icrd] = zcrd
                    ncrd += 1
                logger.info(f"Number of atoms put back: "
                      f"{npbc} / {ncrd} atoms")
                # zmin = min(zcoords)
                # zmax = max(zcoords)
            # AB: make sure the box in centered at the origin
            # AB: if an outsider is found further away from the box center
            # AB: than 0.75 one of the box dimensions
            elif zmax > 1.5*hdim:
                zmid = z_mid - hdim

            zmin = min(zcoords)
            zmax = max(zcoords)
            logger.info(f"Max - Min Z-coords => Z-dim : {zmax} - {zmin} "
                        f"=> {zmax-zmin}, zmid = {zmid} (updated)")

            # AB: is_MolPBC=True puts whole molecules back into the primary cell
            # but here we are not after this (and it's costly)!
            # molsys = self.dcd_traj.update_molsys(frame) #, is_MolPBC=True)

            aidx = 0
            # for molset in molsys.items:
            for molset in self.dcd_traj.molsys.items:
                residue_name = molset[0].name
                if residue_name not in resnames:
                    aidx += len(molset[0])*len(molset[0][0])
                    continue
                for mol in molset:
                    for atom in mol:
                        # AB: NOTE that self._molsys is always centered at the origin.
                        # AB: get Z-coordinate with a shift, so it is positive!
                        # z_atom = atom.getRvec()[2] + z_mid

                        # AB: it's more tricky to deal with bare coordiantes!
                        # z_atom = frame.coordinates[aidx, 2] + z_mid
                        z_atom = zcoords[aidx] + zmid

                        # AB: this only works if all coordinates are positive!
                        bin = int(z_atom / self.bin_size)
                        if bin < num_bins:
                            frame_densities[(residue_name, atom.name)][bin] += binc
                        else:
                            logger.info(f"Z-coord ({atom.name}) = {z_atom} >? {z_max} => bin = {bin}")
                        aidx += 1

            # AB: This adds noticeable overhead! So doing it in-place above...
            # Normalise the bin counts by the volume of the slice
            # for pair, density in frame_densities.items():
            #     for i in range(num_bins):
            #         volume_of_slice = area * self.bin_size  # Volume of each bin slice
            #         if volume_of_slice > 0:  # Avoid division by zero
            #             frame_densities[pair][i] /= volume_of_slice

            # Store the densities for this frame
            for pair, density in frame_densities.items():
                if pair not in self.densities:
                    self.densities[pair] = []  # Initialise if not present
                self.densities[pair].append(density)

    # end of calculate_number_densities()

    @timing
    def save_results(self, out_dir):
        """
        Save the averaged number densities for each atom-residue pair into separate files.
        The results are averaged across all frames and written to .dat files for each atom-residue pair.
        """

        # AB: using max and mid Z dimensions of the cell
        # z_max = max(self.z_lengths)

        # AB: The range is (0, z_max) but we need to center the data in each bin
        # AB: Here z_max fits the total number of bins, so it is not max(self.z_lengths)
        z_max = self.bin_size * self.total_bins
        z_mid = z_max * 0.5
        h_bin = self.bin_size * 0.5
        # AB: so the data points must be shifted by half the bin size (see below)

        # Loop over all atom-residue pairs and save their densities
        for pair, densities_per_frame in self.densities.items():
            residue_name, atom_name = pair

            # Average densities across frames for each bin
            average_density = np.mean(
                np.array(densities_per_frame), axis=0
            )

            if self.is_symmetric:
                lprf = len(average_density)-1
                for iprf in range(0, int(lprf/2)+1):
                    average_density[iprf] += average_density[lprf-iprf]
                    average_density[iprf] /= 2.0
                    average_density[lprf-iprf] = average_density[iprf]

            z_values = np.linspace(-z_mid+h_bin, z_mid-h_bin, len(average_density))

            # Save the data to a file
            file_name = out_dir / f"{atom_name}_{residue_name}.dat"
            with open(file_name, 'w') as f:
                # z1 = None
                for z, d in zip(z_values, average_density):
                    f.write(f"{z:.8f} {d:.8f}\n")
                    # if np.isnan(d):  # Replace NaN values with 0
                    #     d = 0.0
                    # if z != z1:
                    #    f.write(f"{z:.8f} {d:.8f}\n")
                    #    z1 = z
            logger.info(f"Saved {file_name}")
    # end of save_results()

# end of class NumberDensityCalculator


@timing
def main():
    """
    Main function to parse command line arguments and run the number density calculation.
    """
    LogConfiguration()

    args = docopt(__doc__)  # Parse arguments using docopt

    bsize = 0.5
    if args['-b']:
        bsize = float(args['-b'])

    if abs(bsize) < 0.001:
        raise Exception(f"Bin size must be greater than 0.001 (A), got {bsize}")

    ref_input = None
    ref_fname = args['-r']
    ref_fpath = Path(ref_fname)
    extension = ref_fpath.suffix.lower()
    if not ref_fname or extension not in ['.gro','.pdb']:
        raise IOError(f"Reference configuration file name is expected "
                  f"(*.gro or *.pdb), got '{ref_fname}'")

    dcd_input = None
    dcd_fname = args['-d']
    if dcd_fname:
        if not dcd_fname.endswith('.dcd'):
            raise IOError(f"Trajectory in DCD format is expected "
                          f"(*.dcd), got '{dcd_fname }'")
    else:
        raise IOError(f"Trajectory file name is expected "
                      f"(*.dcd), got '{dcd_fname}'")
    dcd_input = DCDTrajectory(dcd_fname, ref_fname, 'r')

    # AB: store cell evolution data
    if args['-s'] is not None:
        fev_name = "cell_evolution.dat"
        if len(args['-s']) > 0:
            fev_name = args['-s']
        # fev_name = os.path.basename(dcd_fname) + "_cell.dat"
        dcd_input.save_cell_evolution(fev_name)

    top_input = None
    top_fname = args['-t']
    if top_fname:
        if top_fname.endswith('.itp'):
            top_input = ITPTopology(top_fname)
        elif top_fname.endswith('.psf'):
            top_input = PSFTopology(top_fname)
        else:
            raise IOError(f"Topology in either PSF or ITP format is expected "
                          f"(*.psf or *.itp), got '{top_fname}'")
        logger.info(f"Using topology from file: {top_fname} -> {top_input}")
        # Initialise the number density calculator
        calculator = NumberDensityCalculator(ref_fname, dcd_input,
                                             top_file=top_input, bin_size=bsize)
    else:
        logger.info("No topology file specified!")
        # Initialise the number density calculator
        calculator = NumberDensityCalculator(ref_fname, dcd_input,
                                             bin_size=bsize)

    out_dir = Path(args.get('--outdir') or args.get('-o') or 'ND_SLD').expanduser()
    out_dir.mkdir(parents=True, exist_ok=True)

    # calculate the densities
    calculator.calculate_number_densities()

    # Save the results to files
    calculator.save_results(out_dir)

    sld = args['--sld']

    if sld: # calculate sld if defined in the command line 
        compute_element_slds_from_ndens(out_dir)

def compute_element_slds_from_ndens(
    out_dir: Path,
    water_resnames = None,
    write_nonwater_elements = True) :

    """
    Scan number density .dat files produced by this script and write per-element SLD profiles.

    Outputs (saved into out_dir):
      - SLD_<Elem>.dat            (e.g., SLD_C.dat, SLD_P.dat) -- SLD_H.dat and SLD_O.dat exclude water
      - SLD_O_water.dat
      - SLD_H_water.dat

    Assumptions:
      * All input *.dat files share the same z-grid.
      * Filenames are of the form "<ATOMNAME>_<RESNAME>.dat", e.g. "P_DPPC.dat", "OH2_TIP3.dat".
      * Each file has at least two columns: z and number_density, separated by a white space.
      * Chemistry.ecsl provides a dict of scattering length where keys are element symbols
        (e.g., 'H', 'C', 'N', 'O', 'P', 'Na', 'Cl', ...).
    """

    out_dir = Path(out_dir)
    if water_resnames is None:
        water_resnames = {"TIP3", "SOL", "WAT", "HOH", "TIP3P"}

    # Collect all number-density files (skip SLD outputs if re-running)
    ndens_files = sorted(
        f for f in out_dir.glob("*.dat")
        if "_" in f.stem and not f.stem.startswith("SLD_") # exclude previous SLD files
    )
    if not ndens_files:
        print(f"[SLD] No number-density .dat files found in {out_dir}")
        return

    # element inference from atom name using Chemistry.ecsl keys
    EC_ELEMS = set(Chemistry.ecsl.keys())  # canonical element symbols, e.g., 'H','C','Na','Cl'
    def infer_element(atom_name):
        # strip digits and punctuation suffixes
        raw = "".join(ch for ch in atom_name.strip() if ch.isalpha()) # get only letters
        if not raw:
            return atom_name[:1].upper()  # fallback
        # try 2-letter then 1-letter match against Chemistry.ecsl
        cand2 = raw[:2].capitalize()
        cand1 = raw[:1].upper()
        if cand2 in EC_ELEMS:
            return cand2
        if cand1 in EC_ELEMS:
            return cand1
        # final fallback: uppercase first letter
        return cand1

    # Initialise
    z_ref = None
    sld_nonwater_by_elem = {}
    sld_water: dict = {"O": None, "H": None}  # we only split O/H water

    # Main loop over atom-density files
    for f in ndens_files:
        stem = f.stem  # e.g., "P_DPPC" or "OH2_TIP3"
        try:
            atom_name, resname = stem.split("_", 1)
        except ValueError:
            # unexpected filename -> skip
            continue

        # Load z and number density
        data = np.loadtxt(f, comments="#")
        if data.ndim != 2 or data.shape[1] < 2:
            print(f"[SLD] Skipping malformed file (need at least 2 columns): {f}")
            continue
        z = data[:, 0]
        nd = data[:, 1]

        # Ensure all datasets share the same z-grid
        if z_ref is None:
            z_ref = z
        else:
            if z.shape != z_ref.shape or not np.allclose(z, z_ref, rtol=1e-6, atol=1e-8):
                raise ValueError(
                    f"[SLD] z-grid mismatch in {f.name}: got {z.shape} that doesn't match reference {z_ref.shape}"
                )

        elem = infer_element(atom_name)
        b = Chemistry.ecsl.get(elem)
        if b is None:
            # No scattering length for this inferred element; skip
            print(f"[SLD] No scattering length for element '{elem}' (from atom '{atom_name}'); skipping {f.name}")
            continue

        # Contribution = number_density * scattering_length
        contrib = nd * b

        if resname.upper() in water_resnames and elem in ("O", "H"):
            # calculate water SLD profiles
            if sld_water[elem] is None:
                sld_water[elem] = contrib.copy()
            else:
                sld_water[elem] += contrib
        else:
            if not write_nonwater_elements:
                continue
            # calculate non-water SLD profiles
            acc = sld_nonwater_by_elem.get(elem)
            if acc is None:
                sld_nonwater_by_elem[elem] = contrib.copy()
            else:
                sld_nonwater_by_elem[elem] += contrib

    if z_ref is None:
        print("[SLD] No usable NDENS files were processed.")
        return

    # Function to write profiles
    def write_profile(path, profile):
        arr = np.column_stack((z_ref, profile))
        np.savetxt(path, arr, fmt="%.6f\t%.8e")

    # Write non-water per-element SLDs (e.g., SLD_C.dat, SLD_P.dat, ...)
    for elem, prof in sorted(sld_nonwater_by_elem.items()):
        write_profile(out_dir / f"SLD_{elem}.dat", prof)

    # Write water O/H SLDs (if present)
    if sld_water["O"] is not None:
        write_profile(out_dir / "SLD_O_water.dat", sld_water["O"])
    if sld_water["H"] is not None:
        write_profile(out_dir / "SLD_H_water.dat", sld_water["H"])

    print("[SLD] Wrote per-element SLD profiles to", out_dir)



if __name__ == "__main__":
    main()

