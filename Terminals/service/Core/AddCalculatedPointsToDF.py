import pandas as pd
from shapely.geometry import Polygon

from StaticDB.StaticData.SystemChoices import SYSTEM_DICTIONARY
from Terminals.service.Core.CalculateSpaceTerminalsInDF import CalculateSpaceTerminalsInDF
from Terminals.service.Core.InsertTerminalsСalculation import InsertTerminals
from Terminals.service.Utils.Exception import ExceptionWriter
from Terminals.service.InputData.InputDataDF import InputDataDF
from Terminals.service.Static.ColumnChoosing import ColumnChoosing
import Terminals.service.Geometry.GeometryLines as gl


class AddCalculatedPointsToDF:
	def __init__(self, system_type: str, input_data_df: InputDataDF):
		"""
		расчитываем необходимое количество теримниалов, геометричекие точки вставки.
		:param system_type: тип системы из SYSTEM_DICTIONARY
		:param input_data_df:
		"""
		self.input_data_df = input_data_df
		self.system_type = system_type
		self.system_df = self._merge_system_df()

	def _merge_system_df(self) -> pd.DataFrame:
		"""
		соединяем space_systems_df с device_geometry_df, для каждой системы.
		соеденяем full_db_df (таблица с пространствами и json геометрией) с выбранным оборудованием.
		:return:
		"""
		__space_systems_df_and_equipment = self.input_data_df.space_systems_df.merge(
			self.input_data_df.device_geometry_df,
			left_on=SYSTEM_DICTIONARY[
				self.system_type].equipment_id_column,
			right_on="id")
		return self.input_data_df.full_db_df.merge(__space_systems_df_and_equipment,
		                                           left_on="S_ID",
		                                           right_on="space_data_id")

	def _create_filter_system_type(self):
		"""делаем фильтрацию по system_type"""
		self.system_df = self.system_df.assign(system_type=self.system_type)
		return self.system_df

	def _add_minimum_calculated_devices_to_df(self):
		"""расчитываем количество терминалов и их тип"""
		terminals_calculated = CalculateSpaceTerminalsInDF(self.system_df, self.input_data_df.equipment_df,
		                                                   SYSTEM_DICTIONARY[self.system_type].system_flow_column)
		self.system_df = terminals_calculated.add_k_ef_and_device_flow_to_DF()
		return self.system_df

	def _add_offset_polygon_to_df(self) -> pd.DataFrame:
		self.system_df['offset_polygon'] = self.system_df.apply(
			lambda df: df.polygon.buffer(-df.wall_offset, join_style=2), axis=1
		)
		return self.system_df

	@staticmethod
	def __polygon_offset_checking(df:pd.DataFrame):
		if isinstance(df.offset_polygon, Polygon):
			return gl.GeometryUtility.get_lines_in_polygon(df.offset_polygon.exterior.coords)
		else:
			ExceptionWriter.exception_wall_offset = f'No flow in space! space {df[ColumnChoosing.S_ID]}'
			ExceptionWriter.exception_wall_offset = f'wrong polygon offset!{df["wall_offset"]}'
			return None

	def _add_lines_of_polygon_to_df(self) -> pd.DataFrame:
		self.system_df['lines'] = self.system_df. \
			apply(lambda df: self.__polygon_offset_checking(df), axis=1)
		return self.system_df

	def _check_line_exist(self):
		self.system_df = self.system_df[self.system_df['lines'].notna()]
		return self.system_df

	def _add_curve_length_to_df(self):
		self.system_df['line_length'] = self.system_df.apply(
			lambda df: InsertTerminals(
				df.lines,
				df.device_orientation_option1,
				df.device_orientation_option2,
				df.single_device_orientation,
				1
			).get_long_curve_length(), axis=1
		)
		return self.system_df

	def _add_points_coordinates_to_df(self) -> pd.DataFrame:
		self.system_df['points'] = self.system_df. \
			apply(lambda df: InsertTerminals(
			df.lines,
			df.device_orientation_option1,
			df.device_orientation_option2,
			df.single_device_orientation,
			df.minimum_device_number
		).get_terminals_points_locations(), axis=1)
		return self.system_df

	def _change_height_of_terminal(self):
		self.system_df['pz_new'] = self.system_df.apply(lambda df: df.pz[0] - df.ceiling_offset, axis=1)
		return self.system_df

	@staticmethod
	def __add_value_to_tuple_lists(tuple_list, add_value):
		if isinstance(tuple_list[0], tuple) or isinstance(tuple_list[0], list):
			new_list = []
			for val in tuple_list:
				temp = val + (add_value,)
				new_list.append(temp)
			return new_list
		else:
			return tuple_list + (add_value,)

	def _add_pz_to_df(self):
		self.system_df['instance_points'] = self.system_df. \
			apply(lambda df: self.__add_value_to_tuple_lists(df.points, df.pz_new), axis=1)
		return self.system_df

	def add_polygon_and_points_to_df(self):
		self._create_filter_system_type()
		self._add_offset_polygon_to_df()
		self._add_lines_of_polygon_to_df()
		self._check_line_exist()
		self._add_curve_length_to_df()
		self._add_minimum_calculated_devices_to_df()
		self._add_points_coordinates_to_df()
		self._change_height_of_terminal()
		self._add_pz_to_df()
		return self.system_df
