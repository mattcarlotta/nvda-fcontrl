#nvda-contrl
==========================

Python script for dynamic control of the fan speed of a Nvidia Card  
Based on the work of Luke Frisken and Mister Pup:  
https://code.google.com/p/nvidia-fanspeed/
https://github.com/MisterPup/Nvidia-Dynamic-Fan-Control

Fan speed changes depending on the temperature of the card  
A modifiable 2D curve of [temp, speed] points is used to control the fan  

Works only with proprietary drivers  
No SLI support (only single GPU configuration)  
It must be used with an open terminal  

On 349.12 and 349.16 versions there is a regression that makes impossibile to control fan speed

DEPENDENCIES  
* python  
* matplotlib  

HOW TO INSTALL  
* Install python  
  `sudo apt-get install python #on debian based distros`
* Install matplotlib  
  `sudo apt-get install python-matplotlib #on debian based distros`
* Add the following line in section "Device" of /etc/X11/xorg.conf  
  `Option         "Coolbits" "28"` or `- nvidia-xconfig --enable-all-gpus && nvidia-xconfig --cool-bits=28`

HOW TO START  
Open a terminal in the folder containing both nvidia-gui.py and nvidiafanspeed.py then execute:  
`python nvd-contrl.py`
