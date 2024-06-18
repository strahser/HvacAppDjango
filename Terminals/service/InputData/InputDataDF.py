from typing import List
import pandas as pd
from shapely import Polygon
from HvacAppDjango.settings import JSON_SPACE_PATH, CONNECTION
from Terminals.service.Utils.list_custom_functions import to_list
from Terminals.service.library_hvac_app.DbFunction.pandas_custom_function import Loader


class DbQuery:
	@staticmethod
	def create_all_table_data(Table_name: str, _id="S_ID") -> pd.DataFrame:
		return pd.read_sql(f"SELECT * FROM {Table_name}", CONNECTION) \
			.drop(["creation_stamp", "update_stamp"], axis=1)

	@staticmethod
	def create_filter_table_data(Table_name: str, id_list, _id="S_ID") -> pd.DataFrame:
		return pd.read_sql(f"SELECT * FROM {Table_name} WHERE {_id} in ({','.join(id_list)})", CONNECTION) \
			.drop(["creation_stamp", "update_stamp"], axis=1)


class InputDataDF:
	def __init__(self, id_list=None):
		self.id_list = self.check_id_list(id_list)
		self.device_geometry_df: pd.DataFrame = DbQuery.create_all_table_data("Terminals_devicegeometry")
		self.equipment_df: pd.DataFrame = DbQuery.create_all_table_data("Terminals_equipmentbase")
		self.full_db_df: pd.DataFrame = self.space_df.merge(self.json_df, how="left", on="S_ID")

	def __create_tabel_data(self, Table_name: str, _id="S_ID") -> pd.DataFrame:
		if self.id_list:
			return DbQuery.create_filter_table_data(Table_name, self.id_list, _id)
		else:
			return DbQuery.create_all_table_data(Table_name)

	@staticmethod
	def check_id_list(id_list: List[str] = None):
		if id_list:
			id_list = to_list(id_list)
			return [str(_id) for _id in to_list(id_list)]
		else:
			return None

	@property
	def space_df(self):
		return self.__create_tabel_data("Terminals_spacedata", "S_ID")

	@property
	def space_systems_df(self):
		return self.__create_tabel_data("Terminals_spacesystems", "space_data_id")

	@property
	def json_df(self):
		if self.id_list:
			json_df: pd.DataFrame = Loader(JSON_SPACE_PATH).load_json_pd()
			json_df['polygon'] = json_df.apply(
				lambda df: Polygon([(x, y) for x, y in zip(df.px, df.py)]), axis=1
			)
			json_df = json_df[json_df["S_ID"].isin(self.id_list)]
			return json_df
		else:
			json_df: pd.DataFrame = Loader(JSON_SPACE_PATH).load_json_pd()
			json_df['polygon'] = json_df.apply(
				lambda df: Polygon([(x, y) for x, y in zip(df.px, df.py)]), axis=1
			)
			return json_df
