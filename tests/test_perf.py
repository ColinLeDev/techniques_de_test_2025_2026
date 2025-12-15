"""Tests de performance pour la triangulation et l'encodage binaire des PointSets."""
import random
import time

import pytest

from models.Point import Point
from models.PointSet import PointSet
from Triangulator import Triangulator

pytestmark = pytest.mark.perf

tri = Triangulator()


def generate_pointset(size: int, distribution: str, amplitude: tuple = (0, 1000)):
    """Génère un PointSet selon une distribution spécifique."""
    minv, maxv = amplitude
    points = []

    match distribution:
        case "uniform":
            # x = U(min_val, max_val), y = U(min_val, max_val)
            points = [
                Point(random.uniform(minv, maxv), random.uniform(minv, maxv))
                for _ in range(size)
            ]
        case "linear":
            # y = m * x, avec m = 1.5
            # x = U(min_val, max_val)
            points = []
            for _ in range(size):
                x = random.uniform(minv, maxv)
                y = x * 1.5
                points.append(Point(x, y))

        case _:
            raise ValueError(f"Distribution inconnue: {distribution}")

    return PointSet(points)


@pytest.mark.parametrize("Amplitude", [(0, 10), (0, 100), (0, 1000)])
@pytest.mark.parametrize("size", [100, 1000, 5000])
@pytest.mark.parametrize("distribution", ["uniform", "linear"])
def test_perf_triangulation_compute(size, distribution, Amplitude):
    """Temps de calcul de la triangulation."""
    pset = generate_pointset(size, distribution, amplitude=Amplitude)

    start_time = time.time()
    if distribution == "linear":
        with pytest.raises(ValueError, match="Collinear points"):
            tri.compute(pset)
    else:
        tri.compute(pset)
    end_time = time.time()

    duration = end_time - start_time
    print(f"\n[Triangulat°] {size} ({distribution}, Amp={Amplitude}) : {duration:.4f}s")

@pytest.mark.parametrize("size", [1000, 10000])
def test_perf_binary_encoding(size):
    """Temps d'encodage binaire d'un PointSet."""
    pset = generate_pointset(size, "uniform")

    start_time = time.time()
    _ = pset.to_bytes()
    end_time = time.time()

    duration = end_time - start_time
    print(f"\n[Encoding] {size} points : {duration:.4f}s")