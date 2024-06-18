from typing import List
import pandas as pd
from django.urls import reverse
from django_pandas.io import read_frame
from django.db import models
from dataclasses import dataclass, asdict
from django.template.loader import render_to_string
# region buttons Data
from AdminUtils import get_standard_display_list


@dataclass
class ButtonData:
    url: str
    pk_name: str = 'pk'
    cls: str = 'info'
    name: str = 'изменить'

    def dict(self):
        return {k: str(v) for k, v in asdict(self).items()}


def button_link(url: str, name: str = "изменить", cls='info'):
    return f'<a href="{url}"class="btn btn-{cls} mr-5"   role="button">{name}</a>'


def create_reverse_button(pk, button_data: ButtonData):
    url = reverse(button_data.url, kwargs={button_data.pk_name: pk})
    res = button_link(url, cls=button_data.cls, name=button_data.name)
    if res:
        return res
    else:
        return ""


def create_group_button(buttons: str) -> str:
    return '<div class="btn-group " role="group" aria-label="Basic example">' + buttons + '</div>'


def create_crud_buttons(qs, group_buttons_data: list[ButtonData]) -> list[str]:
    create_button = []
    for qs_data in qs:
        join_list = []
        for button_data in group_buttons_data:
            button = create_reverse_button(qs_data.id, button_data)
            join_list.append(button)
        create_button.append(create_group_button(''.join(join_list)))
    return create_button


# endregion DD
def df_html(df: pd.DataFrame, table_id="zero_config", index=False, formatters=None) -> str:
    """Обертка со стилями для экспорта дата фрейм в html"""
    return df.to_html(index=index, classes="table table-striped table-bordered ", border=1, render_links=True,
                      justify='center', escape=False, table_id=table_id, formatters=formatters)


def renamed_dict(model_type: models.Model) -> dict[str, str]:
    """переименовываем столбцы модели django согласно заданному verbose name """
    names = get_standard_display_list(model_type)
    res_dict = {}
    for val in names:
        try:
            res_dict[val] = model_type._meta.get_field(val).verbose_name
        except:
            pass
    return res_dict


def create_table_from_model(model_name: models.Model, qs, filter_columns: list[str] = None) -> pd.DataFrame:
    """создаем таблицу на основе модели django (выбираем все записи если qs не задан) через библиотеку
    django_pandas read_frame добавляем столбец с пустой ссылкой на id модели
    задаем id для data table рендера
    """
    res_dict = renamed_dict(model_name)
    df = read_frame(qs, verbose=True, datetime_index=False)
    if filter_columns:
        return df.filter(filter_columns).rename(res_dict, axis="columns")
    else:
        return df.rename(res_dict, axis="columns")


def render_modal_window(pk: int, title: str, modal_body: str, button_name='Детали'):
    """созадаем модльное окно которое можем вызывать из таблицы"""
    context = dict(pk=pk, title=title, modal_body=modal_body, button_name=button_name)
    return render_to_string(template_name='HtmlTemplates/modal.html', context=context)


def create_table_style():
    props = [
        ('border-style', 'none '),
        ('border-width', '1px'),
        ('text-align', 'center'),
        ('background', '#efefef'),
        ('font-weight', 'bold')
    ]
    table_props = [
        ('border', '1px solid #eee'),
        ('table-layout', 'fixed'),
        ('width', '100%'),
        ('margin-bottom', '20px')
    ]
    selector_th = {'selector': 'th', 'props': props}
    selector_td = {'selector': 'td', 'props': props[:-3]}
    selector_table = {'selector': 'table', 'props': table_props}
    return selector_th,selector_td


def style_email_tables(s):
    return [
        'background-color:#fff;'
        if s.name % 2
        else 'background-color: #F7F7F7;'
        for v in s]
