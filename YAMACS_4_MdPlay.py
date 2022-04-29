# YASARA PLUGIN
# TOPIC:       YAMACS - MD play
# TITLE:       YAMACS - MD play
# AUTHOR:      A.Nardiello
# LICENSE:     Non-Commercial
#
# This is a YASARA plugin to be placed in the /plg subdirectory
# Go to www.yasara.org/plugins for documentation and downloads

# YASARA menu entry
"""
MainMenu: YAMACS
  PullDownMenu after 3-MD Run : 4-MD play
    CustomWindow: YAMACS - MD play
      Width: 600
      Height: 400
      TextInput:   X= 20,Y=50,Text="Please insert the path of working folder",Width=250,Chars=250 
      Button:      X=542,Y=348,Text="_O_ K"
    Request: 
"""
import yasara 
import os
import time


macrotarget = str((yasara.selection[0].text[0]))
pathYasara = os.getcwd()

#temporay.ini file contain all the information of input file
if os.path.isfile((macrotarget)+"/temporary.ini"):
  #reading the total number of frames generated during simulation from temporary.ini file
  f = open((macrotarget)+"/temporary.ini", "r")
  content = f.readlines()
  n =int(((content[7]).strip('\n')))

  yasara.run('Delobj all')
  yasara.run("Clear")
  #background image
  ninepng='LoadPNG '+(pathYasara)+'/'+'9.png'
  yasara.run(ninepng)
  yasara.run("ShowImage 1,Alpha=100,Priority=0")
  yasara.run('LoadPDB '+(macrotarget)+'/npt.pdb')
  yasara.run("ZoomAll Steps=20")
  yasara.run('LightSource Alpha=035,Gamma=187,Ambience=085,Shadow=010')
  #loading of each frame in the yasara window
  firstsnapshot=0
  i=firstsnapshot
  step = 1
  j=1
  while i< int(n) : 
    #time.sleep(1)
      snap= 'LoadXTC '+(macrotarget)+'/md_0_1,'+str(i+1)
      yasara.run(snap)
      yasara.run('HideRes sol')
      yasara.run('HideRes Tip')
      yasara.run('HideRes Tp3')
      yasara.run("HideRes cl")
      yasara.run("HideRes Na")
      yasara.run("ZoomAll Steps=20")
      yasara.ShowMessage('Frame number : '+str(j)+'..out of '+str(n)+'')
      #time gap between two frame is one second
      time.sleep(1)
      i= i+step
      j=i+1
    
    
else :
  #tempo.ini file contain all the information of input file
  #reading the total number of frames generated during simulation from tempo.ini file
  f = open((pathYasara)+"/tempo.ini", "r")
  content = f.readlines()
  n =int(((content[7]).strip('\n')))
  
  yasara.run('Delobj all')
  yasara.run("Clear")
  #background image
  ninepng='LoadPNG '+(pathYasara)+'/'+'9.png'
  yasara.run(ninepng)
  yasara.run("ShowImage 1,Alpha=100,Priority=0")
  yasara.run('LoadPDB '+(macrotarget)+'/npt.pdb')
  yasara.run('LightSource Alpha=035,Gamma=187,Ambience=085,Shadow=010')
  yasara.run("ZoomAll Steps=20")
  #loading of each frame in the yasara window
  firstsnapshot=0
  i=firstsnapshot
  step = 1
  j=1
  while i< int(n) : 
    #time.sleep(1)
      snap= 'LoadXTC '+(macrotarget)+'/md_0_1,'+str(i+1)
      yasara.run(snap)
      yasara.run('HideRes sol')
      yasara.run('HideRes Tip')
      yasara.run('HideRes Tp3')
      yasara.run("HideRes Na")
      yasara.run("HideRes cl")
      yasara.run("ZoomAll Steps=20")
      yasara.ShowMessage('Frame number : '+str(j)+'..out of '+str(n)+'')
      #time gap between two frame is one second
      time.sleep(1)
      yasara.run('LightSource Alpha=035,Gamma=187,Ambience=085,Shadow=010')
      i= i+step
      j=i+1

yasara.ShowMessage("Finished")  
yasara.plugin.end()  
