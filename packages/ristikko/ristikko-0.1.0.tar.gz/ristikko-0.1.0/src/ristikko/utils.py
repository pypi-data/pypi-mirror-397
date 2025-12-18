# pylint: disable=line-too-long
"""
Miscellaneous utilities.
"""
import numpy as np

def ragged_to_ndarray(ragged_list, dtype=complex, value=0):
    # pylint: disable=raise-missing-from, consider-using-enumerate
    """
    Convert a list of ndarrays, of different shapes, into an ndarray
    via padding
    """

    # Find the largest subarray
    shapes = []
    for array in ragged_list:
        shapes.append(np.array(array).shape)
    try:
        shapes = np.array(shapes, dtype=int)
    except:
        raise ValueError("All subarrays must have the same number of indices")

    # Largest subarray is our target shape
    target_shape = np.zeros(len(shapes[0]), dtype=int)
    for i in range(len(shapes[0])):
        target_shape[i] = shapes[:, i].max()
    target_shape = tuple(target_shape)
    array = np.zeros(((len(ragged_list),) + target_shape), dtype=dtype)
    for i in range(len(ragged_list)):
        pad_width = [(0, ii - i) for i, ii in zip(np.array(ragged_list[i]).shape, target_shape)]
        array[i] = np.pad(ragged_list[i], pad_width=pad_width, mode="constant", constant_values=value)

    return array
