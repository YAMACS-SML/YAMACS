# YASARA PLUGIN
# TOPIC:       YAMACS - PDB2GMX
# TITLE:       YAMACS - PDB2GMX
# AUTHOR:      J.Santoro, A.Sarkar
# LICENSE:     Non-Commercial
#
# This is a YASARA plugin to be placed in the /plg subdirectory
# Go to www.yasara.org/plugins for documentation and downloads

# YASARA menu entry
"""
MainMenu: YAMACS
  PullDownMenu : 1-System preparation
    CustomWindow: YAMACS - PDB2GMX
      Width: 600
      Height: 400
      TextInput:   X= 20,Y=50,Text="Insert the working folder path",Width=150,Chars=150
      TextInput:   X= 20,Y=110,Text="Name of the system",Width=150,Chars=150
      TextInput:   X= 20,Y=165,Text="Name of the attached object",Width=150,Chars=150
      Text: X= 350,Y= 270,Text="Do you want default mdp files?"
      Text: X= 20,Y= 240,Text="Water model:"     
      RadioButtons:Options=3,Default=1
                   X=20,Y=260,Text="TIP3P"
                   X=20,Y=300,Text="TIP4P"
                   X=20,Y=350,Text="TIP5P"
      Text: X= 165,Y= 240,Text="Type of system:"
      RadioButtons:Options=3,Default=1
                   X=165,Y=260,Text="Protein"
                   X=165,Y=300,Text="Membrane"
                   X=165,Y=340,Text="Other"
      RadioButtons:Options=2,Default=1 
                   X=350,Y=295,Text="Yes"
                   X=450,Y=295,Text="No"                  
      List: X=360,Y=100,Text="Force field"
        Width=190,Height=128,MultipleSelections=No
       Options=8, Text="charmm36-mar2019"
                  Text="amber03"
                  Text="amber94"
                  Text="amber96"
                  Text="amber99"
                  Text="amber99sb"
                  Text="amber99sb-ildn"
                  Text="amberGS"
      Button:    X=542,Y=348,Text="OK"
    Request: 
"""


# YASARA functions, such as retrieving selections
import yasara
import subprocess 
import os
import time
import sys
import shutil
import pathlib
import distutils.dir_util
import urllib.request
import requests 
import zipfile
class cd:
    """Context manager for changing the current working directory"""
    def __init__(self, newPath):
        self.newPath = os.path.expanduser(newPath)

    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)

macrotarget = str((yasara.selection[0].text[0]))
inpu=str((yasara.selection[0].text[1]))
lig=str((yasara.selection[0].text[2]))
mod=(yasara.selection[0].radiobutton[2])
selforce= str((yasara.selection[0].list))
forcefield= (selforce.strip('[]'))
ff= (forcefield.replace("'", ""))
attachedobject=str((yasara.selection[0].radiobutton[1]))
mdp=str((yasara.selection[0].radiobutton[0]))
print (selforce)


if mod == 1:
  mod = 'spce'
  model = str(1)
  grofile='spc216.gro'
elif mod == 2:
  mod = 'tip4p'
  model = str(2)
  grofile='tip4p.gro'
else :
  mod = 'tip5p'
  model = str(4)
  grofile='tip5p.gro'


scriptpath = os.path.realpath(__file__)
plgpath = os.path.normpath(scriptpath + os.sep + os.pardir)
print(plgpath)
###this section provide the information about the object present along with protein
if attachedobject == str(1):
  protein= open((macrotarget)+'/'+'protein.txt', 'w+')
  protein.write("protein system")
  protein.close() 
elif attachedobject == str(2):
  membrane= open((macrotarget)+'/'+'membrane.txt', 'w+')
  membrane.write("membrane system")
  membrane.close()
else :
  others= open((macrotarget)+'/'+'others.txt', 'w+')
  others.write("others system")
  others.close()

#the temporary.ini file contains the input information  
with open(plgpath+'/'+'temporary.ini', 'w') as inifile:
  inifile.write(macrotarget+'\n')
  inifile.write(inpu+'\n')
  inifile.write(mod+'\n')
  inifile.write(ff+'\n')
  inifile.write(attachedobject+'\n')
  inifile.write(lig+'\n')
inifile.close()

input=(inpu+'.pdb')
output=(inpu+ '_gmx.pdb')


#step to move charmm force field file
yasara.run("wait continuebutton")
if ff == 'charmm36-mar2019':
  from_dir = plgpath+"/charmm36"
  to_dir = macrotarget
  distutils.dir_util.copy_tree(from_dir, to_dir)

else :
  print ("Please move the charmm36-mar2019.ff file in working directory")
#step1 generation of gromacs files
print(macrotarget)
print(input)
firstpng='LoadPNG '+(plgpath)+'/'+'1.png'
yasara.run(firstpng)
yasara.run("ShowImage 1,Alpha=100,Priority=0")
yasara.run("JoinObj All,1")
savepdb= 'SavePDB 1,'+(macrotarget)+'/'+(inpu)+'.pdb'
yasara.run(savepdb)
yasara.ShowMessage("Delete objects and atoms which are not required")
yasara.run("wait continuebutton")

