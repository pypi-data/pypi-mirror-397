#!/usr/bin/env python3

##################################################
#                                                #
#  Shapespyer - soft matter structure generator  #
#  Solvation analysis for a cluster of solute(s) #
#                                                #
#  Author: Andrey Brukhno (c) 2020 - 2025        #
#          Daresbury Laboratory, SCD, STFC/UKRI  #
#                                                #
##################################################

# system modules (for parsing arguments, options, handling I/O files etc)
import os, sys, getopt #, glob
import logging

import numpy as np
#from numpy import exp, log, sin, cos, random
#import matplotlib.pyplot as plt

from shapes.basics.utils import LogConfiguration

print("\n##################################################")
print("#                                                #")
print("#  Shapespyer - soft matter structure generator  #")
print("#  Solvation analysis for a cluster of solute(s) #")
print("#                                                #")
print("#  Author: Andrey Brukhno (c) 2020-25            #")
print("#          Daresbury Laboratory, SCD, STFC/UKRI  #")
print("#                                                #")
print("##################################################\n")

logger = logging.getLogger("__main__")

Pi   = np.pi
TwoPi= 2.0*Pi

TINY = 1.0e-8
DMIN = 0.4 # nm - rescale for Angstroems!
BUFF = 1.2 # nm - rescale for Angstroems!

sname = sys.argv[0]
nargs = len(sys.argv)-1

if nargs < 1:
   logger.error(f"{sys.argv[0]}: at least one argument is expected - FULL STOP!")
   sys.exit(1)


def write_mol_gro(fname: str, remark, atms, axyz, box=None, resname='MOL', resid=1, start=0, ntot=0) :

   ierr   = 0
   nlines = 0
   natms  = 0

   # empty title => append another molecule, otherwise new file
   is_new= True
   wmode = 'w'
   if not remark :
      is_new= False
      wmode = 'a'

   try :
      with open(fname, wmode, encoding = 'utf-8') as fout :

         if is_new :
           if ntot==0 : ntot = len(atms)
           logger.info(f"Writing molecule {resid}{resname} into GRO file '{fname}' ...")
           fout.write(remark+"\n")
           fout.write(str(ntot)+"\n")
           nlines += 2
         else :
           logger.info(f"Appending molecule {resid}{resname} to GRO file '{fname}' ...")

         for i in range(len(atms)) :
            line = '{:>5}{:<5}{:>5}{:>5}'.format(resid,resname,atms[i],i+start+1)+ \
                   ''.join('{:>8.3f}{:>8.3f}{:>8.3f}'.format(*axyz[i]))
            fout.write(line+"\n")
            nlines += 1
            natms  += 1

         if box : fout.write('{:>10.5f}{:>10.5f}{:>10.5f}'.format(*box)+"\n")

         #print('{:>5}{:<5}{:>5}{:>5}'.format(resid,resname,atms[i],i+1)+ \
         # ''.join('{:>8.3f}{:>8.3f}{:>8.3f}'.format(*axyz[i])))

   except (IOError, ValueError, EOFError) as err:
      logger.error(f"Oops! Could not open or write file '{fname}' - FULL STOP!")
      logger.exception(err)
      sys.exit(4)

   except Exception as err:
      ierr = 2
      logger.error(f"Oops! Unknown error while writing file '{fname}' - FULL STOP!")
      logger.exception(err)
      sys.exit(4)

   finally:
      if ierr == 0 :
         logger.info(f"File '{fname}' successfully written: nlines = {nlines}"
                     f" & natms = {natms} / {natms+start}\n")

   return (ierr==0)

# end of write_mol_gro()


