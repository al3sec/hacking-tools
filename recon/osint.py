import httpx
import json
import os
from PIL import Image
import pytesseract
from selenium import webdriver
from time import sleep
from PyPDF2 import PdfReader 
from bs4 import BeautifulSoup


baseUrl = 'https://www.registrocivil.cl/OficinaInternet/verificacion/OficinaInternet/'


def validate_cert_argentina(fileName, client):
    reader = PdfReader(fileName) 
    page = reader.pages[0] 
  
    text = page.extract_text() 
    ltest = text.split("\n")
  
    solicitud = ltest[4].split('/')[0].split(' ')[1]
    seguridad = ltest[4].split('/')[1].split(' ')[3]

    url= 'https://www.dnrec.jus.gov.ar/ConsultaCAP/Consulta.aspx'
    certVencido = 'Lo siento, su certificado no pudo ser obtenido. Se ha vencido el plazo de disponibilidad del certificado digital'
  
    try:
        cookies = { "IDNODO" : ".cluster3" }
        headers = {"Connection": "close", "Cache-Control": "max-age=0", "Content-Type": "application/x-www-form-urlencoded", "User-Agent": "Mozilla AppleWebKit 537 like Gecko", "Origin": "https://www.dnrec.jus.gov.ar", "Referer": "https://www.dnrec.jus.gov.ar/ConsultaCAP/Consulta.aspx", "Upgrade-Insecure-Requests": "1", "Accept-Encoding": "gzip, deflate", "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7", "Sec-Ch-Ua": "\"Chromium\";v=\"119\", \"Not?A_Brand\";v=\"24\"", "Sec-Ch-Ua-Mobile": "?0", "Accept-Language": "es-419,es;q=0.9", "Sec-Ch-Ua-Platform": "\"Linux\"", "Sec-Fetch-Site": "same-origin", "Sec-Fetch-Mode": "navigate", "Sec-Fetch-User": "?1", "Sec-Fetch-Dest": "document"}
        data = {"__VIEWSTATE": "/wEPDwUKMTM1MjcxMzIzOQ9kFgJmD2QWAgIDD2QWAgIDD2QWCAIDDw8WBB4IQ3NzQ2xhc3MFFWZvcm0tY29udHJvbCBpbnB1dC1zbR4EXyFTQgICZGQCCQ8PFgQfAAUVZm9ybS1jb250cm9sIGlucHV0LXNtHwECAmRkAhMPDxYCHgdWaXNpYmxlaGRkAhUPDxYCHwJoZGRkGY40qooxOZ5M9blu68eGM2FhiYPtIMQmSQlq+GVESxM=", "__VIEWSTATEGENERATOR": "BC87ADF4", "__EVENTVALIDATION": "/wEdAAZ2kQXgcpEwPru/e20cMbOIhyH/8YcFBx917VGPY+CjCkEQsmjsCJ/J3FRjao4vXz+SoL0UZe+FdDX7hn4h0kbk56tz6k/JHXSB9mn1j0sUWTbghrrMsAV1YGWe8tNVvj95aIK1J97hupv7F8ObO22wpEUpMmu1QqfVFGA1jmc1Gw==", "ctl00$ContentPlaceHolder1$txtCodSolicitud": solicitud, "ctl00$ContentPlaceHolder1$txtCodSegur": seguridad, "ctl00$ContentPlaceHolder1$btConsultar": "CONSULTAR", "ctl00$ContentPlaceHolder1$hidden_solic": '', "ctl00$ContentPlaceHolder1$hidden_segur": ''}
        result = client.post(url, data=data, headers=headers, cookies=cookies)
        soup = BeautifulSoup(result.content, 'html.parser')
        message = soup.find_all('p')[0].text

    except:
        print("there was an exception trying to validate criminal record certificate")      

    if message ==  certVencido:
        print('Certificado Vencido')
    else:
        # we need an updated certificate in order to test this case.
        print('It must check the site pdf')


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
    options = webdriver.FirefoxOptions()
    options.add_argument('--headless')

    # until we've got a good screenshot
    while True:
        driver = webdriver.Firefox(options=options)
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
    files = ['file1.pdf', 'file2.pdf']
    proxies = { "http://": "http://localhost:8080", "https://": "http://localhost:8080"}
    # for f in files:
    #    (result, codigoVerificacion, folio) = check_local_cert(f)
    #
    with httpx.Client(verify=False, proxies=proxies) as client:
    #        validate_cert(codigoVerificacion,folio, client)
        validate_cert_argentina('cert.pdf', client)
    