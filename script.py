from selenium import webdriver
import time
from PIL import Image
import io

limit_inferior = 1000
limit_superior = 2000

driver = webdriver.Chrome()

def calcular_porcentagem_de_azul(imagem):
    pixels = imagem.getdata()
    total_pixels = len(pixels)
    total_pixels_azuis = sum(1 for pixel in pixels if pixel[2] > pixel[0] and pixel[2] > pixel[1])

    porcentagem_azul = (total_pixels_azuis / total_pixels) * 100
    return porcentagem_azul

with open("links.txt", "a") as arquivo:

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
            x1, y1, x2, y2 = 100, 0, 500, 70
            cropped_image = full_image.crop((x1, y1, x2, y2))
            time.sleep(1)

            porcentagem_azul = calcular_porcentagem_de_azul(cropped_image)
            print(f"A porcentagem de azul na imagem {i} é: {porcentagem_azul:.2f}%")
            if porcentagem_azul >= 3.4 and porcentagem_azul <=4:
                cropped_image.save("images/" + str(i) + ".png")
                arquivo.write(url + "\n")
        except Exception as e:
            print("Erro com o " + str(i) + ": " + str(e))

driver.quit()
