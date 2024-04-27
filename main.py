import csv
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time





def scrape(driver,csv_writer):

    try:
        element_sku = driver.find_element(By.CSS_SELECTOR, '[data-component="product-detail-header"] p').text
        sku = element_sku.replace('Part No.:', '').strip()
    except NoSuchElementException:
        print("Elemento SKU no encontrado en el producto")
        sku = "SKU not found"


    # make it selenium-y
    # Obtener el contenido HTML de la página después de hacer clic en los botones de color y tamaño
    soup = BeautifulSoup(driver.page_source, "html.parser") # !!!!!! no bs4 -> browser

    # Extraer la primera imagen
    image = soup.select_one('[data-component="desktop-gallery"] [data-component="styled-image-wrapper"] img')
    if image:
        image_url = image.get('src')
    else:
        image_url = "Image not found"
    
    # Extraer las especificaciones técnicas
    technical_specifications = soup.select('[data-component="technical-specifications-accordion"]')
    technical_specifications_text = [spec.text for spec in technical_specifications]
    
    # Extraer el precio
    price_element = driver.find_elements(By.CSS_SELECTOR, '[data-component="sidebar"] h5')
    if len(price_element)>0:
        price_element=price_element[-1]
        price_text = price_element.text.strip()
        _, price = price_text.split("MSRP:")
        price = price.strip()
    else:
        price = "Price not found"
    
    # Extraer el nombre del producto
    product_name_element = soup.select_one('[data-component="product-detail-header"] h1')
    product_name = product_name_element.text.strip()
    
    # stock = driver.find_element(By.CSS_SELECTOR, ".toast__message")
    # print(stock.text)
    # stock_text=""

    stock_text="In Stock"
    try:
        stock = driver.find_element(By.CSS_SELECTOR, ".toast__message")
    except Exception as e:
        stock=False
    if stock:
        if "Out of Stock Online" in stock.text: 
            stock_text = "Out Of Stock Online"
        elif "Low Stock" in stock.text:
            stock_text = "Low Stock"


    #Extraer el body
    #body_element = driver.find_element(By.CSS_SELECTOR, "body")
    #html_body = body_element.get_attrib
    # ute('innerHTML')
    #print(html_body) # ! get inner html
    # Encontrar el botón en el sidebar
    sidebar_button = driver.find_elements(By.CSS_SELECTOR, "[data-component='container'] >[data-component='sidebar-wrapper'] > [data-component='sidebar'] > div:not([data-component]) > div:not([data-component]) > button[type='button']")[-2]
    
    sidebar_button.click()
    modal = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".modal__content-wrapper")))
    # Clickear en el botón en el sidebar
    # Extraer el inner HTML
    inner_html = modal.get_attribute("innerHTML")
    # Cerrar el modal
    
    close_button = driver.find_element(By.CSS_SELECTOR, ".modal__content-container button")
    close_button.click()
    time.sleep(1)

    # Extraer los tamaños disponibles
    sizes = soup.select('[data-component="size-selection"] button')
    sizes_text = [size.text for size in sizes]

    # Extraer los colores disponibles
    colours = soup.select('[data-component="color-selection"] button')
    colours_text = [colour.get('aria-label') for colour in colours]

    # Extraer los colores seleccionados
    selected_colors = driver.find_elements(By.CSS_SELECTOR, '[data-component="color-selection"] button[aria-pressed="true"]')
    selected_colors_text = [color.get_attribute('aria-label') for color in selected_colors]

    # print(element_sku)
    # print(element_sku.text)
    # Escribir los datos en el archivo CSV
    csv_writer.writerow([
        "",  # Handle
        product_name,  # Title
        inner_html,  # Body (HTML) # ! find element "body", .get_attribute('innerHTML')
        "",  # Vendor
        product_type,  # Product Category
        product_type,  # Type
        "",  # Tags
        "",  # Published
        "Color",
        selected_colors_text[0],
        "Size",
        size_text,
        has_length,  # Option3 Name
        length_text,  # Option3 Value
        sku,
        "",  # Variant Grams
        "",  # Variant Inventory Tracker
        "",  # Variant Inventory Qty
        "",  # Variant Inventory Policy
        "",  # Variant Fulfillment Service
        price,  # Variant Price
        "",  # Variant Compare At Price
        "",  # Variant Requires Shipping
        "",  # Variant Taxable
        "",  # Variant Barcode              UPC
        image_url,  # Image Src
        "",  # Image Position
        "",  # Image Alt Text
        "",  # Gift Card
        "",  # SEO Title
        "",  # SEO Description # ! add product description
        "",  # Google Shopping / Google Product Category
        "",  # Google Shopping / Gender
        "",  # Google Shopping / Age Group
        "",  # Google Shopping / MPN
        "",  # Google Shopping / Condition
        "",  # Google Shopping / Custom Product
        "",  # Google Shopping / Custom Label 0
        "",  # Google Shopping / Custom Label 1
        "",  # Google Shopping / Custom Label 2
        "",  # Google Shopping / Custom Label 3
        "",  # Google Shopping / Custom Label 4
        image_url,  # Variant Image
        "",  # Variant Weight Unit
        "",  # Variant Tax Code
        "",  # Cost per item
        "",  # Included / South Africa
        "",  # Price / South Africa
        "",  # Compare At Price / South Africa
        "",  # Included / International
        "",  # Price / International
        "",  # Compare At Price / International
        stock_text,  # Status
    ])


