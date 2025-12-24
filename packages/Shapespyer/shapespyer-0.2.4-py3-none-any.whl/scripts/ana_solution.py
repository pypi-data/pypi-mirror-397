#!/usr/bin/env python3

##################################################
#                                                #
#  Shapespyer - soft matter structure generator  #
#  Solvation analysis for a cluster of solute(s) #
#                                                #
#  Author: Andrey Brukhno (c) 2020 - 2023        #
#          Daresbury Laboratory, SCD, STFC/UKRI  #
#                                                #
##################################################

# system modules (for parsing arguments, options, handling I/O files etc)
import os, sys, getopt, glob
import logging

import numpy as np
#from numpy import arange, exp, log, sin, cos, random,
#import matplotlib.pyplot as plt

from shapes.basics.defaults import NL_INDENT
from shapes.basics.utils import LogConfiguration

print("\n##################################################")
print("#                                                #")
print("#  Shapespyer - soft matter structure generator  #")
print("#  Solvation analysis for a cluster of solute(s) #")
print("#                                                #")
print("#  Author: Andrey Brukhno (c) 2020-23            #")
print("#          Daresbury Laboratory, SCD, STFC/UKRI  #")
print("#                                                #")
print("##################################################\n")

logger = logging.getLogger("__main__")

Pi   = np.pi
TwoPi= 2.0*Pi

TINY = 1.0e-8
DMIN = 0.4 # nm - rescale for Angstroems!
BUFF = 1.2 # nm - rescale for Angstroems!

digits= {'0', '1', '2', '3', '4', '5', '6', '7', '8', '9'}
elems = ('D', 'H', 'C', 'N', 'O', 'P', 'S')
emass = dict(D=2.014, H=1.0078, C=12.011, N=14.007, O=15.999, P=30.974, S=32.065)
elems_csl = dict(D=6.674, H=-3.741, C=6.648, N=9.360, O=5.805, P=5.130, S=2.847)
elems_sld = dict(D=2.823, H=-1.582, C=7.000, N=3.252, O=2.491, P=1.815, S=1.107)

# logger.debug(f"CSL data for {elems}:")
# logger.debug(LogConfiguration.formatted_iterable(elems_csl))
# logger.debug(f"SLD data for {elems}:")
# logger.debug(LogConfiguration.formatted_iterable(elems_sld))

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
         logger.info(f"File '{fname}' successfully written: nlines = {nlines} & "
                     f"natms = {natms} / {natms+start}")

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
                    f"within a spherical slice, R = [{rint}, {rout}] ...")

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
              logger.error(f"Oops! Unexpected EOF or format in '{fname}' "
                           f"(line {nlines+1}) - FULL STOP!")
              sys.exit(4)

        else : # nlines != nrems+1
           ierr = 1
           logger.error(f"Oops! Unexpected EOF or empty line in '{fname}' "
                        f"(line {nlines+1}) - FULL STOP!")
           sys.exit(4)

   except (IOError, ValueError, EOFError) as err :
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
                     f" =?= {np.linalg.norm(sum(bxyz))/float(len(bxyz))}")

   return (ierr==0)

# end of read_mol_gro0()


