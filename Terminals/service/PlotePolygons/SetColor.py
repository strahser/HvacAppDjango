import random
import pandas as pd
from itertools import cycle

from matplotlib import pyplot as plt
from matplotlib import colors as mcolors


class SetColor:
	def __init__(self, df: pd.DataFrame, color_filter_name) -> None:
		"""
        input df from revit for example. Set color by unique column value.
        """
		self.df = df
		self.color_filter_name = color_filter_name
		self.color_circle = cycle(
			'orange,indigo,lightpink,darkblue,firebrick,orchid,yellowgreen,goldenrod,blue,brown,red,coral,darkmagenta,'
			'green,cyan,deeppink'.split(
				','))

	def set_color_by_category(self):
		"""
        set color to category
        """
		category = pd.unique(self.df[self.color_filter_name])
		category_color = {cat: next(self.color_circle) for en, cat in enumerate(category)}
		new_df = pd.DataFrame(category_color.items(), columns=[self.color_filter_name, "color"])
		return new_df

	def merge_color_df(self):
		"""
        merge df with set color to input(self) 
        df column_name merged column(eq column for color choose)
        """
		merged_df = self.df.merge(
			self.set_color_by_category(), on=self.color_filter_name)
		return merged_df

	@staticmethod
	def __get_color_random():
		"""
        get random color
        """
		color = ["#" + ''.join([random.choice('0123456789ABCDEF')
		                        for j in range(6)])]
		color_out = color[0]
		return color_out

	@staticmethod
	def get_cmap(n, name='hsv'):
		'''Returns a function that maps each index in 0, 1, ..., n-1 to a distinct
        RGB color; the keyword argument name must be a standard mpl colormap name.'''
		return plt.cm.get_cmap(name, n)

	@staticmethod
	def get_all_colors():
		colors = [hex for name, hex in mcolors.cnames.items()]
		return colors
