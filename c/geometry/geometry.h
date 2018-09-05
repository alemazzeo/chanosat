#include <stdio.h>
#include <math.h>

struct _geometry {
    double* point;
    double* normal;
};

struct _sweep {
    double* theta;
    int len_theta;
    double* shift;
    int len_shift;
    double* phi;
    int len_phi;
};

struct _polar {
    double rho;
    double theta;
    double alpha;
    double beta;
};

struct _chano {
    double shift, theta, phi;
    double x, y, z;
    double offset_shift;
    double offset_theta;
    
};

typedef struct _geometry Geometry;
typedef struct _sweep Sweep;
typedef struct _polar Polar;
typedef struct _chano Chano;

int plane_collision(Geometry ray, Geometry plane, Geometry* collision);
int transform_chano(Chano chano, Geometry* ray);
int reflection(Geometry ray, Geometry plane, Geometry* reflection);
int transform_system(Chano ray, Geometry lens, Polar* new_coords);
int explore(char * file, Sweep sweep, Chano chano, Geometry lens,
	    double min_radius, double max_radius);
