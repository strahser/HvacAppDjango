import math
import warnings
from collections import namedtuple

import numpy as np
from shapely.errors import ShapelyDeprecationWarning
from shapely.geometry import Polygon, LineString, Point

warnings.filterwarnings("ignore", category=ShapelyDeprecationWarning)


class Coord(object):
	def __init__(self, x, y):
		self.X = x
		self.Y = y

	def __sub__(self, other):
		# This allows you to subtract vectors
		return Coord(self.X - other.X, self.Y - other.Y)

	def __repr__(self):
		# Used to get human-readable coordinates when printing
		return "Coord(%f,%f)" % (self.X, self.Y)

	def length(self):
		# Returns the length of the vector
		return math.sqrt(self.X ** 2 + self.Y ** 2)

	def angle(self):
		# Returns the vector's angle
		return math.atan2(self.Y, self.X)

	def values(self):
		return self.X, self.Y


class GeometryUtility:
	@staticmethod
	def cut(line, distance):
		# Cuts a line in two at a distance from its starting point
		# This is taken from shapely manual
		if distance <= 0.0 or distance >= line.length:
			return [LineString(line)]
		coords = list(line.coords)
		for i, p in enumerate(coords):
			pd = line.project(Point(p))
			if pd == distance:
				return [
					LineString(coords[:i + 1]),
					LineString(coords[i:])]
			if pd > distance:
				cp = line.interpolate(distance)
				return [
					LineString(coords[:i] + [(cp.x, cp.y)]),
					LineString([(cp.x, cp.y)] + coords[i:])]

	@staticmethod
	def split_line_with_points(line, points):
		"""Splits a line string in several segments considering a list of points.

		The points used to cut the line are assumed to be in the line string
		and given in the order of appearance they have in the line string.

		>>> line = LineString( [(1,2), (8,7), (4,5), (2,4), (4,7), (8,5), (9,18),
		...        (1,2),(12,7),(4,5),(6,5),(4,9)] )
		>>> points = [Point(2,4), Point(9,18), Point(6,5)]
		>>> [str(s) for s in split_line_with_points(line, points)]
		['LINESTRING (1 2, 8 7, 4 5, 2 4)', 'LINESTRING (2 4, 4 7, 8 5, 9 18)', 'LINESTRING (9 18, 1 2, 12 7, 4 5, 6 5)', 'LINESTRING (6 5, 4 9)']

		"""
		segments = []
		current_line = line
		for p in points:
			d = current_line.project(p)
			seg, current_line = GeometryUtility.cut(current_line, d)
			segments.append(seg)
		segments.append(current_line)
		return segments

	@staticmethod
	def get_lines_in_polygon(polygon):
		polygon_boundary = np.array(polygon)
		lines = [Line(polygon_boundary[k:k + 2])
		         for k in range(len(polygon_boundary) - 1)]
		return lines


class Line:
	def __init__(self, coordinates: list = None):
		self.coordinates = coordinates
		self._cheking_input_coordinate_tipe()
		self.line_ = LineString([self.StartPoint.values(), self.EndPoint.values()])

	def _cheking_input_coordinate_tipe(self):
		if isinstance(self.coordinates[0], Coord) and isinstance(self.coordinates[1], Coord):
			self.StartPoint = self.coordinates[0]
			self.EndPoint = self.coordinates[1]
		else:
			self.StartPoint = Coord(*self.coordinates[0])
			self.EndPoint = Coord(*self.coordinates[1])

	def values(self):
		return self.StartPoint.values(), self.EndPoint.values()

	def __ceiling_points_number(self, points_number):
		if not isinstance(points_number, int):
			return math.ceil(points_number)
		else:
			return points_number

	def _PointsAtEqualChordLength(self, points_number):
		points_number = self.__ceiling_points_number(points_number)
		split_coord = [self.line_.interpolate(
			(i / points_number), normalized=True) for i in range(1, points_number)]

		points_x = [(val.x, val.y) for val in split_coord]
		return points_x

	def _get_corner_and_standart_point(self, points_number):
		if points_number > 2:
			return self.StartPoint.values(), self.EndPoint.values(), *self._PointsAtEqualChordLength(points_number - 1)
		else:
			return self._PointsAtEqualChordLength(points_number + 1)

	def _get_standart_points(self, points_number):
		return self._PointsAtEqualChordLength(points_number + 1)

	def _get_central_point(self, points_number):
		if points_number == 1:
			return self._PointsAtEqualChordLength(points_number + 1)[0]

	def _get_corner_point(self, points_number):
		if points_number == 1:
			return self.StartPoint.values()

	def _get_two_corner_points(self, points_number):
		if points_number == 2:
			return self.StartPoint.values(), self.EndPoint.values()

	def _get_points_by_distance_from_corner(self, points_number):
		if points_number > 2:
			points = self._PointsAtEqualChordLength(points_number - 1)
			points.insert(0, self.StartPoint.values())
			points.append(self.EndPoint.values())
			return points

	@property
	def Length(self):
		return self.line_.length

	@staticmethod
	def normalize(coord):
		return Coord(
			coord.X / coord.length(),
			coord.Y / coord.length()
		)

	@staticmethod
	def perpendicular(coord):
		# Shifts the angle by pi/2 and calculate the coordinates
		# using the original vector length
		return Coord(
			coord.length() * math.cos(coord.angle() + math.pi / 2),
			coord.length() * math.sin(coord.angle() + math.pi / 2)
		)

	def get_normolized_line_direction(self):
		return self.normalize(self.EndPoint - self.StartPoint)

	def get_normolized_vector(self):
		return self.perpendicular(self.normalize(self.StartPoint - self.EndPoint))

	def __repr__(self) -> str:
		return f"{self.StartPoint, self.EndPoint}"


def offset_polygon(in_dict: dict, wall_offset=None):
	PolygonOffset = namedtuple('PolygonOffset', ['polygon', 'offset_lines'])
	polygon1 = Polygon([(x, y) for x, y in zip(in_dict["px"], in_dict["py"])])
	# offset_polygon = polygon1.buffer(-wall_offset)
	lines = GeometryUtility.get_lines_in_polygon(polygon1.exterior.coords)
	res = PolygonOffset(polygon1, lines)
	return res
