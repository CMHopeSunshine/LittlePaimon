from __future__ import annotations

from typing import List, Tuple

import numpy as np
from sklearn.cluster import KMeans
from shapely.geometry import Point, Polygon

from .models import XYPoint

Pos = Tuple[float, float]
Poses = List[XYPoint]
Points = List[Point]


def k_means_points(
    points: List[XYPoint], length: int = 500, clusters: int = 3
) -> List[Tuple[XYPoint, XYPoint, Poses]]:
    """
    通过 K-Means 获取集群坐标列表

    参数：
        points: `list[XYPoint]`
            坐标列表，建议预先使用 `convert_pos` 进行坐标转换

        length: `int` (default: 500)
            区域大小，如果太大则可能一个点会在多个集群中

        clusters: `int` (default: 3)
            集群数量

    返回：
        `list[tuple[XYPoint, XYPoint, list[XYPoint]]]`

        tuple 中：
            第 1 个元素为集群最左上方的点
            第 2 个元素为集群最右下方的点
            第 3 个元素为集群内所有点

        list 按照集群内点的数量降序排序

    提示：
        length：
                +---------------------+
                │                     │
                │                     │
                │                     │
                |--length--|--length--│
                │                     │
                │                     │
                │                     │
                +---------------------+
    """
    pos_array = np.array(points)
    k_means = KMeans(n_clusters=clusters).fit(pos_array)
    points_temp: List[Points] = []
    for k_means_pos in k_means.cluster_centers_:
        x = (
            k_means_pos[0] - length if k_means_pos[0] > length else 0,
            k_means_pos[0] + length,
        )
        y = (
            k_means_pos[1] - length if k_means_pos[1] > length else 0,
            k_means_pos[1] + length,
        )
        path = Polygon(
            [(x[0], y[0]), (x[0], y[1]), (x[1], y[1]), (x[1], y[0])]
        )

        points_temp.append(
            [Point(i) for i in pos_array if path.contains(Point(i))]
        )
    return_list = []
    for i in points_temp:
        pos_array_ = np.array([p.xy for p in i])
        return_list.append(
            (
                XYPoint(pos_array_[:, 0].min(), pos_array_[:, 1].min()),
                XYPoint(pos_array_[:, 0].max(), pos_array_[:, 1].max()),
                list(map(lambda p: XYPoint(p.x, p.y), i)),
            )
        )
    return sorted(
        return_list, key=lambda pos_tuple: len(pos_tuple[2]), reverse=True
    )
