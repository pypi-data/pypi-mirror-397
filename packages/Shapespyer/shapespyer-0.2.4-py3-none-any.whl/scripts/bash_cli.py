"""This Module holds entry points for Shapespyer bash scripts.
"""
import os
from subprocess import PIPE, Popen, STDOUT
import sys
from pathlib import Path

from shapes.basics.utils import LogConfiguration


def call_script(script_name: str, *args, cwd: str | Path | None = None):
    logger = LogConfiguration().logger

    if sys.platform.startswith("win"):
        logger.error("The script is not available on Windows")
        return
    
    scripts_dir = os.path.dirname(os.path.realpath(__file__))
    sys.argv[0] = os.path.join(scripts_dir, script_name)

    all_args = sys.argv.copy()
    if len(all_args) > 1 and "jupyter/runtime/kernel" in all_args[1]:
        all_args.pop(1)
    all_args.extend(args)
    all_str_args = list(map(str, all_args))

    with Popen(all_str_args, stdout=PIPE, stderr=STDOUT, text=True, cwd=cwd) as process:
        while process.poll() is None:
            stdout = process.stdout
            if stdout is not None:
                logger.info(stdout.readline().strip())
        stdout = process.stdout
        if stdout is not None:
            logger.info("".join(stdout.readlines()))

        logger.debug(f"Process {all_str_args} terminated with code {process.returncode}")
        

def gmx_add_ions_solv(*args):
    call_script("gmx-add-ions-solv.bsh", *args)

def gmx_ana_clusters_for(*args):
    call_script("gmx-ana-clusters-for.bsh", *args)

def gmx_ana_clusters_prl(*args):
    call_script("gmx-ana-clusters-prl.bsh", *args)

def gmx_ana_clusters(*args):
    call_script("gmx-ana-clusters.bsh", *args)

def gmx_ana_gyration_dirs(*args):
    call_script("gmx-ana-gyration-dirs.bsh", *args)

def gmx_ana_gyration_pieces(*args):
    call_script("gmx-ana-gyration-pieces.bsh", *args)

def gmx_ana_gyration(*args):
    call_script("gmx-ana-gyration.bsh", *args)

def gmx_ana_maxclust_for(*args):
    call_script("gmx-ana-maxclust-for.bsh", *args)

def gmx_ana_solvation(*args):
    call_script("gmx-ana-solvation.bsh", *args)

def gmx_center_cluster(*args):
    call_script("gmx-center-cluster.bsh", *args)

def gmx_equilibrate(*args):
    call_script("gmx-equilibrate.bsh", *args)

def gmx_posres_gro(*args):
    call_script("gmx-posres-gro.bsh", *args)

def gmx_run_for(*args):
    call_script("gmx-run-for.bsh", *args)

def gmx_setup_equil(*args):
    call_script("gmx-setup-equil.bsh", *args)

def gmx_setup_multi(*args):
    call_script("gmx-setup-multi.bsh", *args)
