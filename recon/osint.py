import httpx
import json
import os
from PIL import Image
import pytesseract
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
    fileName = ''

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

    fileName = 'file.png'

    try:
        check_pdf(url, fileName)

    except:
        print("there was an exception trying to proccess criminal record certificate")	


def check_pdf(url, fileName):
    # options = webdriver.FirefoxOptions()
    # options.add_argument('--headless')

    # until we've got a good screenshot
    while True:
        driver = webdriver.Firefox()
        driver.get(url)
        sleep(3)

        driver.get_screenshot_as_file(fileName)
        driver.quit()

        image = Image.open(fileName)
        text = pytesseract.image_to_string(image)
        # print(text)

        if '\n' in text:
            break

        os.remove(fileName)


    ltest = text.split("\n") 

    antecedentes = False
    anotaciones = False

    for i,a in enumerate(ltest):
        if 'SIN ANTECEDEN' in a:
            antecedentes = True
        elif 'SIN ANOTACIONES':
            anotaciones = True


    if antecedentes and anotaciones:
        print('[+] PASSED !')
        return True
    else:
        print('[!] Failed')
        return False




if __name__=="__main__":
    files = ['ANT_XXXX.pdf', 'ANT_YYYY.pdf']

    # proxies = { "http://": "http://localhost:8080", "https://": "http://localhost:8080"}
    for f in files:
        (result, codigoVerificacion, folio) = check_local_cert(f)
   
        with httpx.Client(verify=False) as client:
            validate_cert(codigoVerificacion,folio, client)

