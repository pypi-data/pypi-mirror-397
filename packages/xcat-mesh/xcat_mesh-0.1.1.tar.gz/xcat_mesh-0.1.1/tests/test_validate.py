import numpy as np
import pytest
from xcat_mesh.validate import assert_binary_mask, assert_non_empty
from xcat_mesh.errors import BinaryMaskError, EmptyMaskError

def test_binary_ok():
    m = np.zeros((10, 10, 10), dtype=np.uint8)
    m[3:6, 3:6, 3:6] = 1
    assert_binary_mask(m)
    assert_non_empty(m)

def test_non_binary_raises():
    m = np.zeros((5,5,5), dtype=np.int16)
    m[0,0,0] = 2
    with pytest.raises(BinaryMaskError):
        assert_binary_mask(m)

def test_empty_raises():
    m = np.zeros((5,5,5), dtype=np.uint8)
    assert_binary_mask(m)
    with pytest.raises(EmptyMaskError):
        assert_non_empty(m)
