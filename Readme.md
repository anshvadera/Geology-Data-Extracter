### About Project

1) This Software standardise the company data from various companies about 
   lithology and the code used by various organizations.

2) the end goal is to have a one master code for all lithogies in all companies to avoid confusion and efficient working

3) This is achieved through various python libraries and creating Data pipeline.
   eg - OCR,NLP,IMAGE PROCESSING

4) Database used - PostgreSql 

5) example pdfs folder - input pdf and output image are attached in this

6) requirements.txt  - contains all dependencies for the project

7) front end  - Streamlit is used

### DATABASE

Database used - PostgreSql

Tables 
1) clbody   (columns - companyid, companyname)
2) dhlitho  (columns - attribute column, attribute value, anumber, filename, companyid, companyname, mastercode)
3) mrtfile  (columns - anumber, companyid, filename)

clbody, mrtfile tables are used and interacted between each other to get details and to update dhlitho table.

### Running the project

1) Creating the environment with dependencies
2) Runing the command - streamlit run app.py



