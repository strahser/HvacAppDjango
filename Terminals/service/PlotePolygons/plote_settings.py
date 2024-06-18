from Terminals.service.Utils.list_custom_functions import flatten

box_1 = {
	'facecolor': 'red',
	'edgecolor': 'black',
	'boxstyle': 'round'
}

box_2 = {
	'facecolor': 'pink',
	'edgecolor': 'black',
	'boxstyle': 'round'
}

text_style = {
	"horizontalalignment": 'center',
	"verticalalignment": 'center',
	"fontsize": 14,
	"color": "blue",
	"style": 'italic',
}


class PolygonLimits:

	@staticmethod
	def list_value_points(d_merge, column_name):
		list_val = d_merge[column_name].values
		list_val_fl = flatten(list_val)
		return list_val_fl

	@staticmethod
	def min_max_bord(list_val: list, k=0.3):
		"""
        define min and max point for plot dim
        """
		x_max = max(list_val)
		x_min = min(list_val)
		x_mx = abs(x_max)
		x_mn = abs(x_min)
		x_max_abs = (x_mx + x_mx * k)
		x_min_abs = (x_mn + x_mn * k)

		def return_value(in_value, reform_value):
			if in_value > 0:
				return reform_value
			else:
				return -1 * reform_value

		res_min = return_value(x_min, x_min_abs)
		res_max = return_value(x_max, x_max_abs)
		return res_min, res_max

	def min_max_coord(self, d_merge, px_col_name="px", py_col_name="py"):
		x = self.min_max_bord(self.list_value_points(d_merge, px_col_name))
		y = self.min_max_bord(self.list_value_points(d_merge, py_col_name))
		return x, y
