import struct
from dataclasses import dataclass

@dataclass
class Triangle:
    """Triangle : 3 points in the PointSet - their indices."""
    
    p1: int
    p2: int
    p3: int

    def to_bytes(self) -> bytes:
        """Convert the Triangle to a bytes representation."""
        
        return struct.pack('<III', self.p1, self.p2, self.p3)

    @classmethod
    def from_bytes(cls, data: bytes) -> 'Triangle':
        """Create a Triangle instance from a bytes representation."""
        
        if len(data) < 12:
            raise ValueError("Insufficient data to unpack Triangle")
        
        try:
            p1, p2, p3 = struct.unpack('<III', data[:12])
        except struct.error as e:
            raise ValueError("Failed to unpack Triangle data") from e
        
        return cls(p1, p2, p3)