def read_mol_gro(fname: str, rems, atms, axyz, atms1, axyz1, box,
                 sname='SOL', molatms=3, rlist=[], cnames=[], anames=[], dlist=[]) :

   def getMass(elem: str = ''):
      mass = 1.0
      if elem in emass:
         mass = emass[elem]
      return mass

   rint = 0.0
   rout = 1.0
   dshl = 0.0
   dbin = 0.1 #25
   dbin2= 0.05 #125
   if len(rlist) > 0 :
      rout = rlist[0]
      if len(rlist) > 1 :
         rint = rlist[1]
         if len(rlist) == 3 :
            dshl = rlist[2]
            if len(anames) < 1 and len(dlist) > 0:
               dbin  = dshl
               dbin2 = dshl*0.5
               dshl  = 0.0
   else:
      logger.error(f"List of radii is empty: {rlist} - cannot proceed!")
      sys.exit(11)

   hwater = []
   drange = []
   ishist = False
   if (dbin - rint) > TINY and len(dlist) > 0:
      ishist = True
      nbins  = round((rout-rint)/dbin)
      drange = np.arange(0, nbins, dtype=float)*dbin + dbin2
      dbinV = 4.0*Pi * drange**2 * dbin
      dbinM = dbinV * 602.2
      logger.info(f"Will collect histogram for water: dbin = {dbin} -> {nbins} bins...")
      hwater = np.zeros(nbins)

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

   bname = fname[:-4]
   bfext = fname[-4:]

   try :
     with open(fname, mode='r', encoding = 'utf-8') as finp :

        logger.info(f"Reading GRO file '{fname}' ...")
        logger.info(f"Extracting solvent '{sname}' molecules of {molatms} atoms "
                    f"within a spherical slice, R = [{rint}, {rout}] ...")
        if len(cnames) > 0:
           if len(anames) > 0:
              logger.info(f"Also collecting a subset of those found within {dshl} nm "
                          f"of atoms {anames} on {cnames} solutes (in a cluster)...")
           elif len(rlist) == 3:
              logger.info("Also collecting histograms of atoms and COM groups "
                          f"on {cnames} solutes (in a cluster)...")

        line = finp.readline().lstrip().rstrip()
        # logger.debug(f"Title: '{line}'")
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
                   amass  = 0.0

                latm = line[20:].split()
                apos = np.array([float(latm[0]),float(latm[1]),float(latm[2])])
                cxyz.append(apos)

                aname =line[10:15].lstrip().rstrip()
                catm.append(aname)  # (line[10:15].lstrip().rstrip())

                mass = getMass(aname[0])
                amass  += mass
                ratms  += (apos-hbox)*mass
                natmol += 1

                if natmol == molatms :
                   #rmol = np.linalg.norm(ratms/float(natmol))
                   rmol = np.linalg.norm(ratms/amass)
                   is_molin = False
                   if rint <= rmol <= rout :
                      if ishist:
                         # histogram
                         ibin = int(rmol/dbin)
                         #if -1 < ibin < nbins:
                         hwater[ibin] += 1.0
                      # atom collection
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
                 aname = line[10:15].lstrip().rstrip()
                 apos = np.array([float(latm[0]),float(latm[1]),float(latm[2])]) - hbox
                 rpos = np.linalg.norm(apos)
                 if rint <= rpos <= rout :
                 #if rint <= rpos <= rout and aname[0] != 'H':
                    bxyz.append(apos)
                    bpos.append(rpos)
                    #bpos.append(np.linalg.norm(apos))
                    #aname = line[10:15].lstrip().rstrip()
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
              logger.error(f"Oops! Unexpected EOF or format in '{fname}' "
                           f"(line {nlines+1}) - FULL STOP!")
              sys.exit(4)

        else : # nlines != nrems+1
           ierr = 1
           logger.error(f"Oops! Unexpected EOF or empty line in '{fname}' "
                        f"(line {nlines+1}) - FULL STOP!")
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
                     f"natms = {natms} / {molatms} = nmols = {natms/molatms};"
                     f"Rc(rest) = {np.linalg.norm(ratmb)/float(natmb)}"
                     f" =?= "+str(np.linalg.norm(sum(bxyz))/float(len(bxyz))))

   #####
   if ishist:
      logger.info(f"Now collecting historgrams for {len(batm)} atoms on {cnames} solutes"
                  " (in a cluster)...")

      gprev  = ''
      gmass  = 0.0
      aother = []
      nother = []
      halst  = []
      hlist  = []
      rxyz   = np.array([0.0, 0.0, 0.0])
      for ib, ba in enumerate(batm):
         aname = ba[0]
         rname = ba[1]

         atmlist = [hatm[0][0] for hatm in halst]
         if aname[0] in atmlist:
            ia = atmlist.index(aname[0])
            #ibin = int(np.linalg.norm(bxyz[ib])/dbin)
            ibin = int(bpos[ib]/dbin)
            if -1 < ibin < nbins:
               halst[ia][0][0]  = aname[0]
               halst[ia][0][1] += 1
               halst[ia][1][ibin] += 1.0
         else:
            halst.append([[aname[0], 1, rname], np.zeros(nbins)])
            ibin = int(bpos[ib]/dbin)
            if -1 < ibin < nbins:
               halst[-1][1][ibin] = 1.0

         if aname[0] == 'H':  # add hydrogen to the COM group
            if 'H' in aother:
               nother[aother.index('H')] += 1
            else:
               aother.append('H')
               nother.append(1)
            mass = getMass(aname[0])
            gmass += mass
            rxyz += bxyz[ib]*mass
         elif len(aname)>1 and len(gprev)>0 and aname[1] == gprev[0]:
            # found another atom in the previous COM group
            if aname[0] in aother:
               nother[aother.index(aname[0])] += 1
            else:
               aother.append(aname[0])
               nother.append(1)
            mass = getMass(aname[0])
            gmass += mass
            rxyz += bxyz[ib]*mass
         elif aname != gprev: # increment the count in histogram
            # initiate Rvec for new COM group
            atmlist = [hatm[0][0] for hatm in hlist]
            if len(gprev) > 0:
               agrp = gprev[0]
               if len(aother) > 0:
                  for io, ao in enumerate(aother):
                     agrp = agrp + ao + str(nother[io])
               #print(f"Counting for atom group {gprev} {ib}...")
               if gprev in atmlist:
                  ia = atmlist.index(gprev)
                  ibin = int(np.linalg.norm(rxyz/gmass)/dbin)
                  if -1 < ibin < nbins:
                     hlist[ia][0][1] = agrp
                     hlist[ia][1][ibin] += 1.0
            if aname not in atmlist:
               logger.info(f"Seeding a new atom group {aname} {ib}...")
               hlist.append([[aname,aname,rname], np.zeros(nbins)])
            gmass = getMass(aname[0])
            rxyz  = bxyz[ib]*gmass
            gprev = aname
            aother = []
            nother = []

         if ib == len(batm)-1:  # increment the count in histogram
            agrp = gprev[0]
            if len(aother)>0:
               for io, ao in enumerate(aother):
                  agrp = agrp + ao + str(nother[io])
            atmlist = [hatm[0][0] for hatm in hlist]
            if gprev in atmlist:
               ia = atmlist.index(gprev)
               ibin = int(np.linalg.norm(rxyz/gmass)/dbin)
               if -1 < ibin < nbins:
                  hlist[ia][0][1] = agrp
                  hlist[ia][1][ibin] += 1.0

      ntot = 0
      gntot = []
      hgtot = []
      for ih, hist in enumerate(hlist):
         if ih > 0:
            if hist[0][1] == hlist[ih-1][0][1]:
               hgtot[-1] += hist[1]
            else:
               gntot.append(hist[0][1])
               hgtot.append(hist[1])
         else:
            gntot.append(hist[0][1])
            hgtot.append(hist[1])
         ntot += sum(hist[1])
         logger.info(f"Histogram for group '{hist[0][1]}' @ atom {hist[0][0]} "
                     f"of {sum(hist[1])} counts:{NL_INDENT}"
                     f"{hist[1].T}")

      is_all = 'ALL' in dlist or 'All' in dlist or 'all' in dlist
      checkA = [is_all]
      checkA.extend([ aname[0] for aname in batm if aname[0] in dlist ])
      countA = is_all or checkA.count(True) > 1
      #print(f"\ncountA = {checkA} -> {countA}")
      checkG = [is_all]
      checkG.extend([ gname for gname in gntot if gname in dlist ])
      countG = is_all or checkG.count(True) > 1
      #print(f"\ncountG = {checkG} -> {countG}")
      checkW = [is_all, 'H2O' in dlist, 'D2O' in dlist]
      incH2O = is_all or 'H2O' in dlist
      incD2O = is_all or 'D2O' in dlist

      histSG = np.zeros(nbins)
      histMG = np.zeros(nbins)
      if any(checkG):  # AB: Group contributions
         #dbinV = 4 * Pi * drange ** 2 * dbin
         for ih, hist in enumerate(hgtot):
            gchsl = 0.0
            chsl  = 0.0
            gmass = 0.0
            mass  = 0.0
            edigs = ''
            elems = gntot[ih]
            for ic in range(len(elems)):
               if elems[ic] in digits:
                  edigs += elems[ic]
                  if ic == len(elems)-1:
                     gchsl += chsl*float(edigs)
                     gmass += mass*float(edigs)
                  elif elems[ic+1] not in digits:
                     gchsl += chsl*float(edigs)
                     gmass += mass*float(edigs)
                     edigs = ''
               elif elems[ic] in emass.keys():
                  if ic == len(elems)-1:
                     gchsl += elems_csl[elems[ic]]
                     gmass += emass[elems[ic]]
                  elif elems[ic+1] not in digits:
                     gchsl += elems_csl[elems[ic]]
                     gmass += emass[elems[ic]]
                  else:
                     chsl = elems_csl[elems[ic]]
                     mass = emass[elems[ic]]

            logger.debug(f"Histogram for group '{gntot[ih]}' of {sum(hist)} counts, "
                        f"mass = {gmass}, CSL = {gchsl}:{NL_INDENT}"
                        f"{np.column_stack((drange, hist))}")

            gname = gntot[ih]
            if is_all or gname in dlist:
               np.savetxt(bname+'_hist_'+gntot[ih]+'.dat',
                           np.column_stack((drange, hist)), fmt='%-0.3f %10.7f')
               histN = hist / dbinV
               np.savetxt(bname + '_nden_' + gntot[ih] + '.dat',
                           np.column_stack((drange, histN)), fmt='%-0.3f %10.7f')
               histS   = histN * gchsl * 0.01  # * 10.0
               histSG += histS
               np.savetxt(bname + '_nsld_' + gntot[ih] + '.dat',
                           np.column_stack((drange, histS)), fmt='%-0.3f %10.7f')
               histM   = hist * gmass / dbinM
               histMG += histM
               np.savetxt(bname + '_mden_' + gntot[ih] + '.dat',
                           np.column_stack((drange, histM)), fmt='%-0.3f %10.7f')
               # histS = histN * gchsl * 6.022  / gmass
               # np.savetxt(bname + '_msld_' + gntot[ih] + '.dat',
               #             np.column_stack((drange, histS)), fmt='%-0.3f %10.7f')
         if countG:
            np.savetxt(bname + '_nsld_GRP.dat',
                        np.column_stack((drange, histSG)), fmt='%-0.3f %10.7f')
            np.savetxt(bname + '_mden_GRP.dat',
                        np.column_stack((drange, histMG)), fmt='%-0.3f %10.7f')
         logger.info(f"Overall number of groups = {ntot}")

      histSA = np.zeros(nbins)
      histMA = np.zeros(nbins)
      if any(checkA):  # AB: Atom contributions
         natot = 0
         for ih, hist in enumerate(halst):
            natot += sum(hist[1])
            logger.debug(f"Histogram for atoms '{hist[0]}' of {sum(hist[1])} counts:"
                         f"{NL_INDENT}{np.column_stack((drange, hist[1]))}")

            aname = hist[0][0]
            if is_all or aname in dlist:
               np.savetxt(bname+'_hist_'+hist[0][0]+'.dat',
                           np.column_stack((drange, hist[1])), fmt='%-0.3f %10.7f')
               histN = hist[1] / dbinV
               np.savetxt(bname+'_nden_' + hist[0][0] + '.dat',
                           np.column_stack((drange, histN)), fmt='%-0.3f %10.7f')
               histS   = histN * elems_csl[hist[0][0]] * 0.01  # * 10.0
               histSA += histS
               np.savetxt(bname + '_nsld_' + hist[0][0] + '.dat',
                           np.column_stack((drange, histS)), fmt='%-0.3f %10.7f')
               histM = hist[1] * emass[hist[0][0]] / dbinM
               histMA += histM
               np.savetxt(bname + '_mden_' + hist[0][0] + '.dat',
                           np.column_stack((drange, histM)), fmt='%-0.3f %10.7f')
         if countA:
            np.savetxt(bname + '_nsld_ATM.dat',
                        np.column_stack((drange, histSA)), fmt='%-0.3f %10.7f')
            np.savetxt(bname + '_mden_ATM.dat',
                        np.column_stack((drange, histMA)), fmt='%-0.3f %10.7f')
         logger.info(f"Overall number of atoms = {natot}")

      # AB: Water (H2O or D2O) contributions & totals
      if any(checkW):  # AB: Water contributions
      #if is_all or 'H2O' in dlist or 'D2O' in dlist:
         logger.debug(f"Histogram for waters of {sum(hwater)} counts:",
                      f"{NL_INDENT}{np.column_stack((drange, hwater))}")

         histN = hwater / dbinV
         np.savetxt(bname + '_hist_W.dat',
                     np.column_stack((drange, hwater)), fmt='%-0.3f %10.7f')
         np.savetxt(bname + '_nden_W.dat',
                     np.column_stack((drange, histN)), fmt='%-0.3f %10.7f')

         if incH2O:
         #if is_all or 'H2O' in dlist:
            histM = hwater * (2.0*emass['H'] + emass['O']) / dbinM
            np.savetxt(bname+'_mden_H2O.dat',
                        np.column_stack((drange, histM)), fmt='%-0.3f %10.7f')
            if any(checkG):
               np.savetxt(bname + '_mden_GRP-H2O.dat',
                           np.column_stack((drange, histMG+histM)), fmt='%-0.3f %10.7f')
            if any(checkA):
               np.savetxt(bname + '_mden_ATM-H2O.dat',
                           np.column_stack((drange, histMA+histM)), fmt='%-0.3f %10.7f')
            histS = histN * (2.0*elems_csl['H'] + elems_csl['O']) * 0.01  # * 10.0
            np.savetxt(bname + '_nsld_H2O.dat',
                        np.column_stack((drange, histS)), fmt='%-0.3f %10.7f')
            if any(checkG):
               np.savetxt(bname + '_nsld_GRP-H2O.dat',
                           np.column_stack((drange, histSG+histS)), fmt='%-0.3f %10.7f')
            if any(checkA):
               np.savetxt(bname + '_nsld_ATM-H2O.dat',
                           np.column_stack((drange, histSA+histS)), fmt='%-0.3f %10.7f')

         if incD2O:
         #if is_all or 'D2O' in dlist:
            histM = hwater * (2.0*emass['D'] + emass['O']) / dbinM
            np.savetxt(bname+'_mden_D2O.dat',
                        np.column_stack((drange, histM)), fmt='%-0.3f %10.7f')
            histS = histN * (2.0*elems_csl['D'] + elems_csl['O']) * 0.01  # * 10.0
            np.savetxt(bname + '_nsld_D2O.dat',
                        np.column_stack((drange, histS)), fmt='%-0.3f %10.7f')
            if any(checkG):
               np.savetxt(bname + '_nsld_GRP-D2O.dat',
                           np.column_stack((drange, histSG+histS)), fmt='%-0.3f %10.7f')
            if any(checkA):
               np.savetxt(bname + '_nsld_ATM-D2O.dat',
                           np.column_stack((drange, histSA+histS)), fmt='%-0.3f %10.7f')

         logger.info(f"Overall number of water atoms = {3*sum(hwater)}")

   #####
   return (ierr==0)

