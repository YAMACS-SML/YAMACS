# YASARA PLUGIN
# TOPIC:       YAMACS - Select atom
# TITLE:       YAMACS - Select atom
# AUTHOR:      J. Santoro
# LICENSE:     Non-Commercial
#
# This is a YASARA plugin to be placed in the /plg subdirectory
# Go to www.yasara.org/plugins for documentation and downloads

# YASARA menu entry
"""
MainMenu: YAMACS
  PullDownMenu after 4-MD play: 5-Select Atom 
    CustomWindow: YAMACS - Select atom
      Width: 600
      Height: 400
      Text: X= 20,Y= 48,Text="A new YASARA window will open. Select the atoms in the new window for further calculations"     
      TextInput:   X= 20,Y=150,Text="Please insert the path of working directory",Width=250,Chars=250
      Button:      X=542,Y=348,Text="_O_ K"
    Request: 
"""
 

# YASARA functions, such as retrieving selections
import yasara
import subprocess
import os
from yasara import *
import io
import sys

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
patname=str((macrotarget)+"/file_select.txt")
mcrpath=str((macrotarget)+"/select_atom.mcr")
yas_ndx=str((macrotarget)+"/yas_index.ndx")
print(macrotarget)
print(mcrpath)
print(yas_ndx)
plgpath=os.getcwd()
yasarafld=os.path.normpath(os.getcwd() + os.sep + os.pardir)
print(yasarafld)
if os.path.exists(patname):
  os.remove(patname)
else:
  print("The file does not exist")
if os.path.exists(yas_ndx):
  os.remove(yas_ndx)
else:
  print("The file does not exist")
if os.path.exists(mcrpath):
  os.remove(mcrpath)
else:
  print("The file does not exist")
  
#background image
yasara.run("Clear")
ninepng='LoadPNG '+(plgpath)+'/'+'9.png'
yasara.run(ninepng)
yasara.run("ShowImage 1,Alpha=100,Priority=0")
#write macro
with open(mcrpath, 'a') as the_file:
    the_file.write("showmessage 'Load structure file, select the desired atoms then press continue'\n")
    the_file.write("wait continuebutton\n")
    the_file.write("listatom()= ListAtom Selected,format=ATOMNUM\n")
    the_file.write("showmessage 'Please wait'\n")
    the_file.write("k= CountAtom selected\n")
    the_file.write("for n in listatom()\n")
    the_file.write("  tabulate (n)\n")
    the_file.write("SaveTab 1,"+(patname)+",Format=Text\t,Columns=15,NumFormat=1.0f\n")
    the_file.write("showmessage 'Finished! Close this yasara window to continue'\n")  
    the_file.write("wait continuebutton\n")
#PlayMacro /personale/file/select_atom.mcr
yasafolder=str((yasarafld)+"/yasara") # percorso dove è salvato yasara
yasaramcrpath=(macrotarget) #percorso dove è salvata la macro
cmddue= str(str(yasaramcrpath)+'/select_atom.mcr')
joined=str(yasafolder)+" "+str(cmddue)
print(cmddue)
print (joined)
print (type(joined))

def execute():
  with cd(yasaramcrpath):
    os.system(joined)
  return ()
ex=execute()
print (ex)

f=open(patname)  
f1=open(macrotarget+'/yas_index.ndx','w')
k='[ yasara ]'
f1.writelines(k)
names_list = [line.strip() for line in f if line.strip()]
for x in names_list:
    f1.write('\n')
    #f1.writelines(\n)
    f1.write(x)
f1.write('\n')
f.close()
f1.close()
yasara.ShowMessage("Selection file saved in:" + macrotarget+"/yas_index.ndx")
#RMSD calculation
os.chdir(macrotarget)
os.system('gmx rms -s md_0_1.tpr -n yas_index.ndx -f md_0_1.xtc -o rmsd.xvg -tu ns')
#Radius of gyration calculation
os.system('gmx gyrate -s md_0_1.tpr -n yas_index.ndx -f md_0_1.xtc -o rg.xvg')
#RMSF calculation
os.system('gmx rmsf -s md_0_1.tpr -n yas_index.ndx -f md_0_1.xtc -o rmsf.xvg')
#solvent accessible surface area calculation
os.system('echo "0" | gmx sasa -s md_0_1.tpr -n yas_index.ndx -f md_0_1.xtc -o sasa.xvg -tu ns')
try:
    os.remove(patname)
    os.remove(mcrpath)
except:
    pass
yasara.ShowMessage("Finished")  
yasara.plugin.end()
