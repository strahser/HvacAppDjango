# -*- coding: utf-8 -*-
import Terminals.service.Geometry.GeometryLines as gl
from Terminals.service.Utils.list_custom_functions import Flatten


class CreateCurveConfig:
    curve_dict = {
        'up': ['Y', 'max'],
        'down': ['Y', 'min'],
        'left': ['X', 'min'],
        'right': ['X', 'max'],
        'center_horizontal': ['X', 'max'],
        'center_vertical': ['Y', 'max']
    }


class CheckPointLocation:
    def __init__(self, curve_list, coordinate_name: str, key_min_or_max_need: str):
        """Utility class for CreateCurvesFromStartPoint. Return curve by condition

        Args:
            curve_list (DS Curve): perimeter curves
            coordinate_name (str): 'X','Y'
            key_min_or_max_need (str): 'min','max' for dictionary
        """
        self.curve_list = curve_list
        self.coordinate_name = coordinate_name
        self.key = key_min_or_max_need

    def get_opposite_coordinate(self):
        return "X" if self.coordinate_name == "Y" else 'Y'

    def _get_start_point(self, curve):
        return round(getattr(curve.StartPoint, self.coordinate_name))

    def _get_end_point(self, curve):
        return round(getattr(curve.EndPoint, self.coordinate_name))

    def _get_opposite_start_point(self, curve):
        return round(getattr(curve.StartPoint, self.get_opposite_coordinate()))

    def _get_opposite__end_point(self, curve):
        return round(getattr(curve.EndPoint, self.get_opposite_coordinate()))

    def _get_start_points_list(self):
        start_point_list = [round(self._get_start_point(curve))
                            for curve in self._get_max_min_curves_list()]
        return start_point_list

    def _get_min_max_value(self):
        """ utility for get max value dictionary or min value from start point coordinates

        Returns:
            float: coordinate
        """
        min_max_list = dict(
            min=min(self._get_start_points_list()),
            max=max(self._get_start_points_list())
        )
        return min_max_list[self.key]

    def _get_max_min_curves_list(self):
        """from value of _get_min_max_value

        Returns:
            curve: get all curves in corner
        """

        max_list = []
        for curve in self.curve_list:
            vector_direction = round(
                getattr(self.get_curve_vector(curve), self.coordinate_name))
            if vector_direction == 1 or vector_direction == -1:
                max_list.append(curve)
        return max_list

    def _points_opposite_coordinate_different(self, curve):
        return abs(self._get_opposite_start_point(curve)) - abs(self._get_opposite__end_point(curve))

    def _points_coordinate_different(self, curve):
        return abs(self._get_start_point(curve)) - abs(self._get_end_point(curve))

    def _get_min_coordinate_start_end_point_distance(self):
        """ utility for checkin horizontal or vertical curve

        Returns:
            _type_: _description_
        """
        return min([self._points_coordinate_different(curve) for curve in self._get_max_min_curves_list()])

    @staticmethod
    def get_curve_vector(line: gl.Line):

        return line.get_normolized_vector()

    def get_curve(self):
        chosen_curve = None
        for curve in self._get_max_min_curves_list():
            if self._get_start_point(curve) == self._get_min_max_value():
                chosen_curve = curve
        return chosen_curve