def read_mol_gro0(fname: str, rems, atms, axyz, box, solvname='SOL', molatms=3, radii=[]) : #, rout=1.0) :

   rint =-1.e-12
   rout = 1.0
   if len(radii) > 0 :
      rout = radii[0]
      if len(radii) > 1 :
         rint = radii[1]
   ierr   = 0
   nlines = 0
   nrems  = 1
   matms  = 0
   natms  = 0
   resix0 = 0
   catm   = []
   cxyz   = []
   ratms  = np.array([0.0, 0.0, 0.0])

   natmb  = 0
   batm   = []
   bxyz   = []
   ratmb  = np.array([0.0, 0.0, 0.0])

   hbox = np.array([0.0,0.0,0.0])
   is_boxin = len(box) > 0
   if is_boxin :
      hbox = np.array(box)*0.5

   try :
     with open(fname, mode='r', encoding = 'utf-8') as finp :

        logger.info(f"Reading GRO file '{fname}' ...")
        logger.info(f"Extracting solvent '{solvname}' molecules of {molatms} atoms "
                    f"within a spherical slice, R = [{rint}, {rout}] ...\n")

        line = finp.readline().lstrip().rstrip()
        logger.info(f"Title: '{line}'")
        rems.append(line)

        line = finp.readline().lstrip().rstrip()
        nlines += 2

        # the first line contains number of atoms
        # and possibly number of remarks (by my own convention)
        control = line.split()
        matms   = int(control[0])

        # arrange for abnormal EOF handling
        if nlines == nrems+1 :

           for i in range(matms) :
              # do not lstrip here - relaying on field widths in GRO files!
              line = finp.readline().rstrip()
              if not line :
                 break
              nlines += 1

              resix = int(line[0:5].lstrip().rstrip())
              resnm = line[5:10].lstrip().rstrip()

              if resnm == solvname :
                if resix != resix0 :
                   resix0 = resix
                   natmol = 0
                   catm   = []
                   cxyz   = []
                   ratms  = np.array([0.0, 0.0, 0.0])

                latm = line[20:].split()
                apos = np.array([float(latm[0]),float(latm[1]),float(latm[2])])
                cxyz.append(apos)
                catm.append(line[10:15].lstrip().rstrip())

                ratms += apos-hbox
                natmol += 1

                if natmol == molatms :
                   rmol = np.linalg.norm(ratms/float(natmol))
                   if rint <= rmol <= rout :
                      for j in range(molatms) :
                        natms += 1
                        atms.append(catm[j])
                        axyz.append(list(cxyz[j]))

              else :
                latm = line[20:].split()
                apos = np.array([float(latm[0]),float(latm[1]),float(latm[2])])
                bxyz.append(apos-hbox)
                batm.append(line[10:15].lstrip().rstrip())

                ratmb += apos-hbox
                natmb += 1

           if not is_boxin :
              line = finp.readline().rstrip()
              lbox = line.split()
              box.append(float(lbox[0]))
              box.append(float(lbox[1]))
              box.append(float(lbox[2]))

           # arrange for abnormal EOF handling
           if nlines != nrems+matms+1 :
              ierr = 1
              logger.error(f"Oops! Unexpected EOF or format in '{fname}' (line "
                           f"{nlines+1}) - FULL STOP!\n")
              sys.exit(4)

        else : # nlines != nrems+1
           ierr = 1
           logger.error(f"Oops! Unexpected EOF or empty line in '{fname}' (line "
                        f"{nlines+1}) - FULL STOP!\n")
           sys.exit(4)

   except (IOError, ValueError, EOFError) as err:
      logger.error(f"Oops! Could not open or read file '{fname}' - FULL STOP!")
      logger.exception(err)
      sys.exit(4)

   except Exception as err:
      ierr = 2
      logger.error(f"Oops! Unknown error while reading file '{fname}' - FULL STOP!")
      logger.exception(err)
      sys.exit(4)

   finally :
      if ierr == 0 :
         logger.info(f"File '{fname}' successfully read: nlines = {nlines}; "
                     f"natms = {natms} / {molatms} = nmols = {natms/molatms}; "
                     f"Rc(rest) = {np.linalg.norm(ratmb)/float(natmb)}"
                     f" =?= {np.linalg.norm(sum(bxyz))/float(len(bxyz))}\n")

   return (ierr==0)

# end of read_mol_gro0()


