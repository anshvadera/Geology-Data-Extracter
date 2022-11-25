#=============================================================================
'''
importing all the req lib
'''
#==============================================================================

import streamlit as st
import pandas as pd
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:/Program Files/Tesseract-OCR/tesseract.exe'
import os
import PyPDF2
import sys
sys.path.insert(0, 'C:/Users/Datacode/Desktop/Ansh/ocr')
import logic as a
import cv2
import csv
import psycopg2
from os import path
from glob import glob  

#==============================================================================
'''Removing traceback for custom errors '''
#==============================================================================

sys.tracebacklimit = 0

#==============================================================================
''' Title and HTML for front end'''
#==============================================================================

st.title("")
html_temp = """
<div style="background-color:tomato;padding:8px">
<h2 style="color:white;text-align:center;">Data Extractor </h2>
</div>
"""
st.markdown(html_temp,unsafe_allow_html=True)
path = st.text_input("PATH","Type Here")



from os import listdir
from os.path import isfile, join

try:  
    allfiles = [f for f in listdir(path) if isfile(join(path, f))]
except Exception :
    pass
    


path2 = 'C:\\Users\\Datacode\\Desktop\\finall.csv'
hostname = "localhost" #Database parameters
database = "Lithology"
username = "postgres"
pwd = "Data1234"
port_id = 5432



# combining all the functions together to build a pipeline
def one(path,path2,hostname,database,username,pwd,port_id):
    
    global allfiles
    for i in allfiles:
        
        
        
        file_name = i.split('.')[0]
        file_path = path +'\\'+ i
        
        file = open(file_path, 'rb')        
            
        readpdf = PyPDF2.PdfFileReader(file)
        totalpages = readpdf.numPages
        for k in range(0,totalpages):
            img=a.pdf_to_image(file_path,page=k)
            img=a.remove_lines(img)
            img=a.pre_processing(img)
            ocr_result=pytesseract.image_to_string(img,lang='eng',config='--psm 6')
            text=a.clean(ocr_result)
            patt=a.pattern(text,pat=1) 
            try:
                try:
                    conn = psycopg2.connect(
                               host=hostname,
                               dbname = database,
                               user = username,
                               password = pwd,
                               port = port_id
                               )
                
                
                    cur = conn.cursor()
                except Exception as err:
                    raise Exception(f'Problem in connecting to database --> {err} ')
                
                try:
                    cur.execute(f"SELECT anumber FROM public.mrtfile WHERE filename = " + "'" +file_name + "'")
                    anum = cur.fetchall()
                    anum = anum[0][0]
                except IndexError as err:
                    raise Exception(f'The filename {file_name} does not exist in the database --> {err} ')    
                    
                try:
                    cur.execute(f"SELECT companyid FROM public.mrtfile WHERE filename = " + "'" +file_name + "'")
                    compid = cur.fetchall()
                    compid = compid[0][0]
                except IndexError as err:
                    raise Exception(f'The companyid does not exist in the database --> {err} ')      
                    
                try:
                    cur.execute(f"SELECT companyname FROM public.clbody WHERE companyid = {compid} ")
                    compname = cur.fetchall()
                    compname = compname[0][0]
                except IndexError as err:
                    raise Exception(f'The companyname does not exist in the database --> {err} ')    
                    
            finally:
                cur.close()
                conn.close()
                file.close()
            b=[]
            for i in patt:   
                z=patt[patt.index(i)].split()
                b.append(z)                
            code=[]
            lithology=[]    
            for i in range(len(b)):
                code.append(b[i][0])
                lithology.append(b[i][1:]) 
            litho=[" ".join(i) for i in lithology]
            finall=pd.DataFrame()
            finall['attribute column']=code
            finall['attribute value']=litho
            finall['anumber']= anum
            finall['filename']=file_name
            finall['companyid']= compid
            finall['companyname']=compname
            finall.to_csv(path2,index=False) 
            try:
                from sqlalchemy import create_engine
                engine = create_engine(f'postgresql://postgres:{pwd}@{hostname}:{port_id}/{database}')
                finall.to_sql('dhlitho', engine , if_exists='append')
            except Exception as err:
                raise Exception(f'Problem in trasfering data to database --> {err} ')  

# Creating an Exract button
result =''
if st.button("Extract"):
    one(path,path2,hostname,database,username,pwd,port_id)
    result = 'The data is successfully added to database'
st.success('{}'.format(result))            







