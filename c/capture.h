#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>

#include <getopt.h>             /* getopt_long() */

#include <fcntl.h>              /* low-level i/o */
#include <unistd.h>
#include <errno.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <sys/time.h>
#include <sys/mman.h>
#include <sys/ioctl.h>

#include <linux/videodev2.h>

#define CLEAR(x) memset(&(x), 0, sizeof(x))

struct _buffer {
    void   *start;
    size_t  length;
};

typedef struct _buffer Buffer;

struct _device {
    int      fd;
    char*    dev_name;
    int      width;
    int      height;
    char*    fourcc;
    Buffer*  buffers;
    int      n_buffers;
};

typedef struct _device Device;

static void errno_exit(const char *s);
static int xioctl(int fh, int request, void *arg);

int open_device(Device * dev);
int close_device(Device * dev);
int print_caps(Device * dev);
int get_pixelformat(Device * dev);
int set_pixelformat(Device * dev, int width, int height, char* fourcc);
int init_mmap(Device * dev);
int uninit_device(Device * dev);
int start_capturing(Device *dev);
int stop_capturing(Device * dev);
int disconnect_buffer(Device * dev);
int reconnect_buffer(Device * dev);