def read_mol_gro(fname: str, rems, atms, axyz, atms1, axyz1, box, sname='SOL', molatms=3, rlist=[], cnames=[], anames=[]) :

   rint = 0.0
   rout = 1.0
   dshl = 0.33
   if len(rlist) > 0 :
      rout = rlist[0]
      if len(rlist) > 1 :
         rint = rlist[1]
         if len(rlist) == 3 :
            dshl = rlist[2]
   else:
      logger.error(f"List of radii is empty: {rlist} - cannot proceed!")
      sys.exit(11)
   ierr   = 0
   nlines = 0
   nrems  = 1
   matms  = 0
   natms  = 0
   resix0 = 0
   moln   = 0
   matm   = []
   catm   = []
   cxyz   = []
   ratms  = np.array([0.0, 0.0, 0.0])

   natmb  = 0
   batm   = []
   bxyz   = []
   bpos   = []
   ratmb  = np.array([0.0, 0.0, 0.0])

   hbox = np.array([0.0,0.0,0.0])
   is_boxin = len(box) > 0
   if is_boxin :
      hbox = np.array(box)*0.5

   try :
     with open(fname, mode='r', encoding = 'utf-8') as finp :

        logger.info(f"Reading GRO file '{fname}' ...")
        logger.info(f"Extracting solvent '{sname}' molecules of {molatms} atoms "
                    f"within a spherical slice, R = [{rint}, {rout}] ...")
        if len(cnames) > 0:
           logger.info(f"Also collecting a subset of those found within {dshl} nm "
                       f"of atoms {anames} on {cnames} solutes (in a cluster)...")

        line = finp.readline().lstrip().rstrip()
        #print("Title: '"+line+"'\n")
        rems.append(line)

        line = finp.readline().lstrip().rstrip()
        nlines += 2

        # the first line contains number of atoms 
        # and possibly number of remarks (by my own convention)
        control = line.split()
        matms   = int(control[0])

        # arrange for abnormal EOF handling
        if nlines == nrems+1 :

           for i in range(matms) :
              # do not lstrip here - relying on field widths in GRO files!
              line = finp.readline().rstrip() 
              if not line : # or len(line.split())!=4 :
                 break
              nlines += 1

              resix = int(line[0:5].lstrip().rstrip())
              resnm = line[5:10].lstrip().rstrip()

              if resnm == sname :
                if resix != resix0 :
                   # if natms < 10: print("Read-in resix = " + str(resix) + ", resnm = " + resnm)
                   resix0 = resix
                   natmol = 0
                   catm   = []
                   cxyz   = []
                   ratms  = np.array([0.0, 0.0, 0.0])

                latm = line[20:].split()
                apos = np.array([float(latm[0]),float(latm[1]),float(latm[2])])
                cxyz.append(apos)
                catm.append(line[10:15].lstrip().rstrip())

                ratms  += apos-hbox
                natmol += 1

                if natmol == molatms :
                   rmol = np.linalg.norm(ratms/float(natmol))
                   is_molin = False
                   if rint <= rmol <= rout :
                      for j in range(molatms) :
                        natms += 1
                        atms.append(catm[j])
                        axyz.append(list(cxyz[j]))
                        if len(anames) > 0 :
                           for k in range(len(batm)) :
                              if batm[k][0] in anames : 
                                 if batm[k][1] == cnames[anames.index(batm[k][0])] :
                                    datms = np.linalg.norm(cxyz[j] - bxyz[k]- hbox)
                                    is_molin = is_molin or (datms <= dshl)
                                    #if rint <= bpos[k] <= rout :
                                    #   datms = np.linalg.norm(cxyz[j] - bxyz[k]- hbox)
                                    #   is_molin = is_molin or (datms <= dshl)
                      if is_molin :
                         moln = int((natms-1) / molatms)
                         if moln not in matm :
                            matm.append(moln)
                            molb = moln * molatms
                            mole = (moln + 1) * molatms
                            for j in range(molb, mole) :
                               atms1.append(atms[j])
                               axyz1.append(axyz[j])

              elif resnm in cnames :
                 #if natms < 10: print("Read-in resix = " + str(resix) + ", resnm = " + resnm)
                 latm = line[20:].split()
                 apos = np.array([float(latm[0]),float(latm[1]),float(latm[2])]) - hbox
                 rpos = np.linalg.norm(apos)
                 if rint <= rpos <= rout :
                    bxyz.append(apos)
                    bpos.append(rpos)
                    #bpos.append(np.linalg.norm(apos))
                    aname = line[10:15].lstrip().rstrip()
                    batm.append((aname,resnm))

                    ratmb += apos
                    natmb += 1
                    # AB: uncomment for cases where solvent might precede solutes
                    # if aname in anames :
                    #    if resnm == cnames[anames.index(batm[k][0])] :
                    #    #if rint <= bpos[-1] <= rout:
                    #       for k in range(len(atms)) :
                    #          datms = np.linalg.norm(np.array(axyz[k]) - apos - hbox)
                    #          if datms <= dshl :
                    #             moln = int(k/molatms)
                    #             if moln not in matm :
                    #                matm.append(moln)
                    #                molb = moln*molatms
                    #                mole = (moln+1)*molatms
                    #                for j in range(molb,mole) :
                    #                   atms1.append(atms[j])
                    #                   axyz1.append(axyz[j])

           if not is_boxin :
              line = finp.readline().rstrip()
              lbox = line.split()
              box.append(float(lbox[0]))
              box.append(float(lbox[1]))
              box.append(float(lbox[2]))

           # arrange for abnormal EOF handling
           if nlines != nrems+matms+1 :
              ierr = 1
              logger.error(f"Oops! Unexpected EOF or format in '{fname}' (line "
                           f"{nlines+1}) - FULL STOP!\n")
              sys.exit(4)

        else : # nlines != nrems+1
           ierr = 1
           logger.error("Oops! Unexpected EOF or empty line in '"+fname+"' (line "+ \
                 str(nlines+1)+") - FULL STOP!\n")
           sys.exit(4)

   except (IOError, ValueError, EOFError) as err :
      logger.error("Oops! Could not open or read file '"+fname+"' - FULL STOP!")
      sys.exit(4)

   except : 
      ierr = 2
      logger.error("Oops! Unknown error while reading file '"+fname+"' - FULL STOP!")
      sys.exit(4)

   finally :
      if ierr == 0 :
         logger.info("File '"+fname+"' successfully read: nlines = "+str(nlines)+ \
               "; natms = "+str(natms)+" / "+str(molatms)+" = nmols = "+str(natms/molatms)+ \
               "; Rc(rest) = "+str(np.linalg.norm(ratmb)/float(natmb))+ \
               " =?= "+str(np.linalg.norm(sum(bxyz))/float(len(bxyz)))+"\n")

   return (ierr==0)

