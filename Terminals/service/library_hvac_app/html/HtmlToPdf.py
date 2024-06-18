from PyQt5 import QtCore, QtWidgets
from PyQt5 import QtWebEngineWidgets
from PyQt5.QtGui import QPageLayout, QPageSize

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QPageLayout, QPageSize
from PyQt5.QtPrintSupport import QPrinter
from PyQt5.QtWebEngineWidgets import QWebEngineView


def html_to_pdf(html, pdf):

    app = QtWidgets.QApplication(sys.argv)
    page = QtWebEngineWidgets.QWebEnginePage()

    def define_layout():
        layout = QPageLayout()
        layout.setPageSize(QPageSize(getattr(QPageSize, "A3")))
        layout.setOrientation(getattr(QPageLayout.Orientation, "Landscape"))
        layout.setLeftMargin(20)
        layout.setRightMargin(5)
        layout.setTopMargin(5)
        layout.setBottomMargin(5)
        return layout

    def handle_print_finished(filename, status):
        print("finished", filename, status)
        QtWidgets.QApplication.quit()

    def handle_load_finished(status):
        if status:
            page.printToPdf(pdf,define_layout())
        else:
            print("Failed")
            QtWidgets.QApplication.quit()

    page.pdfPrintingFinished.connect(handle_print_finished)
    page.loadFinished.connect(handle_load_finished)
    page.load(QtCore.QUrl.fromLocalFile(html))
    app.exec_()
def generate_pdf(
        html_file,
        media_dir,
        page_size="A3",
        # page_orientation="Portrait"
        page_orientation="Landscape"
        ):

    #we use an array to pass the result asynchronously
    ob = []

    with open(html_file, 'r',encoding = 'utf-8') as fp:
    # считываем сразу весь файл
        data = fp.read()
    app = QApplication.instance()
    if app is None:
        app = QApplication(['--platform','minimal'])
    web = QWebEngineView()
    url = QUrl.fromLocalFile(media_dir)
    web.setHtml(data,baseUrl=url)
    layout = QPageLayout()
    # you can change the page size / layout here
    layout.setPageSize(QPageSize(getattr(QPageSize, page_size)))
    layout.setOrientation(getattr(QPageLayout.Orientation, page_orientation))

    layout.setLeftMargin(20)
    layout.setRightMargin(5)
    layout.setTopMargin(5)
    layout.setBottomMargin(5)

    def callback(b, ob=ob):
        ob.append(b)
        app.quit()

    def printPage():
        web.page().printToPdf(callback, layout)

    web.loadFinished.connect(printPage)
    app.exec_()
    return ob[0]