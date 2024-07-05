from collections import namedtuple

from Terminals.service.InputData.InputDataDF import *
from Terminals.service.library_hvac_app.DbFunction.pandas_custom_function import create_json_list, df_to_excel_in_memory
import pandas as pd


class TerminalsDownloadResult:
    def __init__(self, concat_df: pd.DataFrame, input_data_df: InputDataDF):
        self.concat_df = concat_df
        self.input_data_df = input_data_df

    def _create_downloads_excel(self):
        concated_df = self.concat_df[self.input_data_df.df_device_result_columns + ['system_name']]
        excel_list = df_to_excel_in_memory([concated_df], ['level_values'])
        return excel_list

    def _create_downloads_json(self):
        json_list = create_json_list(self.concat_df, self.input_data_df.json_df_columns)
        return json_list

    def create_download_data(self):
        DownLoadData = namedtuple('DownLoadData', ['excel_file', 'json_file'])
        excel_file = self._create_downloads_excel()
        json_file = self._create_downloads_json()
        return DownLoadData(excel_file, json_file)
