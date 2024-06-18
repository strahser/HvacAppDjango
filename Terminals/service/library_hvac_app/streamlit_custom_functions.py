import pandas as pd
import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, DataReturnMode, ColumnsAutoSizeMode
from library_hvac_app.DbFunction.pandas_custom_function import df_to_excel_in_memory


class AggGridOptions:
	def __init__(self, df: pd.DataFrame, check_box_show_option=True, key: str = None):
		self.df = df
		self.check_box_show = check_box_show_option
		self.key = key

	def _get_grid_options(self):
		gb = GridOptionsBuilder.from_dataframe(self.df)
		gb.configure_default_column \
			(enablePivot=True,
			 enableValue=True,
			 enableRowGroup=True,
			 editable=True,
			 groupable=True,
			 min_column_width=10
			 )
		gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=15)  # Add pagination
		"""selection_mode – Either ‘single’, ‘multiple’ or ‘disabled’. Defaults to ‘single’."""
		selection_mode = "multiple" if self.check_box_show else 'single'
		gb.configure_selection(selection_mode=selection_mode,
		                       use_checkbox=self.check_box_show,
		                       header_checkbox=self.check_box_show,
		                       groupSelectsChildren=True,
		                       header_checkbox_filtered_only=self.check_box_show
		                       )
		gb.configure_side_bar()
		grid_options = gb.build()
		return grid_options

	def create_ag_selected_row_df(self, select_mode: str = "all_data"):
		"""Select mode -all data or selected rows"""
		"""
		update_mode=GridUpdateMode.SELECTION_CHANGED | GridUpdateMode.VALUE_CHANGED |
		GridUpdateMode.MODEL_CHANGED,
		"""
		if self.check_box_show:
			check_box_show_flag = dict(header_checkbox=True,
			                           headerCheckboxSelection=True,
			                           checkboxSelection=True,
			                           use_checkbox=True
			                           )
		else:
			check_box_show_flag = dict(
			)
		self.agg_table = AgGrid(self.df,
		                        gridOptions=self._get_grid_options(),
		                        columns_auto_size_mode= ColumnsAutoSizeMode.NO_AUTOSIZE,
		                        # height=600,
		                        enable_enterprise_modules=True,
		                        update_mode=GridUpdateMode.MODEL_CHANGED,
		                        data_return_mode=DataReturnMode.AS_INPUT,
		                        fit_columns_on_grid_load=False,
		                        key=self.key,
		                        **check_box_show_flag
		                        )

		return self._check_selection_option(select_mode)

	def _check_selection_option(self, select_mode) -> pd.DataFrame:
		selected_rows = self.agg_table["selected_rows"]
		all_data = self.agg_table['data']
		if select_mode == "all_data":
			return all_data
		else:
			return selected_rows


def get_download_excel_data(download_data, sheet_list, excel_file_name, label_name='Download excel table', index=True):
	buffer_list = df_to_excel_in_memory(download_data, sheet_list, index=index)

	st.download_button(
		label=f'📥 {label_name}',
		data=buffer_list,
		file_name=excel_file_name,
	)


def create_editable_standard_df(options: list[str], _df: pd.DataFrame, num_rows="fixed") -> pd.DataFrame:
	"""
    Args:
     num_rows:
     options:
     _df:
        options:al levels
    """
	df = st.data_editor(_df, num_rows=num_rows,
	                    column_config={
		                    "from_branch": st.column_config.SelectboxColumn(
			                    options=options,
			                    required=True,
		                    ),
		                    "to_branch": st.column_config.SelectboxColumn(
			                    options=options,
			                    required=True,
		                    )
	                    },
	                    hide_index=True,
	                    column_order=["from_branch", "to_branch", "distance", "flow"]
	                    )
	return df
