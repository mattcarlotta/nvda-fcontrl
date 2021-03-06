# nvda-fcontrl
a python script with a GUI that creates a modifiable 2D curve of [temp, speed] points that are used to control the fan speed of a Nvidia GPU within a Linux environment.

![nvfc.png](https://github.com/mattcarlotta/nvda-fcontrl/blob/master/nvfc.png)

## Quickstart Linux

* Install python:  
  `sudo apt-get install python`
* Install matplotlib:  
  `sudo apt-get install python-matplotlib`
* Install Tkinter:  
  `sudo apt-get install python-tk`
* Install pyGTK:  
  `sudo apt-get install python-gtk2-dev`
* Install libcanberra-gtk:  
  `sudo apt-get install libcanberra-gtk-module`
* Allow the Nvidia card's fan to be controlled:  
  `sudo nvidia-xconfig --enable-all-gpus` and `sudo nvidia-xconfig --cool-bits=28`
* Reboot your computer for the GPU settings to take effect:  
  `sudo reboot`
* Open a terminal in the folder containing nvfc.py, then execute:  
  `python nvfc.py`

## Button Actions

* Apply - Applies the curve to the GPU fan for the duration of the session
* Reset - Sets the curve to default values (can be values from `config.csv`)
* Save -  Saves a `config.csv` within the app directory (if missing, loads a default curve)  

## Live Updates

* Temperature - Current GPU temperature (°C)
* Fan Speed - Current GPU fan speed (%)

## Notes
⚠️ Only works with nvidia proprietary drivers

⚠️ Versions 349.12 and 349.16 are not supported due to a regression in the drivers

⚠️ No SLI support (only single GPU configuration)

⚠️ It currently must be used with an open terminal

⚠️ Closing the app resets the GPU fan speed to auto (controlled by driver)



## Dependencies:

* python  
* matplotlib  
* Tkinter
* pyGTK
* libcanberra-gtk

Based on the work of Luke Frisken and Mister Pup:  
* https://code.google.com/p/nvidia-fanspeed/
* https://github.com/MisterPup/Nvidia-Dynamic-Fan-Control
