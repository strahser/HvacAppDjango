import os.path
import kaleido #required
from plotly import graph_objs as go
import streamlit as st
import plotly
from datetime import datetime
import zipfile
import io


def download_all_plt_html(fig: list[go.Figure], file_name: str = "plot"):
	# plt save
	all_data_html = []
	for f_ in fig:
		res = plotly.io.to_html(f_, include_plotlyjs="cdn")
		all_data_html.append(res)
	res_str = "".join(all_data_html)
	today = datetime.today().strftime('%Y-%m-%d-%H-%M')
	st.download_button(
		label="Download Plotly HTML",
		data=res_str,
		file_name=f"{file_name} {today}.html",
		mime="text/html",
	)




def download_jpg_zip(fig: list[go.Figure], file_name: str = "plot"):
	with st.expander("Plotly JPG Files Download"):
		col = st.columns(3)
		with col[0]:
			plot_width = col[0].number_input("Plot width", value=2000)
			plot_height = col[1].number_input("Plot height", value=1000)
			split_html_in_file = col[2].checkbox("Split html in separate files?", label_visibility="visible")
		# Create an in-memory buffer to store the zip file
		all_data_html = []

		with io.BytesIO() as buffer:
			# Write the zip file to the buffer
			with zipfile.ZipFile(buffer, "w") as zip:
				for en, f_ in enumerate(fig):
					# res1 = plotly.io.to_image(f_, "jpg", width=plot_width, height=plot_height, scale=1.5)
					res2 = plotly.io.to_image(f_, "pdf", width=plot_width, height=plot_height, scale=1.5)
					res3 = plotly.io.to_html(f_, include_plotlyjs="cdn", default_width=plot_width,
					                         default_height=plot_height)
					all_data_html.append(res3)
					# zip.writestr(f"{file_name}_{en + 1}.jpg", res1)
					zip.writestr(f"{file_name}_{en + 1}.pdf", res2)
					if split_html_in_file:
						zip.writestr(f"{file_name}_{en + 1}.html", res3)
				res_str = "".join(all_data_html)

				# Reset the buffer's file-pointer to the beginning of the file
				zip.writestr(f"{file_name}_all.html", res_str)
			buffer.seek(0)
			btn = st.download_button(
				label="Download ZIP",
				data=buffer,  # StreamlitDownloadFunctions buffer
				file_name=f"{file_name}.zip"
			)