import math
import pandas as pd
from Terminals.service.Static.ColumnChoosing import ColumnChoosing


class ChooseTerminalsInstanceFromDB:
    def __init__(self, terminal_base: pd.DataFrame, family_device_name: str, space_flow: float, ):
        """choose minimum terminal in terminal db by space flow data

        Args:
            terminal_base (pd.DataFrame): _description_
            family_device_name (str): _description_
            space_flow (float): _description_
        Returns:
            pd.DataFrame: _description_
        """
        self.family_device_name = family_device_name
        self.terminal_base = terminal_base
        self.space_flow = space_flow

    def _get_terminal_instance_family(self) -> pd.DataFrame:
        """make filter in terminals base by family name"""
        filter_ = self.terminal_base[ColumnChoosing.family_device_name] == self.family_device_name
        return self.terminal_base[filter_]

    @staticmethod
    def __query_min_column_value_in_DF(df, column_filter):
        return df[column_filter] == df[column_filter].min()

    def get_minimum_device_number(self) -> pd.DataFrame:
        if self.space_flow > 0:
            terminals_data = self._get_terminal_instance_family().copy()
            terminals_data['minimum_device_number'] = (self.space_flow / terminals_data.max_flow).apply(math.ceil)
            terminals_data = terminals_data[
                self.__query_min_column_value_in_DF(terminals_data, 'minimum_device_number')]
            terminals_data = terminals_data[self.__query_min_column_value_in_DF(terminals_data, 'max_flow')]
            return terminals_data

    @staticmethod
    def __check_correct_terminal_points_quantity(calculated_flow_to_instance, max_terminal_flow):
        flow_value = max_terminal_flow - calculated_flow_to_instance
        return flow_value if flow_value > 0 else None

    def get_terminal_from_points_number(self, calculated_points) -> pd.DataFrame:
        if self.space_flow > 0 and calculated_points:
            terminals_data = self._get_terminal_instance_family().copy()
            terminals_data['minimum_device_number'] = calculated_points
            terminals_data['minimum_terminal_flow'] = float(self.space_flow) / float(calculated_points)
            terminals_data['minimum_terminal_flow'] = terminals_data.apply(
                lambda df:
                self.__check_correct_terminal_points_quantity(df.minimum_terminal_flow, df.max_flow), axis=1)
            terminals_data = terminals_data[self.__query_min_column_value_in_DF(
                terminals_data, 'minimum_terminal_flow')]
            if terminals_data.empty:
                return self.get_minimum_device_number()
            else:
                return terminals_data
        else:
            return self.get_minimum_device_number()