# Definir el límite de productos a scrapear por categoría
#product_limit_per_category = 10
    
# Inicializar el navegador
driver = webdriver.Chrome()

# Definir las URLs de las categorías a scrapear
category_urls = [
      ('Bikes', 'https://www.specialized.com/za/en/c/bikes'),
      ('Components', 'https://www.specialized.com/za/en/c/bikeComponents'),
      ('Clothing', 'https://www.specialized.com/za/en/c/clothing'),
      ('Gear', 'https://www.specialized.com/za/en/c/gear')
]

# # Definir una lista para almacenar todas las URLs a scrapear
all_urls = []

for category, url in category_urls:

    driver.get(url)


    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "section button[aria-label]")))
    pagination_items = driver.find_elements(By.CSS_SELECTOR, "section button[aria-label]")

# Itera sobre todos los elementos li excepto el último
    for i in range(1,int(pagination_items[-1].text.strip())+1):
        driver.get(url+"?page=" + str(i))

        # Esperar a que la página cargue completamente
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "product-list-wrapper")))

        # Obtener los elementos <article> dentro de <ul>
        bike_items = driver.find_elements(By.CSS_SELECTOR, "ul li article")

        # Salir del bucle si no hay más elementos <article> en la página
        if not bike_items:
            break

        # Procesar los elementos <article> en la página
        for bike in bike_items:
            # Buscar el enlace dentro del elemento <article>
            link = bike.find_element(By.TAG_NAME, "a")

            # Verificar si se encontró el enlace
            if link:
                # Obtener el valor del atributo href
                href = link.get_attribute("href")
                full_url = href
                all_urls.append((full_url, category))




    # # Recorrer las categorías
    # for category, category_url in category_urls:
    #     products_scraped = 0
    #     page_number = 1
    #     while True:
    #         url = f"{category_url}?page={page_number}"
    #         driver.get(url)

    #         # Esperar a que la página cargue completamente
    #         WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "product-list-wrapper")))

    #         # Obtener los elementos <article> dentro de <ul>
    #         bike_items = driver.find_elements(By.CSS_SELECTOR, "ul li article")

    #         # Salir del bucle si no hay más elementos <article> en la página
    #         if not bike_items:
    #             break

    #         # Procesar los elementos <article> en la página
    #         for bike in bike_items:
    #             # Buscar el enlace dentro del elemento <article>
    #             link = bike.find_element(By.TAG_NAME, "a")

    #             # Verificar si se encontró el enlace
    #             if link:
    #                 # Obtener el valor del atributo href
    #                 href = link.get_attribute("href")
    #                 full_url = f"https://www.specialized.com{href}"
    #                 all_urls.append((full_url, category))
    #                 products_scraped += 1

    #         # Incrementar el número de página
    #         page_number += 1


#print(all_urls)
                
                
#all_urls=[("https://www.specialized.com/za/en/tarmac-sl8-expert/p/216955?color=357280-216955","Bikes")]


