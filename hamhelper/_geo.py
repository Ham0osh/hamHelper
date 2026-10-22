"""Just enough mapmaking for HamColour.example_map, using only numpy and matplotlib.

The example map used to need Basemap, which is large, awkward to install and missing for some Pythons. All it
did with it was read a polygon shapefile and apply spherical Mercator. Both are short:

    read_shapefile(path)    ESRI .shp (polygons and lines) plus its .dbf table  ->  list of Shape
    read_dbf(path)          the .dbf table on its own                            ->  list of dict
    Mercator(...)           the projection Basemap calls 'merc' (same sphere, same lower-left origin)
    polygon_path(parts)     rings -> one matplotlib Path, with holes left empty

This is not a general GIS toolkit: no points, no multipatch, no reprojection, longitudes are not wrapped at the
date line. Format: ESRI Shapefile Technical Description (July 1998) and the dBASE III table layout.
"""
import os
import struct
from typing import NamedTuple

import numpy as np
from matplotlib.path import Path

__all__ = ['Shape', 'read_shapefile', 'read_dbf', 'Mercator', 'polygon_path']

# Shape types whose records are "bounding box, parts, points": PolyLine, Polygon and their Z / M versions.
# (The Z and M values come after the x, y pairs and are ignored here.)
_PART_TYPES = {3: 'PolyLine', 5: 'Polygon', 13: 'PolyLineZ', 15: 'PolygonZ', 23: 'PolyLineM', 25: 'PolygonM'}


class Shape(NamedTuple):
    """One record of a shapefile.

    number:     record number as stored in the file (1, 2, 3, ...)
    parts:      list of (n, 2) float arrays of x, y. For polygons each part is one ring, closed (first point
                repeated last). In ESRI files outer rings run clockwise and holes anticlockwise.
    attributes: the matching row of the .dbf table, {} when there is none
    """
    number: int
    parts: list
    attributes: dict


def read_shapefile(path, encoding='iso-8859-15'):
    """Read a polygon or polyline shapefile.

    Args:
        path (str): Path to the file, with or without the '.shp' extension. If a '.dbf' table sits beside it
                    the rows are attached to the shapes.
        encoding (str, optional): Text encoding of the .dbf. Defaults to 'iso-8859-15', which is what
                    Statistics Canada's boundary files use.

    Returns:
        list of Shape: one per record, in file order. Null shapes come back with no parts.

    Raises:
        FileNotFoundError: no .shp at that path.
        ValueError: not a shapefile, or a shape type other than polygon / polyline.
    """
    base = path[:-4] if path.lower().endswith('.shp') else path
    shp = base + '.shp'
    with open(shp, 'rb') as f:
        raw = f.read()

    if len(raw) < 100 or struct.unpack('>i', raw[:4])[0] != 9994:
        raise ValueError("'{}' is not a shapefile (bad file code)".format(shp))
    file_type = struct.unpack('<i', raw[32:36])[0]
    if file_type not in _PART_TYPES:
        raise ValueError("'{}' holds shape type {}; only polygon and polyline files are supported"
                         .format(shp, file_type))
    end = struct.unpack('>i', raw[24:28])[0] * 2  # file length is stored in 16-bit words
    end = min(end, len(raw))

    attrs = read_dbf(base + '.dbf', encoding) if os.path.exists(base + '.dbf') else None

    shapes = []
    pos = 100
    while pos + 8 <= end:
        number, words = struct.unpack('>2i', raw[pos:pos + 8])
        body = pos + 8
        pos = body + words * 2
        if struct.unpack('<i', raw[body:body + 4])[0] == 0:  # null shape
            shapes.append((number, []))
            continue
        # type, box (4 doubles), then the two counts
        n_parts, n_points = struct.unpack('<2i', raw[body + 36:body + 44])
        starts = np.frombuffer(raw, dtype='<i4', count=n_parts, offset=body + 44)
        xy = np.frombuffer(raw, dtype='<f8', count=2 * n_points, offset=body + 44 + 4 * n_parts)
        xy = xy.reshape(n_points, 2)
        stops = np.append(starts[1:], n_points)
        shapes.append((number, [xy[a:b] for a, b in zip(starts, stops)]))

    if attrs is not None and len(attrs) != len(shapes):
        raise ValueError("'{}' has {} shapes but its .dbf has {} rows".format(shp, len(shapes), len(attrs)))
    return [Shape(n, parts, attrs[i] if attrs is not None else {}) for i, (n, parts) in enumerate(shapes)]