#mdp file writing 
if mdp ==str(1):
  ions= open((macrotarget)+'/'+'ions.mdp', 'w+')
  ions.write("; LINES STARTING WITH ';' ARE COMMENTS\ntitle		    = Minimization	; Title of run\n\n; Parameters describing what to do, when to stop and what to save\nintegrator	    = steep		; Algorithm (steep = steepest descent minimization)\nemtol		    = 1000.0  	; Stop minimization when the maximum force < 10.0 kJ/mol\nemstep          = 0.01      ; Energy step size\nnsteps		    = 50000	  	; Maximum number of (minimization) steps to perform\n\n; Parameters describing how to find the neighbors of each atom and how to calculate the interactions\nnstlist		    = 40		    ; Frequency to update the neighbor list and long range forces\ncutoff-scheme   = Verlet\nns_type		    = grid		; Method to determine neighbor list (simple, grid)\nrlist		    = 1.0		; Cut-off for making neighbor list (short range forces)\ncoulombtype	    = cutoff	; Treatment of long range electrostatic interactions\nrcoulomb	    = 1.0		; long range electrostatic cut-off\nrvdw		    = 1.0		; long range Van der Waals cut-off\npbc             = xyz 		; Periodic Boundary Conditions")
  ions.close()

  em= open((macrotarget)+'/'+'em.mdp', 'w+')
  em.write("; LINES STARTING WITH ';' ARE COMMENTS\ntitle		    = Minimization	; Title of run\n\n; Parameters describing what to do, when to stop and what to save\nintegrator	    = steep		; Algorithm (steep = steepest descent minimization)\nemtol		    = 1000.0  	; Stop minimization when the maximum force < 10.0 kJ/mol\nemstep          = 0.01      ; Energy step size\nnsteps		    = 25000	  	; Maximum number of (minimization) steps to perform\n\n; Parameters describing how to find the neighbors of each atom and how to calculate the interactions\nnstlist		    = 1		        ; Frequency to update the neighbor list and long range forces\ncutoff-scheme   = Verlet\nns_type		    = grid		    ; Method to determine neighbor list (simple, grid)\nrlist		    = 1.2		    ; Cut-off for making neighbor list (short range forces)\ncoulombtype	    = PME		    ; Treatment of long range electrostatic interactions\nrcoulomb	    = 1.2		    ; long range electrostatic cut-off\nvdwtype         = cutoff\nvdw-modifier    = force-switch\nrvdw-switch     = 1.0\nrvdw		    = 1.2		    ; long range Van der Waals cut-off\npbc             = xyz 		    ; Periodic Boundary Conditions\nDispCorr        = no")
  em.close()

  nvt= open((macrotarget)+'/'+'nvt.mdp', 'w+')
  nvt.write("title                   = OPLS Lysozyme NVT equilibration \ndefine                  = -DPOSRES  ; position restrain the protein\n; Run parameters\nintegrator              = md        ; leap-frog integrator\nnsteps                  = 25000     ;\ndt                      = 0.002     ; 2 fs\n; Output control\nnstxout                 = 500       ; save coordinates every 1.0 ps\nnstvout                 = 500       ; save velocities every 1.0 ps\nnstenergy               = 500       ; save energies every 1.0 ps\nnstlog                  = 500       ; update log file every 1.0 ps\n; Bond parameters\ncontinuation            = no        ; first dynamics run\nconstraint_algorithm    = lincs     ; holonomic constraints \nconstraints             = h-bonds   ; bonds involving H are constrained\nlincs_iter              = 1         ; accuracy of LINCS\nlincs_order             = 4         ; also related to accuracy\n; Nonbonded settings \ncutoff-scheme           = Verlet    ; Buffered neighbor searching\nns_type                 = grid      ; search neighboring grid cells\nnstlist                 = 10        ; 20 fs, largely irrelevant with Verlet\nrcoulomb                = 1.0       ; short-range electrostatic cutoff (in nm)\nrvdw                    = 1.0       ; short-range van der Waals cutoff (in nm)\nDispCorr                = EnerPres  ; account for cut-off vdW scheme\n; Electrostatics\ncoulombtype             = PME       ; Particle Mesh Ewald for long-range electrostatics\npme_order               = 4         ; cubic interpolation\nfourierspacing          = 0.16      ; grid spacing for FFT\n; Temperature coupling is on\ntcoupl                  = V-rescale             ; modified Berendsen thermostat\ntc-grps                 = Protein Non-Protein   ; two coupling groups - more accurate\ntau_t                   = 0.1     0.1           ; time constant, in ps\nref_t                   = 300     300           ; reference temperature, one for each group, in K\n; Pressure coupling is off\npcoupl                  = no        ; no pressure coupling in NVT\n; Periodic boundary conditions\npbc                     = xyz       ; 3-D PBC\n; Velocity generation\ngen_vel                 = yes       ; assign velocities from Maxwell distribution\ngen_temp                = 300       ; temperature for Maxwell distribution\ngen_seed                = -1        ; generate a random seed")
  nvt.close()

  npt= open((macrotarget)+'/'+'npt.mdp', 'w+')
  npt.write("title                   = OPLS Lysozyme NVT equilibration \ndefine                  = -DPOSRES  ; position restrain the protein\n; Run parameters\nintegrator              = md        ; leap-frog integrator\nnsteps                  = 25000     ;\ndt                      = 0.002     ; 2 fs\n; Output control\nnstxout                 = 500       ; save coordinates every 1.0 ps\nnstvout                 = 500       ; save velocities every 1.0 ps\nnstenergy               = 500       ; save energies every 1.0 ps\nnstlog                  = 500       ; update log file every 1.0 ps\n; Bond parameters\ncontinuation            = yes       ; Restarting after NVT \nconstraint_algorithm    = lincs     ; holonomic constraints \nconstraints             = h-bonds   ; bonds involving H are constrained\nlincs_iter              = 1         ; accuracy of LINCS\nlincs_order             = 4         ; also related to accuracy\n; Nonbonded settings \ncutoff-scheme           = Verlet    ; Buffered neighbor searching\nns_type                 = grid      ; search neighboring grid cells\nnstlist                 = 10        ; 20 fs, largely irrelevant with Verlet\nrcoulomb                = 1.0       ; short-range electrostatic cutoff (in nm)\nrvdw                    = 1.0       ; short-range van der Waals cutoff (in nm)\nDispCorr                = EnerPres  ; account for cut-off vdW scheme\n; Electrostatics\ncoulombtype             = PME       ; Particle Mesh Ewald for long-range electrostatics\npme_order               = 4         ; cubic interpolation\nfourierspacing          = 0.16      ; grid spacing for FFT\n; Temperature coupling is on\ntcoupl                  = V-rescale             ; modified Berendsen thermostat\ntc-grps                 = Protein Non-Protein   ; two coupling groups - more accurate\ntau_t                   = 0.1     0.1           ; time constant, in ps\nref_t                   = 300     300           ; reference temperature, one for each group, in K\n; Pressure coupling is on\npcoupl                  = Parrinello-Rahman     ; Pressure coupling on in NPT\npcoupltype              = isotropic             ; uniform scaling of box vectors\ntau_p                   = 2.0                   ; time constant, in ps\nref_p                   = 1.0                   ; reference pressure, in bar\ncompressibility         = 4.5e-5                ; isothermal compressibility of water, bar^-1\nrefcoord_scaling        = com\n; Periodic boundary conditions\npbc                     = xyz       ; 3-D PBC\n; Velocity generation\ngen_vel                 = no        ; Velocity generation is off")
  npt.close()
