import pandas_custom_functions as pd
import numpy as np
import win32com.client as win32
import os
from bs4 import BeautifulSoup  # you also need to install "lxml" for the XML parser
def copy_sheets_active_wb(sheet_names_list, file_path=False, copy_sheet_name="Расчет"):
    """
    create copy of sheet excel in active book or opened book
    """
    app = win32.Dispatch("Excel.Application")
    app.DisplayAlerts = False
    if file_path:
        app.visible = 0
        wb = app.Workbooks.Open(file_path)
    else:
        wb = app.ActiveWorkbook  # in active app
    sheet = wb.Worksheets[copy_sheet_name]
    created_sheets = []
    for en, sn in enumerate(sheet_names_list):
        if wb.Worksheets[en].Name not in sheet_names_list:
            sheet.Copy(Before=wb.Worksheets(copy_sheet_name))
            wb.Worksheets[en].Name = sn
            wb.Worksheets[en].Range('C2').value = sn
            print(wb.sheets[en].Name, en)
            created_sheets.append(wb.sheets[en].Name)
        else:
            pass
    if file_path:
        wb.Save()
        wb.Close(SaveChanges=True)
        app.Quit()
    return created_sheets



def export_excel_diagrams(excel_book, out_folder,chart_title_text = "AHU"):
    xlApp = win32.Dispatch('Excel.Application')
    workbook = xlApp.Workbooks.Open(excel_book)
    xlApp.DisplayAlerts = False
    for sheet in workbook.Worksheets:
        for chartObject in sheet.Shapes:
            if chartObject.Type == 3:
                sheet.ChartObjects(
                    1).Chart.ChartTitle.Text = chart_title_text + sheet.Name
                print(sheet.Name + ':' + chartObject.Name)
                file_name = sheet.Name + ".jpg"
                out_file_png = os.path.join(out_folder, file_name)
                sheet.ChartObjects(1).Chart.Export(out_file_png)
    workbook.Close(SaveChanges=False)



class ExcelToPdf:
    def __init__(self, 
        path_to_excel_file:os.path, 
        out_pdf_folder:os.path,
        project_name:str = None,
        header_name:str = None) -> None:
        """open excel file. Add formating to colontitul and to table. Print to pdf

        Args:
            path_to_excel_file (os.path): path to single file
            out_pdf_folder (os.path): _description_
            project_name (str, optional): _description_. Defaults to None.
            header_name (str, optional): _description_. Defaults to None.
        """
        self.path_to_excel_file = path_to_excel_file
        self.header_name = header_name
        self.project_name = project_name
        self.out_pdf_folder = out_pdf_folder
        self.excel = win32.Dispatch("Excel.Application")
        self.excel.Visible = False
        self.excel.ScreenUpdating = False
        self.excel.DisplayAlerts = False
        self.excel.EnableEvents = False

    def check_header_name(self, work_sheet):
        """
        colontitul header
        """
        if self.header_name == None:
            return work_sheet.Name
        elif self.header_name:
            return self.header_name[work_sheet.Name]

    def open_work_book(self):
        self.wb = self.excel.Workbooks.Open(self.path_to_excel_file)

    def add_ws_format(self):
        for ws in self.wb.Worksheets:
            header_name_out = self.check_header_name(ws)
            ws.Columns.AutoFit()
            ws.Pagesetup.PrintTitleRows = "$1:$1"
            ws.Pagesetup.Orientation = 2
            ws.Pagesetup.Zoom = False
            ws.Pagesetup.FitToPagesWide = 1
            ws.Pagesetup.FitToPagesTall = False
            # ws.Pagesetup.CenterHorizontally = True
            ws.Pagesetup.Papersize = 9
            ws.Pagesetup.LeftMargin = self.excel.CentimetersToPoints(2)
            ws.Pagesetup.RightMargin = self.excel.CentimetersToPoints(0.5)
            ws.Pagesetup.TopMargin = self.excel.CentimetersToPoints(1.5)
            ws.Pagesetup.BottomMargin = self.excel.CentimetersToPoints(1)
            ws.Pagesetup.HeaderMargin = self.excel.CentimetersToPoints(0.5)
            ws.Pagesetup.FooterMargin = self.excel.CentimetersToPoints(0.5)
            ws.PageSetup.LeftHeader = f'&C&"Courier New,Bold Italic"&22{header_name_out}'
            ws.PageSetup.RightFooter = '&"Courier New,Bold Italic"&10 Страница &С&P из &К&N '
            ws.PageSetup.LeftFooter = f'&L&"Courier New,Bold Italic"&10{self.project_name}'

    def print_ws_to_pdf(self):
        for ws in self.wb.Worksheets:
            path_pdf = os.path.join(self.out_pdf_folder, ws.Name)
            ws.ExportAsFixedFormat(0, path_pdf)

    def print_wb_to_pdf(self):
        path_pdf = os.path.join(self.out_pdf_folder, self.wb.Name)
        self.wb.ExportAsFixedFormat(0, path_pdf)

    def close_excel(self):
        self.wb.Save()
        self.wb.Close()
        self.excel.Application.Quit()

def read_excel_sheet_names(excel_file_path):
    from zipfile import ZipFile
    with ZipFile(excel_file_path) as zipped_file:
        summary = zipped_file.open(r'xl/workbook.xml').read()
    soup = BeautifulSoup(summary, "xml")
    sheets = [sheet.get("name") for sheet in soup.find_all("sheet")]
    return sheets

def concat_excel_sheets(excel_file_path, excel_range, key_group_name_cell):
    """
    open excel sheets and create concate. xw engine
    """
    app = win32.Dispatch('Excel.Application')
    app.visible = 0
    wb = app.Workbooks.Open(excel_file_path, ReadOnly=True)
    df_list = []
    for en, ln in enumerate(key_group_name_cell):

        ws = wb.Worksheets[en]
        if str(ws.name) == ln:
            excel_data = ws.Range(excel_range).value  # select excel table
            syste_name_excel = ws.Range(
                key_group_name_cell).value  # select system name
            df = pd.DataFrame(data=excel_data)

            df.rename(columns=df.iloc[0], inplace=True)
            # add system name column
            df = df.assign(system_name=syste_name_excel)

            df.drop(df.index[0], inplace=True)
            # df_drop = df.reindex(df.index.drop(0))
            df.replace("", np.NaN, inplace=True)  # for delate empty column
            # make filtration

            df_list.append(df)
    wb.Close(SaveChanges=False)
    app.Quit()
    df_concat = pd.concat(df_list)
    return df_concat