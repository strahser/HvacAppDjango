# -*- coding: UTF-8 -*-
import os,sys
from jinja2 import Environment,FileSystemLoader


def save_html_file_from_template(
        context_dictionary:dict,
        template_folder:str,
        template_file_name:str,
        result_file_name:os.path
        )->object:
    """crate html from templates

    Args:
        context_dictionary (dict): dictionary for repacking to templates
        template_folder (str): folder
        template_file_name (str):  templates file
        result_file_path (os.path): file path to file
        result_file_name (str): file name without extension
    """
    env = Environment(loader = FileSystemLoader(template_folder),autoescape = True)
    template_df = env.get_template(template_file_name)
    rendered_page = template_df.render(**context_dictionary)

    with open(result_file_name,'w', encoding = 'utf-8') as file_:
            file_.write(rendered_page)
    return rendered_page


