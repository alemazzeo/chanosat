import cv2
import rpyc
import numpy as np
import msgpack
import msgpack_numpy as m

c = rpyc.connect('10.99.39.255', 18861)
f = c.root.get_answer()
x = msgpack.unpackb(f, object_hook=m.decode)
