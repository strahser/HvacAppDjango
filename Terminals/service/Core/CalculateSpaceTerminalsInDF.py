import math
import pandas as pd
from Terminals.service.Core.ChooseTerminalFromDBModel import ChooseTerminalsInstanceFromDB
from Terminals.service.Static.ColumnChoosing import ColumnChoosing


class CalculateSpaceTerminalsInDF:
	def __init__(self, space_and_terminal: pd.DataFrame, equipment_df: pd.DataFrame, system_flow_column: str):
		"""Расчитываем количество device в разных режимах
        """
		self.space_and_terminal = space_and_terminal
		self.system_flow_column = system_flow_column
		self.equipment_df = equipment_df

	def _calculation_factory(self) -> pd.DataFrame:
		"""make general loop from calculation_option in option_df
        Returns:
            pd.DataFrame: terminal choosing instance.
        """
		terminal_base = []
		for index, row in self.space_and_terminal.iterrows():
			option_df = self._checking_calculation_option(row)
			temp = option_df.assign(S_ID=row[ColumnChoosing.S_ID])
			terminal_base.append(temp)
		terminal_base_concat = pd.concat(terminal_base) \
			.reset_index(drop=True) \
			.drop(ColumnChoosing.family_device_name, axis=1)
		return terminal_base_concat

	def _checking_calculation_option(self, row):
		choosing_terminal = ChooseTerminalsInstanceFromDB(
			self.equipment_df,
			row[ColumnChoosing.family_device_name],
			row[self.system_flow_column],
		)

		if row['directive_terminals']:
			res = choosing_terminal.get_terminal_from_points_number(row['directive_terminals'])
			res['calculation_option'] = 'directive_terminals'
			return res

		elif row['directive_length'] and row['directive_length'] > 0:
			calculated_points = math.ceil(row['line_length'] / row['directive_length'])
			res = choosing_terminal.get_terminal_from_points_number(calculated_points)
			res['calculation_option'] = 'directive_length'
			return res

		elif row['device_area'] and row['device_area'] > 0:
			calculated_points = math.ceil(row['S_area'] / row['device_area'])
			res = choosing_terminal.get_terminal_from_points_number(calculated_points)
			res['calculation_option'] = 'device_area'
			return res

		else:
			res = choosing_terminal.get_minimum_device_number()
			res['calculation_option'] = 'minimum_terminals'
			return res

	def __join_spaces_and_terminals_DF(self) -> pd.DataFrame:
		joined_df = self._calculation_factory()
		full_base = self.space_and_terminal.merge(joined_df, how='left', on=ColumnChoosing.S_ID)
		return full_base

	def add_k_ef_and_device_flow_to_DF(self) -> pd.DataFrame:
		full_base = self.__join_spaces_and_terminals_DF()
		full_base['k_ef'] = (full_base[self.system_flow_column] / full_base['minimum_device_number']) / full_base[
			'max_flow']
		full_base['flow_to_device_calculated'] = full_base[self.system_flow_column] / full_base['minimum_device_number']
		return full_base
