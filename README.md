# nvda-contrl

Python script for dynamic fan speed control for Nvidia Cards

Based on the work of Luke Frisken and Mister Pup:  
https://code.google.com/p/nvidia-fanspeed/
https://github.com/MisterPup/Nvidia-Dynamic-Fan-Control

A modifiable 2D curve of [temp, speed] points that is used to control the fan (depending on the temperature of the card)

⚠️ Works only with proprietary drivers  
⚠️ No SLI support (only single GPU configuration)  
⚠️ It currently must be used with an open terminal  
⚠️ On 349.12 and 349.16 versions there is a regression that makes it impossibile to control fan speed

DEPENDENCIES  
* python  
* matplotlib  

HOW TO INSTALL  
* Install python  
  `sudo apt-get install python`
* Install matplotlib  
  `sudo apt-get install python-matplotlib`
* Add the following line in section "Device" of /etc/X11/xorg.conf  
  `Option         "Coolbits" "28"`
  or
  `sudo nvidia-xconfig --enable-all-gpus && nvidia-xconfig --cool-bits=28`

HOW TO START  
Open a terminal in the folder containing both nvda-contrl.py and nvfanspeed.py, then execute:  
`python nvd-contrl.py`