def read_dbf(path, encoding='iso-8859-15'):
    """Read a dBASE III / IV table (the attribute table of a shapefile).

    Text fields are decoded with `encoding` and stripped; numeric fields become int or float (None if blank);
    logical fields become True / False / None; dates stay as 'YYYYMMDD' strings. The deletion flag is ignored
    so that row i still belongs to shape i.

    Returns:
        list of dict: one per row, keys are the field names.
    """
    with open(path, 'rb') as f:
        raw = f.read()
    n_rows, header_len, row_len = struct.unpack('<IHH', raw[4:12])

    fields = []  # (name, type, length, decimals)
    pos = 32
    while pos < header_len - 1 and raw[pos:pos + 1] != b'\r':
        name = raw[pos:pos + 11].split(b'\x00')[0].decode('ascii', 'replace')
        fields.append((name, chr(raw[pos + 11]), raw[pos + 16], raw[pos + 17]))
        pos += 32

    rows = []
    for i in range(n_rows):
        start = header_len + i * row_len + 1  # +1 skips the deletion flag
        row = {}
        for name, kind, length, decimals in fields:
            text = raw[start:start + length].decode(encoding, 'replace').strip()
            start += length
            row[name] = _dbf_value(text, kind, decimals)
        rows.append(row)
    return rows


def _dbf_value(text, kind, decimals):
    if kind in ('N', 'F'):
        try:
            return float(text) if (kind == 'F' or decimals or '.' in text) else int(text)
        except ValueError:
            return None  # blank, or '*****' for a number that did not fit
    if kind == 'L':
        return {'Y': True, 'y': True, 'T': True, 't': True,
                'N': False, 'n': False, 'F': False, 'f': False}.get(text)
    return text


class Mercator(object):
    """Spherical Mercator, the projection Basemap(projection='merc', ...) uses by default.

    Coordinates are metres on the sphere, measured from the lower-left corner of the map, so the map fills
    x in [0, xmax] and y in [0, ymax]. Use it with an equal-aspect axes.

    Args:
        llcrnrlon, llcrnrlat, urcrnrlon, urcrnrlat (float): corners of the map in degrees.
        rsphere (float, optional): radius of the sphere in metres. Defaults to 6370997, Basemap's value. It
                    only scales the numbers, never the shapes.

    Example:
        m = Mercator(-144, 41, -51, 83.7)
        x, y = m(lon, lat)          # arrays or scalars
        lon, lat = m.inverse(x, y)
        ax.set(xlim=(0, m.xmax), ylim=(0, m.ymax), aspect='equal')
    """

    xmin = 0.0
    ymin = 0.0

    def __init__(self, llcrnrlon, llcrnrlat, urcrnrlon, urcrnrlat, rsphere=6370997.0):
        if not (-90 < llcrnrlat < urcrnrlat < 90):
            raise ValueError('latitudes must satisfy -90 < llcrnrlat < urcrnrlat < 90 (Mercator is infinite at '
                             'the poles)')
        if not llcrnrlon < urcrnrlon:
            raise ValueError('llcrnrlon must be less than urcrnrlon')
        self.rsphere = float(rsphere)
        self._lon0 = np.radians(llcrnrlon)
        self._y0 = self._merc(np.radians(llcrnrlat))
        self.llcrnrlon, self.llcrnrlat = llcrnrlon, llcrnrlat
        self.urcrnrlon, self.urcrnrlat = urcrnrlon, urcrnrlat
        self.xmax, self.ymax = (float(v) for v in self(urcrnrlon, urcrnrlat))

    @staticmethod
    def _merc(phi):
        # isometric latitude: ln tan(pi/4 + phi/2)
        return np.log(np.tan(np.pi / 4 + phi / 2))

    def __call__(self, lon, lat):
        """Degrees -> (x, y) in metres from the lower-left corner."""
        x = self.rsphere * (np.radians(lon) - self._lon0)
        y = self.rsphere * (self._merc(np.radians(lat)) - self._y0)
        return x, y

    def inverse(self, x, y):
        """(x, y) in metres from the lower-left corner -> degrees."""
        lon = np.degrees(np.asarray(x) / self.rsphere + self._lon0)
        lat = np.degrees(2 * np.arctan(np.exp(np.asarray(y) / self.rsphere + self._y0)) - np.pi / 2)
        return lon, lat

    def __repr__(self):
        return 'Mercator(llcrnrlon={}, llcrnrlat={}, urcrnrlon={}, urcrnrlat={})'.format(
            self.llcrnrlon, self.llcrnrlat, self.urcrnrlon, self.urcrnrlat)


def polygon_path(parts, projection=None):
    """Join polygon rings into one matplotlib Path.

    One path per shape (rather than one patch per ring) keeps holes empty, because ESRI orients outer rings
    clockwise and holes anticlockwise and matplotlib fills with the non-zero winding rule. It also lets
    matplotlib's path simplification thin out vertices that fall inside one pixel. Rings are not closed with
    CLOSEPOLY (that would switch the simplification off); a filled path closes itself, and shapefile rings
    already repeat their first point.

    Args:
        parts (list of (n, 2) arrays): the rings, x then y.
        projection (callable, optional): e.g. a Mercator; called as projection(x, y) -> (x, y).

    Returns:
        matplotlib.path.Path
    """
    if not len(parts):
        return Path(np.empty((0, 2)))
    verts = np.concatenate(parts)
    if projection is not None:
        x, y = projection(verts[:, 0], verts[:, 1])
        verts = np.column_stack((x, y))
    codes = np.full(len(verts), Path.LINETO, dtype=Path.code_type)
    codes[np.cumsum([0] + [len(p) for p in parts[:-1]])] = Path.MOVETO
    return Path(verts, codes)
