# YASARA PLUGIN
# TOPIC:       YAMACS - MD run
# TITLE:       YAMACS - MD run
# AUTHOR:      J.Santoro, A.Nardiello, A.Sarkaar
# LICENSE:     Non-Commercial
#
# This is a YASARA plugin to be placed in the /plg subdirectory
# Go to www.yasara.org/plugins for documentation and downloads

# YASARA menu entry
"""
MainMenu: YAMACS
  PullDownMenu after 2-System equilibration : 3-MD Run
    CustomWindow: YAMACS - MD run
      Width: 600
      Height: 400
      TextInput:   X= 200,Y=100,Text="Insert your email address to receive notifications",Width=250,Chars=150
      Text: X= 20,Y= 48,Text="Please click OK to start your Molecular Dynamics simulation"
      Text: X= 200,Y= 170,Text="Time duration of simulation (ns):"
      NumberInput: X= 240,Y= 180,Text=" ",Default=1.0,Min=0,Max=1000      
      Button:      X=542,Y=348,Text="_O_ K"
    Request: 
"""
 

# YASARA functions, such as retrieving selections
import yasara
import subprocess
import os
import time                                                                 
from multiprocessing import Process
import sys
import shutil
import pathlib
import re
import distutils.dir_util
import urllib.request
import requests 
import zipfile
import smtplib


class cd:
    """Context manager for changing the current working directory"""
    def __init__(self, newPath):
        self.newPath = os.path.expanduser(newPath)
    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)
    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)

os.system('pkill gmx')
pathYasara = os.getcwd()
email = str((yasara.selection[0].text[0]))
step= ((yasara.selection[0].number[0]))
#calculation of the duration for simulation;(1ns= 500000 nsteps)
timestep=step*500000
ts=int(timestep)
#calculation of the total number of frame;(nsteps/nstxout-compressed)
ds=int(step*50)
#mdrun function
def mdxtc():
     os.chdir(macrotarget)
     #the below mentioned command will start the simulation
     os.system('gmx mdrun -c md_0_1.pdb -deffnm md_0_1 &')
     yasara.ShowMessage("MD simulation in progress. Please wait")
     yasara.run("Delobj all")
     a= 'LoadPDB '+(macrotarget)+'/npt.pdb'
     yasara.run(a) 
     yasara.run("ZoomAll Steps=20")
     time.sleep(2)
     #below this point, the plugin will calculate the size of the '.xtc' trajectory file. 
     #based on the increament of the size of .xtc file, yasara will load the xtc file in the yasara window.
     #the upgradation of the xtc file is controlled by the 'nstxout-compressed ' section of md.mdp file          
     i= 0
     while 1:
         a = os.path.getsize((macrotarget)+'/md_0_1.xtc')
         if a > 0 and i == 0: 
             sizeinit= os.path.getsize((macrotarget)+'/md_0_1.xtc')
             print(str(sizeinit))
             if sizeinit > 0:
               i= i + 1
                    
         else:
             i = i + 1
             time.sleep(5)
             b = os.path.getsize((macrotarget)+'/md_0_1.xtc')
             numeroframe= round((b/sizeinit))
             numero= (numeroframe -1)
             yasara.ShowMessage("Frame number : " + str(numero)+'..out of '+ str(ds))
             if numero > 0:
                 #yasara window will load the frame in the yasara window
                 snap= 'LoadXTC '+(macrotarget)+'/md_0_1,'+str(numero)
                 yasara.run(snap)
                 yasara.run("ZoomAll Steps=20")
                 yasara.run("HideRes sol")
                 yasara.run("HideRes Tip")
                 yasara.run("HideRes Tp3")
                 yasara.run("HideRes cl")
                 yasara.run("HideRes Na")
                 if os.path.isfile((macrotarget)+'/md_0_1.pdb'):
                  #The simulation will be stopped when 'md_0_1.pdb' will be generated in working folder
                   yasara.ShowMessage("MD simulation completed")
                   #the below section will send an email to the user after the simulation and will notify the user that the simulation is complete
                   try:
                     server = smtplib.SMTP('smtp.gmail.com', 587)
                     server.starttls()
                     server.login('yamacssml@gmail.com', 'yamacs2022')
                     server.sendmail('yamacssml@gmail.com', 
                                     ''+(email)+'',
                                     'The simulation of your system on yamacs is complete. please do the further calculation or turn off the system to reduce power consumption.')
                   except:
                      print('Simulation is complete')
                   resultlist =\
                     yasara.ShowWin("Custom","Extended simulation",400,250,
                     "Text", 20, 50, "Do you want to extend the simulation?",
                     "RadioButtons",2,1,
                                    20, 100,"Yes",
                                    200,100,"No",
                     "Button",      150,200," O K")
                   extension= open((macrotarget)+'/extension.txt','w+')
                   extension.write((str(resultlist)).replace("'","").replace(" ", "\n").replace("[","").replace("]","").replace(",","").replace("0",""))
                   extension.close()  
                   f = open((macrotarget)+'/extension.txt', "r")
                   content= f.readlines()
                   b = str((content[0]).strip('\n'))
                   if b == str(1):
                     resultlist =\
                       yasara.ShowWin("Custom","Time Duration",400,250,
                       "Text", 20, 50, "Time duration for extended simulation(ns)",
                       "NumberInput", 20, 88,"Time",1.0,0,1000,
                       "Button",      150,200," O K")
                   
                     extension= open((macrotarget)+'/extension.txt','w+')
                     extension.write((str(resultlist)).replace("'","").replace(" ", "\n").replace("[","").replace("]","").replace(",",""))
                     extension.close()
                     f = open((macrotarget)+'/extension.txt', "r")
                     content= f.readlines()
                     a = str((content[0]).strip('\n'))
                     ext=float(a)*1000
                     print(ext)
                     extds=float(a)*50
                     print(extds)
                     f = open((macrotarget)+'/extension.txt', "w")
                     f.write(str(ext).replace('.0',''))
                     f.write('\n')
                     f.write(str(extds).replace('.0',''))
                     f.close()
                     f = open((macrotarget)+'/extension.txt', "r")
                     content= f.readlines()
                     ext=str((content[0]).strip('\n'))
                     extds=str((content[1]).strip('\n'))
                     finalframe= (int(extds)+int(ds))
                     os.chdir(macrotarget)
                     os.system('gmx convert-tpr -s md_0_1.tpr -extend '+(str(ext))+' -o md_1_2.tpr')
                     os.system('gmx mdrun -deffnm md_1_2 -cpi md_0_1.cpt -noappend -c md_1_2.pdb &')
                     yasara.ShowMessage("MD simulation in progress. Please wait")
                     yasara.run("Delobj all")
                     b= 'LoadPDB '+(macrotarget)+'/npt.pdb'
                     yasara.run(b) 
                     yasara.run("ZoomAll Steps=20")
                     yasara.run("HideRes cl")
                     yasara.run("HideRes Na")
                     time.sleep(2)
                     i= 0
                     while 1:
                         a = os.path.getsize((macrotarget)+'/md_1_2.part0002.xtc')
                         if a > 0 and i == 0:
                             sizeinit= os.path.getsize((macrotarget)+'/md_1_2.part0002.xtc')
                             if sizeinit > 0:
                               i= i + 1
                         else:
                             i = i + 1
                             time.sleep(5)
                             b = os.path.getsize((macrotarget)+'/md_1_2.part0002.xtc')
                             numeroframe= round((b/sizeinit))
                             numero= (numeroframe -1)
                             yasara.ShowMessage("Frame number : " + str(numero)+'..out of '+ str(extds))
                             if numero > 0:
                                 snap= 'LoadXTC '+(macrotarget)+'/md_1_2.part0002.xtc,'+str(numero)
                                 yasara.run(snap)
                                 yasara.run("HideRes sol")
                                 yasara.run("HideRes Tip")
                                 yasara.run("HideRes Tp3")
                                 yasara.run("HideRes cl")
                                 yasara.run("HideRes Na")
                                 yasara.run("ZoomAll Steps=20")
                                 if os.path.isfile((macrotarget)+'/md_1_2.part0002.pdb'):
                                   yasara.ShowMessage("MD simulation completed")
                                   os.mkdir(macrotarget+'/prev_xtc')
                                   src= macrotarget+'/md_0_1.xtc'
                                   dst=macrotarget+'/prev_xtc'
                                   shutil.copy(src,dst)
                                   os.remove((macrotarget)+'/extension.txt')
                                   if os.path.isfile(macrotarget+'/protein.txt'):
                                     #recentering
                                     os.system('echo "1" \ "0" | gmx trjconv -s md_0_1.tpr -f md_0_1.xtc -o md_0_1.xtc -pbc mol -center')
                                     os.remove(macrotarget+'/protein.txt')
                                   elif os.path.isfile(macrotarget+'/membrane.txt'):
                                     os.remove(macrotarget+'/membrane.txt')
                                   elif os.path.isfile(macrotarget+'/others.txt'):
                                     os.system('echo "2" \ "0" | gmx trjconv -s md_0_1.tpr -f md_0_1.xtc -o md_0_1.xtc -pbc mol -center')
                                     os.remove(macrotarget+'/others.txt')
                                   elif os.path.isfile(macrotarget+'/protein-membrane.txt'):
                                     os.system('echo "1" \ "0" | gmx trjconv -s md_0_1.tpr -f md_0_1.xtc -o md_0_1.xtc -pbc mol -center')
                                     os.remove(macrotarget+'/protein-membrane.txt')
                                   else:
                                     print('Please recenter your system')
                                   os.system('gmx trjcat -f md_0_1.xtc md_1_2.part0002.xtc -o md_0_1.xtc')
                                   try:
                                      server = smtplib.SMTP('smtp.gmail.com', 587)
                                      server.starttls()
                                      server.login('yamacssml@gmail.com', 'yamacs2022')
                                      server.sendmail('yamacssml@gmail.com', 
                                                      ''+(email)+'',
                                                      'The simulation of your system on yamacs is complete. please do the further calculation or turn off the system to reduce power consumption.')
                                   except:
                                      print('Simulation is complete')
                                   if os.path.isfile(pathYasara+'/'+'temporary.ini'):                                     
                                     f=open (pathYasara+'/'+'temporary.ini','r+')
                                     content=f.readlines()
                                     f.seek(0)
                                     f.truncate()
                                     f.writelines(content[:-1])
                                     f.write(str(finalframe))
                                     yasara.plugin.end()
                                   else:
                                     f=open (pathYasara+'/'+'tempo.ini','r+')
                                     content=f.readlines()
                                     f.seek(0)
                                     f.truncate()
                                     f.writelines(content[:-1])
                                     f.write(str(finalframe))                                    
                                     yasara.plugin.end()
                   else:
                     #the non-essential files will be removed
                     if os.path.isfile(macrotarget+'/protein.txt'):
                       #recentering
                       os.system('echo "1" \ "0" | gmx trjconv -s md_0_1.tpr -f md_0_1.xtc -o md_0_1.xtc -pbc mol -center')
                       os.remove(macrotarget+'/protein.txt')
                     elif os.path.isfile(macrotarget+'/membrane.txt'):
                       os.remove(macrotarget+'/membrane.txt')
                     elif os.path.isfile(macrotarget+'/others.txt'):
                       os.system('echo "2" \ "0" | gmx trjconv -s md_0_1.tpr -f md_0_1.xtc -o md_0_1.xtc -pbc mol -center')
                       os.remove(macrotarget+'/others.txt')
                     elif os.path.isfile(macrotarget+'/protein-membrane.txt'):
                       os.system('echo "1" \ "0" | gmx trjconv -s md_0_1.tpr -f md_0_1.xtc -o md_0_1.xtc -pbc mol -center')
                       os.remove(macrotarget+'/protein-membrane.txt')
                     else :
                       print('please recenter your system') 
                     yasara.plugin.end()


