import pandas as pd
from library_hvac_app.DbFunction.pandas_custom_function import df_to_excel_in_memory

import streamlit as st


def download_excel_sheets(df_list: list[pd.DataFrame],
                          df_list_name: list[str],
                          index: bool = False,
                          convert_to_table: bool = True,
                          renamed_sheet_dict: dict[str, str] = None):
	buffer_list = df_to_excel_in_memory(df_list, df_list_name,
	                                    index=index,
	                                    convert_to_table=convert_to_table,
	                                    renamed_sheet_dict=renamed_sheet_dict
	                                    )
	st.download_button(label='📥 Download Excel',
	                   data=buffer_list,
	                   file_name="excel_sheets.xlsx", )