# end of read_mol_gro()

def read_box_gro(fname: str, box) :

   ierr   = 0
   nlines = 0
   #nrems  = 1

   try :
     with open(fname, mode='r', encoding = 'utf-8') as finp :
        logger.info("Reading GRO (box) file '"+fname+"' ...")
        nlines = 1
        line = finp.readline().rstrip()
        lbox = line.split()
        box.append(float(lbox[0]))
        box.append(float(lbox[1]))
        box.append(float(lbox[2]))

   except (IOError, ValueError, EOFError) as err :
      logger.error("Oops! Could not open or read file '"+fname+"' - FULL STOP!")
      sys.exit(4)

   except : 
      ierr = 2
      logger.error("Oops! Unknown error while reading file '"+fname+"' - FULL STOP!")
      sys.exit(4)

   finally :
      if ierr == 0 :
         logger.info("File '"+fname+"' successfully read: nlines = "+str(nlines))

   return (ierr==0)

#end of read_box_gro()


def write_out_gro(dfout, rem, gbox, atms, axyz, nmols, matms, res='MOL') :

   nout = matms*nmols
   obox = None
   for k in range(nmols) :
      if k == 1 : rem = None
      if k == nmols-1 : obox = gbox
      nbeg = k*matms
      nend = nbeg+matms
      write_mol_gro(dfout, rem, atms[nbeg:nend], axyz[nbeg:nend], obox, \
                    resname=res, resid=k+1, start=nbeg, ntot=nout)