#the temporary.ini file contains information about input files. if this file is present in the plg folder of yasara, then the plugin will prompt the simulation
if os.path.isfile(((pathYasara)+"/temporary.ini")):
  f = open((pathYasara)+"/temporary.ini", "r")
  content = f.readlines()
  macrotarget = str((content[0]).strip('\n'))
  inpu=str((content[1]).strip('\n'))
  lig=str((content[2]).strip('\n'))
  mod=str((content[3]).strip('\n'))
  selforce=str((content[4]).strip('\n'))
  size=str((content[5]).strip('\n'))
  md = str(macrotarget)
  print (macrotarget)
  endfile = pathlib.Path("md_0_1_prev.cpt")
  #the temporary.ini file will write down the time duration of the simulation and the number of frame that will be generated during simulation
  with open(pathYasara+'/'+'temporary.ini', 'w') as inifile:
    inifile.write(macrotarget+'\n')
    inifile.write(inpu+'\n')
    inifile.write(lig+'\n')
    inifile.write(mod+'\n')
    inifile.write(selforce+'\n')
    inifile.write(size+'\n')
    inifile.write("nsteps= ")
    inifile.write((str(ts))+';\n')
    inifile.write((str(ds)))
  inifile.close()
#the information regarding time duration is inserted in the md.mdp file which will be used to run the the simulation
  lines = data2 = "" 
  with open((macrotarget)+'/'+'md.mdp', 'r+') as f:
      lines= f.read()
      f.write('\n')
      f.write("nsteps= ")
      f.write((str(ts))+';\n')
    
  #the temporary.ini file will be moved to the working directory
  from_dir=(pathYasara+'/'+'temporary.ini')
  to_dir=((macrotarget)+'/'+'temporary.ini')
  shutil.move(from_dir,to_dir)
  yasara.run("Clear")
  seventhpng='LoadPNG '+(pathYasara)+'/'+'7.png'
  yasara.run(seventhpng)
  yasara.run("ShowImage 1,Alpha=100,Priority=0")
  #the next part is formation of md_0_1.tpr file to run the simulation. For that Gromacs will use 'grompp' engine.
  #For more information please visit 'https://manual.gromacs.org/documentation/current/onlinehelp/gmx-grompp.html'
  if os.path.isfile(macrotarget+'/index.ndx'):
    #if any heteroatom is present in the system then the command will use the restrained file (index.ndx) information for simulation
    os.chdir(macrotarget)
    os.system('gmx grompp -f md.mdp -c npt.gro -t npt.cpt -p topol.top -n index.ndx -o md_0_1.tpr -maxwarn 5')
  
  else :
    #if only protein system is present, then the below mentioned command will initiate the simulation 
    os.chdir(macrotarget)
    os.system('gmx grompp -f md.mdp -c npt.gro -t npt.cpt -p topol.top -o md_0_1.tpr -maxwarn 5')
  mdxtc()
    

#below this section will only work for a yasara input system with a specific simcell size which can be indicated through yasara
#make sure that 'temporary.ini' file is not present in yasara plg folder, if it is present then the below mentioned window will not appear
else:
  #deleting ions
  yasara.run('DelRes CIM CIP')
  #background image
  eightpng='LoadPNG '+(pathYasara)+'/'+'8.png'
  yasara.run(eightpng)
  yasara.run("ShowImage 1,Alpha=100,Priority=0")
  cell=yasara.run('Cell')
  resultlist =\
    yasara.ShowWin("Custom","YAMACS - MD run",600,400,
    "TextInput", 20, 48,"Please insert the path of working folder",150,150, 
    "TextInput", 20, 110,"Name of the system",150,150,
    "TextInput", 20, 165,"Name of the attached object",150,150, 
    "Text", 350, 240, "Do you want default mdp files?",
    "Text", 20, 240, "Water model:",
    "RadioButtons",3,1,
                   20, 260,"TIP3P",
                   20, 300,"TIP4P",
                   20, 350,"TIP5P",
    "Text", 180, 240, "System:",
    "RadioButtons",3,1,
                   165, 260,"Protein",
                   165, 300,"Membrane",
                   165, 340,"Others",
    "RadioButtons",2,1,
                    350, 295,"Yes",
                    450, 295,"No",    
    "List",        360,70,"Force field",190,128,"No",                 
                   8,     "charmm36",
                          "amber3",
                          "amber94",
                          "amber96",
                          "amber99",
                          "amber99sb",
                          "amber99sb-ildn",
                          "amberGS",
    "Button",      542,348," O K")

  scriptpath = os.path.realpath(__file__)
  pathYasara = os.path.normpath(scriptpath + os.sep + os.pardir)
  temp= open((pathYasara)+'/'+'tempo.ini', 'w+')
  temp.write((str(resultlist)).replace("'","").replace(" ", "\n").replace("[","").replace("]","").replace(",","").replace("0",""))
  temp.write('\n')
  temp.write(str(ds))
  temp.close()

  del_line = 7
  with open((pathYasara)+'/'+'tempo.ini', 'r') as fr:
      list = list(fr)
      del list[del_line - 1]
 
  with open((pathYasara)+'/'+'tempo.ini', 'w') as fr:
      for n in list:
          fr.write(n)

#the tempo.ini contains the input file information
  f = open(pathYasara+'/'+'tempo.ini', "r")
  content= f.readlines()
  macrotarget= str((content[0]).strip('\n'))
  inpu=str((content[1]).strip('\n'))
  lig=str((content[2]).strip('\n'))
  mod=str((content[3]).strip('\n'))
  system=str((content[4]).strip('\n'))
  mdp=str((content[5]).strip('\n'))
  ff=str((content[6]).strip('\n'))
  #ts=str((content[7]).strip('\n'))
  ds=str((content[7]).strip('\n'))


##water model
  if mod == str(1):
    mod = 'spce'
    model = str(1)
    grofile= 'spc216.gro'
  elif mod == str(2):
    mod = 'tip4p'
    model = str(2)
    grofile='tip4p.gro'
  elif mod == str(3):
    mod = 'tip5p' 
    model = str(4) 
    grofile='tip5p.gro'
  else:
    print('please selet water model')  
#system  
  if system == str(1):
    system = 'protein'
    txt=open((macrotarget)+'/'+'protein.txt','w')
    txt.write('protein')
    txt.close()
 
  elif system == str(2):
    system = 'membrane'
    txt=open((macrotarget)+'/'+'membrane.txt','w')
    txt.write('membrane')
    txt.close()

  else :
    txt=open((macrotarget)+'/'+'others.txt','w')
    txt.write('others')
    txt.close()
