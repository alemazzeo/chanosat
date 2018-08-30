#include "geometry.h"

int plane_collision(Geometry ray, Geometry plane, Geometry* collision){

    double n=0, s=0;
    
    for (int i=0; i<3; i++){
	n += plane.normal[i] * ray.normal[i];
	s += plane.normal[i] * (plane.point[i] - ray.point[i]);
    }

    if (fabs(n) < 1e-6){
	return -1;
    }

    for (int i=0; i<3; i++){
	collision->point[i] = ray.normal[i] * s + ray.point[i];
	collision->normal[i] = ray.normal[i];
    }

    return 0;
}

int transform_chano(Chano chano, Geometry* ray){

    ray->point[0] = chano.x + chano.shift * cos(chano.theta);
    ray->point[1] = chano.y + chano.shift * sin(chano.theta);
    ray->point[2] = chano.z;
    
    ray->normal[0] = sin(chano.phi) * cos(chano.theta);
    ray->normal[1] = sin(chano.phi) * sin(chano.theta);
    ray->normal[2] = cos(chano.phi);

    return 0;
}

int reflection(Geometry ray, Geometry plane, Geometry* reflection){

    double dot1=0, dot2=0;
    double diff[3];
    int r;

    r = plane_collision(ray, plane, reflection);
    
    if (r != 0)
	return -1;

    for (int i=0; i<3; i++){
	dot1 += plane.normal[i] * ray.normal[i];
	dot2 += ray.normal[i] * ray.normal[i];
    }

    for (int i=0; i<3; i++){
	diff[i] = 2 * plane.normal[i] * dot1 / dot2;
	reflection->normal[i] = ray.normal[i] - diff[i];
    }

    return 0;
}

int transform_system(Chano chano, Geometry lens, Polar* new_coords){
    
    Geometry ray, collision;
    double x, y;
    int r;
    
    double r_point[3], r_normal[3];
    double c_point[3], c_normal[3];
    ray.point = r_point;
    ray.normal = r_normal;
    collision.point = c_point;
    collision.normal = c_normal;

    transform_chano(chano, &ray);
    r = plane_collision(ray, lens, &collision);

    if (r != 0)
	return -1;

    x = collision.point[0] - lens.point[0];
    y = collision.point[1] - lens.point[1];
    
    new_coords->rho = sqrt(x*x + y*y);
    new_coords->theta = atan2(y, x);

    new_coords->alpha = chano.phi * cos(chano.theta - new_coords->theta);
    new_coords->beta = chano.phi * sin(chano.theta - new_coords->theta);
    
    return 0;
}

int explore(char * file, Sweep sweep, Chano chano, Geometry lens,
	    double min_radius, double max_radius){

    Polar result;

    FILE * fp;

    chano.theta = 1;
    
    printf("Open file...");

    fp = fopen(file, "w+");

    printf("Done.\nPrinting header...");

    fprintf(fp, "#%-9s%-9s%-9s%-9s%-9s%-9s%-9s\n\n",
	    "rho", "theta", "alpha", "beta",
	    "theta", "phi", "shift");

    printf("Done.\n");
    
    for (int i=0; i<sweep.len_theta; i++){
	for (int j=0; j<sweep.len_phi; j++){
	    for (int k=0; k<sweep.len_shift; k++){
		chano.theta = sweep.theta[i];
		chano.phi = sweep.phi[j];
		chano.shift = sweep.shift[k];
		transform_system(chano, lens, &result);

		if (result.rho <= max_radius && result.rho >= min_radius){   
		    fprintf(fp,
			    "%-+9.3f,%-+9.3f,%-+9.3f,%-+9.3f,"\
			    "%-+9.5f,%-+9.5f,%-+9.3f\n",
			    result.rho, result.theta,
			    result.alpha, result.beta,
			    chano.theta, chano.phi, chano.shift);
		}
	    }
	}
    }

    fclose(fp);

    return 0;
}
