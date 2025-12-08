
from dataclasses import dataclass, field
import struct

from .Point import Point

ptSize = 8 # Size of a Point in bytes (2 floats of 4 bytes each)

@dataclass
class PointSet:
    """Represents a set of points."""
    
    points: list[Point] = field(default_factory=list)

    def to_bytes(self) -> bytes:
        """Serializes the PointSet to bytes."""
        byte_data = struct.pack('I', len(self.points))  # Number of points
        for point in self.points:
            byte_data += point.to_bytes()
        return byte_data

    @classmethod
    def from_bytes(cls, byte_data: bytes) -> 'PointSet':
        """Deserializes bytes to a PointSet."""
        
        if len(byte_data) < 4:
            raise ValueError("Insufficient data to unpack PointSet.")
        
        num_points = struct.unpack('<I', byte_data[:4])[0]
        points = []
        offset = 4
        
        for k in range(num_points):
            if offset + ptSize > len(byte_data):
                raise ValueError(f"Insufficient data to unpack Point ({k}/ {num_points}).")
            
            bytePoint = byte_data[offset:offset + ptSize]
            point = Point.from_bytes(bytePoint)
            points.append(point)
            offset += ptSize
            
        return cls(points)