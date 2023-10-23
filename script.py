from selenium import webdriver
import time
from PIL import Image
import io
from ftplib import FTP
import json
from selenium.webdriver.chrome.options import Options

chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-gpu') 

with open("cfg.json", "r") as cfg_json:
    cfg = json.loads(cfg_json.read())

file = "index.html"
host = cfg['host']
usuario = cfg['usuario']
senha = cfg['senha']
arquivo_remoto = cfg['arquivo_remoto']

print('Logando no servidor via FTP')
print(usuario, senha)
ftp = FTP(host)
ftp.login(usuario, senha)
print('Logado')

limit_inferior = cfg['limit_inferior']
limit_superior = cfg['limit_superior']

driver = webdriver.Chrome(options=chrome_options)

def calcular_porcentagem_de_azul(imagem):
    pixels = imagem.getdata()
    total_pixels = len(pixels)
    total_pixels_azuis = sum(1 for pixel in pixels if pixel[2] > pixel[0] and pixel[2] > pixel[1])

    porcentagem_azul = (total_pixels_azuis / total_pixels) * 100
    return porcentagem_azul

for i in range(limit_inferior, limit_superior):
    try:
        url = "https://ted.transferegov.sistema.gov.br/ted/programa/detalhe/"+str(i)+"/beneficiarios"
        driver.get(url)

        time.sleep(1)

        main_element = driver.find_element("css selector", "main.page-content")
        current_style = main_element.get_attribute("style")
        new_style = f"{current_style} margin-bottom: 1000px;"
        driver.execute_script(f"arguments[0].setAttribute('style', '{new_style}')", main_element)

        checkbox_element = driver.find_element("id", "checkChamamentoPublico")
        label_element = driver.find_element("css selector", "label[for='checkChamamentoPublico']")
        driver.execute_script("arguments[0].scrollIntoView();", label_element)

        time.sleep(1)

        screenshot = driver.get_screenshot_as_png()
        full_image = Image.open(io.BytesIO(screenshot))
        x1, y1, x2, y2 = 0, 0, 500, 70
        cropped_image = full_image.crop((x1, y1, x2, y2))
        time.sleep(1)

        porcentagem_azul = calcular_porcentagem_de_azul(cropped_image)
        print(f"A porcentagem de azul na imagem {i} é: {porcentagem_azul:.2f}%")
        content = ""
        with open(file, "r") as arquivo_html:
            content = arquivo_html.read()
        linhas = content.split('\n')
        if porcentagem_azul >= 1.5 and porcentagem_azul <= 1.8:
            cropped_image.save("images/" + str(i) + ".png")
            if not url in content:
                with open(file, "a") as arquivo_html:
                    paragrafo = f"<p><a class='list-group-item list-group-item-action list-group-item-primary' href='{url}'>Chamada {i}</a></p>\n"
                    arquivo_html.write(paragrafo)
                with open(file, "rb") as arquivo_html:
                    ftp.storbinary(f"STOR {arquivo_remoto}", arquivo_html)
        elif url in content:
            with open(file, "w") as arquivo_modificado:
                for linha in linhas:
                    if url not in linha:
                        arquivo_modificado.write(linha + '\n')
            with open(file, "rb") as arquivo_html:
                ftp.storbinary(f"STOR {arquivo_remoto}", arquivo_html)

    except Exception as e:
        print("Erro com o " + str(i) + ": " + str(e))

ftp.quit()
driver.quit()
