import warnings

import numpy
from affine import Affine

from rioxarray._spatial_utils import affine_to_coords


def test_affine_to_coords_avoids_deprecated_matrix_multiplication() -> None:
    transform = Affine(1, 0, 0, 0, -1, 4)
    with warnings.catch_warnings():
        warnings.simplefilter("error", PendingDeprecationWarning)
        coords = affine_to_coords(transform, width=4, height=4)

    numpy.testing.assert_array_equal(coords["x"], [0.5, 1.5, 2.5, 3.5])
    numpy.testing.assert_array_equal(coords["y"], [3.5, 2.5, 1.5, 0.5])
