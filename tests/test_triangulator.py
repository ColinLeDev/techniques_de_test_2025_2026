"""Unit tests for the Triangulator class."""
import pytest

from models.Point import Point
from models.PointSet import PointSet
from Triangulator import Triangulator

tri = Triangulator()

def test_three_points_produces_one_triangle():
    """Given 3 non-colinear points, Triangulator should return exactly 1 triangle.
    
    and the triangle should reference the three input points.
    """
    points = [Point(0.0, 0.0), Point(1.0, 0.0), Point(0.0, 1.0)]
    pset = PointSet(points)
    result = tri.compute(pset)
    assert len(result.triangles) == 1
    t = result.triangles[0]
    indices = {t.p1, t.p2, t.p3}
    assert indices == {0, 1, 2}

def test_square_produces_two_triangles():
    """Given 4 points forming a square (or rectangle), should return 2 triangles."""
    points = [Point(0.0, 0.0), Point(1.0, 0.0), Point(1.0, 1.0), Point(0.0, 1.0)]
    pset = PointSet(points)
    result = tri.compute(pset)
    assert len(result.triangles) == 2

def test_regular_polygon_produces_n_minus_2_triangles():
    """Polygon with n points (n>=3), should return n-2 triangles.
    
    Example: pentagon -> 3 triangles.
    """
    points = [
        Point(0, 10), Point(10, 0), Point(10, 10),
        Point(0, 0), Point(5, 15)
    ]
    pset = PointSet(points)
    result = tri.compute(pset)
    expected_triangles = len(points) - 2
    assert len(result.triangles) == expected_triangles

def test_no_points_returns_empty_triangles():
    """Empty pointset, should return zero triangles."""
    pset = PointSet([])
    result = tri.compute(pset)
    assert len(result.triangles) == 0
    assert len(result.points) == 0

def test_one_point_returns_empty_triangles():
    """Given a single point, Triangulator should return zero triangles."""
    pset = PointSet([Point(0.0, 0.0)])
    result = tri.compute(pset)
    assert len(result.triangles) == 0

def test_two_points_returns_empty_triangles():
    """Given two distinct points, Triangulator should return zero triangles."""
    pset = PointSet([Point(0.0, 0.0), Point(1.0, 1.0)])
    result = tri.compute(pset)
    assert len(result.triangles) == 0

def test_duplicate_points_handled_or_error():
    """Given point sets containing duplicate points.
    
    - Return triangles based on unique geometry
    - or simply handle it gracefully without crashing.
    """
    points = [Point(0, 0), Point(1, 0), Point(0, 1), Point(0, 0)]
    pset = PointSet(points)
    result = tri.compute(pset)
    assert len(result.triangles) <= 1

def test_colinear_points_no_triangles():
    """Given multiple colinear points, triangulation must produce zero triangles."""
    points = [Point(0, 0), Point(1, 1), Point(2, 2)]
    pset = PointSet(points)
    with pytest.raises(ValueError, match="All points are collinear."):
        tri.compute(pset)

def test_triangle_indices_within_pointset_range():
    """All vertex must be indices in point range."""
    points = [Point(0, 0), Point(10, 0), Point(5, 5)]
    pset = PointSet(points)
    result = tri.compute(pset)
    max_index = len(points) - 1
    for t in result.triangles:
        assert 0 <= t.p1 <= max_index
        assert 0 <= t.p2 <= max_index
        assert 0 <= t.p3 <= max_index

def test_invalid_input_type_raises():
    """Test invalid input types handling.

    Given invalid input types (e.g. None, wrong structure), Triangulator should
    raise an Exception (AttributeError or TypeError).
    """
    with pytest.raises((AttributeError, TypeError)):
        tri.compute(None)