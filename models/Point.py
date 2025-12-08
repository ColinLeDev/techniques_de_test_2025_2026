from dataclasses import dataclass
import struct

@dataclass
class Point:
    """
    Represents a point in 2D space with x and y coordinates.
    """
    x: float
    y: float

    def to_bytes(self) -> bytes:
        """Serialize the Point instance to bytes (little endian)."""
        return struct.pack('<ff', self.x, self.y)

    @classmethod
    def from_bytes(cls, data: bytes) -> 'Point':
        """Deserialize bytes to a Point instance (little endian)."""
        try:
            x, y = struct.unpack('<ff', data)
        except struct.error as e:
            raise ValueError("Invalid byte data for Point deserialization") from e
        return cls(x, y)
        
    def to_tuple(self) -> tuple[float, float]:
        """Convert the Point instance to a tuple : (x, y)."""
        return (self.x, self.y)