# Definir el nombre del archivo CSV
csv_filename = 'SpecializedDemo.csv'

# Abrir el archivo CSV en modo escritura
with open(csv_filename, mode='w', newline='') as csv_file:
    # Crear el escritor CSV
    csv_writer = csv.writer(csv_file)
    # Escribir encabezados en el archivo CSV
    csv_writer.writerow([
        'Handle', 'Title', 'Body (HTML)', 'Vendor', 'Product Category', 'Type', 'Tags', 'Published',
        'Option1 Name', 'Option1 Value', 'Option2 Name', 'Option2 Value', 'Option3 Name', 'Option3 Value',
        'Variant SKU', 'Variant Grams', 'Variant Inventory Tracker', 'Variant Inventory Qty',
        'Variant Inventory Policy', 'Variant Fulfillment Service', 'Variant Price', 'Variant Compare At Price',
        'Variant Requires Shipping', 'Variant Taxable', 'Variant Barcode', 'Image Src', 'Image Position',
        'Image Alt Text', 'Gift Card', 'SEO Title', 'SEO Description', 'Google Shopping / Google Product Category',
        'Google Shopping / Gender', 'Google Shopping / Age Group', 'Google Shopping / MPN', 'Google Shopping / Condition',
        'Google Shopping / Custom Product', 'Google Shopping / Custom Label 0', 'Google Shopping / Custom Label 1',
        'Google Shopping / Custom Label 2', 'Google Shopping / Custom Label 3', 'Google Shopping / Custom Label 4',
        'Variant Image', 'Variant Weight Unit', 'Variant Tax Code', 'Cost per item', 'Included / South Africa',
        'Price / South Africa', 'Compare At Price / South Africa', 'Included / International', 'Price / International',
        'Compare At Price / International', 'Status'
    ])

    # Visitar cada URL almacenada en la lista
    for url, product_type in all_urls:
        print(url)
        time.sleep(2)
        driver.get(url)
        # Esperar a que la página cargue completamente
        try:
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '[data-component="color-selection"]')))
        except Exception as e:
            print(e)
            print(url)
            continue
        print(url)
        # try:
        #     element_sku = driver.find_element_by_css_selector('.product-detail-header p')
        # except NoSuchElementException:
        #     print("Elemento no encontrado en el producto")
        #     continue

        # Obtener el contenido HTML de la página después de hacer clic en los botones de color y tamaño
        soup = BeautifulSoup(driver.page_source, "html.parser")

        # Encontrar todos los botones de color y hacer clic en cada uno
        color_buttons = driver.find_elements(By.CSS_SELECTOR, '[data-component="color-selection"] button')
        for color_button in color_buttons:
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '[data-component="color-selection"] button')))

            driver.execute_script("arguments[0].click();", color_button)
            
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '[data-component="size-selection"]')))
            
            # Encontrar todos los botones de tamaño y hacer clic en cada uno
            buttoncitos = driver.find_elements(By.CSS_SELECTOR, '[data-component="size-selection"]')

            WebDriverWait(buttoncitos[0], 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'button')))
            size_buttons=buttoncitos[0].find_elements(By.CSS_SELECTOR, 'button')
            
            
            for size_button in size_buttons:
                has_length = ""  # Inicializar has_length como False para cada botón de tamaño
                length_text = ""    # Inicializar length_text como una cadena vacía

                size_text = size_button.text  # Extraer el texto del botón de tamaño
                driver.execute_script("arguments[0].click();", size_button)

                if len(buttoncitos) > 1:
                    WebDriverWait(buttoncitos[1], 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'button')))
                    length_buttons = buttoncitos[1].find_elements(By.CSS_SELECTOR, 'button')
                    has_length = "Length"  # Actualizar has_length a True si se encontró un botón de longitud

                    for length_button in length_buttons:
                        length_text = length_button.text  # Extraer el texto del botón de longitud
                        driver.execute_script("arguments[0].click();", length_button)
                        scrape(driver, csv_writer)
                        
                else:
                    scrape(driver, csv_writer)



                # WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '[data-component="size-selection"] button')))

                #size_button.click()
                
                

# Cerrar el navegador
driver.quit()