##forcefield
  if ff == 'charmm36':
    from_dir = pathYasara+"/charmm36"
    to_dir = macrotarget
    distutils.dir_util.copy_tree(from_dir, to_dir)
    ff='charmm36-mar2019'

  elif ff == 'amber3':
      ff = 'amber03'
  else :
    print ("Please keep the force field files in working diractory")
 #the simcell size information of yasara input will be noted down at 'cellinfo.txt' file
  cellinfo= open(macrotarget+'/cellinfo.txt', 'w+')
  cellinfo.write(str(cell).replace('Cell size is','').replace('A,','').replace('alpha=90.00, beta=90.00, gamma=90.00, center at 20.34/20.34/20.34, volume 67270.17 A^3','').replace('[','').replace(']','').replace('x','').replace(', ','\n'))
  cellinfo.close()

  f = open(macrotarget+'/cellinfo.txt', "r")
  content= f.readlines()
  x= str((content[0]).strip('\n'))
  y=str((content[1]).strip('\n'))
  z=str((content[2]).strip('\n'))
  print(x)
  print(y)
  print(z)
  
  cellx=float(x)*0.1 
  celly=float(y)*0.1 
  cellz=float(z)*0.1
  print(cellx)
  print(celly)
  print(cellz)
  yasara.run("DelObj SimCell") 
  
  
  #inputs
  pinput=(inpu+'_protein.pdb')
  poutput=(inpu+'_gmx.pdb')
  newbox=(inpu+ '_newbox.gro')
  wmodel = (str(mod)+'.gro')
  liginput=(lig+'.pdb')
  solvgro=(inpu+'_solv.gro')
  solviongro=(inpu+'_solv_ions.gro')
  solvionpdb=(inpu+'_solv_ions.pdb')
  nvtfile= ((macrotarget)+'/nvt.mdp')
  nptfile= ((macrotarget)+'/npt.mdp')
  otherinput=(inpu+'.pdb')
  
  
   #commands will be used for gromacs
    
  pdb2gmx= 'gmx pdb2gmx -f '+pinput+' -o '+poutput+' -ff '+ff+' -water '+(mod)+' -ignh'
  newboxformation='gmx editconf -f '+(poutput)+' -o '+(newbox)+' -box '+(str(cellx))+' '+(str(celly))+' '+(str(cellz))+' -bt cubic'
  solvgroformation='gmx solvate -cp '+(newbox)+' -cs '+(grofile)+' -p topol.top -o '+(solvgro)+''
  ionstpr='gmx grompp -f ions.mdp -c '+(solvgro)+' -p topol.top -o ions.tpr  -maxwarn 5'
  salt='echo 15 | gmx genion -s ions.tpr -o '+(solviongro)+' -p topol.top -pname NA -nname CL -neutral'
  energy='gmx grompp -f em.mdp  -c '+(solviongro)+' -p topol.top -o em.tpr -maxwarn 5'
  runenergy='gmx mdrun -v -deffnm em'
  nvttpr='gmx grompp -f nvt.mdp -c em.gro -r em.gro -p topol.top -o nvt.tpr -maxwarn 5'
  runnvt='gmx mdrun -deffnm nvt'
  npttpr='gmx grompp -f npt.mdp -c nvt.gro -r nvt.gro -t nvt.cpt -p topol.top -o npt.tpr -maxwarn 5'
  runnpt='gmx mdrun -deffnm npt'
  mdtpr='gmx grompp -f md.mdp -c npt.gro -t npt.cpt -p topol.top -o md_0_1.tpr'
  complexnvt='gmx grompp -f '+(nvtfile)+' -c em.gro -r em.gro -p topol.top -n index.ndx -o nvt.tpr -maxwarn 5'
  complexnpt='gmx grompp -f '+(nptfile)+' -c nvt.gro -r nvt.gro -t nvt.cpt -p topol.top -n index.ndx -o npt.tpr -maxwarn 5'
  complexmdtpr='gmx grompp -f md.mdp -c npt.gro -t npt.cpt -p topol.top -n index.ndx -o md_0_1.tpr'
  otherfile='gmx editconf -f '+(otherinput)+' -o '+(poutput)+''  
 #mdrun commands

  #loading of background images
  ##yasara.run("Clear")
  #ninepng='LoadPNG '+(pathYasara)+'/'+'9.png'
  #yasara.run(ninepng)
  #yasara.run("ShowImage 1,Alpha=100,Priority=0")
  
  #generation of mdp files
  if os.path.isfile(macrotarget+'/protein.txt'):
    #protein separation
    #yasara.ShowMessage("If it is a membrane protein system, please delete all water molecules")
    yasara.run('DelMol sol')
    yasara.run('DelRes sol')
    yasara.run('DelRes hoh')
    yasara.run('DelRes Tip')
    yasara.run('DelRes Tp3')
    yasara.run("JoinObj All,1")
    s=yasara.run("CountMol all")
    savepdb= 'SavePDB 1,'+(macrotarget)+'/'+(inpu)+'.pdb'
    yasara.run(savepdb)
    yasara.run("Delobj all")
    deltext= open(macrotarget+'/deltext.txt','w')
    deltext.write(str(s).replace('molecule(s) match the selection.','').replace('[','').replace(']',''))
    deltext.close()
    g = open((macrotarget)+"/deltext.txt", "r")
    content = g.readlines()
    heteroatom=str((content[0]).strip('\n'))
    renameheteroatom='NameMol '+ str(heteroatom)+',L'
    yasara.run("Clear")
    yasara.LoadPDB((macrotarget)+'/'+(inpu)+'.pdb')
    yasara.ShowMessage("Please separate the attached object and save as pdb file in the working directory")
    yasara.run("wait continuebutton")
    yasara.run("Delobj all")
    #background image
    eightpng='LoadPNG '+(pathYasara)+'/'+'8.png'
    yasara.run(eightpng)
    yasara.run("ShowImage 1,Alpha=100,Priority=0")
    yasara.LoadPDB((macrotarget)+'/'+(inpu)+'.pdb')
    if os.path.isfile(macrotarget+'/'+liginput) :
      yasara.run(renameheteroatom)
      yasara.run('DelMol L')
    else:
      print('apo-protein system')
    ###yasara.run("Clear")
    os.remove(macrotarget+"/deltext.txt")
    yasara.run("JoinObj All,1")
    savepdb= 'SavePDB All,'+(macrotarget)+'/'+(inpu)+'_protein.pdb'
    yasara.run(savepdb)
    yasara.run("Delobj all")
    ###yasara.run("Clear")
    yasara.LoadPDB((macrotarget)+'/'+(inpu)+'.pdb')
    os.chdir(macrotarget)
    os.system(pdb2gmx)
    if mdp ==str(1):
      md= open((macrotarget)+'/'+'md.mdp', 'w+')
      md.write("title                   = OPLS Lysozyme NPT equilibration\n; Run parameters\nintegrator              = md        ; leap-frog integrator\ndt                      = 0.002     ; 2 fs\n; Output control\nnstxout                 = 0         ; suppress bulky .trr file by specifying \nnstvout                 = 0         ; 0 for output frequency of nstxout,\nnstfout                 = 0         ; nstvout, and nstfout\nnstenergy               = 5000      ; save energies every 10.0 ps\nnstlog                  = 5000      ; update log file every 10.0 ps\nnstxout-compressed      = 10000       ; save compressed coordinates every 10.0 s\ncompressed-x-grps       = System    ; save the whole system\n; Bond parameters\ncontinuation            = yes       ; Restarting after NPT \nconstraint_algorithm    = lincs     ; holonomic constraints\nconstraints             = h-bonds   ; bonds involving H are constrained\nlincs_iter              = 1         ; accuracy of LINCS\nlincs_order             = 4         ; also related to accuracy\n; Neighborsearching\ncutoff-scheme           = Verlet    ; Buffered neighbor searching\nns_type                 = grid      ; search neighboring grid cells\nnstlist                 = 10        ; 20 fs, largely irrelevant with Verlet scheme\nrcoulomb                = 1.0       ; short-range electrostatic cutoff (in nm)\nrvdw                    = 1.0       ; short-range van der Waals cutoff (in nm)\n; Electrostatics\ncoulombtype             = PME       ; Particle Mesh Ewald for long-range electrostatics\npme_order               = 4         ; cubic interpolation\nfourierspacing          = 0.16      ; grid spacing for FFT\n; Temperature coupling is on\ntcoupl                  = V-rescale             ; modified Berendsen thermostat\ntc-grps                 = Protein Non-Protein   ; two coupling groups - more accurate\ntau_t                   = 0.1     0.1           ; time constant, in ps\nref_t                   = 300     300           ; reference temperature, one for each group, in K\n; Pressure coupling is on\npcoupl                  = Parrinello-Rahman     ; Pressure coupling on in NPT\npcoupltype              = isotropic             ; uniform scaling of box vectors\ntau_p                   = 2.0                   ; time constant, in ps\nref_p                   = 1.0                   ; reference pressure, in bar\ncompressibility         = 4.5e-5                ; isothermal compressibility of water, bar^-1\n; Periodic boundary conditions\npbc                     = xyz       ; 3-D PBC\n; Dispersion correction\nDispCorr                = EnerPres  ; account for cut-off vdW scheme\n; Velocity generation\ngen_vel                 = no        ; Velocity generation is off \nnsteps= ")
      md.write(str(ts))
      md.close()
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
      yasara.ShowMessage("Please put the Gromacs mdp files inside the working directory")
