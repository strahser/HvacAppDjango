import pandas as pd
from HvacAppDjango.settings import CONNECTION

# Create your tests here.
from StaticDB.StaticData.SystemChoices import SYSTEM_DICTIONARY
from Terminals.service.Core.AddCalculatedPointsToDF import AddCalculatedPointsToDF
from Terminals.service.InputData.InputDataDF import InputDataDF
from Terminals.service.PlotePolygons.PlotTerminals import PlotTerminalsAndSpaces
from Terminals.service.PlotePolygons.PolygonPlotter import PolygonPlotter
from Terminals.service.Static.ColumnChoosing import ColumnChoosing

space_data = pd.read_excel(r"./DbTestData/TestDb.xlsx",sheet_name='db')
equipment_data = pd.read_excel(r"./DbTestData/EquipmentBaseDb.xlsx")


equipment = "Terminals_equipmentbase"
spaces = 'Spaces_spacedata'


def get_equipment_choices():
	cursor = CONNECTION.cursor()
	cursor.execute(f"SELECT DISTINCT family_device_name  from {equipment} ")
	queryset = cursor.fetchall()
	choices = [(val[0], val[0]) for val in queryset]
	print(choices)


def add_space_data() -> None:
	space_data.to_sql(f"{spaces}", CONNECTION, if_exists="append", index=False)


def add_equipment_data() -> None:
	equipment_data.to_sql(f"{equipment}", CONNECTION, if_exists="append", index=False)


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

# add_equipment_data()
# add_space_data()
