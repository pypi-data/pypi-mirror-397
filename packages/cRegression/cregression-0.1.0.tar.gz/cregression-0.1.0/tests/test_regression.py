import pytest
from cRegression import LinearRegression

def test_basic():
    x = [1,2,3]
    y = [2,4,6]
    lr = LinearRegression(x, y)
    assert round(lr.predict([4])[0], 5) == 8.0