#if user developed the inputs from charmm-gui, then this below mentioned window will appear
#user must need to keep the extracte charmm-gui folder in the working directory
    if os.path.isdir(macrotarget+'/charmm-gui'):
      resultlist =\
        yasara.ShowWin("Custom","YAMACS - MD run",400,250,
        "Text", 20, 50, "Attached object",
        "RadioButtons",2,1,
                       20, 100,"Others",
                       200,100,"Membrane",
        "Button",      150,200," O K")
      
      attach= open((macrotarget)+'/protein.txt','w+')
      attach.write((str(resultlist)).replace("'","").replace(" ", "\n").replace("[","").replace("]","").replace(",","").replace("0",""))
      attach.close()  
      f = open((macrotarget)+'/protein.txt', "r")
      content= f.readlines()
      a = str((content[0]).strip('\n'))
      if a == str(1):
        #the extraction of gromacs charmm-gui files at the working directory
        brr = os.listdir(macrotarget + '/charmm-gui')
        innerfolder= (str(brr).replace('[','').replace("'", "").replace("]", "").replace(",", "\n"))
        print(innerfolder)
        arr = os.listdir(macrotarget+'/charmm-gui/'+innerfolder+'/gromacs/toppar')
        from_dir = macrotarget+'/charmm-gui/'+innerfolder+'/gromacs'
        to_dir = macrotarget
        distutils.dir_util.copy_tree(from_dir, to_dir)
        yasara.run('Delobj all')
        ##yasara.run('clear')
        yasara.LoadPDB(str(macrotarget+'/step3_input.pdb'))
        yasara.run("Hideres Tp3")
        yasara.run("ZoomAll Steps=20")
        #edition of step5_production.mdp file to set the time duration of simulation
        if mdp == str(1):          
          os.remove(macrotarget+'/step5_production.mdp')
          production= open(macrotarget+'/step5_production.mdp', 'w')
          production.write("title                   = OPLS Lysozyme NPT equilibration\n; Run parameters\nintegrator              = md        ; leap-frog integrator\ndt                      = 0.002     ; 2 fs\n; Output control\nnstxout                 = 0         ; suppress bulky .trr file by specifying \nnstvout                 = 0         ; 0 for output frequency of nstxout,\nnstfout                 = 0         ; nstvout, and nstfout\nnstenergy               = 5000      ; save energies every 10.0 ps\nnstlog                  = 5000      ; update log file every 10.0 ps\nnstxout-compressed      = 10000       ; save compressed coordinates every 10.0 s\ncompressed-x-grps       = System    ; save the whole system\n; Bond parameters\ncontinuation            = yes       ; Restarting after NPT \nconstraint_algorithm    = lincs     ; holonomic constraints\nconstraints             = h-bonds   ; bonds involving H are constrained\nlincs_iter              = 1         ; accuracy of LINCS\nlincs_order             = 4         ; also related to accuracy\n; Neighborsearching\ncutoff-scheme           = Verlet    ; Buffered neighbor searching\nns_type                 = grid      ; search neighboring grid cells\nnstlist                 = 10        ; 20 fs, largely irrelevant with Verlet scheme\nrcoulomb                = 1.0       ; short-range electrostatic cutoff (in nm)\nrvdw                    = 1.0       ; short-range van der Waals cutoff (in nm)\n; Electrostatics\ncoulombtype             = PME       ; Particle Mesh Ewald for long-range electrostatics\npme_order               = 4         ; cubic interpolation\nfourierspacing          = 0.16      ; grid spacing for FFT\n; Temperature coupling is on\ntcoupl                  = V-rescale             ; modified Berendsen thermostat\ntc_grps                 = SOLU SOLV\ntau_t                   = 1.0 1.0\nref_t                   = 303.15 303.15\n; Pressure coupling is on\npcoupl                  = Parrinello-Rahman     ; Pressure coupling on in NPT\npcoupltype              = isotropic             ; uniform scaling of box vectors\ntau_p                   = 2.0                   ; time constant, in ps\nref_p                   = 1.0                   ; reference pressure, in bar\ncompressibility         = 4.5e-5                ; isothermal compressibility of water, bar^-1\n; Periodic boundary conditions\npbc                     = xyz       ; 3-D PBC\n; Dispersion correction\nDispCorr                = EnerPres  ; account for cut-off vdW scheme\n; Velocity generation\ngen_vel                 = no        ; Velocity generation is off \nnsteps= ")
          production.write(str(ts))
          production.close()
          #edition of step4.1_equilibration.mdp file to set the steps for equilibration
          os.remove(macrotarget+'/step4.1_equilibration.mdp')
          equil= open(macrotarget+'/step4.1_equilibration.mdp', 'w')
          equil.write("define                  = -DPOSRES -DPOSRES_FC_BB=400.0 -DPOSRES_FC_SC=40.0\nintegrator              = md\ndt                      = 0.001\nnsteps                  = 2500\nnstxtcout               = 5000\nnstvout                 = 5000\nnstfout                 = 5000\nnstcalcenergy           = 100\nnstenergy               = 1000\nnstlog                  = 1000\n;\ncutoff-scheme           = Verlet\nnstlist                 = 20\nrlist                   = 1.2\nvdwtype                 = Cut-off\nvdw-modifier            = Force-switch\nrvdw_switch             = 1.0\nrvdw                    = 1.2\ncoulombtype             = PME\nrcoulomb                = 1.2\n;\ntcoupl                  = Nose-Hoover\ntc_grps                 = SOLU SOLV\ntau_t                   = 1.0 1.0\nref_t                   = 303.15 303.15\n;\nconstraints             = h-bonds\nconstraint_algorithm    = LINCS\n;\nnstcomm                 = 100\ncomm_mode               = linear\ncomm_grps               = SOLU SOLV\n;\ngen-vel                 = yes\ngen-temp                = 303.15\ngen-seed                = -1")
          equil.close()
        else :
          yasara.ShowMessage("Please put the Gromacs mdp files inside the working directory")
        ##below this point nothing is required to change
        os.chdir(macrotarget)
        yasara.ShowMessage(("System optimization in progress. Please wait"))
        # energy minimization step
        os.system('gmx grompp -f step4.0_minimization.mdp -o step4.0_minimization.tpr -c step3_input.gro -r step3_input.gro -p topol.top -n index.ndx -maxwarn 5')
        os.system('gmx mdrun -c step4.0_minimization.pdb -v -deffnm step4.0_minimization')
        yasara.run('Delobj all')
        ##yasara.run('clear')
        yasara.ShowMessage(("System optimization in progress. Please wait"))
        yasara.LoadPDB(str(macrotarget+'/step4.0_minimization.pdb'))
        yasara.run("ZoomAll Steps=20")
        yasara.run("HideRes cl")
        yasara.run("HideRes Na")
        #equilibration step
        os.system('gmx grompp -f step4.1_equilibration.mdp -o npt.tpr  -c step4.0_minimization.pdb -r step3_input.gro -p topol.top -n index.ndx -maxwarn 5')
        os.system('gmx mdrun -c npt.pdb -v -deffnm npt')
        #mdrun step
        os.system('gmx grompp -f step5_production.mdp -o md_0_1.tpr  -c npt.pdb -r step3_input.gro -p topol.top -n index.ndx -maxwarn 5')
        yasara.run('Delobj all')
        #yasara.run('clear')
        yasara.ShowMessage(("System optimization in progress. Please wait"))
        yasara.LoadPDB(str(macrotarget+'/npt.pdb'))
        yasara.run("ZoomAll Steps=20")
        yasara.run("HideRes cl")
        yasara.run("HideRes Na")
        mdxtc()         
      else :
        #if the input of charmm-gui is a membrane system, then the gromacs charmm-gui file will be extracted at working directory
        brr = os.listdir(macrotarget + '/charmm-gui')
        innerfolder= (str(brr).replace('[','').replace("'", "").replace("]", "").replace(",", "\n"))
        print(innerfolder)
        arr = os.listdir(macrotarget+'/charmm-gui/'+innerfolder+'/gromacs/toppar')
        from_dir = macrotarget+'/charmm-gui/'+innerfolder+'/gromacs'
        to_dir = macrotarget
        distutils.dir_util.copy_tree(from_dir, to_dir)
        yasara.run('Delobj all')
        #yasara.run('clear')
        yasara.LoadPDB(str(macrotarget+'/step5_input.pdb'))
        yasara.run("ZoomAll Steps=20")
        #edition of step6.0_minimization.mdp file to set the steps for minimization
        os.remove(macrotarget+'/step6.0_minimization.mdp')
        newem= open(macrotarget+'/step6.0_minimization.mdp','w')
        newem.write("define                  = -DPOSRES -DPOSRES_FC_BB=4000.0 -DPOSRES_FC_SC=2000.0 -DPOSRES_FC_LIPID=1000.0 -DDIHRES -DDIHRES_FC=1000.0\nintegrator              = steep\nemtol                   = 1000.0\nnsteps                  = 2500\nnstlist                 = 10\ncutoff-scheme           = Verlet\nrlist                   = 1.2\nvdwtype                 = Cut-off\nvdw-modifier            = Force-switch\nrvdw_switch             = 1.0\nrvdw                    = 1.2\ncoulombtype             = PME\nrcoulomb                = 1.2\n;\nconstraints             = h-bonds\nconstraint_algorithm    = LINCS")
        newem.close()
        if mdp== str(1):
          #edition of step7_production.mdp file to set the steps for md production
          os.remove(macrotarget+'/step7_production.mdp')
          production= open(macrotarget+'/step7_production.mdp', 'w')
          production.write("title                   = OPLS Lysozyme NPT equilibration\n; Run parameters\nintegrator              = md        ; leap-frog integrator\ndt                      = 0.002     ; 2 fs\n; Output control\nnstxout                 = 0         ; suppress bulky .trr file by specifying \nnstvout                 = 0         ; 0 for output frequency of nstxout,\nnstfout                 = 0         ; nstvout, and nstfout\nnstenergy               = 5000      ; save energies every 10.0 ps\nnstlog                  = 5000      ; update log file every 10.0 ps\nnstxout-compressed      = 10000       ; save compressed coordinates every 10.0 s\ncompressed-x-grps       = System    ; save the whole system\n; Bond parameters\ncontinuation            = yes       ; Restarting after NPT \nconstraint_algorithm    = lincs     ; holonomic constraints\nconstraints             = h-bonds   ; bonds involving H are constrained\nlincs_iter              = 1         ; accuracy of LINCS\nlincs_order             = 4         ; also related to accuracy\n; Neighborsearching\ncutoff-scheme           = Verlet    ; Buffered neighbor searching\nns_type                 = grid      ; search neighboring grid cells\nnstlist                 = 10        ; 20 fs, largely irrelevant with Verlet scheme\nrcoulomb                = 1.0       ; short-range electrostatic cutoff (in nm)\nrvdw                    = 1.0       ; short-range van der Waals cutoff (in nm)\n; Electrostatics\ncoulombtype             = PME       ; Particle Mesh Ewald for long-range electrostatics\npme_order               = 4         ; cubic interpolation\nfourierspacing          = 0.16      ; grid spacing for FFT\n; Temperature coupling is on\ntcoupl                  = V-rescale             ; modified Berendsen thermostat\ntc_grps                 = SOLU MEMB SOLV\ntau_t                   = 1.0 1.0 1.0\nref_t                   = 303.15 303.15 303.15\n; Pressure coupling is on\npcoupl                  = Parrinello-Rahman     ; Pressure coupling on in NPT\npcoupltype              = isotropic             ; uniform scaling of box vectors\ntau_p                   = 2.0                   ; time constant, in ps\nref_p                   = 1.0                   ; reference pressure, in bar\ncompressibility         = 4.5e-5                ; isothermal compressibility of water, bar^-1\n; Periodic boundary conditions\npbc                     = xyz       ; 3-D PBC\n; Dispersion correction\nDispCorr                = EnerPres  ; account for cut-off vdW scheme\n; Velocity generation\ngen_vel                 = no        ; Velocity generation is off \nnsteps= ")
          production.write(str(ts))
          production.close()
          #edition of step4.1_equilibration.mdp file to set the steps for equilibration
          os.remove(macrotarget+'/step6.1_equilibration.mdp')
          equil= open(macrotarget+'/step6.1_equilibration.mdp', 'w')
          equil.write("define                  = -DPOSRES -DPOSRES_FC_BB=4000.0 -DPOSRES_FC_SC=2000.0 -DPOSRES_FC_LIPID=1000.0 -DDIHRES -DDIHRES_FC=1000.0\nintegrator              = md\ndt                      = 0.001\nnsteps                  = 5000\nnstxtcout               = 5000\nnstvout                 = 5000\nnstfout                 = 5000\nnstcalcenergy           = 100\nnstenergy               = 1000\nnstlog                  = 1000\n;\ncutoff-scheme           = Verlet\nnstlist                 = 20\nrlist                   = 1.2\nvdwtype                 = Cut-off\nvdw-modifier            = Force-switch\nrvdw_switch             = 1.0\nrvdw                    = 1.2\ncoulombtype             = PME\nrcoulomb                = 1.2\n;\ntcoupl                  = berendsen\ntc_grps                 = SOLU MEMB SOLV\ntau_t                   = 1.0 1.0 1.0\nref_t                   = 303.15 303.15 303.15\n;\nconstraints             = h-bonds\nconstraint_algorithm    = LINCS\n;\nnstcomm                 = 100\ncomm_mode               = linear\ncomm_grps               = SOLU_MEMB SOLV\n;\ngen-vel                 = yes\ngen-temp                = 303.15\ngen-seed                = -1")
          equil.close()
        else :
           yasara.ShowMessage("Please put the Gromacs mdp files inside the working directory")  
        ##below this point no change is required
        yasara.ShowMessage(("System optimization in progress. Please wait"))
        # energy minimization step
        os.system('gmx grompp -f step6.0_minimization.mdp -o step6.0_minimization.tpr -c step5_input.gro -r step5_input.gro -p topol.top -n index.ndx -maxwarn 5')
        os.system('gmx mdrun -c step6.0_minimization.pdb -v -deffnm step6.0_minimization')
        yasara.run('Delobj all')
        #yasara.run('clear')
        yasara.ShowMessage(("System optimization in progress. Please wait"))
        yasara.LoadPDB(str(macrotarget+'/step6.0_minimization.pdb'))
        yasara.run("ZoomAll Steps=20")
        #equilibration step
        os.system('gmx grompp -f step6.1_equilibration.mdp -o npt.tpr  -c step6.0_minimization.pdb -r step5_input.gro -p topol.top -n index.ndx -maxwarn 5')
        os.system('gmx mdrun -c npt.pdb -v -deffnm npt')
        #md production step
        os.system('gmx grompp -f step7_production.mdp -o md_0_1.tpr  -c npt.pdb -r step5_input.gro -p topol.top -n index.ndx -maxwarn 5')
        yasara.run('Delobj all')
        #yasara.run('clear')
        yasara.ShowMessage(("System optimization in progress. Please wait"))
        yasara.LoadPDB(str(macrotarget+'/npt.pdb'))
        yasara.run("ZoomAll Steps=20")
        yasara.run("HideRes cl")
        yasara.run("HideRes Na")
        mdxtc()
