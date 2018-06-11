# nvda-fcontrl
a python script that creates a modifiable 2D curve of [temp, speed] points that are used to control the fan speed within a Linux envirnoment.

## Quickstart Linux

* Install python:  
  `sudo apt-get install python`
* Install matplotlib:  
  `sudo apt-get install python-matplotlib`
* Install Tkinter:  
  `sudo apt-get install python-tk`
* Allow the Nvidia card's fan to be controlled:  
  `sudo nvidia-xconfig --enable-all-gpus && nvidia-xconfig --cool-bits=28`
* Open a terminal in the folder containing nvda-fcontrl.py, then execute:  
  `python nvd-fcontrl.py`

## Notes
⚠️ Only works with Nvidia proprietary drivers  
⚠️ No SLI support (only single GPU configuration)  
⚠️ It currently must be used with an open terminal  
⚠️ Versions 349.12 and 349.16 are not supported due to a regression in the drivers

Dependencies:  
* python  
* matplotlib  
* Tkinter

Based on the work of Luke Frisken and Mister Pup:  
* https://code.google.com/p/nvidia-fanspeed/
* https://github.com/MisterPup/Nvidia-Dynamic-Fan-Control
