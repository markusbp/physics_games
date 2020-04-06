import pytest

def test_1():
    assert 5e-4 + 5e-4 == pytest.approx(1e-3)