#if there is any heteroatom in the system, then below mentioned will appear
    elif os.path.isfile(macrotarget+'/'+liginput):
      resultlist =\
        yasara.ShowWin("Custom","YAMACS - MD run",400,250,
        "Text", 20, 50, "Attached object",
        "RadioButtons",2,1,
                       20, 100,"Others",
                       200,100,"Membrane",
        "Button",      150,200," O K")
      
      attach= open((macrotarget)+'/protein.txt','w+')
      attach.write((str(resultlist)).replace("'","").replace(" ", "\n").replace("[","").replace("]","").replace(",","").replace("0",""))
      attach.close()  
      f = open((macrotarget)+'/protein.txt', "r")
      content= f.readlines()
      a = str((content[0]).strip('\n'))
      if a == str(1) and ff == 'charmm36-mar2019':
        #Below this point the script will generate the mol2 files of the heterogenous structure and will generate the essential .itp files of the structure by using https://www.swissparam.ch server
        #the forcefield must be charmm36, as https://www.swissparam.ch server only generate the input for charmm36 files 
        yasara.run("Delobj all")
        yasara.LoadPDB(str(macrotarget+'\\'+lig+'.pdb'))
        yasara.run("AddHydObj 1")
        savemol2= 'SaveMOL2 1,'+(macrotarget)+'/'+(lig)+'.mol2,transform=Yes'
        yasara.run(savemol2)
        os.remove(macrotarget+'/'+lig+'.pdb')
        yasara.ShowMessage("Generation of itp file in progress using https://www.swissparam.ch server")
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
                        yasara.ShowMessage("itp file generated using https://www.swissparam.ch server")
                        os.chdir(macrotarget)
                        newliginput=(lig+'.pdb')
                        ligoutput=(lig+'_gmx.pdb')
                        lines = []
                        p = subprocess.Popen(['gmx', 'editconf', '-f', (newliginput), '-o', (ligoutput)], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
                        subprocess_return = p.stdout.read()
                        p.communicate(b'1\n0\n')
                        p.wait()
                        #complex formation
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
                        yasara.run("ZoomAll Steps=20")
                        yasara.ShowMessage("Complex file saved in:" + macrotarget)
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
                        #solvation box formation with the specific dimention of simcell in yasara input
                        os.system('gmx editconf -f '+(newcomplex)+' -o '+(newbox)+' -box '+(str(cellx))+' '+(str(celly))+' '+(str(cellz))+' -bt cubic')
                        os.chdir(macrotarget)
                        #time.sleep(20)
                        os.system(solvgroformation)
                        #step3 ion addition

                        yasara.ShowMessage("System optimization in progress. Please wait")
                        
                        os.chdir(macrotarget)
                        #time.sleep(2)
                        os.system(ionstpr)
                        os.system (salt)
                        #conversion of '.gro' file to '.pdb' file
                        os.system('gmx editconf -f '+(solviongro)+' -o '+(solvionpdb)+'')
                        #Below this point nothing needs to be changed
                        os.system(energy)
                        os.system(runenergy)
                        #ligand restraining
                        liggmxinput=(lig+'_gmx.pdb')
                        indexoutput=(lig+'_index.ndx')
                        out2=(lig+'_porse.itp')
                        os.chdir(macrotarget)
                        # create an index group for heteroatoms that contains only its non-hydrogen atoms
                        cmd='echo "0 & ! a H*\nq" | gmx make_ndx -f '+(liggmxinput)+' -o ' +(indexoutput)
                        os.system(cmd)
                        #Then, execute the genrestr module and select this newly created index group 
                        cmd2='echo "3" | gmx genrestr -f '+(liggmxinput)+' -n '+(indexoutput)+' -o '+(out2)+' -fc 1000 1000 1000'
                        os.system (cmd2)
                        cmd3='echo " 1 | 13" ; echo "q" | gmx make_ndx -f em.gro -o index.ndx'
                        os.system (cmd3)
                        #insertion of restrained file information into topology file
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
                        #NVT equilibirum
                        os.system(complexnvt)
                        yasara.ShowMessage(("System optimization in progress. Please wait"))
                        os.system(runnvt)
                        c = subprocess.Popen(['gmx', 'editconf', '-f', 'nvt.gro', '-o', 'nvt.pdb'], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
                        subprocess_return = c.stdout.read()
                        c.communicate(b'1\n0\n')
                        c.wait()
                        yasara.run("Delobj all")
                        ##yasara.run("Clear")
                        yasara.LoadPDB(str(macrotarget+'\\'+'nvt.pdb'))
                        yasara.run("ZoomAll Steps=20")
                        yasara.run("HideRes cl")
                        yasara.run("HideRes Na")
                        #NPT equilibirum
                        os.system(complexnpt)
                        yasara.ShowMessage(("System optimization in progress. Please wait"))
                        os.system(runnpt)
                        f = subprocess.Popen(['gmx', 'editconf', '-f', 'npt.gro', '-o', 'npt.pdb'], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
                        subprocess_return = f.stdout.read()
                        f.communicate(b'1\n0\n')
                        f.wait()
                        yasara.run("Delobj all")
                        ##yasara.run("Clear")
                        yasara.LoadPDB(str(macrotarget+'\\'+'npt.pdb'))
                        yasara.run("ZoomAll Steps=20") 
                        yasara.run("HideRes cl")
                        yasara.run("HideRes Na")
                        os.system(complexmdtpr)
                        mdxtc()
      elif a == str(1) and ff == 'amber03' or ff == "amber94" or ff == "amber96" or ff== "amber99" or ff=="amber99sb" or ff=="amber99sb-ildn" or ff=="amberGS":
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
        #formation of ligand topology by antechamber and acpype
        yasara.ShowMessage(("Generation of itp file in progress using ACPYPE and ANTECHAMBER"))
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
        #os.remove(macrotarget+'/'+lig+'.pdb')
        os.rename(macrotarget+'/'+'sqm.pdb', macrotarget+'/'+lig+'_gmx.pdb')
        with open(macrotarget+'/'+lig+'_gmx.pdb', 'r') as fp:
            data = fp.read()
        with open((macrotarget)+'/'+inpu+'_gmx.pdb') as fp:
            lines = fp.read()
        complexf= open(macrotarget+'/'+inpu+'_gmx.pdb','w')
        complexf.write(str(lines).replace('TER',data).replace('ENDMDL','TER\nENDMDL'))
        complexf.close()
        yasara.run("Delobj all")
        yasara.LoadPDB(str(macrotarget+'\\'+inpu+'_gmx.pdb'))
        yasara.run("ZoomAll Steps=20")
        yasara.ShowMessage("Complex file saved in:" + macrotarget)
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
        #solvation box formation with the specific dimention of simcell in yasara input
        os.system('gmx editconf -f '+(newcomplex)+' -o '+(newbox)+' -box '+(str(cellx))+' '+(str(celly))+' '+(str(cellz))+' -bt cubic')
        os.chdir(macrotarget)
        #time.sleep(20)
        os.system(solvgroformation)
        #step3 ion addition
        yasara.ShowMessage("System optimization in progress. Please wait")
        os.chdir(macrotarget)
        os.system(ionstpr)
        os.system (salt)
        #conversion of '.gro' file to '.pdb' file
        os.system('gmx editconf -f '+(solviongro)+' -o '+(solvionpdb)+'')
        #Below this point nothing needs to be changed
        os.system(energy)
        os.system(runenergy)
        #ligand restraining
        liggmxinput=(lig+'_gmx.pdb')
        indexoutput=(lig+'_index.ndx')
        out2=(lig+'_porse.itp')
        os.chdir(macrotarget)
        # create an index group for heteroatoms that contains only its non-hydrogen atoms
        cmd='echo "0 & ! a H*\nq" | gmx make_ndx -f '+(liggmxinput)+' -o ' +(indexoutput)
        os.system(cmd)
        #Then, execute the genrestr module and select this newly created index group 
        cmd2='echo "3" | gmx genrestr -f '+(liggmxinput)+' -n '+(indexoutput)+' -o '+(out2)+' -fc 1000 1000 1000'
        os.system (cmd2)
        cmd3='echo " 1 | 13" ; echo "q" | gmx make_ndx -f em.gro -o index.ndx'
        os.system (cmd3)
        #insertion of restrained file information into topology file
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
        #NVT equilibirum
        os.system(complexnvt)
        yasara.ShowMessage(("System optimization in progress. Please wait"))
        os.system(runnvt)
        c = subprocess.Popen(['gmx', 'editconf', '-f', 'nvt.gro', '-o', 'nvt.pdb'], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        subprocess_return = c.stdout.read()
        c.communicate(b'1\n0\n')
        c.wait()
        yasara.run("Delobj all")
        ##yasara.run("Clear")
        yasara.LoadPDB(str(macrotarget+'\\'+'nvt.pdb'))
        yasara.run("ZoomAll Steps=20")
        yasara.run("HideRes cl")
        yasara.run("HideRes Na")
        #NPT equilibirum
        os.system(complexnpt)
        yasara.ShowMessage(("System optimization in progress. Please wait"))
        os.system(runnpt)
        f = subprocess.Popen(['gmx', 'editconf', '-f', 'npt.gro', '-o', 'npt.pdb'], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        subprocess_return = f.stdout.read()
        f.communicate(b'1\n0\n')
        f.wait()
        yasara.run("Delobj all")
        ##yasara.run("Clear")
        yasara.LoadPDB(str(macrotarget+'\\'+'npt.pdb'))
        yasara.run("ZoomAll Steps=20") 
        yasara.run("HideRes cl")
        yasara.run("HideRes Na")
        os.system(complexmdtpr)
        mdxtc()
                                    
      else :
          print("Please generate the innput files of your system for specific force field from Charmm-gui")
    else :
      os.chdir(macrotarget)
      os.system(newboxformation)
      os.system(solvgroformation)
      os.system(ionstpr)
      os.system('echo 13 | gmx genion -s ions.tpr -o '+(solviongro)+' -p topol.top -pname NA -nname CL -neutral')
      os.system(energy)
      yasara.ShowMessage("System optimization in progress. Please wait") 
      os.system(runenergy)
      os.system('gmx editconf -f em.gro -o em.pdb')
      yasara.run("Delobj all")
      yasara.LoadPDB(str(macrotarget+'/em.pdb')) 
      yasara.run("HideRes sol") 
      yasara.run("HideRes cl") 
      yasara.run("HideRes Na")   
      os.system(nvttpr)
      yasara.ShowMessage("System optimization in progress. Please wait") 
      os.system(runnvt)
      os.system('gmx editconf -f nvt.gro -o nvt.pdb')
      yasara.run("Delobj all")
      yasara.LoadPDB(str(macrotarget+'/nvt.pdb')) 
      yasara.run("HideRes cl")
      yasara.run("HideRes Na")
      os.system(npttpr)
      yasara.ShowMessage("System optimization in progress. Please wait") 
      os.system(runnpt)
      os.system('gmx editconf -f npt.gro -o npt.pdb')
      yasara.run("Delobj all")
      yasara.LoadPDB(str(macrotarget+'/npt.pdb'))  
      yasara.run("HideRes cl")
      yasara.run("HideRes Na")
      os.system(mdtpr)
      mdxtc()

  #For only membrane system is present, then user must need to generate the input file from charmm-gui
  elif os.path.isfile(macrotarget+'/membrane.txt'):
    if os.path.isdir(macrotarget+'/charmm-gui'):   
       #extraction of charmm-gui files in working folder
        brr = os.listdir(macrotarget + '/charmm-gui')
        innerfolder= (str(brr).replace('[','').replace("'", "").replace("]", "").replace(",", "\n"))
        print(innerfolder)
        arr = os.listdir(macrotarget+'/charmm-gui/'+innerfolder+'/gromacs/toppar')
        from_dir = macrotarget+'/charmm-gui/'+innerfolder+'/gromacs'
        to_dir = macrotarget
        distutils.dir_util.copy_tree(from_dir, to_dir)
        yasara.run('Delobj all')
        #yasara.run('clear')
        yasara.LoadPDB(str(macrotarget+'/step5_input.pdb'))
        yasara.run("ZoomAll Steps=20")
        os.remove(macrotarget+'/step6.0_minimization.mdp')
        newem= open(macrotarget+'/step6.0_minimization.mdp','w')
        newem.write("define                  = -DPOSRES -DPOSRES_FC_LIPID=1000.0 -DDIHRES -DDIHRES_FC=1000.0\nintegrator              = steep\nemtol                   = 1000.0\nnsteps                  = 2500\nnstlist                 = 10\ncutoff-scheme           = Verlet\nrlist                   = 1.2\nvdwtype                 = Cut-off\nvdw-modifier            = Force-switch\nrvdw_switch             = 1.0\nrvdw                    = 1.2\ncoulombtype             = PME\nrcoulomb                = 1.2\n;\nconstraints             = h-bonds\nconstraint_algorithm    = LINCS")
        newem.close()
        #step7_production.mdp file edition to set the time duration for simulation
        if mdp == str(1):
          os.remove(macrotarget+'/step7_production.mdp')
          production= open(macrotarget+'/step7_production.mdp', 'w')
          production.write("title                   = OPLS Lysozyme NPT equilibration\n; Run parameters\nintegrator              = md        ; leap-frog integrator\ndt                      = 0.002     ; 2 fs\n; Output control\nnstxout                 = 0         ; suppress bulky .trr file by specifying \nnstvout                 = 0         ; 0 for output frequency of nstxout,\nnstfout                 = 0         ; nstvout, and nstfout\nnstenergy               = 5000      ; save energies every 10.0 ps\nnstlog                  = 5000      ; update log file every 10.0 ps\nnstxout-compressed      = 10000       ; save compressed coordinates every 10.0 s\ncompressed-x-grps       = System    ; save the whole system\n; Bond parameters\ncontinuation            = yes       ; Restarting after NPT \nconstraint_algorithm    = lincs     ; holonomic constraints\nconstraints             = h-bonds   ; bonds involving H are constrained\nlincs_iter              = 1         ; accuracy of LINCS\nlincs_order             = 4         ; also related to accuracy\n; Neighborsearching\ncutoff-scheme           = Verlet    ; Buffered neighbor searching\nns_type                 = grid      ; search neighboring grid cells\nnstlist                 = 10        ; 20 fs, largely irrelevant with Verlet scheme\nrcoulomb                = 1.0       ; short-range electrostatic cutoff (in nm)\nrvdw                    = 1.0       ; short-range van der Waals cutoff (in nm)\n; Electrostatics\ncoulombtype             = PME       ; Particle Mesh Ewald for long-range electrostatics\npme_order               = 4         ; cubic interpolation\nfourierspacing          = 0.16      ; grid spacing for FFT\n; Temperature coupling is on\ntcoupl                  = V-rescale             ; modified Berendsen thermostat\ntc_grps                 = MEMB SOLV\ntau_t                   = 1.0 1.0\nref_t                   = 303.15 303.15\n; Pressure coupling is on\npcoupl                  = Parrinello-Rahman     ; Pressure coupling on in NPT\npcoupltype              = isotropic             ; uniform scaling of box vectors\ntau_p                   = 2.0                   ; time constant, in ps\nref_p                   = 1.0                   ; reference pressure, in bar\ncompressibility         = 4.5e-5                ; isothermal compressibility of water, bar^-1\n; Periodic boundary conditions\npbc                     = xyz       ; 3-D PBC\n; Dispersion correction\nDispCorr                = EnerPres  ; account for cut-off vdW scheme\n; Velocity generation\ngen_vel                 = no        ; Velocity generation is off \nnsteps=")
          production.write(str(ts))
          production.close()
          #step6.1_equilibration.mdp file edition to set the steps for equilibration
          os.remove(macrotarget+'/step6.1_equilibration.mdp')
          equil= open(macrotarget+'/step6.1_equilibration.mdp', 'w')
          equil.write("define                  = -DPOSRES -DPOSRES_FC_LIPID=1000.0 -DDIHRES -DDIHRES_FC=1000.0\nintegrator              = md\ndt                      = 0.001\nnsteps                  = 5000\nnstxtcout               = 5000\nnstvout                 = 5000\nnstfout                 = 5000\nnstcalcenergy           = 100\nnstenergy               = 1000\nnstlog                  = 1000\n;\ncutoff-scheme           = Verlet\nnstlist                 = 20\nrlist                   = 1.2\nvdwtype                 = Cut-off\nvdw-modifier            = Force-switch\nrvdw_switch             = 1.0\nrvdw                    = 1.2\ncoulombtype             = PME\nrcoulomb                = 1.2\n;\ntcoupl                  = berendsen\ntc_grps                 = MEMB SOLV\ntau_t                   = 1.0 1.0\nref_t                   = 303.15 303.15\n;\nconstraints             = h-bonds\nconstraint_algorithm    = LINCS\n;\nnstcomm                 = 100\ncomm_mode               = linear\ncomm_grps               = MEMB SOLV\n;\ngen-vel                 = yes\ngen-temp                = 303.15\ngen-seed                = -1")
          equil.close()
        else :
           yasara.ShowMessage("Please put the Gromacs mdp files inside the working directory")
        #below this point no change is required
        os.chdir(macrotarget)
        yasara.ShowMessage(("System optimization in progress. Please wait"))
        #energy minimization
        os.system('gmx grompp -f step6.0_minimization.mdp -o step6.0_minimization.tpr -c step5_input.gro -r step5_input.gro -p topol.top -n index.ndx -maxwarn 5')
        os.system('gmx mdrun -c step6.0_minimization.pdb -v -deffnm step6.0_minimization')
        yasara.run('Delobj all')
        #yasara.run('clear')
        yasara.ShowMessage(("System optimization in progress. Please wait"))
        yasara.LoadPDB(str(macrotarget+'/step6.0_minimization.pdb'))
        yasara.run("ZoomAll Steps=20")
        #equilibration
        os.system('gmx grompp -f step6.1_equilibration.mdp -o npt.tpr  -c step6.0_minimization.pdb -r step5_input.gro -p topol.top -n index.ndx -maxwarn 5')
        os.system('gmx mdrun -c npt.pdb -v -deffnm npt')
        #md production
        os.system('gmx grompp -f step7_production.mdp -o md_0_1.tpr  -c npt.pdb -r step5_input.gro -p topol.top -n index.ndx -maxwarn 5')
        yasara.run('Delobj all')
        #yasara.run('clear')
        yasara.ShowMessage(("System optimization in progress. Please wait"))
        yasara.LoadPDB(str(macrotarget+'/npt.pdb'))
        yasara.run("ZoomAll Steps=20")  
        yasara.run("HideRes cl")
        yasara.run("HideRes Na")
        mdxtc() 
    else :   
        print("Please generate the input files of your system from charmm-gui")    
  
  else :  
      #if the system is a heteroatoms like-small molecules, ions etc, then the below mentioned command will develop the topology file of the system and will prompt to md simulation
      yasara.ShowMessage("Please delete all objects except the required one")
      yasara.run("wait continuebutton")
      yasara.run("DelRes sol")
      yasara.run("DelRes hoh")
      yasara.run("DelRes Tip")
      yasara.run("DelRes Tp3")
      yasara.run("JoinObj All,1")
      savepdb= 'SavePDB 1,'+(macrotarget)+'/'+(inpu)+'.pdb'
      yasara.run(savepdb)
      #writing of mdp files     
      if mdp== str(1):
        mdedit= open((macrotarget)+'/'+'md.mdp', "w")
        mdedit.write('title                   = OPLS Lysozyme NPT equilibration\n; Run parameters\nintegrator              = md        ; leap-frog integrator\ndt                      = 0.002     ; 2 fs\n; Output control\nnstxout                 = 0         ; suppress bulky .trr file by specifying \nnstvout                 = 0         ; 0 for output frequency of nstxout,\nnstfout                 = 0         ; nstvout, and nstfout\nnstenergy               = 5000      ; save energies every 10.0 ps\nnstlog                  = 5000      ; update log file every 10.0 ps\nnstxout-compressed      = 10000      ; save compressed coordinates every 10.0 ps\ncompressed-x-grps       = System    ; save the whole system\n; Bond parameters\ncontinuation            = yes       ; Restarting after NPT \nconstraint_algorithm    = lincs     ; holonomic constraints\nconstraints             = h-bonds   ; bonds involving H are constrained\nlincs_iter              = 1         ; accuracy of LINCS\nlincs_order             = 4         ; also related to accuracy\n; Neighborsearching\ncutoff-scheme           = Verlet    ; Buffered neighbor searching\nns_type                 = grid      ; search neighboring grid cells\nnstlist                 = 10        ; 20 fs, largely irrelevant with Verlet scheme\nrcoulomb                = 1.0       ; short-range electrostatic cutoff (in nm)\nrvdw                    = 1.0       ; short-range van der Waals cutoff (in nm)\n; Electrostatics\ncoulombtype             = PME       ; Particle Mesh Ewald for long-range electrostatics\npme_order               = 4         ; cubic interpolation\nfourierspacing          = 0.16      ; grid spacing for FFT\n; Temperature coupling is on\ntcoupl                  = V-rescale             ; modified Berendsen thermostat\ntc-grps                 = ')
        mdedit.write(inpu)
        mdedit.write(' water   ; two coupling groups - more accurate\ntau_t                   = 0.1     0.1           ; time constant, in ps\nref_t                   = 300     300           ; reference temperature, one for each group, in K\n; Pressure coupling is on\npcoupl                  = Parrinello-Rahman     ; Pressure coupling on in NPT\npcoupltype              = isotropic             ; uniform scaling of box vectors\ntau_p                   = 2.0                   ; time constant, in ps\nref_p                   = 1.0                   ; reference pressure, in bar\ncompressibility         = 4.5e-5                ; isothermal compressibility of water, bar^-1\n; Periodic boundary conditions\npbc                     = xyz       ; 3-D PBC\n; Dispersion correction\nDispCorr                = EnerPres  ; account for cut-off vdW scheme\n; Velocity generation\ngen_vel                 = no        ; Velocity generation is off\nnsteps= ')
        mdedit.write(str(ts))
        mdedit.close()
        ions= open((macrotarget)+'/'+'ions.mdp', 'w+')
        ions.write("; LINES STARTING WITH ';' ARE COMMENTS\ntitle		    = Minimization	; Title of run\n\n; Parameters describing what to do, when to stop and what to save\nintegrator	    = steep		; Algorithm (steep = steepest descent minimization)\nemtol		    = 1000.0  	; Stop minimization when the maximum force < 10.0 kJ/mol\nemstep          = 0.01      ; Energy step size\nnsteps		    = 50000	  	; Maximum number of (minimization) steps to perform\n\n; Parameters describing how to find the neighbors of each atom and how to calculate the interactions\nnstlist		    = 40		    ; Frequency to update the neighbor list and long range forces\ncutoff-scheme   = Verlet\nns_type		    = grid		; Method to determine neighbor list (simple, grid)\nrlist		    = 1.0		; Cut-off for making neighbor list (short range forces)\ncoulombtype	    = cutoff	; Treatment of long range electrostatic interactions\nrcoulomb	    = 1.0		; long range electrostatic cut-off\nrvdw		    = 1.0		; long range Van der Waals cut-off\npbc             = xyz 		; Periodic Boundary Conditions")
        ions.close()

        em= open((macrotarget)+'/'+'em.mdp', 'w+')
        em.write("; LINES STARTING WITH ';' ARE COMMENTS\ntitle		    = Minimization	; Title of run\n\n; Parameters describing what to do, when to stop and what to save\nintegrator	    = steep		; Algorithm (steep = steepest descent minimization)\nemtol		    = 1000.0  	; Stop minimization when the maximum force < 10.0 kJ/mol\nemstep          = 0.01      ; Energy step size\nnsteps		    = 25000	  	; Maximum number of (minimization) steps to perform\n\n; Parameters describing how to find the neighbors of each atom and how to calculate the interactions\nnstlist		    = 1		        ; Frequency to update the neighbor list and long range forces\ncutoff-scheme   = Verlet\nns_type		    = grid		    ; Method to determine neighbor list (simple, grid)\nrlist		    = 1.2		    ; Cut-off for making neighbor list (short range forces)\ncoulombtype	    = PME		    ; Treatment of long range electrostatic interactions\nrcoulomb	    = 1.2		    ; long range electrostatic cut-off\nvdwtype         = cutoff\nvdw-modifier    = force-switch\nrvdw-switch     = 1.0\nrvdw		    = 1.2		    ; long range Van der Waals cut-off\npbc             = xyz 		    ; Periodic Boundary Conditions\nDispCorr        = no")
        em.close()
        newnvt = open((macrotarget)+'/'+'nvt.mdp', "w")
        newnvt.write('title                   = OPLS Lysozyme NVT equilibration \ndefine                  = -DPOSRES  ; position restrain the protein\n')
        newnvt.write('; Run parameters\nintegrator              = md        ;leap-frog integrator\nnsteps                  = 25000     ;\ndt                      = 0.002     ; 2 fs\n')
        newnvt.write('; Output control\nnstxout                 = 500       ; update log file every 1.0 ps\n; Bond parameters\ncontinuation            = no        ; first dynamics run\n')
        newnvt.write('constraint_algorithm    = lincs     ; holonomic constraints \nconstraints             = h-bonds   ; bonds involving H are constrained\nlincs_iter              = 1         ; accuracy of LINCS\nlincs_order             = 4         ; also related to accuracy\n; Nonbonded settings \ncutoff-scheme           = Verlet    ; Buffered neighbor searching\nns_type                 = grid      ; search neighboring grid cells\nnstlist                 = 10        ; 20 fs, largely irrelevant with Verlet\nrcoulomb                = 1.0       ; short-range electrostatic cutoff (in nm)\nrvdw                    = 1.0       ; short-range van der Waals cutoff (in nm)\nDispCorr                = EnerPres  ; account for cut-off vdW scheme\n; Electrostatics\ncoulombtype             = PME       ; Particle Mesh Ewald for long-range electrostatics\npme_order               = 4         ; cubic interpolation\nfourierspacing          = 0.16      ; grid spacing for FFT\n; Temperature coupling is on\ntcoupl                  = V-rescale             ; modified Berendsen thermostat\ntc-grps                 = ')
        newnvt.write(inpu)
        newnvt.write(" water  ; two coupling groups - more accurate\ntau_t                   = 0.1     0.1           ; time constant, in ps\nref_t                   = 300     300           ; reference temperature, one for each group, in K\n; Pressure coupling is off\npcoupl                  = no        ; no pressure coupling in NVT\n; Periodic boundary conditions\npbc                     = xyz       ; 3-D PBC\n; Velocity generation\ngen_vel                 = yes       ; assign velocities from Maxwell distribution\ngen_temp                = 300       ; temperature for Maxwell distribution\ngen_seed                = -1        ; generate a random seed")
        newnvt.close()
        #os.remove((macrotarget)+'/'+'npt.mdp')
        newnpt = open((macrotarget)+'/'+'npt.mdp', "w")
        newnpt.write('title                   = OPLS Lysozyme NVT equilibration \ndefine                  = -DPOSRES  ; position restrain the protein\n; Run parameters\nintegrator              = md        ; leap-frog integrator\nnsteps                  = 25000     ;\ndt                      = 0.002     ; 2 fs\n; Output control\nnstxout                 = 500       ; save coordinates every 1.0 ps\nnstvout                 = 500       ; save velocities every 1.0 ps\nnstenergy               = 500       ; save energies every 1.0 ps\nnstlog                  = 500       ; update log file every 1.0 ps\n; Bond parameters\ncontinuation            = yes       ; Restarting after NVT \nconstraint_algorithm    = lincs     ; holonomic constraints \nconstraints             = h-bonds   ; bonds involving H are constrained\nlincs_iter              = 1         ; accuracy of LINCS\nlincs_order             = 4         ; also related to accuracy\n; Nonbonded settings \ncutoff-scheme           = Verlet    ; Buffered neighbor searching\nns_type                 = grid      ; search neighboring grid cells\nnstlist                 = 10        ; 20 fs, largely irrelevant with Verlet\nrcoulomb                = 1.0       ; short-range electrostatic cutoff (in nm)\nrvdw                    = 1.0       ; short-range van der Waals cutoff (in nm)\nDispCorr                = EnerPres  ; account for cut-off vdW scheme\n; Electrostatics\ncoulombtype             = PME       ; Particle Mesh Ewald for long-range electrostatics\npme_order               = 4         ; cubic interpolation\nfourierspacing          = 0.16      ; grid spacing for FFT\n; Temperature coupling is on\ntcoupl                  = V-rescale             ; modified Berendsen thermostat\ntc-grps                 = ')
        newnpt.write(inpu)
        newnpt.write(' water   ; two coupling groups - more accurate\ntau_t                   = 0.1     0.1           ; time constant, in ps\nref_t                   = 300     300           ; reference temperature, one for each group, in K\n; Pressure coupling is on\npcoupl                  = Parrinello-Rahman     ; Pressure coupling on in NPT\npcoupltype              = isotropic             ; uniform scaling of box vectors\ntau_p                   = 2.0                   ; time constant, in ps\nref_p                   = 1.0                   ; reference pressure, in bar\ncompressibility         = 4.5e-5                ; isothermal compressibility of water, bar^-1\nrefcoord_scaling        = com\n; Periodic boundary conditions\npbc                     = xyz       ; 3-D PBC\n; Velocity generation\ngen_vel                 = no        ; Velocity generation is off')
        newnpt.close()
      else:
         yasara.ShowMessage("Please put the Gromacs mdp files inside the working directory")
      #below this point no changes are required
      if ff == 'charmm36-mar2019':
        yasara.run("Delobj all")       
        yasara.LoadPDB((macrotarget)+'/'+inpu+'.pdb')
        yasara.run("ZoomAll Steps=20")
        #yasara.run("JoinObj All,1")
        yasara.run("AddHydObj 1")
        savemol2= 'SaveMOL2 1,'+(macrotarget)+'/'+(inpu)+'.mol2,transform=Yes'
        yasara.run(savemol2)
        yasara.ShowMessage("Generation of itp file in progress using https://www.swissparam.ch server")
        FILE_TO_SEND= macrotarget+'/'+inpu+".mol2";
        FILE_DI_OUTPUT= macrotarget+'/'+'output.html';
        ZIP_DI_OUTPUT= macrotarget+'/'+'output.zip';
        WHERE_TO_UNZIP= macrotarget
        #if the  forcefield is charmm36, then the script will generate the .itp file of the molecule by using https://www.swissparam.ch server
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
                        yasara.ShowMessage("itp file generated using https://www.swissparam.ch server")
                        time.sleep(2)
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
                        os.chdir(macrotarget)
                        os.system(otherfile)
                        #formation of solvation box
                        os.system(newboxformation)
                        os.system(solvgroformation)
                        os.system(ionstpr)
                      #ions addition in to the system
                        os.system('echo 4 | gmx genion -s ions.tpr -o '+(solviongro)+' -p topol.top -pname NA -nname CL -neutral')
                        os.system('gmx editconf -f '+(solviongro)+' -o '+(solvionpdb)+'')
                        yasara.run("Delobj all")
                        ##yasara.run("Clear")
                        yasara.LoadPDB(str(macrotarget)+'\\'+inpu+'_solv_ions.pdb')
                        yasara.run("ZoomAll Steps=20")
                        #energy minimization
                        os.system(energy)
                        yasara.ShowMessage("System optimization in progress. Please wait")
                        os.system(runenergy)
                        othersgmxinput=(inpu+'_gmx.pdb')
                        othersindexoutput=(inpu+'_index.ndx')
                        othersout2=(inpu+'_porse.itp')
                        nvt=str(macrotarget)
                        nvtfile=(nvt+'/nvt.mdp')
                        npt=str(macrotarget)
                        nptfile=(npt+'/npt.mdp')
                        #restraining of the system
                        cmd='echo "0 & ! a H*\nq" | gmx make_ndx -f '+(othersgmxinput)+' -o ' +(othersindexoutput)
                        os.system(cmd)
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
                        #NVT equilibration
                        os.system(complexnvt)
                        yasara.ShowMessage("System optimization in progress. Please wait")
                        os.system(runnvt)
                        os.system('echo "2" \ "0" | gmx trjconv -s nvt.tpr -f nvt.trr -o nvt.gro -pbc mol -center')
                        os.system('gmx editconf -f nvt.gro -o nvt.pdb')
                        yasara.run("Delobj all")
                        ##yasara.run("Clear")
                        yasara.LoadPDB(str(macrotarget+'\\'+'nvt.pdb'))
                        yasara.run("ZoomAll Steps=20")
                        yasara.run("HideRes cl")
                        yasara.run("HideRes Na")
                        #NPT equilibration
                        os.system(complexnpt)
                        yasara.ShowMessage("System optimization in progress. Please wait")
                        os.system(runnpt)
                        os.system('echo "2" \ "0" | gmx trjconv -s npt.tpr -f npt.trr -o npt.gro -pbc mol -center')
                        os.system('gmx editconf -f npt.gro -o npt.pdb')
                        yasara.run("Delobj all")
                        ##yasara.run("Clear")
                        yasara.LoadPDB(str(macrotarget+'\\'+'npt.pdb'))
                        yasara.run("ZoomAll Steps=20")
                        yasara.run("HideRes cl")
                        os.system(complexmdtpr)
                        mdxtc() 
      elif ff == 'amber03' or ff == "amber94" or ff == "amber96" or ff== "amber99" or ff=="amber99sb" or ff=="amber99sb-ildn" or ff=="amberGS":
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
        yasara.ShowMessage(("Generation of itp file in progress using ACPYPE and ANTECHAMBER"))
        os.system('acpype -i '+(FILe_mol2)+'')
        os.chdir(macrotarget+'/'+inpu+'.acpype')
        os.remove(macrotarget+'/'+inpu+'.acpype/em.mdp')
        os.remove(macrotarget+'/'+inpu+'.acpype/md.mdp')
        os.chdir(macrotarget)
        src= macrotarget+'/'+inpu+'.acpype'
        dst=macrotarget
        distutils.dir_util.copy_tree(src,dst)
        os.rename(macrotarget+'/'+inpu+'_GMX.itp',macrotarget+'/'+inpu+'.itp')
        #os.rename(macrotarget+'/'+inpu+'_GMX.top',macrotarget+'/topol.top')
        os.chdir(macrotarget)
        os.remove(macrotarget+'/'+inpu+'.pdb')
        os.rename(macrotarget+'/'+'sqm.pdb', macrotarget+'/'+inpu+'.pdb')
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
        os.chdir(macrotarget)   
        os.system(otherfile)
        #formation of solvation box
        os.system(newboxformation)
        os.system(solvgroformation)
        os.system(ionstpr)
        #ions addition in to the system
        os.system('echo 4 | gmx genion -s ions.tpr -o '+(solviongro)+' -p topol.top -pname NA -nname CL -neutral')
        os.system('gmx editconf -f '+(solviongro)+' -o '+(solvionpdb)+'')
        yasara.run("Delobj all")
        ##yasara.run("Clear")
        yasara.LoadPDB(str(macrotarget)+'\\'+inpu+'_solv_ions.pdb')
        yasara.run("ZoomAll Steps=20")
        #energy minimization
        os.system(energy)
        yasara.ShowMessage("System optimization in progress. Please wait")
        os.system(runenergy)
        othersgmxinput=(inpu+'_gmx.pdb')
        othersindexoutput=(inpu+'_index.ndx')
        nvt=str(macrotarget)
        nvtfile=(nvt+'/nvt.mdp')
        npt=str(macrotarget)
        nptfile=(npt+'/npt.mdp')
        #restraining of the system
        cmd='echo "0 & ! a H*\nq" | gmx make_ndx -f '+(othersgmxinput)+' -o ' +(othersindexoutput)
        os.system(cmd)
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
        #NVT equilibration
        os.system(complexnvt)
        yasara.ShowMessage("System optimization in progress. Please wait")
        os.system(runnvt)
        os.system('echo "2" \ "0" | gmx trjconv -s nvt.tpr -f nvt.trr -o nvt.gro -pbc mol -center')
        os.system('gmx editconf -f nvt.gro -o nvt.pdb')
        yasara.run("Delobj all")
        ##yasara.run("Clear")
        yasara.LoadPDB(str(macrotarget+'\\'+'nvt.pdb'))
        yasara.run("ZoomAll Steps=20")
        yasara.run("HideRes cl")
        #NPT equilibration
        os.system(complexnpt)
        yasara.ShowMessage("System optimization in progress. Please wait")
        os.system(runnpt)
        os.system('echo "2" \ "0" | gmx trjconv -s npt.tpr -f npt.trr -o npt.gro -pbc mol -center')
        os.system('gmx editconf -f npt.gro -o npt.pdb')
        yasara.run("Delobj all")
        ##yasara.run("Clear")
        yasara.LoadPDB(str(macrotarget+'\\'+'npt.pdb'))
        yasara.run("ZoomAll Steps=20")
        yasara.run("HideRes cl")
        os.system(complexmdtpr)
        mdxtc()
      else:
        yasara.ShowMessage("Please put the input files inside working the directory")                 