else :
  yasara.ShowMessage("Please insert the mdp files inside the working directory")
  yasara.run("wait continuebutton")

os.chdir(macrotarget)
#this section is for heterogenous compounds
if os.path.isfile((macrotarget)+'/others.txt') and ff == 'charmm36-mar2019':
    #this section will generate the required mdp files for heterogenous compounds. One can edit the parameters of mdp files at this section or can provide their own mdp files
    if mdp ==str(1):
      os.remove((macrotarget)+'/'+'nvt.mdp')
      newnvt = open((macrotarget)+'/'+'nvt.mdp', "w")
      newnvt.write('title                   = OPLS Lysozyme NVT equilibration \ndefine                  = -DPOSRES  ; position restrain the protein\n')
      newnvt.write('; Run parameters\nintegrator              = md        ;leap-frog integrator\nnsteps                  = 25000     ;\ndt                      = 0.002     ; 2 fs\n')
      newnvt.write('; Output control\nnstxout                 = 500       ; update log file every 1.0 ps\n; Bond parameters\ncontinuation            = no        ; first dynamics run\n')
      newnvt.write('constraint_algorithm    = lincs     ; holonomic constraints \nconstraints             = h-bonds   ; bonds involving H are constrained\nlincs_iter              = 1         ; accuracy of LINCS\nlincs_order             = 4         ; also related to accuracy\n; Nonbonded settings \ncutoff-scheme           = Verlet    ; Buffered neighbor searching\nns_type                 = grid      ; search neighboring grid cells\nnstlist                 = 10        ; 20 fs, largely irrelevant with Verlet\nrcoulomb                = 1.0       ; short-range electrostatic cutoff (in nm)\nrvdw                    = 1.0       ; short-range van der Waals cutoff (in nm)\nDispCorr                = EnerPres  ; account for cut-off vdW scheme\n; Electrostatics\ncoulombtype             = PME       ; Particle Mesh Ewald for long-range electrostatics\npme_order               = 4         ; cubic interpolation\nfourierspacing          = 0.16      ; grid spacing for FFT\n; Temperature coupling is on\ntcoupl                  = V-rescale             ; modified Berendsen thermostat\ntc-grps                 = ')
      newnvt.write(inpu)
      newnvt.write(" water  ; two coupling groups - more accurate\ntau_t                   = 0.1     0.1           ; time constant, in ps\nref_t                   = 300     300           ; reference temperature, one for each group, in K\n; Pressure coupling is off\npcoupl                  = no        ; no pressure coupling in NVT\n; Periodic boundary conditions\npbc                     = xyz       ; 3-D PBC\n; Velocity generation\ngen_vel                 = yes       ; assign velocities from Maxwell distribution\ngen_temp                = 300       ; temperature for Maxwell distribution\ngen_seed                = -1        ; generate a random seed")
      newnvt.close()
      os.remove((macrotarget)+'/'+'npt.mdp')
      newnpt = open((macrotarget)+'/'+'npt.mdp', "w")
      newnpt.write('title                   = OPLS Lysozyme NVT equilibration \ndefine                  = -DPOSRES  ; position restrain the protein\n; Run parameters\nintegrator              = md        ; leap-frog integrator\nnsteps                  = 25000     ;\ndt                      = 0.002     ; 2 fs\n; Output control\nnstxout                 = 500       ; save coordinates every 1.0 ps\nnstvout                 = 500       ; save velocities every 1.0 ps\nnstenergy               = 500       ; save energies every 1.0 ps\nnstlog                  = 500       ; update log file every 1.0 ps\n; Bond parameters\ncontinuation            = yes       ; Restarting after NVT \nconstraint_algorithm    = lincs     ; holonomic constraints \nconstraints             = h-bonds   ; bonds involving H are constrained\nlincs_iter              = 1         ; accuracy of LINCS\nlincs_order             = 4         ; also related to accuracy\n; Nonbonded settings \ncutoff-scheme           = Verlet    ; Buffered neighbor searching\nns_type                 = grid      ; search neighboring grid cells\nnstlist                 = 10        ; 20 fs, largely irrelevant with Verlet\nrcoulomb                = 1.0       ; short-range electrostatic cutoff (in nm)\nrvdw                    = 1.0       ; short-range van der Waals cutoff (in nm)\nDispCorr                = EnerPres  ; account for cut-off vdW scheme\n; Electrostatics\ncoulombtype             = PME       ; Particle Mesh Ewald for long-range electrostatics\npme_order               = 4         ; cubic interpolation\nfourierspacing          = 0.16      ; grid spacing for FFT\n; Temperature coupling is on\ntcoupl                  = V-rescale             ; modified Berendsen thermostat\ntc-grps                 = ')
      newnpt.write(inpu)
      newnpt.write(' water   ; two coupling groups - more accurate\ntau_t                   = 0.1     0.1           ; time constant, in ps\nref_t                   = 300     300           ; reference temperature, one for each group, in K\n; Pressure coupling is on\npcoupl                  = Parrinello-Rahman     ; Pressure coupling on in NPT\npcoupltype              = isotropic             ; uniform scaling of box vectors\ntau_p                   = 2.0                   ; time constant, in ps\nref_p                   = 1.0                   ; reference pressure, in bar\ncompressibility         = 4.5e-5                ; isothermal compressibility of water, bar^-1\nrefcoord_scaling        = com\n; Periodic boundary conditions\npbc                     = xyz       ; 3-D PBC\n; Velocity generation\ngen_vel                 = no        ; Velocity generation is off')
      newnpt.close()
      
    else :
     print('Please provide the mdp files') 
    
    yasara.run("Delobj all")        
    yasara.LoadPDB((macrotarget)+'/'+inpu+'.pdb')
    #Below this point the script will generate the mol2 files of the heterogenous structure and will generate the essential .itp files of the structure by using https://www.swissparam.ch server
    #the forcefield must be charmm36, as https://www.swissparam.ch server only generate the input for charmm36 files 
    yasara.run("AddHydObj 1")
    savemol2= 'SaveMOL2 1,'+(macrotarget)+'/'+(inpu)+'.mol2,transform=Yes'
    yasara.run(savemol2)
    yasara.ShowMessage("Generation of itp file is in process by using https://www.swissparam.ch server")
    FILE_TO_SEND= macrotarget+'/'+inpu+".mol2";
    FILE_DI_OUTPUT= macrotarget+'/'+'output.html';
    ZIP_DI_OUTPUT= macrotarget+'/'+'output.zip';
    WHERE_TO_UNZIP= macrotarget


    def download_url(url, save_path, chunk_size=128):
        r = requests.get(url, stream=True)
        with open(save_path, 'wb') as fd:
            for chunk in r.iter_content(chunk_size=chunk_size):
                fd.write(chunk)
            
    print("SENDING THE FILE...")
    os.system('curl -F "MAX_FILE_SIZE=30000000"  -F "mol2Files=@'+FILE_TO_SEND+'"  -o "'+FILE_DI_OUTPUT+'" https://www.swissparam.ch/submit.php ')
    print("FILE SENT!")
    URL_TO_ANALYSE = ""
    with open(FILE_DI_OUTPUT) as reader:
        for l in reader.read().split("\n"):        
           if ("/results/" in l):
               l = l.split(">")[5].split("<")[0]
               URL_TO_ANALYSE=l
               break;
               reader.close()
    print("READING " + URL_TO_ANALYSE)
    while 1:
        response = urllib.request.urlopen(URL_TO_ANALYSE)
        data = response.read()      # a `bytes` object
        text = data.decode('utf-8')
        if ("Topology and parameters were succes" in text):
            print("complete. DOWNLOADING THE ZIP")        
            for T in text.split("\n"):
                if ("http://www.swissparam.ch/results/" in T):
                    ZIP_URL = T.split(">")[0].split("=")[2]
                    ZIP_URL = ZIP_URL.replace('"','')
                    download_url(ZIP_URL,ZIP_DI_OUTPUT)
                    print(ZIP_URL)   
                    print("UNZIPPING")
                    with zipfile.ZipFile(ZIP_DI_OUTPUT, 'r') as zip_ref:
                        zip_ref.extractall(WHERE_TO_UNZIP)
                    print("UNZIPPED") 
                    yasara.ShowMessage("itp file is generated by using https://www.swissparam.ch server")
                    time.sleep(2)
                    #below this section the script will develop the topology file (topol.top) of heterogenous compound
                    lines = [] 
                    with open((str(macrotarget))+'/'+inpu+'.itp', 'r') as fp:
                        for count, line in enumerate(fp):
                            pass
                    a=(count + 1)
                    with open((str(macrotarget))+'/'+inpu+'.itp', 'r') as fp: 
                        lines = fp.readlines()
                        for count, line in enumerate(fp):
                            pass
                        a=(count + 1) 
                        printablecontent= (lines[0:a])
                    newtop = open((macrotarget)+'/'+'topol.top', "w")  
                    newtop.write('; Include forcefield parameters\n#include "./')
                    newtop.write(ff)
                    newtop.write('.ff/forcefield.itp"\n')
                    newtop.writelines(printablecontent)
                    newtop.write('\n\n; Include water topology\n#include "./')
                    newtop.write(ff)
                    newtop.write('.ff/')
                    newtop.write(mod)
                    newtop.write('.itp"\n')
                    newtop.write('\n\n; Ligand position restraints\n#ifdef POSRES_LIG\n#include "')
                    newtop.write(inpu)
                    newtop.write('_porse.itp"\n#endif \n')
                    newtop.write('\n\n; Include topology for ions\n#include "./')
                    newtop.write(ff)
                    newtop.write('.ff/ions.itp"\n')
                    newtop.write("\n\n[ system ]\n; Name\n")
                    newtop.write(inpu)
                    newtop.write(" in water\n\n[ molecules ]\n; Compound        #mols\n")
                    newtop.write(inpu)
                    newtop.write("               1\n")
                    newtop.close()  
                    otherinput=(inpu+'.pdb')
                    otheroutput=(inpu+'_gmx.pdb') 
                    p = subprocess.Popen(['gmx', 'editconf', '-f', (otherinput), '-o', (otheroutput)], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
                    subprocess_return = p.stdout.read()
                    p.communicate(b'1\n0\n')
                    p.wait()
                    yasara.ShowMessage("GROMACS reminds you: PDB2GMX conversion is complete") 
                    yasara.plugin.end()           
            exit()
        else:
           if ("ur job is currently being performed." in text):
               print("STILL WORKING...")
           else:
               if ("Unfortunately, topology and parameters we"):
                   print("ERRORE :)")
                   print(text)
                   exit()
               else:
                   print("CANNOT HANDLE IT")
                   print(text)
                   exit()
#for amber force field
elif os.path.isfile((macrotarget)+'/others.txt'):    
    if mdp ==str(1):
      os.remove((macrotarget)+'/'+'nvt.mdp')
      newnvt = open((macrotarget)+'/'+'nvt.mdp', "w")
      newnvt.write('title                   = OPLS Lysozyme NVT equilibration \ndefine                  = -DPOSRES  ; position restrain the protein\n')
      newnvt.write('; Run parameters\nintegrator              = md        ;leap-frog integrator\nnsteps                  = 25000     ;\ndt                      = 0.002     ; 2 fs\n')
      newnvt.write('; Output control\nnstxout                 = 500       ; update log file every 1.0 ps\n; Bond parameters\ncontinuation            = no        ; first dynamics run\n')
      newnvt.write('constraint_algorithm    = lincs     ; holonomic constraints \nconstraints             = h-bonds   ; bonds involving H are constrained\nlincs_iter              = 1         ; accuracy of LINCS\nlincs_order             = 4         ; also related to accuracy\n; Nonbonded settings \ncutoff-scheme           = Verlet    ; Buffered neighbor searching\nns_type                 = grid      ; search neighboring grid cells\nnstlist                 = 10        ; 20 fs, largely irrelevant with Verlet\nrcoulomb                = 1.0       ; short-range electrostatic cutoff (in nm)\nrvdw                    = 1.0       ; short-range van der Waals cutoff (in nm)\nDispCorr                = EnerPres  ; account for cut-off vdW scheme\n; Electrostatics\ncoulombtype             = PME       ; Particle Mesh Ewald for long-range electrostatics\npme_order               = 4         ; cubic interpolation\nfourierspacing          = 0.16      ; grid spacing for FFT\n; Temperature coupling is on\ntcoupl                  = V-rescale             ; modified Berendsen thermostat\ntc-grps                 = ')
      newnvt.write(inpu)
      newnvt.write(" water  ; two coupling groups - more accurate\ntau_t                   = 0.1     0.1           ; time constant, in ps\nref_t                   = 300     300           ; reference temperature, one for each group, in K\n; Pressure coupling is off\npcoupl                  = no        ; no pressure coupling in NVT\n; Periodic boundary conditions\npbc                     = xyz       ; 3-D PBC\n; Velocity generation\ngen_vel                 = yes       ; assign velocities from Maxwell distribution\ngen_temp                = 300       ; temperature for Maxwell distribution\ngen_seed                = -1        ; generate a random seed")
      newnvt.close()
      os.remove((macrotarget)+'/'+'npt.mdp')
      newnpt = open((macrotarget)+'/'+'npt.mdp', "w")
      newnpt.write('title                   = OPLS Lysozyme NVT equilibration \ndefine                  = -DPOSRES  ; position restrain the protein\n; Run parameters\nintegrator              = md        ; leap-frog integrator\nnsteps                  = 25000     ;\ndt                      = 0.002     ; 2 fs\n; Output control\nnstxout                 = 500       ; save coordinates every 1.0 ps\nnstvout                 = 500       ; save velocities every 1.0 ps\nnstenergy               = 500       ; save energies every 1.0 ps\nnstlog                  = 500       ; update log file every 1.0 ps\n; Bond parameters\ncontinuation            = yes       ; Restarting after NVT \nconstraint_algorithm    = lincs     ; holonomic constraints \nconstraints             = h-bonds   ; bonds involving H are constrained\nlincs_iter              = 1         ; accuracy of LINCS\nlincs_order             = 4         ; also related to accuracy\n; Nonbonded settings \ncutoff-scheme           = Verlet    ; Buffered neighbor searching\nns_type                 = grid      ; search neighboring grid cells\nnstlist                 = 10        ; 20 fs, largely irrelevant with Verlet\nrcoulomb                = 1.0       ; short-range electrostatic cutoff (in nm)\nrvdw                    = 1.0       ; short-range van der Waals cutoff (in nm)\nDispCorr                = EnerPres  ; account for cut-off vdW scheme\n; Electrostatics\ncoulombtype             = PME       ; Particle Mesh Ewald for long-range electrostatics\npme_order               = 4         ; cubic interpolation\nfourierspacing          = 0.16      ; grid spacing for FFT\n; Temperature coupling is on\ntcoupl                  = V-rescale             ; modified Berendsen thermostat\ntc-grps                 = ')
      newnpt.write(inpu)
      newnpt.write(' water   ; two coupling groups - more accurate\ntau_t                   = 0.1     0.1           ; time constant, in ps\nref_t                   = 300     300           ; reference temperature, one for each group, in K\n; Pressure coupling is on\npcoupl                  = Parrinello-Rahman     ; Pressure coupling on in NPT\npcoupltype              = isotropic             ; uniform scaling of box vectors\ntau_p                   = 2.0                   ; time constant, in ps\nref_p                   = 1.0                   ; reference pressure, in bar\ncompressibility         = 4.5e-5                ; isothermal compressibility of water, bar^-1\nrefcoord_scaling        = com\n; Periodic boundary conditions\npbc                     = xyz       ; 3-D PBC\n; Velocity generation\ngen_vel                 = no        ; Velocity generation is off')
      newnpt.close()
      
    else :
     print('Please provide the mdp files')    

    if ff == 'amber03' or ff == "amber94" or ff == "amber96" or ff== "amber99" or ff=="amber99sb" or ff=="amber99sb-ildn" or ff=="amberGS":
      print('make sure antechamber and acepype is installed in the system')
      yasara.run("Delobj all")
      yasara.LoadPDB(str(macrotarget+'\\'+inpu+'.pdb'))
      yasara.run("AddHydObj 1")
      yasara.run("NameMol all,Lig")
      yasara.run("NameRes all,Lig")
      savemol2= 'SaveMOL2 1,'+(macrotarget)+'/'+(inpu)+'.mol2,transform=Yes'
      yasara.run(savemol2)
      FILe_mol2= macrotarget+'/'+inpu+".mol2"
      os.chdir(macrotarget)
      yasara.ShowMessage(("Generation of itp file is in process by using ACPYPE and ANTECHAMBER"))
      os.system('acpype -i '+(FILe_mol2)+'')
      os.chdir(macrotarget+'/'+inpu+'.acpype')
      os.remove(macrotarget+'/'+inpu+'.acpype/em.mdp')
      os.remove(macrotarget+'/'+inpu+'.acpype/md.mdp')
      os.chdir(macrotarget)
      src= macrotarget+'/'+inpu+'.acpype'
      dst=macrotarget
      distutils.dir_util.copy_tree(src,dst)
      os.rename(macrotarget+'/'+inpu+'_GMX.itp',macrotarget+'/'+inpu+'.itp')
      os.chdir(macrotarget)
      os.remove(macrotarget+'/'+inpu+'.pdb')
      os.rename(macrotarget+'/'+'sqm.pdb', macrotarget+'/'+inpu+'.pdb') 
      x=inpu+'.pdb'
      y=inpu+'_gmx.pdb'  
      othersout2=(inpu+'_porse.itp')
      lines = [] 
      with open((str(macrotarget))+'/'+inpu+'.itp', 'r') as fp:
          for count, line in enumerate(fp):
              pass
      a=(count + 1)
      with open((str(macrotarget))+'/'+inpu+'.itp', 'r') as fp: 
          lines = fp.readlines()
          for count, line in enumerate(fp):
              pass
          a=(count + 1) 
          printablecontent= (lines[0:a])
        #topology edition
      newtop = open((macrotarget)+'/'+'topol.top', "w")  
      newtop.write('; Include forcefield parameters\n#include "./')
      newtop.write(ff)
      newtop.write('.ff/forcefield.itp"\n')
      newtop.write('#include "')
      newtop.write(macrotarget)
      newtop.write('/')
      newtop.write(inpu)
      newtop.write('.itp"\n')
      newtop.write('\n\n; Include water topology\n#include "./')
      newtop.write(ff)
      newtop.write('.ff/')
      newtop.write(mod)
      newtop.write('.itp"\n')
      newtop.write('\n\n; Ligand position restraints\n#ifdef POSRES_LIG\n#include "')
      newtop.write(inpu)
      newtop.write('_porse.itp"\n#endif \n')
      newtop.write('\n\n; Include topology for ions\n#include "./')
      newtop.write(ff)
      newtop.write('.ff/ions.itp"\n')
      newtop.write("\n\n[ system ]\n; Name\n")
      newtop.write(inpu)
      newtop.write(" in water\n\n[ molecules ]\n; Compound        #mols\n")
      newtop.write(inpu)
      newtop.write("               1\n")
      newtop.close() 
      os.system('gmx editconf -f '+(x)+' -o '+(y)+'')
      yasara.ShowMessage("GROMACS reminds you: PDB2GMX conversion is complete")


##The input files for membrane must be generated through charmm-gui and should directly click on '3-MD' plugin for simulation         
elif os.path.isfile((macrotarget)+'/membrane.txt'):
    yasara.ShowMessage("Please generate the input files from Charmm-gui. For information see the terminal")
    os.remove(plgpath+'/temporary.ini')
    print('Generate input files of your system from charmm-gui and directly click on "3-MD" plugin')


#if the system is a protein system then, the below mentioned codes will generate the gromacs input of the system
else :
  def pdb2gmx(inp,out,ff):
      with cd(macrotarget):
          os.system('gmx pdb2gmx -f '+inp+' -o '+out+' -ff '+ff+' -water '+(mod)+' -ignh')
         #the above mentioned code will take the pdb file of the sytem and will generate the gromacs file of system by using specific force field and water model 
    
  prep=pdb2gmx(input,output,ff)
  print(prep)
  yasara.run("Delobj all")
  yasara.LoadPDB(str(macrotarget+'\\'+inpu+'_gmx.pdb'))
  liginput=(lig+'.pdb')
  ligoutput=(lig+'_gmx.pdb')
  os.chdir(macrotarget)
  #if there is any heteroatom present in the system, then the below window will apear and will ask for the type of the heteroatom
  if os.path.isfile(liginput):
      a=os.path.getsize((macrotarget)+'/'+lig+'.pdb')
      resultlist =\
        yasara.ShowWin("Custom","Attached object",400,250,
        "Text", 20, 50, "Please define the type of attached object",
        "RadioButtons",2,1,
                       20, 100,"Ligand",
                       200,100,"Membrane",
        "Button",      150,200," O K")
      
      attach= open((macrotarget)+'/protein.txt','w+')
      attach.write((str(resultlist)).replace("'","").replace(" ", "\n").replace("[","").replace("]","").replace(",","").replace("0",""))
      attach.close()  
      f = open((macrotarget)+'/protein.txt', "r")
      content= f.readlines()
      x = str((content[0]).strip('\n'))
      #if the heteroatom is a small molecule and forcefield is charmm36, then the script will generate the .itp file of the molecule by using https://www.swissparam.ch server
      if x == str(1) and ff == 'charmm36-mar2019':
        yasara.run("Delobj all")
        yasara.LoadPDB(str(macrotarget+'\\'+lig+'.pdb'))
        yasara.run("AddHydObj 1")
        savemol2= 'SaveMOL2 1,'+(macrotarget)+'/'+(lig)+'.mol2,transform=Yes'
        yasara.run(savemol2)
        yasara.run("wait continuebutton")
        os.remove(macrotarget+'/'+lig+'.pdb')
        
        yasara.ShowMessage("Generation of itp file is in process by using https://www.swissparam.ch server")
        FILE_TO_SEND= macrotarget+'/'+lig+".mol2";
        FILE_DI_OUTPUT= macrotarget+'/'+'output.html';
        ZIP_DI_OUTPUT= macrotarget+'/'+'output.zip';
        WHERE_TO_UNZIP= macrotarget


        def download_url(url, save_path, chunk_size=128):
            r = requests.get(url, stream=True)
            with open(save_path, 'wb') as fd:
                for chunk in r.iter_content(chunk_size=chunk_size):
                    fd.write(chunk)
            
        print("SENDING THE FILE...")
        os.system('curl -F "MAX_FILE_SIZE=30000000"  -F "mol2Files=@'+FILE_TO_SEND+'"  -o "'+FILE_DI_OUTPUT+'" https://www.swissparam.ch/submit.php ')
        print("FILE SENT!")
        URL_TO_ANALYSE = ""
        with open(FILE_DI_OUTPUT) as reader:
            for l in reader.read().split("\n"):        
               if ("/results/" in l):
                   l = l.split(">")[5].split("<")[0]
                   URL_TO_ANALYSE=l
                   break;
                   reader.close()
        print("READING " + URL_TO_ANALYSE)
        while 1:
            response = urllib.request.urlopen(URL_TO_ANALYSE)
            data = response.read()      # a `bytes` object
            text = data.decode('utf-8')
            if ("Topology and parameters were succes" in text):
                print("complete. DOWNLOADING THE ZIP")        
                for T in text.split("\n"):
                    if ("http://www.swissparam.ch/results/" in T):
                        ZIP_URL = T.split(">")[0].split("=")[2]
                        ZIP_URL = ZIP_URL.replace('"','')
                        download_url(ZIP_URL,ZIP_DI_OUTPUT)
                        print(ZIP_URL)   
                        print("UNZIPPING")
                        with zipfile.ZipFile(ZIP_DI_OUTPUT, 'r') as zip_ref:
                            zip_ref.extractall(WHERE_TO_UNZIP)
                        print("UNZIPPED") 
                        #complex formation
                        os.system('gmx editconf -f '+(liginput)+' -o '+(ligoutput)+'')
                        lines = []
                        with open(macrotarget+'/'+lig+'_gmx.pdb', 'r') as fp:
                            lines = fp.readlines()
                        with open(macrotarget+'/'+lig+'_gmx.pdb', 'w') as fp:    
                            for number, line in enumerate(lines):
                                if number not in [0, 1]:
                                   fp.write(line)
                        lines = data2 = "" 
                        with open((macrotarget)+'/'+inpu+'_gmx.pdb') as fp:
                            lines = fp.readlines()
                            lines = lines[:-1]
                        with open((macrotarget)+'/'+lig+'_gmx.pdb') as fp: 
                            data2 = fp.readlines() 
                        lines += "\n"
                        lines += data2 
                        with open ((macrotarget)+'/'+inpu+'_gmx.pdb', 'w') as fp:
                            fp.writelines(lines)
                        yasara.run("Delobj all")
                        yasara.LoadPDB(str(macrotarget+'\\'+inpu+'_gmx.pdb'))
                        yasara.ShowMessage("complex file saved in:" + macrotarget)
                        #below this section, the script will edit the topology file (topol.top) of the system and will insert heteroatom information in the topology file.
                        f_old = open((macrotarget)+'/'+'topol.top')
                        f_new = open((macrotarget)+'/'+'topol1.top', "w")
                        a =(lig+'.itp')
                        for line in f_old:
                            f_new.write(line)
                            if '/forcefield.itp"' in line:
                                f_new.write('#include ')
                                f_new.write('"')
                                f_new.write(a)
                                f_new.write('"\n')
                        f_old.close()
                        f_new.close()
                        os.remove((macrotarget)+'/'+'topol.top')
                        os.rename((macrotarget)+'/'+'topol1.top', (macrotarget)+'/'+'topol.top')
                        with open((macrotarget)+'/'+'topol.top') as read:
                            filesread= read.readlines()
                        topology= open((macrotarget)+'/'+'topol.top','w')
                        topology.writelines(filesread)
                        topology.write(lig)
                        topology.write('                 1\n')
                        topology.close()
                        yasara.ShowMessage("itp file is generated by using https://www.swissparam.ch server")
                        yasara.ShowMessage("GROMACS reminds you: PDB2GMX conversion is complete") 
                        yasara.plugin.end()

                exit()
            else:
                if ("ur job is currently being performed." in text):
                    print("STILL WORKING...")
                else:
                    if ("Unfortunately, topology and parameters we"):
                        print("ERRORE :)")
                        print(text)
                        exit()
                    else:
                        print("CANNOT HANDLE IT")
                        print(text)
                        exit()
      
      #generating input by acpype and antechamber
      elif x == str(1) and ff == 'amber03' or ff == "amber94" or ff == "amber96" or ff== "amber99" or ff=="amber99sb" or ff=="amber99sb-ildn" or ff=="amberGS":
        print('make sure antechamber and acepype is installed in the system')
        yasara.run("Delobj all")
        yasara.LoadPDB(str(macrotarget+'\\'+lig+'.pdb'))
        yasara.run("AddHydObj 1")
        yasara.run("NameMol all,Lig")
        yasara.run("NameRes all,Lig")
        savemol2= 'SaveMOL2 1,'+(macrotarget)+'/'+(lig)+'.mol2,transform=Yes'
        yasara.run(savemol2)
        FILe_mol2= macrotarget+'/'+lig+".mol2"
        os.chdir(macrotarget)
        yasara.ShowMessage(("Generation of itp file is in process by using ACPYPE and ANTECHAMBER"))
        os.system('acpype -i '+(FILe_mol2)+'')
        os.chdir(macrotarget+'/'+lig+'.acpype')
        os.remove(macrotarget+'/'+lig+'.acpype/em.mdp')
        os.remove(macrotarget+'/'+lig+'.acpype/md.mdp')
        os.chdir(macrotarget)
        src= macrotarget+'/'+lig+'.acpype'
        dst=macrotarget
        distutils.dir_util.copy_tree(src,dst)
        os.rename(macrotarget+'/'+lig+'_GMX.itp',macrotarget+'/'+lig+'.itp')
        #complex formation
        os.remove(macrotarget+'/'+lig+'.pdb')
        os.rename(macrotarget+'/'+'sqm.pdb', macrotarget+'/'+lig+'.pdb')
        with open(macrotarget+'/'+lig+'.pdb', 'r') as fp:
            data = fp.read()
        with open((macrotarget)+'/'+inpu+'_gmx.pdb') as fp:
            lines = fp.read()
        complexf= open(macrotarget+'/'+inpu+'_gmx.pdb','w')
        complexf.write(str(lines).replace('TER',data).replace('ENDMDL','TER\nENDMDL'))
        complexf.close()
        yasara.run("Delobj all")
        yasara.LoadPDB(str(macrotarget+'\\'+inpu+'_gmx.pdb'))
        yasara.run("ZoomAll Steps=20")
        yasara.ShowMessage("complex file saved in:" + macrotarget)
         #topology edition
        f_old = open((macrotarget)+'/'+'topol.top')
        f_new = open((macrotarget)+'/'+'topol1.top', "w")
        a =(lig+'.itp')
        for line in f_old:
           f_new.write(line)
           if '/forcefield.itp"' in line:
               f_new.write('#include ')
               f_new.write('"')
               f_new.write(a)
               f_new.write('"\n')
        f_old.close()
        f_new.close()
        os.remove((macrotarget)+'/'+'topol.top')
        os.rename((macrotarget)+'/'+'topol1.top', (macrotarget)+'/'+'topol.top')
        with open((macrotarget)+'/'+'topol.top') as read:
            filesread= read.readlines()
        topology= open((macrotarget)+'/'+'topol.top','w')
        topology.writelines(filesread)
        topology.write(lig)
        topology.write('                 1\n')
        topology.close()
        newcomplex=(inpu+'_gmx.pdb')
        yasara.ShowMessage("GROMACS reminds you: PDB2GMX conversion is complete")
      
      #if user wants to perform the simulation with other forcefield then user must generate the input from charmm-gui server and must directly click the third plugin
      elif x == str(2):
        yasara.ShowMessage("Please generate the input files for this specific force field from Charmm-gui")
        yasara.plugin.end()
      #if the heteroatom is a lipid(dppc) and forcefield is gromos96 53a6, then the below described script will work.
      #the script is developed by following the tutorial of 'Membrane Protein: KALP15 in DPPC'  by Prof. Justin A. Lemkul.(www.mdtutorials.com/gmx/membrane_protein/index.html)
  else :
    yasara.ShowMessage("PDB2GMX conversion is complete")   


yasara.plugin.end()

