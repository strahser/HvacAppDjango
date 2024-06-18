import streamlit as st


def download_svg_file(plot_fig):
	st.download_button(label='📥 Download  svg',
	                   data=plot_fig,
	                   file_name='_plot.svg')
