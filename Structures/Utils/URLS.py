import inspect
import os


def get_root_dir():
	current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
	parent_dir = os.path.dirname(current_dir)
	return os.path.dirname(parent_dir)