### MAIN ###

def main(argv=sys.argv) :
   LogConfiguration()

   dinp = '.'
   dout = '.'
   name = 'config'
   sbox = '.box'
   sxyz = '.xyz'
   spdb = '.pdb'
   sgro = '.gro'
   oext = ''
   exts =  [sgro] # [sxyz,spdb,sgro]

   #fcfg = 'CONFIG'
   #fhst = 'HISTORY'
   #ftrj = 'TRAJOUT'

   finp = name+sgro
   fout = name

   script = os.path.basename(argv[0])

   try :
      opts, args = getopt.getopt(argv[1:],"h:d:b:i:o:x:s:c:a:n:r:", \
                   ["help","box=","dio=","inp=","out=","ext=","solvent=","nsatm=","cluster=","atoms=","rs="])
   except getopt.GetoptError :
      logger.error("Try: "+script+" --help")
      sys.exit(1)

   is_head = False
   is_box  = False

   nmols = 1
   molid = 1
   resnm = 'SOL'
   atoms = []
   clust = []
   radii = []

   shape = 'ball'
   #shape = 'disk'
   ndisk = 1
   nstep = 0
   alpha = 0.0
   theta = 0.0

   radius= 1.0
   natmol= 3

   for opt, arg in opts :
      if (opt == '-h' or opt == '--help') :
         #print('\n')
         print('Extracting solvent molecules bound to within a sphere or a spherical layer.\n'
               'Optionally, also extracting solvation shell subset for specific atomic species.\n')
         print('\n======')
         print('Usage:')
         print('======\n')
         print(script+' [-d <dio>] -i <inp> -o <out> -x <ext> -s <solvent> -n <nsatm> -r <rs> [-c <cluster> -a <atoms>]\n')
         print('--dio=<dio> : in/out directory (optional) {.}')
         print('--box=<box> : input  file with box dimensions: Lx Ly Lz {'+name+sbox+'}')
         print('--inp=<inp> : input  file with system coordinates where solute cluster is centered at origin {config.gro}')
         print('--out=<out> : output file base name, to be automatically extended with appropriate suffices {'+name+'}')
         print('--ext=<ext> : output file extension {.gro}\n')
         print('--solvent=<solvent_name>\n'
               '            : name of solvent molecules to extract {SOL}')
         print('--nsatm=<n_solvent_atoms>\n'
               '            : number of atoms per solvent molecule {3}')
         print('--cluster=<solute_names>\n'
               '            : name(s) of solute(s) forming a cluster (comma-delimited) {N/A}')
         print('--atoms=<atom_names>\n'
               '            : name(s) of solvated atom(s), one per solute in the cluster (comma-delimited) {N/A}')
         print('--rs=<r_ext[,r_int[,r_shell]>\n'
               '            : radius/radii of bounding sphere(s) centered at origin {1.0}; if more than one entry given:\n'
               '            : the first entry must always be the radius of the external bounding sphere,\n'
               '            : the second entry must be the radius of the internal bounding sphere,\n'
               '            : the third entry must be the radius of shells centered at atom(s) specified in <atoms>;\n'
               '            : i.e. it is necessary if at least one entry is given by <cluster> and <atoms> options\n')
         #print('\n')
         sys.exit(0)
      elif opt in ("-d", "--dio") :
         dinp = arg.rstrip()
         dout = dinp
      elif opt in ("-b", "--box") :
         is_box = True
         fbox = arg.rstrip()
      elif opt in ("-i", "--inp") :
         finp = arg.rstrip()
      elif opt in ("-o", "--out") :
         name = arg.rstrip()
      elif opt in ("-x", "--ext") :
         oext = arg.rstrip()
      elif opt in ("-s", "--solvent") :
         resnm = arg.rstrip()
