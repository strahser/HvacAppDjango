import xlwings_custom_functions as xw
import os
import pandas_custom_functions as pd
def data_frame_to_excel_open(df, filename, sheet_name, start_position="A1"):
    """
    open excel file and add df
    """
    app = xw.App(visible=False)
    book = app.books.open(filename)
    ws = book.sheets[sheet_name]
    ws.clear()
    ws.range(start_position).options(pd.DataFrame, index=False).value = df
    table = ws.tables.add(source=ws[start_position].expand())
    ws.autofit("c")
    book.save()
    book.close()
    app.quit()

def data_frame_to_excel_open(
        df: pd.DataFrame,
        filename: os.path,
        sheet_name: str,
        start_position: str = "A1"):
    """ open excel book.choose sheet. choose start row column. save df to sheet
    based on xw!.

    Args:
        df (pd.DataFrame): df to save
        filename (os.path): path to file
        sheet_name (str): excel sheet name
        start_position (str, optional):  Defaults to "A1".
    """
    app = xw.App(visible=False)
    book = app.books.open(filename)
    ws = book.sheets[sheet_name]
    ws.clear()
    ws.range(start_position).options(pd.DataFrame, index=False).value = df
    ws.tables.add(source=ws[start_position].expand())
    ws.autofit("c")
    book.save()
    book.close()
    app.quit()
