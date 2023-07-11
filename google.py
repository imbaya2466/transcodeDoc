from google.cloud import translate_v3beta1 as translate
from google.cloud import language_v1
from tkinter import *
from PyPDF2 import *
import sys
import os
import tkinter
import logging


def translate_document(
        file_path: str,
        file_path_out: str,
        target_language_code: str
) -> translate.TranslationServiceClient:

    mime_type = {".txt" : "text/plain", \
                ".pdf" : "application/pdf", \
                ".doc" : "application/msword", \
                ".docx" : "application/vnd.openxmlformats-officedocument.wordprocessingml.document", \
                ".ppt" : "application/vnd.ms-powerpoint", \
                ".pptx" : "application/vnd.openxmlformats-officedocument.presentationml.presentation", \
                ".xls" : "application/vnd.ms-excel", \
                ".xlsx" : "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" }

    project_id = "test-391113"
    file_name, file_ext = os.path.splitext(file_path)

    if file_ext not in mime_type :
        logger.warning(f'file ext err {file_path}')
        return

    client = translate.TranslationServiceClient()
    location = "us-central1"
    parent = f"projects/{project_id}/locations/{location}"

    # Supported file types: https://cloud.google.com/translate/docs/supported-formats
    with open(file_path, "rb") as document:
        document_content = document.read()

    document_input_config = {
        "content": document_content,
        "mime_type": mime_type[file_ext],
    }

    response = client.translate_document(
        request={
            "parent": parent,
            "target_language_code": target_language_code,
            "document_input_config": document_input_config,
        }
    )

    f = open(file_path_out, 'wb')
    f.write(response.document_translation.byte_stream_outputs[0])
    f.close()

    # If not provided in the TranslationRequest, the translated file will only be returned through a byte-stream
    # and its output mime type will be the same as the input file's mime type
    print(f"transcode:{file_path} ret {response.document_translation.detected_language_code}")

    return response

def split_doc(
        file_path: str,
        list_file
):
    file_name, file_ext = os.path.splitext(file_path)

    if file_ext == ".pdf" :
        with open(file_path,'rb') as in_pdf:
            pdf_file = PdfReader(in_pdf)
            pagenum = len(pdf_file.pages)
            for start in range(0, pagenum, 10):
                output = PdfWriter()
                for i in range(start, start + 10):
                    if i >= pagenum :
                        break
                    output.add_page(pdf_file.pages[i])
                pdf_out = file_name + "_" + str(start) + file_ext
                with open(pdf_out,'ab') as out_pdf:
                    output.write(out_pdf)
                list_file.append(pdf_out)
    else :
        list_file.append(file_path)

    return list_file

path = sys.argv[1]
list_file = []
logging.basicConfig(filename="transcode.log", filemode="w", format="%(asctime)s %(name)s:%(levelname)s:%(message)s", datefmt="%d-%M-%Y %H:%M:%S", level=logging.DEBUG)
target = "en"
win=tkinter.Tk() 

def ENCallBack():
    global target
    target = "en"
    win.destroy()

def CNCallBack():
    global target
    target = "zh-CN"
    win.destroy()

B1 = tkinter.Button(win, text ="转英语", command = ENCallBack)
B1.pack(side = LEFT)
B2 = tkinter.Button(win, text ="转汉语", command = CNCallBack)
B2.pack(side = RIGHT)
screenWidth = win.winfo_screenwidth()   
screenHeight = win.winfo_screenheight() 
w = 150
h = 60
x = (screenWidth - w) / 2
y = (screenHeight - h) / 2
win.geometry("%dx%d+%d+%d" % (w, h, x, y)) 
win.mainloop() 

if os.path.isdir(path):
    for root, dirs, files in os.walk(path):
        for file_name in files:
            file_name = os.path.join(root, file_name)
            size = os.stat(file_name).st_size / 1024 / 1024
            if size >= 10 :
                split_doc(file_name, list_file)
            else :
                list_file.append(file_name) 
elif os.path.isfile(path):
    size = os.stat(path).st_size / 1024 / 1024
    if size >= 10 :
        split_doc(path, list_file)
    else :
        list_file.append(path) 

logging.info(f"target:{target}")
logging.info(f"list_file:{list_file}")

for file_in in list_file:
    file_name, file_ext = os.path.splitext(file_in)
    file_out = file_name + "_" + target + file_ext
    try:
        translate_document(file_in, file_out, target)
    except Exception as e:
        logging.info(f"Exception:{e}")

print("完成\n")
os.system('pause')