class CreateCurveDictionary:
    def __init__(self, perimeter_curve: list[gl.Line]):
        """_summary_
        ceiling_offset (int, optional): offset from ceiling. Defaults to -500.
        """
        self.perimeter_curve = perimeter_curve

    def get_curves_location(self):
        for key, value in CreateCurveConfig().curve_dict.items():
            setattr(self, key, CheckPointLocation(
                self.perimeter_curve, value[0], value[1]).get_curve())
        return [getattr(self, key) for key in CreateCurveConfig().curve_dict.keys()]

    def _get_up_down_curves(self):
        return self.up, self.down

    def _get_left_right_curves(self):
        return self.left, self.right

    @staticmethod
    def _get_central_point(curve: gl.Line):
        return curve._get_central_point(1)

    @staticmethod
    def choose_long_short_curve_filter(curve_dictionary: dict,
                                       device_orientation_option1: str,
                                       device_orientation_option2: str):
        option_1: gl.Line = curve_dictionary[device_orientation_option1]
        option_2: gl.Line = curve_dictionary[device_orientation_option2]
        main_condition = option_1.Length >= option_2.Length
        if main_condition:
            long_curve = option_1
            short_curve = option_2
        else:
            long_curve = option_2
            short_curve = option_1
        return long_curve, short_curve

    def _get_center_curve(self, curve_location1, curve_location2):
        """create line by central points.

        Args:
            curve_location1 (str): left,up
            curve_location2 (_type_): right,down

        Returns:
            curve: central space curve for filtration
        """
        central_point1 = self._get_central_point(
            getattr(self, curve_location1))
        central_point2 = self._get_central_point(
            getattr(self, curve_location2))
        return gl.Line([central_point1, central_point2])

    def _get_central_line_curves(self):
        """using surface get vertical and horizontal isoline

        Returns:
            tuple of curves: vertical and horizontal isoline
        """
        self.vertical_center_curve = self._get_center_curve('up', 'down')
        self.horizontal_center_curve = self._get_center_curve('left', 'right')
        return self.vertical_center_curve, self.horizontal_center_curve

    def get_filter_curve_dict(self) -> dict[str, list]:
        self.get_curves_location()
        keys_list = CreateCurveConfig.curve_dict.keys()
        curves_list = Flatten(
            [self._get_up_down_curves(),
             self._get_left_right_curves(),
             self._get_central_line_curves()]
        )
        filter_curve_dict = {}
        for key_, curve_ in zip(keys_list, curves_list):
            filter_curve_dict[key_] = curve_
        return filter_curve_dict


class CreateCurvesFilters:
    def __init__(self,
                 curve_dictionary,
                 device_orientation_option1,
                 device_orientation_option2,
                 location_type,
                 device_points_number,
                 two_terminals_on_short_side=False):
        """_summary_

        Args:
            curve_dictionary (dict): CreateCurvesOnSurface.get_filter_curve_dict
            location_type (str): corner,center
            device_points_number (int): number of terminals,devices
            two_terminals_on_short_side(bool) - how we have to locate two terminal
        """
        self.curve_dictionary = curve_dictionary
        self.device_orientation_option1 = device_orientation_option1
        self.device_orientation_option2 = device_orientation_option2
        self.location_type = location_type
        self.device_points_number = device_points_number
        self.point_offset = 0.01
        self.min_wall_length = 1500
        self.two_terminals_on_short_side = two_terminals_on_short_side
        self.short_curve = None
        self.long_curve = None

    def choose_long_short_curve_filter(self):
        self.long_curve, self.short_curve = CreateCurveDictionary. \
            choose_long_short_curve_filter(self.curve_dictionary, self.device_orientation_option1,
                                           self.device_orientation_option2)
        return self.long_curve, self.short_curve

    def _choose_two_points_filter(self):
        return self.short_curve.Length > self.min_wall_length and self.two_terminals_on_short_side

    def split_curve_by_point_definition(self):

        self.choose_long_short_curve_filter()

        if self.location_type == "corner" and self.device_points_number == 1:
            return self.long_curve._get_corner_point(1)

        elif self.location_type == "center" and self.device_points_number == 1:
            return self.long_curve._get_central_point(1)

        elif self.device_points_number > 2:
            return self.long_curve._get_corner_and_standart_point(self.device_points_number)

        elif self.device_points_number == 2 and self._choose_two_points_filter():
            return self.short_curve._get_two_corner_points(2)

        elif self.device_points_number == 2:
            return self.long_curve._get_two_corner_points(2)
