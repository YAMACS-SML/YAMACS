# YASARA PLUGIN
# TOPIC:       YAMACS - System equilibration
# TITLE:       YAMACS - System equilibration
# AUTHOR:      J.Santoro, A.Sarkar
# LICENSE:     Non-Commercial
#
# This is a YASARA plugin to be placed in the /plg subdirectory
# Go to www.yasara.org/plugins for documentation and downloads

# YASARA menu entry
"""
MainMenu: YAMACS
  PullDownMenu after 1-System preparation : 2-System equilibration
    CustomWindow: YAMACS - System equilibration
      Width: 600
      Height: 400
      Text: X= 20,Y= 68,Text="Please insert all the mdp files inside the working folder:"
      Text: X= 370,Y= 170,Text="solute-box distance(nm):"
      NumberInput: X= 440,Y= 180,Text=" ",Default=1.0,Min=0,Max=10
      List: X=20,Y=140,Text="Solvation box:"
        Width=200,Height=128,MultipleSelections=No
       Options=1, Text="cubic"      
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

class cd:
    """Context manager for changing the current working directory"""
    def __init__(self, newPath):
        self.newPath = os.path.expanduser(newPath)

    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)

size= str((yasara.selection[0].number[0]))



box= str((yasara.selection[0].list))
boxtype= (box.strip('[]'))
solvationbox= (boxtype.replace("'", ""))

#step1 generation of gromacs files



scriptpath = os.path.realpath(__file__)
plgpath = os.path.normpath(scriptpath + os.sep + os.pardir)
print(plgpath)

f = open(plgpath+'/'+'temporary.ini', "r")
content= f.readlines()
macrotarget= str((content[0]).strip('\n'))
inpu=str((content[1]).strip('\n'))
mod=str((content[2]).strip('\n'))
selforce=str((content[3]).strip('\n'))
attachedobject=str((content[4]).strip('\n'))
lig=str((content[5]).strip('\n'))

wmodel = (str(mod)+'.gro')
outsol=(str(inpu)+ '_solv.gro')
input=(inpu+'_gmx.pdb')
newbox=(inpu+ '_newbox.pdb')
newboxgro=(inpu+ '_newbox.gro')
#step1 generation of gromacs files
with open(plgpath+'/'+'temporary.ini', 'w') as inifile:
  inifile.write(macrotarget+'\n')
  inifile.write(inpu+'\n')
  inifile.write(mod+'\n')
  inifile.write(selforce+'\n')
  inifile.write(attachedobject+'\n')
  inifile.write(lig+'\n')
  inifile.write(solvationbox+'\n')
  inifile.write(size+'\n')
inifile.close()


if mod == 'spce':
  grofile='spc216.gro'
  
elif mod == 'tip4p':
  grofile='tip4p.gro'
  
else :
  mod = 'tip5p'
  grofile='tip5p.gro'

#this section will write the essential md.mdp files for the simulation. But the time duration of the simulation will be written in the third plugin
md= open((macrotarget)+'/'+'md.mdp', 'w+')
md.write("title                   = OPLS Lysozyme NPT equilibration\n; Run parameters\nintegrator              = md        ; leap-frog integrator\ndt                      = 0.002     ; 2 fs\n; Output control\nnstxout                 = 0         ; suppress bulky .trr file by specifying \nnstvout                 = 0         ; 0 for output frequency of nstxout,\nnstfout                 = 0         ; nstvout, and nstfout\nnstenergy               = 5000      ; save energies every 10.0 ps\nnstlog                  = 5000      ; update log file every 10.0 ps\nnstxout-compressed      = 10000      ; save compressed coordinates every 10.0 ps\ncompressed-x-grps       = System    ; save the whole system\n; Bond parameters\ncontinuation            = yes       ; Restarting after NPT \nconstraint_algorithm    = lincs     ; holonomic constraints\nconstraints             = h-bonds   ; bonds involving H are constrained\nlincs_iter              = 1         ; accuracy of LINCS\nlincs_order             = 4         ; also related to accuracy\n; Neighborsearching\ncutoff-scheme           = Verlet    ; Buffered neighbor searching\nns_type                 = grid      ; search neighboring grid cells\nnstlist                 = 10        ; 20 fs, largely irrelevant with Verlet scheme\nrcoulomb                = 1.0       ; short-range electrostatic cutoff (in nm)\nrvdw                    = 1.0       ; short-range van der Waals cutoff (in nm)\n; Electrostatics\ncoulombtype             = PME       ; Particle Mesh Ewald for long-range electrostatics\npme_order               = 4         ; cubic interpolation\nfourierspacing          = 0.16      ; grid spacing for FFT\n; Temperature coupling is on\ntcoupl                  = V-rescale             ; modified Berendsen thermostat\ntc-grps                 = Protein Non-Protein   ; two coupling groups - more accurate\ntau_t                   = 0.1     0.1           ; time constant, in ps\nref_t                   = 300     300           ; reference temperature, one for each group, in K\n; Pressure coupling is on\npcoupl                  = Parrinello-Rahman     ; Pressure coupling on in NPT\npcoupltype              = isotropic             ; uniform scaling of box vectors\ntau_p                   = 2.0                   ; time constant, in ps\nref_p                   = 1.0                   ; reference pressure, in bar\ncompressibility         = 4.5e-5                ; isothermal compressibility of water, bar^-1\n; Periodic boundary conditions\npbc                     = xyz       ; 3-D PBC\n; Dispersion correction\nDispCorr                = EnerPres  ; account for cut-off vdW scheme\n; Velocity generation\ngen_vel                 = no        ; Velocity generation is off ")
md.close()

yasara.run("Clear")
secondpng='LoadPNG '+(plgpath)+'/'+'2.png'
yasara.run(secondpng)
yasara.run("ShowImage 1,Alpha=100,Priority=0")


if os.path.isfile((macrotarget)+'/others.txt'):
    os.chdir(str(macrotarget))
    #newbox formation of the system with a specific solute-box distance
    p = subprocess.Popen(['gmx', 'editconf', '-f', (input), '-o', (newboxgro), '-d', (size), '-bt', (solvationbox)], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    subprocess_return = p.stdout.read()
    p.communicate(b'1\n0\n')
    p.wait()
    #the below command will convert the .gro file into .pdb file
    os.system('gmx editconf -f '+(newboxgro)+' -o '+(newbox)+'')
    solvgro=(inpu+'_solv.gro')
    #solvation of the system
    d = subprocess.Popen(['gmx', 'solvate', '-cp', (newboxgro),'-cs', (grofile), '-p','topol.top', '-o', (solvgro)], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    subprocess_return2 = d.stdout.read()
    d.communicate(b'1\n0\n')
    d.wait()
    yasara.run("wait continuebutton")
    yasara.ShowMessage("Solvated system file saved in:" + macrotarget)
    yasara.run("Delobj all")
    yasara.run("Clear")
    thirdpng='LoadPNG '+(plgpath)+'/'+'3.png'
    yasara.run(thirdpng)
    yasara.run("ShowImage 1,Alpha=100,Priority=0")
    yasara.LoadPDB(str(macrotarget+'\\'+inpu+'_newbox.pdb'))
    yasara.run("ZoomAll Steps=20")
    solvpdb=(inpu+'_solv.pdb')
    print(solvpdb)
    #ion addition to the system
    ion= str(macrotarget)
    ionfile=(ion+'/ions.mdp')
    print(ionfile)
    yasara.run("Delobj all")
    time.sleep(2)
    k = subprocess.Popen(['gmx', 'grompp', '-f','ions.mdp', '-c', (solvgro), '-p', 'topol.top','-o','ions.tpr', '-maxwarn', '5'], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    subprocess_return = k.stdout.read()
    k.communicate(b'1\n0\n')
    k.wait()
    j = subprocess.Popen(['gmx', 'editconf', '-f', (solvgro), '-o', (solvpdb)], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    subprocess_return = j.stdout.read()
    j.communicate(b'1\n0\n')
    j.wait()
    yasara.LoadPDB(str(macrotarget+'\\'+inpu+'_solv.pdb'))
    yasara.run("ZoomAll Steps=20")
    time.sleep(2)
    #salt addition
    solviongro=(inpu+'_solv_ions.gro')
    solvionpdb=(inpu+'_solv_ions.pdb')
    print(solviongro)
    print(solvionpdb)
    cmd='echo 4 | gmx genion -s ions.tpr -o '+(solviongro)+' -p topol.top -pname NA -nname CL -neutral'
    os.system (cmd)
    l = subprocess.Popen(['gmx', 'editconf', '-f', (solviongro), '-o', (solvionpdb)], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    subprocess_return = l.stdout.read()
    l.communicate(b'1\n0\n')
    l.wait()
    yasara.ShowMessage("Ions addition completed")
    yasara.run("Delobj all")
    yasara.run("Clear")
    fourthpng='LoadPNG '+(plgpath)+'/'+'4.png'
    yasara.run(fourthpng)
    yasara.run("ShowImage 1,Alpha=100,Priority=0")
    yasara.LoadPDB(str(macrotarget)+'\\'+inpu+'_solv_ions.pdb')
    yasara.run("ZoomAll Steps=20")
    #Energy minimization
    minim=str(macrotarget)
    minimfile=(minim+'/em.mdp')
    print(minimfile)    
    m = subprocess.Popen(['gmx', 'grompp', '-f',(minimfile), '-c', (solviongro), '-p', 'topol.top','-o','em.tpr'], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    subprocess_return = m.stdout.read()
    m.communicate(b'1\n0\n')
    m.wait()   
    cmd='gmx mdrun -v -deffnm em'
    yasara.ShowMessage("Energy minimization in progress")
    os.system (cmd)
    yasara.ShowMessage("Energy minimization completed")   
    othersgmxinput=(inpu+'_gmx.pdb')
    othersindexoutput=(inpu+'_index.ndx')
    othersout2=(inpu+'_porse.itp')
    nvt=str(macrotarget)
    nvtfile=(nvt+'/nvt.mdp')
    npt=str(macrotarget)
    nptfile=(npt+'/npt.mdp')
    #Restraining of the system
    cmd='echo "0 & ! a H*\nq" | gmx make_ndx -f '+(othersgmxinput)+' -o ' +(othersindexoutput)
    os.system(cmd)
    yasara.ShowMessage("Attached object restraining in progress")
    cmd2='echo "3" | gmx genrestr -f '+(othersgmxinput)+' -n '+(othersindexoutput)+' -o '+(othersout2)+' -fc 1000 1000 1000'
    os.system (cmd2)
    cmd3='echo " 1 | 13" ; echo "q" | gmx make_ndx -f em.gro -o index.ndx'
    os.system (cmd3)
    f = open((str(macrotarget))+'/'+'index.ndx', 'r')
    filedata = f.read()
    f.close()
    newdata = filedata.replace('non-Water', inpu)
    f = open((str(macrotarget))+'/'+'index.ndx','w')
    f.write(newdata)
    f.close()
    yasara.run("Clear")
    fifthpng='LoadPNG '+(plgpath)+'/'+'5.png'
    yasara.run(fifthpng)
    yasara.run("ShowImage 1,Alpha=100,Priority=0")
    yasara.LoadPDB(str(macrotarget)+'\\'+inpu+'_solv_ions.pdb')
    yasara.run("ZoomAll Steps=20")
   #NVT equilibration
    b = subprocess.Popen(['gmx', 'grompp', '-f',(nvtfile), '-c', 'em.gro', '-r', 'em.gro', '-p', 'topol.top','-o','nvt.tpr', '-n', 'index.ndx','-maxwarn', '5'], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    subprocess_return = b.stdout.read()
    b.communicate(b'1\n0\n')
    b.wait()
    nvtrun='gmx mdrun -deffnm nvt'
    yasara.ShowMessage("NVT-equilibration in progress")
    os.system(nvtrun)
    os.system('echo "2" \ "0" | gmx trjconv -s nvt.tpr -f nvt.trr -o nvt.gro -pbc mol -center')
    c = subprocess.Popen(['gmx', 'editconf', '-f', 'nvt.gro', '-o', 'nvt.pdb'], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    subprocess_return = c.stdout.read()
    c.communicate(b'1\n0\n')
    c.wait()
    yasara.run("Delobj all")
    yasara.LoadPDB(str(macrotarget+'\\'+'nvt.pdb'))
    yasara.run("Delobj all")
    yasara.run("Clear")
    sixthpng='LoadPNG '+(plgpath)+'/'+'6.png'
    yasara.run(sixthpng)
    yasara.run("ShowImage 1,Alpha=100,Priority=0")
    yasara.LoadPDB(str(macrotarget+'\\'+'nvt.pdb'))
    yasara.run("ZoomAll Steps=20")
    yasara.ShowMessage("NVT-equilibration completed")
    #NPT equilibration
    e = subprocess.Popen(['gmx', 'grompp', '-f',(nptfile), '-c', 'nvt.gro', '-r', 'nvt.gro','-t', 'nvt.cpt', '-p', 'topol.top','-o','npt.tpr','-n', 'index.ndx','-maxwarn', '5'], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    subprocess_return = e.stdout.read()
    e.communicate(b'1\n0\n')
    e.wait()
    nptrun='gmx mdrun -deffnm npt'
    yasara.ShowMessage("NPT-equilibration in progress")
    os.system(nptrun)
    os.system('echo "2" \ "0" | gmx trjconv -s npt.tpr -f npt.trr -o npt.gro -pbc mol -center')
    f = subprocess.Popen(['gmx', 'editconf', '-f', 'npt.gro', '-o', 'npt.pdb'], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    subprocess_return = f.stdout.read()
    f.communicate(b'1\n0\n')
    f.wait()
    yasara.run("Delobj all")
    yasara.LoadPDB(str(macrotarget+'\\'+'npt.pdb'))
    yasara.run("ZoomAll Steps=20")
    yasara.ShowMessage("NPT-equilibration completed") 
    os.remove((macrotarget)+'/'+'md.mdp')
    mdedit= open((macrotarget)+'/'+'md.mdp', "w")
    mdedit.write('title                   = OPLS Lysozyme NPT equilibration\n; Run parameters\nintegrator              = md        ; leap-frog integrator\ndt                      = 0.002     ; 2 fs\n; Output control\nnstxout                 = 0         ; suppress bulky .trr file by specifying \nnstvout                 = 0         ; 0 for output frequency of nstxout,\nnstfout                 = 0         ; nstvout, and nstfout\nnstenergy               = 5000      ; save energies every 10.0 ps\nnstlog                  = 5000      ; update log file every 10.0 ps\nnstxout-compressed      = 10000      ; save compressed coordinates every 10.0 ps\ncompressed-x-grps       = System    ; save the whole system\n; Bond parameters\ncontinuation            = yes       ; Restarting after NPT \nconstraint_algorithm    = lincs     ; holonomic constraints\nconstraints             = h-bonds   ; bonds involving H are constrained\nlincs_iter              = 1         ; accuracy of LINCS\nlincs_order             = 4         ; also related to accuracy\n; Neighborsearching\ncutoff-scheme           = Verlet    ; Buffered neighbor searching\nns_type                 = grid      ; search neighboring grid cells\nnstlist                 = 10        ; 20 fs, largely irrelevant with Verlet scheme\nrcoulomb                = 1.0       ; short-range electrostatic cutoff (in nm)\nrvdw                    = 1.0       ; short-range van der Waals cutoff (in nm)\n; Electrostatics\ncoulombtype             = PME       ; Particle Mesh Ewald for long-range electrostatics\npme_order               = 4         ; cubic interpolation\nfourierspacing          = 0.16      ; grid spacing for FFT\n; Temperature coupling is on\ntcoupl                  = V-rescale             ; modified Berendsen thermostat\ntc-grps                 = ')
    mdedit.write(inpu)
    mdedit.write(' water   ; two coupling groups - more accurate\ntau_t                   = 0.1     0.1           ; time constant, in ps\nref_t                   = 300     300           ; reference temperature, one for each group, in K\n; Pressure coupling is on\npcoupl                  = Parrinello-Rahman     ; Pressure coupling on in NPT\npcoupltype              = isotropic             ; uniform scaling of box vectors\ntau_p                   = 2.0                   ; time constant, in ps\nref_p                   = 1.0                   ; reference pressure, in bar\ncompressibility         = 4.5e-5                ; isothermal compressibility of water, bar^-1\n; Periodic boundary conditions\npbc                     = xyz       ; 3-D PBC\n; Dispersion correction\nDispCorr                = EnerPres  ; account for cut-off vdW scheme\n; Velocity generation\ngen_vel                 = no        ; Velocity generation is off')
    mdedit.close()
##The input files for membrane must be generated through charmm-gui and should directly click on '3-MD' plugin for simulation
elif os.path.isfile((macrotarget)+'/membrane.txt'):
    yasara.ShowMessage("Please generate the input files from Charmm-gui. For information see the terminal")
    print('Generate input files of your system from charmm-gui and directly click on "3-MD" plugin')
#if the system is a protein-membrane complex developed by gromacs by using GROMOS53A6 force field, then the plugin will run by below described script

else :
#Below mentioned commands will work for protein system only
  os.chdir(macrotarget)
  os.system('gmx editconf -f '+(input)+' -o '+(newboxgro)+' -d '+(size)+' -bt '+(solvationbox)+'')
  #the above command will generate a sovation box with a specific solute-box distance(nm) that will satisfy the periodic boundary image conversion of the system
  solvpdb=(inpu+'_solv.pdb')
  solvgro=(inpu+'_solv.gro')
  newbox=(inpu+ '_newbox.pdb')
  newboxgro=(inpu+ '_newbox.gro')
  os.chdir(macrotarget)
#addition of watermolecules
  os.system('gmx solvate -cp '+(newboxgro)+' -cs '+(grofile)+' -p topol.top -o '+(solvgro)+'')
#converting '.gro' file format to '.pdb' file format  
  os.system('gmx editconf -f '+newboxgro+' -o '+newbox+'')
  os.system('gmx editconf -f '+solvgro+' -o '+solvpdb+'')


  yasara.ShowMessage("Solvated system file saved in:" + macrotarget)
  yasara.run("Delobj all")
  yasara.run("Clear")
  thirdpng='LoadPNG '+(plgpath)+'/'+'3.png'
  yasara.run(thirdpng)
  yasara.run("ShowImage 1,Alpha=100,Priority=0")
  yasara.LoadPDB(str(macrotarget+'\\'+inpu+'_newbox.pdb'))
  yasara.run("ZoomAll Steps=20")

  #step3 ion addition
  solvpdb=(inpu+'_solv.pdb')
  print(solvpdb)
  ion= str(macrotarget)
  ionfile=(ion+'/ions.mdp')
  print(ionfile)

  yasara.run("Delobj all")
  #the below command will prompt ions addition in the system. This command will use the ions.mdp file information to insert the ions in the system which will generate ions.tpr file
  def grompp(solvgro,ionf):
      with cd(macrotarget):
          p = subprocess.Popen(['gmx', 'grompp', '-f','ions.mdp', '-c', (solvgro), '-p', 'topol.top','-o','ions.tpr', '-maxwarn', '5'], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
          subprocess_return = p.stdout.read()
          p.communicate(b'1\n0\n')
          p.wait()
      p.wait()
      return (subprocess_return)

  prep=grompp(solvgro,ionfile)
  print('-------------')
  print(prep)
  yasara.LoadPDB(str(macrotarget+'\\'+inpu+'_solv.pdb'))
  yasara.run("ZoomAll Steps=20")
  

  solviongro=(inpu+'_solv_ions.gro')
  solvionpdb=(inpu+'_solv_ions.pdb')
  print(solviongro)
  print(solvionpdb)

  #By using the previously generated ions.tpr file, gromacs will insert salt (Nacl) in the system. one can change the ions type by replacing the NA and Cl
  #For more information please visit 'https://manual.gromacs.org/documentation/current/onlinehelp/gmx-genion.html'
  os.chdir(macrotarget)
  if os.path.isfile(macrotarget+'/'+lig+'.pdb'):
      os.system('echo 15 | gmx genion -s ions.tpr -o '+(solviongro)+' -p topol.top -pname NA -nname CL -neutral')
  else:
      os.system('echo 13 | gmx genion -s ions.tpr -o '+(solviongro)+' -p topol.top -pname NA -nname CL -neutral')

  os.system('gmx editconf -f '+solviongro+' -o '+solvionpdb+'')
  yasara.ShowMessage("Ions addition completed")
  yasara.run("Delobj all")
  yasara.run("Clear")
  fourthpng='LoadPNG '+(plgpath)+'/'+'4.png'
  yasara.run(fourthpng)
  yasara.run("ShowImage 1,Alpha=100,Priority=0")
  yasara.LoadPDB(str(macrotarget)+'\\'+inpu+'_solv_ions.pdb')
  yasara.run("ZoomAll Steps=20")

  #Below mentioned command is for energy minimization of the system. To do that, gromacs will use em.mdp file information
  minim=str(macrotarget)
  minimfile=(minim+'/em.mdp')
  print(minimfile)

  #Initiating energy minimization by creation 'em.tpr' file by using 'grompp' engine of gromacs.
  #For more nformation please visit 'https://manual.gromacs.org/documentation/current/onlinehelp/gmx-grompp.html'
  def emgromp(solvionpdb,minimfile):
      with cd(macrotarget):
          p = subprocess.Popen(['gmx', 'grompp', '-f','em.mdp', '-c', (solviongro), '-p', 'topol.top','-o','em.tpr', '-maxwarn', '5'], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
          subprocess_return = p.stdout.read()
          p.communicate(b'1\n0\n')
          p.wait()
      p.wait()
      return (subprocess_return)
    
  prep=emgromp(solvionpdb,minimfile)
  print(prep)

  #The below mentioned command will start the energy minimization by using the previously generated 'em.tpr' file
  def mdrun():
      with cd(macrotarget):
        cmd='gmx mdrun -v -deffnm em'
        yasara.ShowMessage("Energy minimization in progress")
        os.system (cmd)
      return ()

  em=mdrun()
  print(em)
  yasara.ShowMessage("Energy minimization completed")
  #ligand restraining
  liggmxinput=(lig+'_gmx.pdb')
  indexoutput=(lig+'_index.ndx')
  out2=(lig+'_porse.itp')
  nvt=str(macrotarget)
  nvtfile=(nvt+'/nvt.mdp')
  npt=str(macrotarget)
  nptfile=(npt+'/npt.mdp')
  os.chdir(macrotarget)
#if any heteroatoms are present along with the protein system, then one must need to restrain the hetereatoms.
#the below mentioned commands will restarin the heteroatoms  
  if os.path.isfile(liggmxinput):
      #size of the heteroatoms
      sizeoflig=os.path.getsize((macrotarget)+'/'+lig+'.pdb')
      print(sizeoflig)        
      if os.path.isfile(liggmxinput):
        # create an index group for heteroatoms that contains only its non-hydrogen atoms
        cmd='echo "0 & ! a H*\nq" | gmx make_ndx -f '+(liggmxinput)+' -o ' +(indexoutput)
        os.system(cmd)
        yasara.ShowMessage("Attached object restraining in process")
        #Then, execute the genrestr module and select this newly created index group 
        cmd2='echo "3" | gmx genrestr -f '+(liggmxinput)+' -n '+(indexoutput)+' -o '+(out2)+' -fc 1000 1000 1000'
        os.system (cmd2)
        cmd3='echo " 1 | 13" ; echo "q" | gmx make_ndx -f em.gro -o index.ndx'
        os.system (cmd3)
        #insertion of this newly created index group information in the topology file (topol.top)
        posre_old = open((macrotarget)+'/'+'topol.top')
        posre_new = open((macrotarget)+'/'+'topol1.top', "w")
        for line in posre_old:
            posre_new.write(line)
            if '#include "posre.itp"' in line:
                posre_new.write('\n')
                posre_new.write('#endif\n\n\n')
                posre_new.write('; Ligand position restraints\n#ifdef POSRES_LIG\n#include ')
                posre_new.write('"')
                posre_new.write(lig)
                posre_new.write('_porse.itp"\n\n')
        posre_old.close()
        posre_new.close()
        os.remove(macrotarget+'/topol.top')
        os.rename(macrotarget+'/topol1.top', macrotarget+'/topol.top')        
        yasara.run("Clear")
        fifthpng='LoadPNG '+(plgpath)+'/'+'5.png'
        yasara.run(fifthpng)
        yasara.run("ShowImage 1,Alpha=100,Priority=0")
        yasara.LoadPDB(str(macrotarget)+'\\'+inpu+'_solv_ions.pdb')
        yasara.run("ZoomAll Steps=20")
        #Next step is NVT equilibration. For this gromacs will use the nvt.mdp file information and will generate the nvt.tpr file by using 'grompp' engine of gromacs        
        os.system('gmx grompp -f '+(nvtfile)+' -c em.gro -r em.gro -p topol.top -n index.ndx -o nvt.tpr -maxwarn 5')
        #the below command will run the nvt equilibration
        nvtrun='gmx mdrun -deffnm nvt'
        yasara.ShowMessage("NVT-equilibration in progress")
        os.system(nvtrun)
        #the below command will convert the .gro file into .pdb file
        c = subprocess.Popen(['gmx', 'editconf', '-f', 'nvt.gro', '-o', 'nvt.pdb'], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        subprocess_return = c.stdout.read()
        c.communicate(b'1\n0\n')
        c.wait()
        yasara.run("Delobj all")
        yasara.LoadPDB(str(macrotarget+'\\'+'nvt.pdb'))
        yasara.run("Delobj all")
        yasara.run("Clear")
        sixthpng='LoadPNG '+(plgpath)+'/'+'6.png'
        yasara.run(sixthpng)
        yasara.run("ShowImage 1,Alpha=100,Priority=0")
        yasara.LoadPDB(str(macrotarget+'\\'+'nvt.pdb'))
        yasara.run("ZoomAll Steps=20")
        yasara.ShowMessage("NVT-equilibration completed")
        #Next step is NPT equilibration. For this gromacs will use the npt.mdp file information and will generate the npt.tpr file by using 'grompp' engine of gromacs    
        os.system('gmx grompp -f '+(nptfile)+' -c nvt.gro -r nvt.gro -t nvt.cpt -p topol.top -n index.ndx -o npt.tpr -maxwarn 5')
        #the below command will run the nvt equilibration
        nptrun='gmx mdrun -deffnm npt'
        yasara.ShowMessage("NPT-equilibration in progress")
        os.system(nptrun)
        #the below command will convert the .gro file into .pdb file
        f = subprocess.Popen(['gmx', 'editconf', '-f', 'npt.gro', '-o', 'npt.pdb'], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        subprocess_return = f.stdout.read()
        f.communicate(b'1\n0\n')
        f.wait()
        yasara.run("Delobj all")
        yasara.LoadPDB(str(macrotarget+'\\'+'npt.pdb'))
        yasara.run("ZoomAll Steps=20")
        yasara.ShowMessage("NPT-equilibration completed")
        yasara.plugin.end()
#if the system does not contain any heteroatoms then the plugin will follow the following commands to run the equilibration
  else :
    yasara.ShowMessage("Energy minimization completed")
    yasara.run("Clear")
    fifthpng='LoadPNG '+(plgpath)+'/'+'5.png'
    yasara.run(fifthpng)
    yasara.run("ShowImage 1,Alpha=100,Priority=0")
    yasara.LoadPDB(str(macrotarget)+'\\'+inpu+'_solv_ions.pdb')
    yasara.run("ZoomAll Steps=20")
    #Next step is NVT equilibration. For this gromacs will use the nvt.mdp file information and will generate the nvt.tpr file by using 'grompp' engine of gromacs   
    nvt=str(macrotarget)
    nvtfile=(nvt+'/nvt.mdp')
    print(nvtfile)
    
    def nvtgrompp(NVF):
        with cd(macrotarget):
            p = subprocess.Popen(['gmx', 'grompp', '-f',(NVF), '-c', 'em.gro', '-r', 'em.gro', '-p', 'topol.top','-o','nvt.tpr'], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
            subprocess_return = p.stdout.read()
            p.communicate(b'1\n0\n')
            p.wait()
        p.wait()
        return (subprocess_return)

    ##the below command will run the nvt equilibration
    def nvtmdrun():
        with cd(macrotarget):
           cmd='gmx mdrun -deffnm nvt'
           yasara.ShowMessage("NVT-equilibration in progress")
           os.system (cmd)      
        return ()


    nvt=nvtgrompp(nvtfile)
    print(nvt)


    nvtmdrun=nvtmdrun()
    print(nvtmdrun)


     #the below command will convert the .gro file into .pdb file
    def nvteditconf():
        with cd(macrotarget):
            p = subprocess.Popen(['gmx', 'editconf', '-f', 'nvt.gro', '-o', 'nvt.pdb'], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
            subprocess_return = p.stdout.read()
            p.communicate(b'1\n0\n')
            p.wait()
        p.wait()
        return (subprocess_return)
    
    prep1=nvteditconf()
    print(prep1)

    yasara.run("Delobj all")
    yasara.run("Clear")
    sixthpng='LoadPNG '+(plgpath)+'/'+'6.png'
    yasara.run(sixthpng)
    yasara.run("ShowImage 1,Alpha=100,Priority=0")
    yasara.LoadPDB(str(macrotarget+'\\'+'nvt.pdb'))
    yasara.run("ZoomAll Steps=20")
    yasara.ShowMessage("NVT-equilibration completed")
    try:
        os.remove(patname)
        os.remove(mcrpath)
    except:
        pass
    
    

    #Next step is NPT equilibration. For this gromacs will use the npt.mdp file information and will generate the npt.tpr file by using 'grompp' engine of gromacs 
    npt=str(macrotarget)
    nptfile=(npt+'/npt.mdp')
    print(nptfile)
    
    def nptgrompp(NPf):
        with cd(macrotarget):
            p = subprocess.Popen(['gmx', 'grompp', '-f',(NPf), '-c', 'nvt.gro', '-r', 'nvt.gro','-t', 'nvt.cpt', '-p', 'topol.top','-o','npt.tpr'], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
            subprocess_return = p.stdout.read()
            p.communicate(b'1\n0\n')
            p.wait()
        p.wait()
        return (subprocess_return)

    ##the below command will run the nvt equilibration
    def nptmdrun():
        with cd(macrotarget):
            cmd='gmx mdrun -deffnm npt'
            yasara.ShowMessage("NPT-equilibration in progress")
            os.system (cmd)
        return ()


    prep=nptgrompp(nptfile)
    print(prep)


    nptmdrun=nptmdrun()
    print(nptmdrun)

    #the below command will convert the .gro file into .pdb file
    def npteditconf():
        with cd(macrotarget):
            p = subprocess.Popen(['gmx', 'editconf', '-f', 'npt.gro', '-o', 'npt.pdb'], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
            subprocess_return = p.stdout.read()
            p.communicate(b'1\n0\n')
            p.wait()
        p.wait()
        return (subprocess_return)
    
    nptedit=npteditconf()
    print(nptedit)
 
    yasara.run("Delobj all")
    yasara.LoadPDB(str(macrotarget+'\\'+'npt.pdb'))
    yasara.run("ZoomAll Steps=20")
    yasara.ShowMessage("NPT-equilibration completed")
  
  
yasara.plugin.end()