#         names = arg.split(',')
#         if len(names) > 1:
#            resnm = str(names[0].rstrip())
#            for nm in names:
#               lnames.append(str(nm.rstrip()))
#         else:
#            resnm = str(arg.rstrip())
#            lnames.append(resnm)
      elif opt in ("-c", "--cluster") :
         clust = arg.split(',')
#         if len(names) > 1:
#            for nm in names:
#               clust.append(str(nm.rstrip()))
#         else:
#            clust.append(str(arg.rstrip()))
      elif opt in ("-a", "--atoms") :
         atoms = arg.split(',')
#         if len(names) > 1:
#            for nm in names:
#               clust.append(str(nm.rstrip()))
#         else:
#            clust.append(str(arg.rstrip()))
      elif opt in ("-r", "--rs") :
         sradii = arg.split(',')
         if len(sradii) > 1:
            radius = float(sradii[0].rstrip())
            for rs in sradii:
               radii.append(float(rs.rstrip()))
         else:
            radius = abs(float(arg.rstrip()))
            radii.append(radius)
      elif opt in ("-n", "--nsatm") :
         natmol = max(abs(int(arg.rstrip())),1)
      else :
        logger.error(f"Unrecognised option(s): {arg}")
        logger.info(f"Try: {script} --help")
        sys.exit(1)

   iext = finp[-4:]
   logger.info(f"Input file extension: '{iext}'")
   if (iext not in exts) : # and finp!='CONFIG' :
      if iext[1]=='.' :
         logger.error(f"Unsupported input extension: '{iext}' [.gro]")
      else :
         logger.error(f"Unsupported input file-name: '{finp}'")
      sys.exit(2)
   #else :
   #   logger.debug(f"Using input file: '{finp}'")

   #name = name + '_' + resnm + '_R_' + str(radius) + 'nm'
   if len(radii) > 1 and radii[1] > 1.e-10 :
      name = name + '_' + resnm + '_Rc_' + str(radii[1]) + '-' + str(radii[0]) + 'nm'
   else:
      name = name + '_' + resnm + '_Rc_' + str(radius) + 'nm'

   fout = name+oext
   if len(oext)<1 :
      oext=fout[-4:]
      if '.' not in oext : 
         oext=''

   #logger.debug(f"Output file extension: '{oext}'")

   if len(oext)>0 and (oext not in exts) :
      logger.error(f"Unsupported output extension: '{oext}' [.gro/.xyz/?.pdb; N/A for DL_POLY CONFIG]")
      sys.exit(3)
   elif len(oext)<1 and fout!='CONFIG' :
      logger.error(f"Unsupported output file-name: '{fout}' [no extension => DL_POLY 'CONFIG']")
      sys.exit(3)
   #else :
   #   logger.debug(f"Using output file: '{fout}' (extension: '{oext}')")

   ierr  = 0
   matms = 0
   natms = 0

   gbox = []
   cell = []

   rems_inp = []
   atms_inp = []
   axyz_inp = []
   atms_out = []
   axyz_out = []

   if os.path.isdir(dinp) :

      dfbox = str(dinp+'/'+fbox)
      dfinp = str(dinp+'/'+finp)
      dfout = str(dout+'/'+fout)

      if os.path.isfile(dfinp) :

         logger.info("Doing: input '"+finp+"' => output '"+fout+"'")

         # Reading input for one molecule

         if finp[-4:]==sgro :

            if is_box :
               read_box_gro(dfbox, gbox)

            #if len(clust) > 0 : #or len(radii) > 1 :
            if len(atoms) > 0 : #or len(radii) > 1 :

               logger.info(f"Solvation analysis for atoms {atoms} in molecular cluster "
                           f"of {clust} species")

               if len(atoms) != len(clust):
                  logger.error(f"Insufficient input for atoms: {atoms} (refer to help) "
                               "- FULL STOP!")
                  sys.exit(10)

               if len(radii) < 3:
                  logger.error(f"Insufficient input for radii: {radii} (refer to help) "
                               "- FULL STOP!")
                  sys.exit(11)

               read_mol_gro(dfinp, rems_inp, atms_inp, axyz_inp, atms_out, axyz_out, gbox, \
                            resnm, natmol, radii, clust, atoms)
            else :
               read_mol_gro0(dfinp, rems_inp, atms_inp, axyz_inp, gbox, resnm, natmol, radii) #, radius)

            matms = len(atms_inp)
            natms = matms

            hbox = 0.0
            hmax = 0.0
            if len(gbox)>0 : 
               hbox = np.array(gbox)*0.5
               hmax = np.amax(hbox)
               if not is_box :
                  gbox[0] = 0.0
                  gbox[1] = 0.0
                  gbox[2] = 0.0

               #print("Read-in GRO box: "+'({:>8.3f}{:>8.3f}{:>8.3f})'.format(*gbox)+ \
               #      "; "+'({:>8.3f}{:>8.3f}{:>8.3f})'.format(*hbox))

         #elif finp[-4:]==sxyz :
         #   read_mol_xyz(dfinp, rems_inp, atms_inp, axyz_inp)
         #   matms = len(atms_inp)
         #   natms = matms
         #elif finp[-4:]==spdb :
            #read_mol_pdb(dfinp, rems_inp, atms_inp, axyz_inp, gbox, resname=resnm)
         #elif finp=='CONFIG-MOL' :
            #read_mol_dlp(dfinp, rems_inp, atms_inp, axyz_inp, gbox, resname=resnm)
         else :
            logger.error(f"Unrecongnised input format: '{fout}' [no extension => "
                         "DL_POLY CONFIG]")
            sys.exit(2)

         if fout[-4:]==sgro :
            #logger.debug(f"GRO input '{finp}' => GRO output '{fout}'")

            rem = rems_inp[0]

