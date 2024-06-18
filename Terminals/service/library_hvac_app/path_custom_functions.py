import os,io, zipfile
import win32clipboard  # http://sourceforge.net/projects/pywin32/



def create_folder(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)


def create_zip_from_directory(file_path):     
    data = io.BytesIO()
    with zipfile.ZipFile(data, mode='w') as zipf:
        for file_to_zip in os.listdir(file_path):
            file_to_zip_full_path = os.path.join(file_path, file_to_zip)
            zipf.write(filename=file_to_zip_full_path, arcname=file_to_zip)
    data.seek(0)
    return data
    


def copy(text):
    win32clipboard.OpenClipboard()
    win32clipboard.EmptyClipboard()
    win32clipboard.SetClipboardText(text, win32clipboard.CF_UNICODETEXT)
    win32clipboard.CloseClipboard()
def paste():
    win32clipboard.OpenClipboard()
    data = win32clipboard.GetClipboardData(win32clipboard.CF_UNICODETEXT)
    win32clipboard.CloseClipboard()
    return data