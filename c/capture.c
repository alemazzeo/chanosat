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
                exit(EXIT_FAILURE);
        }

        if (!S_ISCHR(st.st_mode)) {
                fprintf(stderr, "%s is no device\n", dev->dev_name);
                exit(EXIT_FAILURE);
        }

        dev->fd = open(dev->dev_name, O_RDWR /* required */ | O_NONBLOCK, 0);

        if (-1 == dev->fd) {
                fprintf(stderr, "Cannot open '%s': %d, %s\n",
                         dev->dev_name, errno, strerror(errno));
                exit(EXIT_FAILURE);
        }
	return 0;
}

int close_device(Device * dev)
{
        if (-1 == close(dev->fd))
                errno_exit("close");

        dev->fd = -1;
	return 0;
}

int print_caps(Device * dev)
{
    struct v4l2_capability caps = {};
    if (-1 == xioctl(dev->fd, VIDIOC_QUERYCAP, &caps))
    {
	perror("Querying Capabilities");
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
	perror("Querying Cropping Capabilities");
	return 1;
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

int get_pixelformat(Device * dev)
{
    struct v4l2_format fmt = {0};
    
    if (-1 == xioctl(dev->fd, VIDIOC_G_FMT, &fmt))
	errno_exit("VIDIOC_G_FMT");

    dev->width = fmt.fmt.pix.width;
    dev->height = fmt.fmt.pix.height;
    strncpy(dev->fourcc, (char *)&fmt.fmt.pix.pixelformat, 4);

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
	perror("Setting Pixel Format");
	get_pixelformat(dev);
	return 1;
    }

    get_pixelformat(dev);
    
    return 0;
}

int init_mmap(Device * dev)
{
    struct v4l2_requestbuffers req;
    
    CLEAR(req);
    
    req.count = 4;
    req.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
    req.memory = V4L2_MEMORY_MMAP;
    
    if (-1 == xioctl(dev->fd, VIDIOC_REQBUFS, &req)) {
	if (EINVAL == errno) {
	    fprintf(stderr, "%s does not support "
		    "memory mapping\n", dev->dev_name);
	    exit(EXIT_FAILURE);
	} else {
	    errno_exit("VIDIOC_REQBUFS");
	}
    }
    
    if (req.count < 2) {
	fprintf(stderr, "Insufficient buffer memory on %s\n",
		dev->dev_name);
	exit(EXIT_FAILURE);
    }
    
    dev->buffers = calloc(req.count, sizeof(*(dev->buffers)));
    
    if (!dev->buffers) {
	fprintf(stderr, "Out of memory\n");
	exit(EXIT_FAILURE);
    }
    
    for (dev->n_buffers = 0; dev->n_buffers < req.count; ++dev->n_buffers) {
	struct v4l2_buffer buf;
	
	CLEAR(buf);
	
	buf.type        = V4L2_BUF_TYPE_VIDEO_CAPTURE;
	buf.memory      = V4L2_MEMORY_MMAP;
	buf.index       = dev->n_buffers;
	
	if (-1 == xioctl(dev->fd, VIDIOC_QUERYBUF, &buf))
	    errno_exit("VIDIOC_QUERYBUF");
	
	dev->buffers[dev->n_buffers].length = buf.length;
	dev->buffers[dev->n_buffers].start =
	    mmap(NULL /* start anywhere */,
		 buf.length,
		 PROT_READ | PROT_WRITE /* required */,
		 MAP_SHARED /* recommended */,
		 dev->fd, buf.m.offset);
	
	if (MAP_FAILED == dev->buffers[dev->n_buffers].start)
	    errno_exit("mmap");
    }
    
    return 0;
}

int uninit_device(Device * dev)
{
    unsigned int i;
    
    for (i = 0; i < dev->n_buffers; ++i)
	if (-1 == munmap(dev->buffers[i].start, dev->buffers[i].length))
	    errno_exit("munmap");
    
    free(dev->buffers);
    return 0;
}

int start_capturing(Device *dev)
{
    unsigned int i;
    enum v4l2_buf_type type;
    
    for (i = 0; i < dev->n_buffers; ++i) {
	struct v4l2_buffer buf;
	
	CLEAR(buf);
	buf.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
	buf.memory = V4L2_MEMORY_MMAP;
	buf.index = i;
	
	if (-1 == xioctl(dev->fd, VIDIOC_QBUF, &buf))
	    errno_exit("VIDIOC_QBUF");
    }
    type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
    if (-1 == xioctl(dev->fd, VIDIOC_STREAMON, &type))
	errno_exit("VIDIOC_STREAMON");
    return 0;
}

int stop_capturing(Device * dev)
{
        enum v4l2_buf_type type;

	type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
	if (-1 == xioctl(dev->fd, VIDIOC_STREAMOFF, &type))
	    errno_exit("VIDIOC_STREAMOFF");

	return 0;
}

int disconnect_buffer(Device * dev)
{
    struct v4l2_buffer buf;

    CLEAR(buf);
    
    buf.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
    buf.memory = V4L2_MEMORY_MMAP;
    
    if (-1 == xioctl(dev->fd, VIDIOC_DQBUF, &buf)) {
	switch (errno) {
	    case EAGAIN:
		return 0;
		
	    case EIO:
		/* Could ignore EIO, see spec. */
		
		/* fall through */
		
	    default:
		errno_exit("VIDIOC_DQBUF");
	}
    }

    return 0;
}

int reconnect_buffer(Device * dev)
{
    struct v4l2_buffer buf;

    CLEAR(buf);
    
    buf.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
    buf.memory = V4L2_MEMORY_MMAP;
    assert(buf.index < dev->n_buffers);
    
    if (-1 == xioctl(dev->fd, VIDIOC_QBUF, &buf))
	errno_exit("VIDIOC_QBUF");
        
    return 0;
}
