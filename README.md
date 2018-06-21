# chanosat
Characterization device for a star tracker's lens based on Chanoscopio from Juan Bujjamer

# geometry.py
## Geometry
Base class for plane and ray

### Plane and Ray
Display planes and ray in 3d. Allow modifications in cartesian and spherical way.
Base class for Reflection, Point and Intersection

### Chanosat
Special case of Ray with Chanoscopio's common movements.

### Reflection, Point and Intersection
Objects dependent of the interaction between rays and planes (with updates in cascade).

### Example:
```
from geometry import Plane, Ray, Chanosat, Reflection, Intersection
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

plt.ion()
fig = plt.figure()
ax = fig.gca(projection='3d')
ax.set_xlim(-100, 100)
ax.set_ylim(-90, 90)
ax.set_zlim(0, 600)


p1, p2 = Plane(ax=ax), Plane(ax=ax)
p1.z, p2.z = 300, 500
p1.phi, p2.phi = 45, 45

r1 = Chanosat(ax=ax)

r2, r3 = Reflection(r1, p1), Reflection(r1, p2)
a = Intersection(r1, p1)
b = Intersection(r1, p2)
c = Intersection(r3, p1)
```