# end of read_mol_gro()

def read_box_gro(fname: str, box) :

   ierr   = 0
   nlines = 0
   #nrems  = 1

   try :
     with open(fname, mode='r', encoding = 'utf-8') as finp :
        logger.info(f"Reading GRO (box) file '{fname}' ...")
        nlines = 1
        line = finp.readline().rstrip()
        lbox = line.split()
        box.append(float(lbox[0]))
        box.append(float(lbox[1]))
        box.append(float(lbox[2]))

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
      if ierr == 0:
         logger.info(f"File '{fname}' successfully read: nlines = {nlines}")

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

   fbox = name+sbox
   finp = name+sgro
   fout = name

   script = os.path.basename(argv[0])

   try :
      opts, args = getopt.getopt(argv[1:],"h:d:b:i:o:x:s:c:a:n:r:", \
                   ["help","box=","dio=","inp=","out=","ext=",
                    "solvent=","nsatm=","cluster=","atoms=","dens=","rs="])
   except getopt.GetoptError :
      logger.error(f"Try: {script} --help")
      sys.exit(1)

   is_head = False
   is_box  = False

   nmols = 1
   molid = 1
   resnm = 'SOL'
   atoms = []
   clust = []
   radii = []
   denslist = []

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
         dinp = arg.strip()
         dout = dinp
      elif opt in ("-b", "--box") :
         is_box = True
         fbox = arg.strip()
      elif opt in ("-i", "--inp") :
         finp = arg.strip()
      elif opt in ("-o", "--out") :
         name = arg.strip()
      elif opt in ("-x", "--ext") :
         oext = arg.strip()
      elif opt in ("-s", "--solvent") :
         resnm = arg.strip()
