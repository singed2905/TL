from dataclasses import dataclass
from typing import List, Dict, Any
from dataclasses import dataclass


@dataclass
class Point2D:
    x: str
    y: str


@dataclass
class Point3D:
    x: str
    y: str
    z: str


@dataclass
class Line3D:
    A: str
    B: str
    C: str
    X: str
    Y: str
    Z: str


@dataclass
class Plane:
    a: str
    b: str
    c: str
    d: str


@dataclass
class Circle:
    x: str
    y: str
    r: str


@dataclass
class Sphere:
    x: str
    y: str
    z: str
    r: str


class GeometryData:
    def __init__(self):
        self.pheptoan_map = {
            "Tương giao": "qT2",
            "Khoảng cách": "qT3",
            "Diện tích": "qT4",
            "Thể tích": "qT5",
            "PT đường thẳng": "qT6"
        }

        self.default_group_a_tcodes = {
            "Điểm": "T1",
            "Đường thẳng": "T4",
            "Mặt phẳng": "T7",
            "Đường tròn": "Tz",
            "Mặt cầu": "Tj"
        }

        self.default_group_b_tcodes = {
            "Điểm": "T2",
            "Đường thẳng": "T5",
            "Mặt phẳng": "T8",
            "Đường tròn": "Tx",
            "Mặt cầu": "Tk"
        }

        self.operation_tcodes = {
            "Diện tích": {
                "group_a": {"Đường tròn": "T1", "Mặt cầu": "T4"},
                "group_b": {"Đường tròn": "T2", "Mặt cầu": "T5"}
            },
            "Thể tích": {
                "group_a": {"Mặt cầu": "T7"},
                "group_b": {"Mặt cầu": "T8"}
            }
        }




