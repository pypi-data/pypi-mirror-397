import math
import numpy as np
from typing import Union

class SVec:
    def __init__(self, *components):
        self.lookup = {
            'x': 0,
            'y': 1,
            'z': 2,
            'w': 3,
            'r': 0,
            'g': 1,
            'b': 2,
            'a': 3,
        }
        flat_components = []
        for item in components:
            if isinstance(item, SVec):
                flat_components.extend(item.components.tolist())
            elif isinstance(item, (list, tuple, np.ndarray)):
                flat_components.extend(item)
            else:
                flat_components.append(item)
        self.components = np.array(flat_components, dtype=float)

    def __len__(self):
        return len(self.components)

    def __iter__(self):
        return iter(self.components)

    def __getitem__(self, index):
        return self.components[index]

    def __setitem__(self, index, value):
        self.components[index] = value

    def __str__(self):
        return str([round(value, 2) for value in self.components.tolist()])

    def toNPArray(self) -> np.ndarray:
        """Returns the internal NumPy array of the vector's components"""
        return self.components

    def __getattr__(self, swizzle):
        for component in swizzle:
            if not component in self.lookup:
                raise AttributeError(f"'{type(self).__name__}' object has no component '{component}'")
        swizzled_components = []
        for component in swizzle:
            swizzled_components.append(self.components[self.lookup[component]])
        if len(swizzled_components) == 1:
            return swizzled_components[0]
        if len(swizzled_components) == 2:
            return SVec2(*swizzled_components)
        if len(swizzled_components) == 3:
            return SVec3(*swizzled_components)
        if len(swizzled_components) == 4:
            return SVec4(*swizzled_components)
        else:
            return SVec(*swizzled_components)

    def __setattr__(self, swizzle, other):
        if swizzle in {"components", "lookup"}:
            super().__setattr__(swizzle, other)
            return
        for component in swizzle:
            if component not in self.lookup:
                raise AttributeError(f"'{type(self).__name__}' object has no component '{component}'")
        if len(swizzle) == 1:
            if not isinstance(other, (int, float)):
                raise TypeError(f"Expected a single number for assignment to '{swizzle}', got {type(other).__name__}")
            self.components[self.lookup[swizzle]] = other
        else:
            if not hasattr(other, "__iter__") or len(swizzle) != len(other):
                raise ValueError(f"Number of swizzle components must match the size of the value being assigned")
            for i, component in enumerate(swizzle):
                self.components[self.lookup[component]] = other[i]

    def __add__(self, other):
        if len(self) != len(other):
            raise ValueError("Vectors must have the same size")
        return self.__class__(*(self.components + other.components))

    def __sub__(self, other):
        if len(self) != len(other):
            raise ValueError("Vectors must have the same size")
        return self.__class__(*(self.components - other.components))

    def __mul__(self, scalar: Union[int, float]):
        return self.__class__(*(self.components * scalar))

    def __truediv__(self, scalar: Union[int, float]):
        return self.__class__(*(self.components / scalar))

    def __floordiv__(self, scalar: Union[int, float]):
        return self.__class__(*(self.components // scalar))

class SVec2(SVec):
    def __init__(self, *components):
        super().__init__(*components)
        if len(self.components) != 2:
            raise ValueError("SVec2 must have exactly two components")

class SVec3(SVec):
    def __init__(self, *components):
        super().__init__(*components)
        if len(self.components) != 3:
            raise ValueError("SVec3 must have exactly three components")

class SVec4(SVec):
    def __init__(self, *components):
        super().__init__(*components)
        if len(self.components) != 4:
            raise ValueError("SVec4 must have exactly four components")


# All the functions below could be methods, but since
# I aim for similarity with OpenGL, I added them as
# standalone functions

# Dimension agnostic operations:
def sdot(a: SVec, b: SVec):
    if len(a) != len(b):
        raise ValueError("Vectors must have the same size")
    return np.dot(a.components, b.components)

def slength(a: SVec):
    return np.linalg.norm(a.components)

def snormalize(a: SVec):
    length = slength(a)
    if length == 0:
        return a # Or return a zero vector of the same type/dimension
    normalized_vec = a.__class__(*(a.components / length))
    return normalized_vec

def sdistance(a: SVec, b: SVec):
    return np.linalg.norm(a.components - b.components)

def sprojection(a: SVec, b: SVec):
    return b * sdot(a, b) / sdot(b, b)

def sangle_between(a: SVec, b: SVec):
    length_a = slength(a)
    length_b = slength(b)
    if length_a == 0 or length_b == 0:
        return 0
    a_norm = a.components / length_a
    b_norm = b.components / length_b
    dot = np.dot(a_norm, b_norm)
    angle = np.arccos(np.clip(dot, -1.0, 1.0))
    return angle


# 2D vector functions
def sangle(a: SVec2):
    return np.arctan2(a.y, a.x)

def srotate(a: SVec2, angle: Union[float,int]):
    c = np.cos(angle)
    s = np.sin(angle)
    return SVec2(a.x * c - a.y * s, a.x * s + a.y * c)


# 3D vector functions
def scross(a: SVec3, b: SVec3):
    return SVec3(*(np.cross(a.components, b.components)))

def srotate_x(a: SVec3, angle: Union[float, int]):
    c = np.cos(angle)
    s = np.sin(angle)
    return SVec3(a.x, a.y * c - a.z * s, a.y * s + a.z * c)

def srotate_y(a: SVec3, angle: Union[float, int]):
    c = np.cos(angle)
    s = np.sin(angle)
    return SVec3(a.x * c + a.z * s, a.y, a.z * c - a.x * s)

def srotate_z(a: SVec3, angle: Union[float, int]):
    c = np.cos(angle)
    s = np.sin(angle)
    return SVec3(a.x * c - a.y * s, a.y * c + a.x * s, a.z)

def sazimuth_elevation_between(a: SVec3, b: SVec3):
    # Azimuth
    azimuth = -sangle_between(a.xz, b.xz)

    # Elevation angle is a bit different
    # We gotta take into account both x and z components
    # to get vectors as hipotenuses of a right triangle
    # made with their projection to the xz plane
    ah = snormalize(SVec2(slength(a.xz), a.y))
    bh = snormalize(SVec2(slength(b.xz), b.y))
    elevation = sangle_between(ah, bh)

    return azimuth, elevation

def srotate_by_azimuth_elevation(a: SVec2, azimuth: Union[float,int], elevation: Union[float,int]):
    # Elevation rotation
    result = SVec3(srotate(SVec2(slength(a.xz), a.y), elevation),0)

    # Azimuth rotation
    # Need a temporary SVec2 for the angle calculation, as sangle_between operates on SVecs
    temp_vec2_for_angle = SVec2(1,0)
    result.xz = srotate(result.xz, sangle_between(a.xz, temp_vec2_for_angle) + azimuth)

    return result

def sorthonormal_basis(a: SVec3, reference=SVec3(0,1,0)):
    a = snormalize(a)

    # If vectors are colinear, change reference
    if abs(sdot(a, reference)) == 1:
        reference = reference.zxy

    base_x = snormalize(scross(a, reference))
    base_y = snormalize(scross(a, base_x))

    return a, base_x, base_y
