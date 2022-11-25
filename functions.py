'''
Importing required libraries

'''

import re
import pandas as pd
import PyPDF2
import cv2 
from pdf2image import convert_from_path
import numpy as np
import os

# =============================================================================
# import pytesseract
# pytesseract.pytesseract.tesseract_cmd = r'C:/Program Files/Tesseract-OCR\tesseract.exe'
# 
# =============================================================================
import re
from nltk.corpus import stopwords



def pdf_to_image(path,Dpi=300,page=0):
        
    images = convert_from_path(path,dpi=Dpi)
    a=images[page] 
    open_cv_image = np.array(a) 
    open_cv_image = open_cv_image[:, :, ::-1].copy()
    img=open_cv_image
    return img



#==============================================================================
'''REMOVING VERTICAL AND HORIZONTAL LINES FROM THE IMAGES'''
#==============================================================================

def remove_lines(img,ksize=1,iterations=2,c_thickness=5):
        
    result = img.copy()
    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    
    kernel_len = np.array(img).shape[1]//100
    
    # Remove horizontal lines
    horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (kernel_len,ksize))
    remove_horizontal = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, horizontal_kernel, iterations=iterations)
    cnts = cv2.findContours(remove_horizontal, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]
    for c in cnts:
        cv2.drawContours(result, [c], -1, (255,255,255), c_thickness)    
     
    # Remove vertical lines
    vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (ksize,kernel_len))
    remove_vertical = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, vertical_kernel, iterations=iterations)
    cnts = cv2.findContours(remove_vertical, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]
    for c in cnts:
        cv2.drawContours(result, [c], -1, (255,255,255), 7)    
    
    return result



#==============================================================================
'''IMAGE PREPROCESSING 
   PARAMETERS TAKEN - IMAGE, BW(IF TRUE THE IMAGE WILL GET BLACK AND WHITE ELSE
                           IT WILL BE IN GRAY SCALE)
   converting gray scale and binarization of image'''
#==============================================================================

def pre_processing(image,bw=True):
    img=cv2.resize(image,(0,0),fx=1.5,fy=1.5)
    gray_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    if bw==True:
        thresh, im_bw = cv2.threshold(gray_image,160, 230, cv2.THRESH_BINARY)
        return im_bw
    if bw==False:
        return gray_image

#==============================================================================

'''cleaning of text extracted from the image 
    1) Removing all text other than alphabets
    2) spliting in lines
    3) removing stop words in the sentence
'''
# =============================================================================



def clean(ocr_result):
        
    words_pattern = re.compile(r'[^a-zA-Z\s]+')
    matches56=words_pattern.findall(ocr_result)
    string=re.sub(words_pattern," ",ocr_result)
    x =string.splitlines(True)
        
    stop_words=pd.read_csv('C:\\Users\\Datacode\\Desktop\\vh\\stop_words.csv')
    stop_words=[a.lower() for a in stop_words['stop_words']]
        
    text=[]
    for i in x:
        j=i.split()
        g=" ".join([word for word in j if word.lower() not in stop_words])
        text.append(g)
    text=str(text)     
    return text  
    
#==============================================================================
'''
Matching pattern with REGEX so that it can extract the results we wanted
pat = 1 => when pdf consist of code followed by lithology description
pat = 2 => when pdf consist of description first and then code.
takes two arguments, text and pat = 1 or 2

'''
#==============================================================================
        
def pattern(text,pat=1):
    if pat==1:
        pattern4=re.compile(r'\b\s?\w{1,3}\s\w{4,65}\s\w{4,65}\s\w{4,45}\s\w{4,45}')
        matches4=pattern4.findall(text)
        mod_string=re.sub(pattern4,"",text) 
        
        pattern3 = re.compile(r'\b\s?\w{1,3}\s\w{4,65}\s\w{4,65}\s\w{4,45}')
        matches3=pattern3.findall(mod_string)
        mod_string=re.sub(pattern3,"",mod_string)  
        
        pattern2=re.compile(r'\b\s?\w{1,3}\s\w{4,65}\s\w{4,65}')
        matches2=pattern2.findall(mod_string)
        mod_string=re.sub(pattern2,"",mod_string)  
        
        pattern1=re.compile(r'\b\s?\w{1,3}\s\w{4,65}')
        matches1=pattern1.findall(mod_string)
        mod_string=re.sub(pattern1,"",mod_string)  
        
        matches_com=matches1+matches2+matches3+matches4
        
        return matches_com
    
    if pat==2:
                
        pattern4=re.compile(r'\b\s?\w{3,65}\s\w{4,65}\s\w{4,65}\s\w{4,45}\s\w{1,3}\s')
        matches4=pattern4.findall(text)
        mod_string=re.sub(pattern4,"",text) 
        
        pattern3 = re.compile(r'\b\s?\w{4,65}\s\w{4,65}\s\w{4,65}\s\w{1,3}\s')
        matches3=pattern3.findall(mod_string)
        mod_string=re.sub(pattern3,"",mod_string)  
        
        pattern2=re.compile(r'\b\s?\w{4,65}\s\w{4,65}\s\w{1,3}')
        matches2=pattern2.findall(mod_string)
        mod_string=re.sub(pattern2,"",mod_string)  
        
        pattern1=re.compile(r'\b\s?\w{4,65}\s\w{1,3}')
        matches1=pattern1.findall(mod_string)
        mod_string=re.sub(pattern1,"",mod_string) 
        
        matches_com=matches1+matches2+matches3+matches4
        
        return matches_com

# =============================================================================    
'''
converting our statement/pattern extracted into required  data format
and saving it into csv file in our path specified
takes 2 arguments , pattern extracted and path for saving our data in csv format

'''    
# ==============================================================================
                
def data(patt,path):
        
    b=[]
    for i in patt:   
        a=patt[patt.index(i)].split()
        b.append(a)                
    code=[]
    lithology=[]    
    for i in range(len(b)):
        code.append(b[i][0])
        lithology.append(b[i][1:]) 
    litho=[" ".join(i) for i in lithology]
    finall=pd.DataFrame()
    finall['code']=code
    finall['lithology']=litho
    finall.to_csv(path,index=False)    
    
'''
 Getting the file name from the path specified

'''    
def filename(path):
    d=os.path.basename(path)
    return d

path='C:\\Users\\Datacode\\Desktop\\Ansh\\ocr\\GSWA_codes\\GSWA Company Geol Codes'  
e=os.path.basename(path)
f=filename(path)    
