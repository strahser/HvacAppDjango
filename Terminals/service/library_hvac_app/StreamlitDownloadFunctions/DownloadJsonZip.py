import json
import zipfile
import io
import streamlit as st


def download_json_zip(json_string: dict):
	# Create an in-memory buffer to store the zip file
	with io.BytesIO() as buffer:
		# Write the zip file to the buffer
		with zipfile.ZipFile(buffer, "w") as zip:
			zip.writestr("Data.json", json.dumps(json_string, ensure_ascii=False, indent=4))
		buffer.seek(0)
		btn = st.download_button(
			label="Download ZIP",
			data=buffer,  # StreamlitDownloadFunctions buffer
			file_name="file.zip"
		)
