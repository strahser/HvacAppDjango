import io

import matplotlib
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from matplotlib.patches import Polygon as mplPolygon
import math

from Terminals.service.PlotePolygons.plote_settings import text_style, PolygonLimits
from Terminals.service.Static.ColumnChoosing import ColumnChoosing
from Terminals.service.Utils.list_custom_functions import flatten, to_list

matplotlib.use('Agg')


class PolygonPlotter:
	def __init__(self, input_data_df: pd.DataFrame, level_val: str = None) -> None:
		"""draw polygons and add text to polygons
        """
		self.fig, self.ax = plt.subplots()
		self.fig.set_size_inches(10, 10)
		self._df = input_data_df

		self.level_column = ColumnChoosing.S_level
		self.level_val = level_val
		max_coordinates = flatten(PolygonLimits().min_max_coord(self._df, "px", "py"))
		self.x_min_max = max_coordinates[0], max_coordinates[1]
		self.y_min_max = max_coordinates[2], max_coordinates[3]

	def make_level_filter(self):
		if self.level_val:
			self._df = self._df[self._df[self.level_column] == self.level_val]
			return self._df

	def create_polygon_data(self, pol_x="px", pol_y="py"):
		"""
        create new column for zip(x,y) polygon coordinates from json polygon coordinates px,py
        """
		self._df = self._df.assign(polygon_coord=self._df.apply(lambda x: list(zip(x[pol_x], x[pol_y])), axis=1))
		return self._df

	def draw_polygons(self, is_filled: bool = False):
		for index, row in self._df.iterrows():
			p = mplPolygon(row["polygon_coord"], color="grey", fill=bool(is_filled))
			self.ax.add_patch(p)

	def add_coordinate_axis(self):
		if self._df[ColumnChoosing.S_ID].count() > 2:
			self.ax.set_xlim(*self.x_min_max)
			self.ax.set_ylim(*self.y_min_max)

	def add_ticks(self):
		if self.x_min_max and self.y_min_max:
			self.ax.set_xticks(
				np.arange(*self.x_min_max, math.ceil(self.x_min_max[1] / 10)))
			self.ax.set_yticks(
				np.arange(*self.y_min_max, math.ceil(self.y_min_max[1] / 10)))

	def add_title(self):
		self.ax.set_title(f'План {self.level_val}.', fontsize=20, style='italic', weight="bold")

	@staticmethod
	def round_for_str(val):
		try:
			res = round(val)
		except:
			res = val
		return res

	def add_text_from_df(
			self,
			df_,
			x_color_column,
			y_color_column,
			prefix_list: str,
			column_list,
			**kwargs):
		"""
        join string columns from df and add prefix
        """
		column_list = to_list(column_list)
		prefix_list = prefix_list.split(",") if isinstance(
			prefix_list, str) else prefix_list
		df_ = df_.assign(temp="").copy()
		if len(prefix_list) == len(column_list):
			for pref, colum in zip(prefix_list, column_list):
				temp_str = pref + df_[colum].apply(lambda x: self.round_for_str(x)).astype(str) + "\n"
				df_["temp"] = df_["temp"].astype(str).str.cat(temp_str)
				[
					self.ax.text(x, y, txt, kwargs) for x, y, txt in zip(
					df_[x_color_column], df_[y_color_column], df_["temp"])
				]
			df_ = df_.drop("temp", axis=1)
			return df_
		else:
			for colum in column_list:
				temp_str = df_[colum].apply(lambda x: self.round_for_str(x)).astype(str) + "\n"
				df_["temp"] = df_["temp"].astype(str).str.cat(temp_str)
				[
					self.ax.text(x, y, txt, kwargs) for x, y, txt in zip(
					df_[x_color_column], df_[y_color_column], df_["temp"])
				]
			df_ = df_.drop("temp", axis=1)
			return df_

	def save_plot(self):
		img = io.StringIO()
		self.fig.savefig(img, format='svg')
		return '<svg' + img.getvalue().split('<svg')[1]

	def plot_polygons(self, text_prefix: str = '', column_list: list = None):
		"""
        call methodes for plot polygons by level and color and add text
        """
		plt.axis('off')
		self.make_level_filter()
		self.add_coordinate_axis()
		self.create_polygon_data()
		self.add_title()
		self.draw_polygons()
		self.add_text_from_df(
			self._df,
			"pcx", "pcy",
			text_prefix,
			column_list,
			# bbox=box_1,
			**text_style)
		return self.fig
