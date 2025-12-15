"""Module defining the TriangleSet data structure and its serialization."""
import struct
from dataclasses import dataclass, field

from .Point import Point
from .PointSet import PointSet, ptSize
from .Triangle import Triangle

t_size = 12  # Each triangle consists of 3 unsigned integers (4 bytes each)


@dataclass
class TriangleSet:
    """A set of triangles defined by points."""

    points: list[Point] = field(default_factory=list)
    triangles: list[Triangle] = field(default_factory=list)

    def to_bytes(self) -> bytes:
        """Serialize the TriangleSet to bytes."""
        ps = PointSet(self.points)
        ps__bytes = ps.to_bytes()


        ts_header = struct.pack('<I', len(self.triangles))
        ts_body = b"".join(struct.pack('<III', t.p1, t.p2, t.p3) \
            for t in self.triangles)

        return ps__bytes + ts_header + ts_body

    @classmethod
    def from_bytes(cls, data: bytes) -> 'TriangleSet':
        """Deserialize a TriangleSet from bytes."""
        if len(data) < 4:
            raise ValueError("Data too short to contain TriangleSet")

        ps_count = struct.unpack_from('<I', data, 0)[0]
        ps_size = 4 + ps_count * ptSize

        if len(data) < ps_size + 4:
            raise ValueError("Data too short to contain both PointSet and TriangleSet")

        data_ps = data[:ps_size]
        data_ts = data[ps_size:]

        ps = PointSet.from_bytes(data_ps)


        t_count = struct.unpack_from('<I', data_ts[:4])[0]
        triangles = []
        offset = 4
        for k in range(t_count):
            try:
                p1, p2, p3 = struct.unpack_from('<III', data_ts[offset:offset + t_size])
            except struct.error as e:
                raise ValueError(f"Failed to unpack triangle ({k}/{t_count}): {e}") \
                    from e

            triangles.append(Triangle(p1, p2, p3))
            offset += t_size

        return cls(points=ps.points, triangles=triangles)