#            for i in range(len(atms_inp)) :
#               axyz_inp[i][0] -= gbox[0]*0.5
#               axyz_inp[i][1] -= gbox[1]*0.5
#               axyz_inp[i][2] -= gbox[2]*0.5
#               axyz_out[i][0] += gbox[0]*0.5
#               axyz_out[i][1] += gbox[1]*0.5
#               axyz_out[i][2] += gbox[2]*0.5

            rem = "Species '" + resnm + "' found for Rc <= " + str(radius) + " nm"
            if len(radii) > 1 and radii[1] > 1.e-10 :
               rem = "Species '" + resnm + "' found for Rc in [" + str(radii[1]) + ', ' + str(radii[0]) + "] nm"

            write_out_gro(dfout, rem, gbox, atms_inp, axyz_inp, 1, matms, res=resnm)

            #if len(clust) > 0 :
            if len(atoms) > 0 :
               satoms = '-'.join(atoms)
               solute = '-'.join(clust)
               rem  = rem + " within " + str(radii[2]) + f" nm from atoms {atoms} on species {clust}"
               fout = name + '_Rsh_' + str(radii[2]) + f'nm_of_{satoms}_on_{solute}' + oext
               dfout = str(dout + '/' + fout)
               write_out_gro(dfout, rem, gbox, atms_out, axyz_out, 1, len(atms_out), res=resnm)

         #elif fout[-4:]==sxyz :
         #   logger.debug(f"GRO input '{finp}' => XYZ output '{fout}'")
         #   write_out_xyz()
         #elif fout[-4:]==spdb :
         #   logger.debug(f"GRO input '{finp}' => PDB output '{fout}'")
         #elif fout=='CONFIG' :
         #   logger.debug(f"GRO input '{finp}' => DLP output '{fout}'")
         else :
            logger.error(f"Unrecongnised output format: '{fout}'")
            sys.exit(3)
      else :
         logger.error(f"Input file not found: '{dfinp}")
         sys.exit(2)
   else :
      logger.error(f"Directory not found: '{dinp}")
      sys.exit(2)

# end of main(argv)

### END OF MAIN ###


if __name__ == "__main__":
   main()
   sys.exit(0)
