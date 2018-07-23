#include "capture.h"

static void errno_exit(const char *s)
{
        fprintf(stderr, "%s error %d, %s\n", s, errno, strerror(errno));
        exit(EXIT_FAILURE);
}

static int xioctl(int fh, int request, void *arg)
{
        int r;

        do {
                r = ioctl(fh, request, arg);
        } while (-1 == r && EINTR == errno);

        return r;
}

int open_device(Device * dev)
{
    struct stat st;
    
    if (-1 == stat(dev->dev_name, &st)) {
	fprintf(stderr, "Cannot identify '%s': %d, %s\n",
		dev->dev_name, errno, strerror(errno));
	return -1;
    }
    
    if (!S_ISCHR(st.st_mode)) {
	fprintf(stderr, "%s is no device\n", dev->dev_name);
	return -1;
    }
    
    dev->fd = open(dev->dev_name, O_RDWR /* required */ | O_NONBLOCK, 0);
    
    if (-1 == dev->fd) {
	fprintf(stderr, "Cannot open '%s': %d, %s\n",
		dev->dev_name, errno, strerror(errno));
	return -1;
    }
    return 0;
}

int close_device(Device * dev)
{
    if (-1 == close(dev->fd))
	return -1;
    
    dev->fd = -1;
    return 0;
}

int print_caps(Device * dev)
{
    struct v4l2_capability caps = {};
    if (-1 == xioctl(dev->fd, VIDIOC_QUERYCAP, &caps))
    {
	return 1;
    }
    
    printf( "Driver Caps:\n"
	    "  Driver: \"%s\"\n"
	    "  Card: \"%s\"\n"
	    "  Bus: \"%s\"\n"
	    "  Version: %d.%d\n"
	    "  Capabilities: %08x\n\n",
	    caps.driver,
	    caps.card,
	    caps.bus_info,
	    (caps.version>>16)&&0xff,
	    (caps.version>>24)&&0xff,
	    caps.capabilities);
    
    
    struct v4l2_cropcap cropcap = {0};
    cropcap.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
    if (-1 == xioctl (dev->fd, VIDIOC_CROPCAP, &cropcap))
    {
	return -1;
    }
    
    printf( "Camera Cropping:\n"
	    "  Bounds: %dx%d+%d+%d\n"
	    "  Default: %dx%d+%d+%d\n"
	    "  Aspect: %d/%d\n",
	    cropcap.bounds.width,
	    cropcap.bounds.height,
	    cropcap.bounds.left,
	    cropcap.bounds.top,
	    cropcap.defrect.width,
	    cropcap.defrect.height,
	    cropcap.defrect.left,
	    cropcap.defrect.top,
	    cropcap.pixelaspect.numerator,
	    cropcap.pixelaspect.denominator);
    
    struct v4l2_fmtdesc fmtdesc = {0};
    fmtdesc.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
    char c, e;
    printf("  FMT : CE Desc\n--------------------\n");
    while (0 == xioctl(dev->fd, VIDIOC_ENUM_FMT, &fmtdesc))
    {
	strncpy(dev->fourcc, (char *)&fmtdesc.pixelformat, 4);
	c = fmtdesc.flags & 1? 'C' : ' ';
	e = fmtdesc.flags & 2? 'E' : ' ';
	printf("  %s: %c%c %s\n", dev->fourcc, c, e, fmtdesc.description);
	fmtdesc.index++;
    }
    printf("\n");
    return 0;
}

int set_pixelformat(Device * dev, int width, int height, char* fourcc)
{
    char c1 = fourcc[0];
    char c2 = fourcc[1];
    char c3 = fourcc[2];
    char c4 = fourcc[3];
    
    struct v4l2_format fmt = {0};
    
    fmt.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
    fmt.fmt.pix.width = width;
    fmt.fmt.pix.height = height;
    fmt.fmt.pix.pixelformat = v4l2_fourcc(c1, c2, c3, c4);
    fmt.fmt.pix.field = V4L2_FIELD_NONE;
    
    if (-1 == xioctl(dev->fd, VIDIOC_S_FMT, &fmt))
    {
	return -1;
    }

    dev->width = width;
    dev->height = height;
    strncpy(dev->fourcc, fourcc, 4);
    
    return 0;
}

