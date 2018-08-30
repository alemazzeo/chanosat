.PHONY: default help object executable all clean
CC = gcc

LD = $(CC)

BIN = ../../bin/

SOURCE_C = $(wildcard *.c)
OBJECTS_C = $(patsubst %.c, $(BIN)%_c.o, $(SOURCE_C))

CFLAGS = -std=gnu99 -Wall -fPIC
LIBRARY = ../../lib/libv4l2py.so
LDFLAGS = -lm -L/usr/local/lib/sentech/ -lstcam

default: help

help:
	@echo "\
Options:\n\n\
  make objects:       compiler makes objects for every *.c\n\
  make library        build library capture.so\n\
  make all:           build all previous\n\
  make clean:         delete output files\n\
  make help:          display this help"

objects: $(OBJECTS_C)

library: $(LIBRARY)

all: objects library

$(BIN)%_c.o: %.c
	$(CC) $(CFLAGS) -g -c -fPIC $^ -o $@

%.so: $(OBJECTS_C)
	$(LD) $^ $(LDFLAGS) -shared -o $@

clean:
	rm -rfv $(OBJECTS_C) $(LIBRARY)
