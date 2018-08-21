import argparse
import numpy as np
import matplotlib.pyplot as plt
from skimage.measure import label, regionprops
from skimage.transform import rotate

plt.style.use('dark_background')
