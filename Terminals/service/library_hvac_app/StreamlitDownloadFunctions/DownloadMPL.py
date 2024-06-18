import base64  # Standard Python Module
import io  # Standard Python Module
from datetime import datetime
import streamlit as st


class DownloadMPL:
	@staticmethod
	def download_mpl_pdf(fig_mpl):
		# mpl save
		mpl_buffer = io.BytesIO()
		fig_mpl.savefig(mpl_buffer, format="pdf")
		today = datetime.today().strftime('%Y-%m-%d')
		st.download_button(
			label="Download Matplotlib pdf",
			data=mpl_buffer.getvalue(),
			file_name="principal_schem" + today + ".pdf",
			mime="pdf",
		)
	
	@staticmethod
	def download_mpl_svg(save_plot_data):
		st.title("Downloads")
		st.download_button(
			label="Download Image",
			data=save_plot_data,
			file_name="image-name.svg",
			mime="svg",
		)