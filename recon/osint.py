import httpx
import json
import img2pdf
from PIL import Image
from selenium import webdriver
from time import sleep
from PyPDF2 import PdfReader 


baseUrl = 'https://www.registrocivil.cl/OficinaInternet/verificacion/OficinaInternet/'

def check_local_cert(fileName):
    # creating a pdf reader object 
    reader = PdfReader(fileName) 
  
    # getting a specific page from the pdf file 
    page = reader.pages[0] 
  
    # extracting text from page 
    text = page.extract_text() 
    ltest = text.split("\n") 

    codigoVerificacion = ltest[5]
    folio = ltest[6]
    antecedentes = ltest[14]
    intraFamiliar = ltest[18]
    result = False

    if 'SIN ANTECEDENTES' in antecedentes and 'SIN ANOTACIONES' in intraFamiliar:
	    print('[+] PASSED !')
	    result = True
    else:
	    print('[!] Failed')
	    
    return (result, codigoVerificacion, folio)
    

def validate_cert(codigoVerificacion, folio, client):
        url= baseUrl + '/verificacion/verificarCertificado.srcei'

        try:
            data = { 'ver_nameInputTextFolio': folio, 'ver_nameInputTextCodVerificador': codigoVerificacion }
            headers = { 'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8', 'Host': 'www.registrocivil.cl', 'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko)' }
            result = client.post(url, data=data, headers=headers)
            json_object = json.loads(result.text)
            fileName = json_object['fileName']
            print(fileName)

        except:
            print("there was an exception trying to validate criminal record certificate")	

        #downloading file
        url= baseUrl + 'verCopiaPdf.srcei?fileName=' + fileName
        print(url)

        try:
            save_page(url)

        except:
            print("there was an exception trying to download criminal record certificate")	

        try:
            png_to_pdf()

        except:
            print("there was an exception trying to convert certificate from png to pdf")	
      

def save_page(url):
    driver = webdriver.Firefox()
    driver.get(url)
    sleep(1)

    driver.get_screenshot_as_file("file.png")
    driver.quit()


def png_to_pdf():
    # opening image
    image = Image.open('file.png')
 
    # converting into chunks using img2pdf
    pdf_bytes = img2pdf.convert(image.filename)
 
    # opening or creating pdf file
    file = open('file.pdf', "wb")
 
    # writing pdf files with chunks
    file.write(pdf_bytes)
 
    # closing image file
    image.close()
 
    # closing pdf file
    file.close()
 
    # output
    print("Successfully made pdf file")


if __name__=="__main__":
    files = ['ANT_FE_xxxxx_yyyyyyyy.pdf', 'ANT_FE_zzzzz_wwwwwwww.pdf']

    (result, codigoVerificacion, folio) = check_local_cert(files[0])
    print(result)
    print(codigoVerificacion)
    print(folio)

    check_local_cert('file.pdf')    
   
    # proxies = { "http://": "http://localhost:8080", "https://": "http://localhost:8080"}

    # with httpx.Client(verify=False) as client:
    #    validate_cert(codigoVerificacion,folio, client)

    #for f in files:
    #   check_local_cert(f)