int init_mmap(Device * dev)
{
    struct v4l2_requestbuffers req;
    static struct v4l2_buffer buf;
    
    CLEAR(req);
    
    req.count = 1;
    req.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
    req.memory = V4L2_MEMORY_MMAP;
    
    if (-1 == xioctl(dev->fd, VIDIOC_REQBUFS, &req)) {
	if (EINVAL == errno) {
	    fprintf(stderr, "%s does not support "
		    "memory mapping\n", dev->dev_name);
	    exit(EXIT_FAILURE);
	} else {
	    return -1;
	}
    }
    	
    CLEAR(buf);
    
    buf.type        = V4L2_BUF_TYPE_VIDEO_CAPTURE;
    buf.memory      = V4L2_MEMORY_MMAP;
	
    if (-1 == xioctl(dev->fd, VIDIOC_QUERYBUF, &buf))
        return -1;
	
    dev->buffer.length = buf.length;
    dev->buffer.start =
	mmap(NULL /* start anywhere */,
	     buf.length,
	     PROT_READ | PROT_WRITE /* required */,
	     MAP_SHARED /* recommended */,
	     dev->fd, buf.m.offset);
	
	if (MAP_FAILED == dev->buffer.start)
	    errno_exit("mmap");

    
    return 0;
}

int uninit_device(Device * dev)
{
    if (-1 == munmap(dev->buffer.start, dev->buffer.length))
        return -1;
    
    return 0;
}

int start_capturing(Device *dev)
{
    enum v4l2_buf_type type;
    static struct v4l2_buffer buf;
    
    CLEAR(buf);
    buf.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
    buf.memory = V4L2_MEMORY_MMAP;
	
    if (-1 == xioctl(dev->fd, VIDIOC_QBUF, &buf))
	return -1;
    
    type = V4L2_BUF_TYPE_VIDEO_CAPTURE;

    if (-1 == xioctl(dev->fd, VIDIOC_STREAMON, &type))
        return -1;
    return 0;
}

int stop_capturing(Device * dev)
{
    enum v4l2_buf_type type;
    
    type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
    if (-1 == xioctl(dev->fd, VIDIOC_STREAMOFF, &type))
	return -1;
    
    return 0;
}

int disconnect_buffer(Device * dev)
{
    static struct v4l2_buffer buf;
    	
    CLEAR(buf);
    buf.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
    buf.memory = V4L2_MEMORY_MMAP;
    
    if (-1 == xioctl(dev->fd, VIDIOC_DQBUF, &buf)) {
	switch (errno) {
	    case EAGAIN:
		return 1;
		
	    case EIO:
		/* Could ignore EIO, see spec. */
		return 2;
		/* fall through */
		
	    default:
	        return -1;
	}
    }

    return 0;
}

int reconnect_buffer(Device * dev)
{
    
    static struct v4l2_buffer buf;
    
    CLEAR(buf);
    buf.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
    buf.memory = V4L2_MEMORY_MMAP;
    
    if (-1 == xioctl(dev->fd, VIDIOC_QBUF, &buf))
	return -1;
    //errno_exit("VIDIOC_QBUF");

    return 0;
}

int setDriverCtrlValue(Device * dev, unsigned int id, int value)
{
    struct v4l2_control control;
    control.id = id;
    control.value = value;

    if (-1 == xioctl(dev->fd, VIDIOC_S_CTRL, &control))
        return -1;

    return 0;  
}

int getDriverCtrlValue(Device * dev, unsigned int id, int * value)
{
    struct v4l2_control control;
    control.id = id;

    if (-1 == xioctl(dev->fd, VIDIOC_G_CTRL, &control))
        return -1;

    *value = control.value;
    return 0;
}
