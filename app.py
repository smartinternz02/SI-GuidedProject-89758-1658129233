from __future__ import division, print_function
from flask import Flask, request, render_template
#from werkzeug import secure_filename
from werkzeug.utils import secure_filename
from gevent.pywsgi import WSGIServer
import numpy as np
import cv2
from PIL import Image
import pytesseract
import sys
import img2pdf
from pdf2image import convert_from_path
import os 
pytesseract.pytesseract.tesseract_cmd = r'E:\Tesseract-OCR\tesseract.exe'
import os.path
import glob
import random
app = Flask(__name__, static_url_path='')
@app.route('/') 
def home():
    return render_template('index.html')
@app.route('/upload', methods=['POST']) 
def upload():
    if request.method == 'POST': 
             f = request.files['filename']
             basepath = os.path.dirname(__file__)
             file_path = os.path.join(basepath, 'uploads', secure_filename(f.filename))
             f.save(file_path)
             if ('.jpg' in f.filename) or ('.png' in f.filename):
                 # opening image
                 image = Image.open(file_path)
                 # storing pdf path
                 file_path = os.path.join(basepath, 'uploads', secure_filename(f.filename)[:-3]+"pdf")
                 # converting into chunks using img2pdf
                 pdf_bytes = img2pdf.convert(image.filename)
                 # opening or creating pdf file
                 file = open(file_path, "wb")
                 # writing pdf files with chunks
                 file.write(pdf_bytes)
                 # closing image file
                 image.close()
                 # closing pdf file
                 file.close()
             PDF_file = file_path
             pages = convert_from_path(PDF_file)
             image_counter = 1
             for page in pages:
                 filename = r"images/page_"+str(image_counter)+".jpg"
                 page.save(filename, 'JPEG')
                 image_counter = image_counter + 1
             filelimit = image_counter-1
             # Creating a text file to write the output
             basepath = os.path.dirname(__file__)
             file_path2 = os.path.join( basepath, 'outputs', "output"+str(random.randint(1, 100000))+".txt")
             f = open(file_path2, "a") 
             for i in range(1, filelimit + 1):
                 filename = r"images/page_"+str(i)+".jpg"
                 text = str(pytesseract.image_to_string(Image.open(filename)))
                 text = text.replace('-\n', '')
                 f.write(text)
             f.close()
    return 'Output Text File is saved at '+file_path2
port=os.getenv('VCAP_APP_PORT','5000')
if __name__=='__main__':
    app.secret_key=os.urandom(12)
    app.run(debug=True,host='0.0.0.0',port=port)
