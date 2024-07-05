import pandas as pd
from HvacAppDjango.settings import CONNECTION
import json
# Create your tests here.
from StaticDB.StaticData.SystemChoices import SYSTEM_DICTIONARY
from Terminals.service.Core.AddCalculatedPointsToDF import AddCalculatedPointsToDF
from Terminals.service.InputData.DbNames import DbNames
from Terminals.service.InputData.InputDataDF import InputDataDF
from Terminals.service.PlotePolygons.PlotTerminals import PlotTerminalsAndSpaces
from Terminals.service.PlotePolygons.PolygonPlotter import PolygonPlotter
from Terminals.service.Static.ColumnChoosing import ColumnChoosing

space_data = pd.read_excel(r"./DbTestData/TestDb.xlsx", sheet_name='db')
equipment_data = pd.read_excel(r"./DbTestData/EquipmentBaseDb.xlsx")


def get_equipment_choices():
	cursor = CONNECTION.cursor()
	cursor.execute(f"SELECT DISTINCT family_device_name  from {DbNames.equipment_base} ")
	queryset = cursor.fetchall()
	choices = [(val[0], val[0]) for val in queryset]

	print(choices)


def add_space_data() -> None:
	space_data.to_sql(f"{DbNames.space_data}", CONNECTION, if_exists="append", index=False)


def add_equipment_data() -> None:
	equipment_data.to_sql(f"{DbNames.equipment_base}", CONNECTION, if_exists="append", index=False)


def polygon_creator_test(_input_data_df: InputDataDF):
	all_levels = _input_data_df.full_db_df[ColumnChoosing.S_level].unique().tolist()
	plot_list = []
	for level_value in all_levels:
		polygon_plotter = PolygonPlotter(_input_data_df.full_db_df, level_value)
		polygon_plotter.create_polygon_data()
		polygon_plotter.plot_polygons("№", ["S_Number"])
		for system in SYSTEM_DICTIONARY.keys():
			calc_df = AddCalculatedPointsToDF(system, _input_data_df)
			calc_df_res = calc_df.add_polygon_and_points_to_df()
			print(calc_df_res.columns)
			terminals = PlotTerminalsAndSpaces(calc_df_res, system, level_value)
			terminals.add_color_to_df()
			terminals.plot_terminals(polygon_plotter.ax)
		plot_list.append(polygon_plotter.save_plot())


def plot_db_data():
	_input_data_df = InputDataDF()  # [928208,928209]
	_input_data_df.json_df.to_html("json_df.html")
	_input_data_df.space_systems_df.to_html("space_systems_df.html")
	_input_data_df.space_df.to_html("full_db_df.html")
	polygon_creator_test(_input_data_df)


def add_json_data_to_data_base(json_path):
	cursor = CONNECTION.cursor()
	cursor.execute("select S_ID from Spaces_spacedata")
	id_list = [val[0] for val in cursor.fetchall()]
	with open(json_path) as f:
		json_data = json.load(f)
	for k, v in json_data.items():
		if k in id_list:
			sql_update_query = "Update Spaces_spacedata set geometry_data = json_insert (?) where S_ID = ?"
			data = (json.dumps(v), str(k))
			cursor.execute(sql_update_query, data)
			CONNECTION.commit()
			print(f"Запись{k} успешно обновлена")
	cursor.close()


# add_equipment_data()
# add_space_data()
# _input_data_df = InputDataDF()  # [928208,928209]
# _input_data_df.json_df.to_html("json_df.html")
# _input_data_df.space_systems_df.to_html("space_systems_df.html")
json_path = r'C:\Users\Strakhov\YandexDisk\ProjectCoding\HvacAppDjango\polygon_data_file.json'
add_json_data_to_data_base(json_path)
