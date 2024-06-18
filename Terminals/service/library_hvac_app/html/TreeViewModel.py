from dataclasses import dataclass, fields, field, asdict
import streamlit as st
from streamlit_tree_select import tree_select


@dataclass
class TreeViewData:
	label: str
	value: str
	children: list = field(default_factory=list)


def get_tree_data_from_db(label: str, data: list[str]) -> dict:
	"""data provide list of string for example names of DB"""
	table_db_children = TreeViewData(label=label, value=label, children=data)
	table_db = TreeViewData(label=label, value=label,
	                        children=[{"label": val, "value": val} for val in table_db_children.children]
	                        )
	nodes = asdict(table_db)
	return nodes


def create_tree_select_view(nodes, key):
	"""add nodes key to session"""
	if key not in st.session_state:
		st.session_state[key] = {}
		if "checked" not in st.session_state[key]:
			st.session_state[key]["checked"] = []
	checked = st.session_state[key]
	if isinstance(checked, str):
		selected = tree_select(
			nodes, check_model="leaf", key=key)
		return selected

	elif isinstance(checked, dict):
		selected = tree_select(
			nodes, check_model="leaf", key=key, checked=checked.get("checked"))
		return selected
