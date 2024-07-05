import io
import pandas as pd
from matplotlib import pyplot as plt

from Terminals.service.PlotePolygons.SetColor import SetColor
from Terminals.service.Static.ColumnChoosing import ColumnChoosing
from StaticDB.StaticData.SystemChoices import SYSTEM_DICTIONARY


class StaticPlots:
	@staticmethod
	def plot_scatters(ax, points_coordinates, dimension: float = 100, color: str = "c", geometry: str = "o"):
		dimension = dimension if isinstance(dimension, (int, float)) else int(dimension)
		point_style = dict(s=dimension / 2, c=color, marker=geometry)
		if points_coordinates:
			if isinstance(points_coordinates[0], float) or isinstance(points_coordinates[0], int):
				ax.scatter(points_coordinates[0], points_coordinates[1], **point_style)
			else:
				ax.scatter([x[0] for x in points_coordinates], [x[1] for x in points_coordinates],
				           **point_style)

	@staticmethod
	def add_text_to_df_terminals_points_column(ax, points_, text_):
		if isinstance(points_[0], float) or isinstance(points_[0], int):
			ax.text(points_[0] + 500, points_[1] + 600, text_)
		else:
			[ax.text(p_[0] + 500, p_[1], text_) for p_ in points_]

	@staticmethod
	def save_plot(fig):
		img = io.StringIO()
		plt.axis('off')
		fig.savefig(img, format='svg')
		# clip off the xml headers from the image
		svg_img = '<svg' + img.getvalue().split('<svg')[1]
		return svg_img


class PlotTerminalsAndSpaces:
	"""static class for plotting points(terminals) and polygons(spaces). Config grid"""

	def __init__(self, terminal_df: pd.DataFrame, system_type: str, level_val: str = None):
		self.terminal_df = self.make_level_filter(terminal_df, level_val)
		self.system_type = system_type

	@staticmethod
	def make_level_filter(_df, level_val):
		if level_val:
			_df = _df[_df[ColumnChoosing.S_level] == level_val]
			return _df
		else:
			return _df

	def add_color_to_df(self):
		""" From inst class SetColor
		add color to each row by filtered column"""
		color = SetColor(self.terminal_df, SYSTEM_DICTIONARY[self.system_type].system_name_column)
		color.set_color_by_category()
		self.terminal_df = color.merge_color_df()

	def plot_terminals(self, ax):
		system_name = SYSTEM_DICTIONARY[self.system_type].system_name_column
		for index, row in self.terminal_df.iterrows():
			StaticPlots.plot_scatters(ax, row["points"], float(row["dimension1"]), row["color"],
			                          row["geometry"])
			StaticPlots.add_text_to_df_terminals_points_column(ax, row.points, row[system_name])