#         names = arg.split(',')
#         if len(names) > 1:
#            resnm = str(names[0].rstrip())
#            for nm in names:
#               lnames.append(str(nm.rstrip()))
#         else:
#            resnm = str(arg.rstrip())
#            lnames.append(resnm)
      elif opt in ("-c", "--cluster") :
         clust = arg.strip().replace('[', '').replace(']', '').split(',')
#         if len(names) > 1:
#            for nm in names:
#               clust.append(str(nm.rstrip()))
#         else:
#            clust.append(str(arg.rstrip()))
      elif opt in ("-a", "--atoms") :
         atoms = arg.strip().replace('[', '').replace(']', '').split(',')
#         if len(names) > 1:
#            for nm in names:
#               clust.append(str(nm.rstrip()))
#         else:
#            clust.append(str(arg.rstrip()))
      elif opt in ("--dens") :
         #adens = arg.split(',')
         denslist = arg.strip().replace('[', '').replace(']', '').split(',')
         #adens = re.sub(r'[\[\]\(\)]', '', arg).split(',')
      elif opt in ("-r", "--rs") :
         #sradii = arg.split(',')
         #sradii = re.sub(r'[\[\]\(\)]', '', arg).split(',')
         sradii = arg.strip().replace('[', '').replace(']', '').split(',')
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
      logger.error(f"Unsupported output extension: '{oext}' [.gro/.xyz/?.pdb; N/A for "
                   "DL_POLY CONFIG]")
      sys.exit(3)
   elif len(oext)<1 and fout!='CONFIG' :
      logger.error(f"Unsupported output file-name: '{fout}' [no extension => DL_POLY "
                   "'CONFIG']")
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

         logger.info(f"Doing: input '{finp}' => output '{fout}'")

         # Reading input
         if finp[-4:]==sgro :

            if not is_box :
               import subprocess
               #subprocess.run(["ls -l", ""], shell=True)
               #subprocess.run([f"ls -l {dfinp[:-4]+sbox}", ], shell=True)
               #print(f"> ls {dfinp[:-4]+sbox}\n")
               xcode = subprocess.call("ls "+dfinp[:-4]+sbox, shell=True)
               if xcode == 0:
                  logger.info(f"Found & will use {dfinp[:-4] + sbox} as box input ...")
                  dfbox = str(dinp+'/'+dfinp[:-4]+sbox)
                  is_box = True
               else:
                  logger.info(f"Creating {dfinp[:-4] + sbox} ...")
                  rcode = subprocess.call(f"tail -n 1 {dfinp} > {dfinp[:-4]+sbox}", shell=True)
                  if rcode == 0:
                     logger.info(f"Created & will use {dfinp[:-4] + sbox} as box input "
                                 "...\n")
                     dfbox = str(dinp + '/' + dfinp[:-4] + sbox)
                     is_box = True
                  else:
                     logger.error(f"Could not create {dfinp[:-4] + sbox} as box input "
                                  "...\n")
                     sys.exit(1)

            if is_box :
               read_box_gro(dfbox, gbox)

            if len(clust) > 0 and len(radii) > 2 :
            #if len(atoms) > 0 : #or len(radii) > 1 :

               logger.info(f"Solvation analysis for atoms {atoms} in molecular cluster "
                           f"of {clust} species\n")

               # if len(atoms) != len(clust):
               #    print(f"Insufficient input for atoms: {atoms} (refer to help) - FULL STOP!\n")
               #    sys.exit(10)

               if len(radii) < 3:
                  logger.error(f"Insufficient input for radii: {radii} (refer to help) "
                               "- FULL STOP!\n")
                  sys.exit(11)

               read_mol_gro(dfinp, rems_inp, atms_inp, axyz_inp, atms_out, axyz_out, gbox, \
                            resnm, natmol, radii, clust, atoms, denslist)
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
               #      "; "+'({:>8.3f}{:>8.3f}{:>8.3f})'.format(*hbox)+"\n")

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
                         "DL_POLY CONFIG]\n")
            sys.exit(2)

         if fout[-4:]==sgro :
            #print("GRO input '"+finp+"' => GRO output '"+fout+"'\n")

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
         #   print("GRO input '"+finp+"' => XYZ output '"+fout+"'\n")
         #   write_out_xyz()
         #elif fout[-4:]==spdb :
         #   print("GRO input '"+finp+"' => PDB output '"+fout+"'\n")
         #elif fout=='CONFIG' :
         #   print("GRO input '"+finp+"' => DLP output '"+fout+"'\n")
         else:
            logger.error(f"Unrecongnised output format: '{fout}'")
            sys.exit(3)
      else:
         logger.error(f"Input file not found: '{dfinp}'")
         sys.exit(2)
   else :
      logger.error(f"Directory not found: '{dinp}'")
      sys.exit(2)

# end of main(argv)

### END OF MAIN ###


if __name__ == "__main__":
   main()
   sys.exit(0)
