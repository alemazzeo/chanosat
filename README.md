# chanosat
Characterization device for a star tracker's lens based on Chanoscopio from Juan Bujjamer

# Structure of repository
## Python folder

### v4l2_python.py
Wrapper (ctypes) for self developed camera's driver (see capture.c).

### geometry.py
Contents base classes geometry, ray, plane, intersecction and others.
Used by devices.py and driver.py for simulation and real control of Chanosat.

### devices.py
Contents Chanosat class. Uses ray from geometry.py and others tools and reconstruct the Chanosat device. Can be used to simulate, but designed as base of driver.

### driver.py
Based on Chanosat class from devices.py. Add serial comunication with Arduino to execute real movements

### measure.py
Control the measure process and data store. Work with task list, allow to set them from yaml file.

### viewer.py
Simple viewer for data. Allow to navigate images with arrow keys.

## C folder

### capture.c
Library of functions of Sentech camera. Based on v4l2 protocols.

### map_exposure.c
Exposure traslate from clock to time.

## Etc folder

### measure.yaml
Configuration file for measures. Allow to load lists of tasks to do.

### config.yaml
Some general configuration values.
