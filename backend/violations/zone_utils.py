from typing import List, Tuple

Point = Tuple[float, float]


def point_in_polygon(point: Point, polygon: List[Point]) -> bool:
    """
    Ray-casting point-in-polygon test. `polygon` is a list of (x, y)
    vertices in order (not necessarily closed - first point isn't repeated
    at the end).
    """
    x, y = point
    n = len(polygon)
    inside = False
    j = n - 1
    for i in range(n):
        xi, yi = polygon[i]
        xj, yj = polygon[j]
        intersect = ((yi > y) != (yj > y)) and (
            x < (xj - xi) * (y - yi) / (yj - yi + 1e-12) + xi
        )
        if intersect:
            inside = not inside
        j = i
    return inside