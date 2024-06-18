import streamlit as st
def make_grid(cols: int, rows: int)->st.columns :
	grid = [0] * cols
	for i in range(cols):
		with st.container():
			grid[i] = st.columns(rows)
	return grid