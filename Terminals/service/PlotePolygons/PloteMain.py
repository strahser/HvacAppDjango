from StaticDB.StaticData.SystemChoices import SYSTEM_DICTIONARY
from Terminals.service.Core.AddCalculatedPointsToDF import AddCalculatedPointsToDF
from Terminals.service.InputData.InputDataDF import InputDataDF
from Terminals.service.PlotePolygons.PlotTerminals import PlotTerminalsAndSpaces
from Terminals.service.PlotePolygons.PolygonPlotter import PolygonPlotter
from Terminals.service.Static.ColumnChoosing import ColumnChoosing


def calculate_and_plot(_input_data_df: InputDataDF):
	all_levels = _input_data_df.full_db_df[ColumnChoosing.S_level].unique().tolist()
	plot_list = []
	for level_value in all_levels:
		polygon_plotter = PolygonPlotter(_input_data_df.full_db_df, level_value)
		polygon_plotter.create_polygon_data()
		polygon_plotter.plot_polygons("№", ["S_Number"])
		for system in SYSTEM_DICTIONARY.keys():
			calc_df = AddCalculatedPointsToDF(system, _input_data_df)
			calc_df_res = calc_df.add_polygon_and_points_to_df()
			terminals = PlotTerminalsAndSpaces(calc_df_res, system, level_value)
			terminals.add_color_to_df()
			terminals.plot_terminals(polygon_plotter.ax)
		plot_list.append(polygon_plotter.save_plot())