
import numpy as np
from scipy import interpolate


def to_hdr(stack, exposures, mininum, maximum):
    """Convert a stack of images with different exposure time
    to a High Dynamic Range Image.

    Parameters
    ----------
    stack : ndarray
        3D numpy array with the background corrected images.
        shape=(M, N, O) where M is the number of exposures.
    exposures : iterable of numbers (len=M)
        exposure times fore each slice of the stack.
    mininum : float
    maximum : float

    Returns
    -------
    ndarray, ndarray, ndarray
        hdr image, standard deviation image, values used image.
        shape of each image (N, O)

    """

    assert stack.shape[0] == len(exposures)

    tmp = np.array(stack, dtype=np.float)

    tmp[tmp < mininum] = np.nan
    tmp[tmp > maximum] = np.nan

    for ndx, factor in enumerate(exposures):
        tmp[ndx, :, :] /= factor

    return np.nanmean(tmp, axis=0), np.nanstd(tmp, axis=0), np.sum(~np.isnan(tmp), axis=0)


def substract_background(stack, exposures, bgfunc):
    """Substract background of a stack of images

    Parameters
    ----------
    stack : ndarray
        3D numpy array with the image. shape=(M, N, O) where M is the number of exposures.
    exposures : iterable of numbers (len=M)
        exposure time for each slice of the stack.
    bgfunc : func
        a callable that returns the background value any given exposure time.

    Returns
    -------
    ndarray
        background substracted stack. shape=(M, N, O)
    """

    assert stack.shape[0] == len(exposures)

    tmp = np.array(stack, dtype=np.float)

    for ndx, exposure in enumerate(exposures):
        tmp[ndx, :, :] -= bgfunc(exposure)

    return tmp


def bgfunc_from_stack(stack, exposures):
    """

    Parameters
    ----------
    stack
    exposures

    Returns
    -------

    """

    assert stack.shape[0] == len(exposures)
    y = [np.mean(stack[ndx, :]) for ndx in range(stack.shape[0])]

    return interpolate.interp1d(exposures, y, bounds_error=True)


def hdr_builder(background, bg_exposures, minimum, maximum):
    """

    THIS ASSUMES GAMMA = 1

    Parameters
    ----------
    background
    exposures

    Returns
    -------

    """

    bgfunc = bgfunc_from_stack(background, bg_exposures)

    def _internal(stack, exposures):
        corrected = substract_background(stack, exposures, bgfunc)

        return to_hdr(corrected, exposures, minimum, maximum)

    return _internal
