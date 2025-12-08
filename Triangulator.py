import urllib.error
import urllib.request

from models.Point import Point
from models.PointSet import PointSet
from models.Triangle import Triangle
from models.TriangleSet import TriangleSet

class Triangulator:
    """Triangulator implementation"""
    
    def __init__(self):
        """Initialize Triangulator instance"""
        self.manager_url = "http://localhost:3000"
        
    def triangulate(self, pointSetID) -> TriangleSet:
        """Triangulate a PointSet identified by pointSetID
        
        Args:
            pointSetID (str): The ID of the PointSet to triangulate.
        
        Returns:
            TriangleSet: The resulting TriangleSet after triangulation.
        """
        if len(pointSetID) != 36: # quick check for UUID format
            raise ValueError("Invalid PointSet ID format.")
        
        try:
            pset = self.get_ps(pointSetID)
            triangles = self.compute(pset)
            
            return triangles.to_bytes()
        
        except Exception as e:
            raise RuntimeError(f"Triangulation failed: {e}")
            
    def get_ps(self, pointSetID) -> PointSet:
        """Retrieve PointSet from manager service using pointSetID
        
        Args:
            pointSetID (str): The ID of the PointSet to retrieve.
        Returns:
            PointSet: The retrieved PointSet.
        """
        url = f"{self.manager_url}/pointsets/{pointSetID}"
        try:
            with urllib.request.urlopen(url) as response:
                data = response.read()
                return PointSet.from_bytes(data)
        except urllib.error.URLError as e:
            match e.code:
                case 404:
                    raise ValueError(f"PointSet with ID {pointSetID} not found.") from e
                case 500:
                    raise RuntimeError("Manager service encountered an internal error.")
                case _:
                    raise RuntimeError(f"Failed to retrieve PointSet: {e.reason}")
                
        except Exception as e:
            raise RuntimeError(f"Failed to retrieve PointSet: {e}")
        
    def compute(self, pset: PointSet) -> TriangleSet:
        """
        Compute triangulation for the given PointSet
        
        Args:
            pset (PointSet): The PointSet to triangulate.
        Returns:
            TriangleSet: The resulting TriangleSet after triangulation.
        """
        points = sorted(pset.points, key=lambda p: p.x) # Sort points by x-coordinate
        
        n = len(points)
        if n < 3:
            return TriangleSet(points, []) # Not enough points to form triangles
        
        self._check_colinearity(points)
        
        final_triangles = []
        all_points, act_triangles = self._create_super_triangle(points)
        
        for i, pt in enumerate(points):
            bad_triangles, new_act_triangles, def_triangles = self._find_bad_triangles(pt, act_triangles)
            final_triangles.extend(def_triangles)
            
            poly = self._fill_hole_boundary(bad_triangles)
            act_triangles = new_act_triangles
            
            self._fill_hole(poly, i, all_points, act_triangles)
            
        for t in act_triangles:
            final_triangles.append(t[0])
            
        result_triangles = []
        for t in final_triangles:
            # Exclude triangles that include super triangle vertices (index >= n)
            if (t.p1 >= n) or (t.p2 >= n) or (t.p3 >= n):
                continue
            result_triangles.append(t)
            
        # Return TriangleSet with original points only (to be SAFE)
        return TriangleSet(points, result_triangles)
    
    def _check_colinearity(self, points):
        """Check if all points are collinear.
        
        Args:
            points (list[Point]): List of points to check.
        Raises:
            ValueError: If all points are collinear.
        """
        if len(points) < 3:
            raise ValueError("At least three points are required to check collinearity.")
        
        min_x = points[0].x # points sorted by x
        max_x = points[-1].x 
        max_y = max(points, key=lambda p: p.y).y
        min_y = min(points, key=lambda p: p.y).y

        if abs(max_x - min_x) < 1e-9 and abs(max_y - min_y) < 1e-9:
            raise ValueError("All points are collinear.")

        p0 = points[0]
        p_end = points[-1]

        for p in points[1:-1]:
            if self._triangle_area(p0, p_end, p) > 1e-12:
                break
        else:
            raise ValueError("All points are collinear.")
        
    def _create_super_triangle(self, points):
        """
        Create a super triangle that encompasses all points.
        Args:
            points (list[Point]): List of points to encompass.
        Returns:
            Triangle: The super triangle.
        """
        if len(points) < 3:
            raise ValueError("At least three points are required to create a super triangle.")
        
        min_x = points[0].x # points sorted by x
        max_x = points[-1].x 
        max_y = max(p.y for p in points)
        min_y = min(p.y for p in points)
        
        dx = max_x - min_x
        dy = max_y - min_y
        
        delta_max = max(dx, dy)
        mid_x = (min_x + max_x) / 2
        mid_y = (min_y + max_y) / 2
        
        # Define super triangle vertices
        # 20 times the delta_max to ensure it encompasses all points
        p1 = Point(mid_x - 20 * delta_max, mid_y - delta_max)
        p2 = Point(mid_x + 20 * delta_max, mid_y - delta_max)
        p3 = Point(mid_x, mid_y + 20 * delta_max)
        
        all_points = points + [p1, p2, p3]
        
        n = len(points)
        super_triangle = Triangle(n, n+1, n+2)
        c0, r0_sq = self._get_circumcircle(p1, p2, p3)
        
        triangles = [(super_triangle, c0[0], c0[1], r0_sq)]
        
        return all_points, triangles

    def _find_bad_triangles(self, point, triangles):
        """
        Find triangles that are 'bad' with respect to the given point
        
        Args:
            triangles (list[Triangle]): List of triangles to check.
            point (Point): The point to check against.
        
        Returns:
            list[Triangle]: List of bad triangles.
        """
        bad_triangles = [] # triangles that are 'bad' (point is inside circumcircle)
        new_triangles = [] # triangles that need to be re-evaluated later
        def_triangles = [] # triangles that can be definitively classified as 'good'
        
        px, py = point.x, point.y
        
        for item in triangles:
            t, cx, cy, r_sq = item
            
            dx = px - cx
            
            # If squared distance on x > radius squared
            # & dx is positive, point is outside circumcircle (https://mathworld.wolfram.com/images/eps-svg/Circumcircle_800.svg)
            # No future point can be inside either
            if dx > 0 and (dx ** 2) > r_sq:
                def_triangles.append(t)
                continue
            
            # Point in circumcircle
            dsq = (cx - px) ** 2 + (cy - py) ** 2
            if dsq < r_sq:
                bad_triangles.append(t)
            else:
                new_triangles.append(item)
                
        return bad_triangles, new_triangles, def_triangles
    
    def _get_circumcircle(self, p1: Point, p2: Point, p3: Point):
        """Return ((center_x, center_y), radius_sq)."""
        # https://en.wikipedia.org/wiki/Circumcircle
        
        ax, ay = p1.x, p1.y
        bx, by = p2.x, p2.y
        cx, cy = p3.x, p3.y
        
        # 2 * area of triangle
        d = 2 * (ax * (by - cy) + bx * (cy - ay) + cx * (ay - by))
        if abs(d) < 1e-12:
            raise ValueError("Points are collinear; circumcircle is undefined.")
        
        # Center
        ux = ((ax**2 + ay**2) * (by - cy) + (bx**2 + by**2) * (cy - ay) + (cx**2 + cy**2) * (ay - by)) / d
        uy = ((ax**2 + ay**2) * (cx - bx) + (bx**2 + by**2) * (ax - cx) + (cx**2 + cy**2) * (bx - ax)) / d
        
        # Radius squared
        r_sq = (ux - ax)**2 + (uy - ay)**2
        
        
        return (ux, uy), r_sq
    
    def _triangle_area(self, p1: Point, p2: Point, p3: Point) -> float:
        """
        Calculate the area of a triangle given its vertices.
        
        Args:
            p1 (Point): First vertex of the triangle.
            p2 (Point): Second vertex of the triangle.
            p3 (Point): Third vertex of the triangle.
        
        Returns:
            float: The area of the triangle.
        """
        return abs((p1.x * (p2.y - p3.y) + p2.x * (p3.y - p1.y) + p3.x * (p1.y - p2.y)) / 2.0)
    
    def _fill_hole_boundary(self, bad_triangles):
        """
        Identify the boundary edges of the polygonal hole formed by bad triangles.
        
        Args:
            bad_triangles (list[Triangle]): List of bad triangles.
        
        Returns:
            list[tuple[int, int]]: List of boundary edges as tuples of point indices.
        """
        edge_count = {}
        
        for t in bad_triangles:
            for edge in [(t.p1, t.p2), (t.p2, t.p3), (t.p3, t.p1)]:
                sorted_edge = tuple(sorted(edge))
                # Count occurrences of each edge
                # 2 times means it's internal, 1 time means it's a boundary edge
                edge_count[sorted_edge] = edge_count.get(sorted_edge, 0) + 1
        
        # Boundary edges are those that appear only once
        boundary_edges = [edge for edge, count in edge_count.items() if count == 1]
        
        return boundary_edges
    
    def _fill_hole(self, poly, pt_index, points, triangles):
        """
        Fill the polygonal hole with new triangles
        
        Args:
            poly (list[tuple[int, int]]): List of polygon edges as tuples of point indices.
            pt_index (int): Index of the new point being added.
            points (list[Point]): List of all points.
            triangles (list[tuple[Triangle, float, float, float]]): Current list of triangles with circumcircle data.
        
        Returns:
            None
        """
        new_point = points[pt_index]
        
        for edge in poly:
            p1 = points[edge[0]]
            p2 = points[edge[1]]
            new_triangle = Triangle(pt_index, edge[0], edge[1])
            
            try:
                (cx, cy), r_sq = self._get_circumcircle(new_point, p1, p2)
                triangles.append((new_triangle, cx, cy, r_sq))
            except ValueError:
                continue