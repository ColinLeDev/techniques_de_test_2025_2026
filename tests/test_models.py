"""Tests for models serialization and deserialization to/from bytes."""
import math

import pytest

from models.Point import Point
from models.PointSet import PointSet
from models.Triangle import Triangle
from models.TriangleSet import TriangleSet


def approx_points(p1: Point, p2: Point, rel_tol=1e-6):
    """Check if two points are approximately equal."""
    return math.isclose(p1.x, p2.x, rel_tol=rel_tol) \
        and math.isclose(p1.y, p2.y, rel_tol=rel_tol)


def test_point_bytes():
    """Point.to_bytes -> Point.from_bytes bytes preserves coordinates."""
    p = Point(1.5, -2.25)
    b = p.to_bytes()
    assert isinstance(b, (bytes, bytearray))
    p2 = Point.from_bytes(b)
    assert approx_points(p, p2)


def test_triangle_bytes():
    """Triangle.to_bytes -> Triangle.from_bytes preserves indices."""
    t = Triangle(0, 5, 2)
    b = t.to_bytes()
    assert isinstance(b, (bytes, bytearray))
    t2 = Triangle.from_bytes(b)
    assert (t.p1, t.p2, t.p3) == (t2.p1, t2.p2, t2.p3)


def test_pointset_bytes():
    """PointSet.to_bytes -> PointSet.from_bytes preserves points."""
    pts = [Point(0.0, 0.0), Point(1.0, 2.0), Point(-3.5, 4.25)]
    ps = PointSet(points=pts)
    b = ps.to_bytes()
    assert isinstance(b, (bytes, bytearray))
    ps2 = PointSet.from_bytes(b)
    assert len(ps.points) == len(ps2.points)
    for a, bpt in zip(ps.points, ps2.points, strict=True):
        assert approx_points(a, bpt)


def test_pointset_empty_bytes():
    """Empty PointSet bytes."""
    ps = PointSet(points=[])
    b = ps.to_bytes()
    assert isinstance(b, (bytes, bytearray))
    ps2 = PointSet.from_bytes(b)
    assert ps2.points == []


def test_triangles_bytes():
    """Triangles.to_bytes -> Triangles.from_bytes preserves points and indices."""
    pts = [Point(0.0, 0.0), Point(1.0, 0.0), Point(0.0, 1.0), Point(1.0, 1.0)]
    tris = [Triangle(0, 1, 2), Triangle(1, 3, 2)]
    T = TriangleSet(points=pts, triangles=tris)
    b = T.to_bytes()
    assert isinstance(b, (bytes, bytearray))
    T2 = TriangleSet.from_bytes(b)
    assert len(T.points) == len(T2.points)
    assert len(T.triangles) == len(T2.triangles)
    for p_old, p_new in zip(T.points, T2.points, strict=True):
        assert approx_points(p_old, p_new)
    for t_old, t_new in zip(T.triangles, T2.triangles, strict=True):
        assert (t_old.p1, t_old.p2, t_old.p3) == (t_new.p1, t_new.p2, t_new.p3)


def test_triangles_empty_bytes():
    """Empty Triangles (no points, no triangles)."""
    T = TriangleSet(points=[], triangles=[])
    b = T.to_bytes()
    assert isinstance(b, (bytes, bytearray))
    T2 = TriangleSet.from_bytes(b)
    assert T2.points == []
    assert T2.triangles == []


def test_point_partial_bytes():
    "Point.from_bytes raises error on incomplete bytes."""
    P = Point(1.0, 2.0)
    b = P.to_bytes()
    b = b[:4]  # Truncate bytes
    with pytest.raises(ValueError):
        Point.from_bytes(b)

def test_triangle_partial_bytes():
    "Triangle.from_bytes raises error on incomplete bytes."""
    T = Triangle(0, 1, 2)
    b = T.to_bytes()
    b = b[:4]  # Truncate bytes
    with pytest.raises(ValueError):
        Triangle.from_bytes(b)

def test_pointset_partial_bytes():
    """PointSet.from_bytes raises error on incomplete bytes."""
    pts = [Point(0.0, 0.0), Point(1.0, 2.0)]
    ps = PointSet(points=pts)
    b = ps.to_bytes()
    b = b[:-4]  # Truncate bytes
    with pytest.raises(ValueError):
        PointSet.from_bytes(b)

def test_triangles_partial_bytes():
    """TriangleSet.from_bytes raises error on incomplete bytes."""
    pts = [Point(0.0, 0.0), Point(1.0, 0.0), Point(0.0, 1.0)]
    tris = [Triangle(0, 1, 2)]
    T = TriangleSet(points=pts, triangles=tris)
    b = T.to_bytes()
    b = b[:-4]  # Truncate bytes
    with pytest.raises(ValueError):
        TriangleSet.from_bytes(b)