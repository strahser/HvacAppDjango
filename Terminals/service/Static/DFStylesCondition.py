def style_less_then(value, key_value=0.8, ):
	if value < 0.6:
		return 'background-color:yellow'

	elif key_value > value > 0.6:
		return 'background-color:green'
	elif value > 0.9:
		return 'background-color:red'


def apply_style_to_df(df_out, output_columns):
	return df_out[output_columns].style.applymap(style_less_then, subset='k_ef')
