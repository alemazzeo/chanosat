#include <stdio.h>
#include <fcntl.h>
#include <unistd.h>
#include <errno.h>
#include <getopt.h>
#include <sys/ioctl.h>

#include <sentech/stcam_dd.h>
#include <sentech/stcam_lib.h>

int Cloak2Time(unsigned long clock);

int Clock2Time(char * dev_name, unsigned long * clock, float * time, int n)
{
    int i = 0;
    int retVal = 0;
    int devHandle;
    void* libHandle;
    float fValue = 0;

    printf("dev_name: %s\n", dev_name);
    devHandle = open(dev_name, O_RDWR | O_NONBLOCK, 0);
    printf("devHandle: %d\n", (int)devHandle);
    libHandle = StCam_Open(devHandle);
    printf("libHandle: %p\n", libHandle);

    for (i=0; i<n; i++)
    {
	printf("Clock: %7lu -> ", clock[i]);
	retVal = StCam_GetExposureTimeFromClock(libHandle,
						clock[i],
						&fValue);

	if (retVal != 0)
	{
	    printf("Time: %11.6f - Error code %d \n", fValue, retVal);
	}
	else
	{
	    printf("Time: %11.6f \n", fValue);
	}
	    
	time[i] = fValue;
    }

    StCam_Close(libHandle);
    close(devHandle);

    return 0;
}
