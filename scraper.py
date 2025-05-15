import requests
from bs4 import BeautifulSoup
import os
import re
from pydantic import BaseModel
from typing import List
from urllib.parse import urljoin, urlparse
import json


class NewsData(BaseModel):
    titulo: str
    contenido: str
    fecha: str
    imagenes: List[str]

# Nueva estructura para documentos descargables
class DocumentoDescargable(BaseModel):
    titulo: str
    descripcion: str
    url_descarga: str


def extraer_datos(url) -> NewsData | None:
    """
    Dada una URL, obtiene el HTML y extrae ciertos datos de la noticia.
    Devuelve un objeto NewsData o None si falla.
    El método de extracción depende del dominio de la URL.
    """
    respuesta = requests.get(url)
    if respuesta.status_code != 200:
        print(f"Error al acceder a la URL: {respuesta.status_code}")
        return None

    soup = BeautifulSoup(respuesta.text, 'html.parser')
    dominio = urlparse(url).netloc

    if dominio == "www.ftf.es":
        article = soup.body.find('article') if soup.body else None
        if not article:
            print("No se encontró la etiqueta <article>")
            return None
        # Título: primer h2 dentro de <article>
        h2 = article.find('h2')
        titulo = h2.get_text(strip=True) if h2 else ''
        # Contenido: concatenar todos los <p> dentro de <article>
        parrafos = article.find_all('p')
        contenido = '\n'.join([p.get_text(strip=True) for p in parrafos])
        # Fecha: buscar <i> con clase 'ti-calendar' y extraer el texto completo de su padre <a> o <li>
        fecha = ''
        fecha_icon = article.find('i', class_='ti-calendar')
        if fecha_icon:
            parent_a = fecha_icon.find_parent('a')
            parent_li = fecha_icon.find_parent('li')
            if parent_a and parent_a.get_text(strip=True):
                fecha = parent_a.get_text(strip=True).replace(fecha_icon.get_text(strip=True), '').strip()
            elif parent_li and parent_li.get_text(strip=True):
                fecha = parent_li.get_text(strip=True).replace(fecha_icon.get_text(strip=True), '').strip()
            else:
                if fecha_icon.next_sibling:
                    fecha = fecha_icon.next_sibling.strip()
        # Imágenes: todas las <img> dentro de <article>, con src absoluto
        imagenes = []
        for img in article.find_all('img'):
            src = img.get('src')
            if src:
                src_absoluto = urljoin(url, src)
                imagenes.append(src_absoluto)
    elif dominio == "www.fiflp.com":
        # Título: <header class="blog-post">, dentro el <h1>
        header = soup.find('header', class_='blog-post')
        titulo = ''
        fecha = ''
        if header:
            h1 = header.find('h1')
            titulo = h1.get_text(strip=True) if h1 else ''
            # Fecha: <small class="fsize13">, segundo <span> dentro
            small = header.find('small', class_='fsize13')
            if small:
                spans = small.find_all('span')
                if len(spans) >= 2:
                    fecha = spans[1].get_text(strip=True)
        # Contenido: todos los <p> dentro de <article>
        contenido = ''
        article = soup.find('article')
        if article:
            parrafos = article.find_all('p')
            contenido = '\n'.join([p.get_text(strip=True) for p in parrafos])
        # Imágenes: todas las <img> dentro de <section class="container">
        imagenes = []
        section = soup.find('section', class_='container')
        if section:
            for img in section.find_all('img'):
                src = img.get('src')
                if src:
                    src_absoluto = urljoin(url, src)
                    imagenes.append(src_absoluto)
    else:
        print(f"Dominio no soportado para extracción de datos: {dominio}")
        return None

    try:
        datos = NewsData(
            titulo=titulo,
            contenido=contenido,
            fecha=fecha,
            imagenes=imagenes
        )
        return datos
    except Exception as e:
        print(f"Error validando datos con Pydantic: {e}")
        return None

# NUEVA FUNCIÓN: Extraer documentos descargables de páginas tipo circulares FTF
def extraer_documentos_descargables(url) -> List[DocumentoDescargable]:
    respuesta = requests.get(url)
    if respuesta.status_code != 200:
        print(f"Error al acceder a la URL: {respuesta.status_code}")
        return []
    soup = BeautifulSoup(respuesta.text, 'html.parser')
    documentos = []
    urls_vistos = set()
    # Buscar solo bloques con enlace de descarga
    for enlace in soup.find_all('a', string=re.compile(r'Descargar', re.I)):
        bloque = enlace.find_parent(['section', 'div', 'article'])
        if not bloque:
            continue
        # Buscar título (h3 o h4) antes del enlace
        h3 = bloque.find(['h3', 'h4'])
        titulo = h3.get_text(strip=True) if h3 else ''
        # Buscar descripción (primer <p> después del título)
        descripcion = ''
        if h3:
            p = h3.find_next('p')
            if p:
                descripcion = p.get_text(strip=True)
        url_descarga = urljoin(url, enlace.get('href'))
        if url_descarga not in urls_vistos and titulo and url_descarga:
            documentos.append(DocumentoDescargable(
                titulo=titulo,
                descripcion=descripcion,
                url_descarga=url_descarga
            ))
            urls_vistos.add(url_descarga)
    return documentos

def contar_paginas_paginadas(url_base, max_paginas=100):
    """
    Dada una URL base, comprueba cuántas páginas paginadas existen añadiendo ?p=2, ?p=3, etc.
    Devuelve el número total de páginas encontradas y la lista de URLs de las noticias.
    El método de extracción depende del dominio de la URL base.
    """
    pagina = 1
    urls_noticias = []
    titulo_listado = None
    dominio = urlparse(url_base).netloc
    while pagina <= max_paginas:
        if pagina == 1:
            url = url_base
        else:
            if '?' in url_base:
                url = f"{url_base}&p={pagina}"
            else:
                url = f"{url_base}?p={pagina}"
        respuesta = requests.get(url)
        if respuesta.status_code != 200:
            break
        soup = BeautifulSoup(respuesta.text, 'html.parser')
        if pagina == 1:
            # Obtener el título de la página de listado

            if dominio == "www.ftf.es":
                titulo_listado = soup.title.string.strip() if soup.title else 'listado_noticias'
            elif dominio == "www.fiflp.com":
                titulo_listado = soup.find('h1').get_text(strip=True)

        # Proceso para www.ftf.es
        if dominio == "www.ftf.es":
            articulos = soup.body.find_all('article') if soup.body else []
            if not articulos:
                break
            for articulo in articulos:
                h3 = articulo.find('h3')
                if h3:
                    a = h3.find('a')
                    if a and a.get('href'):
                        url_noticia = urljoin(url, a.get('href'))
                        urls_noticias.append(url_noticia)
        # Proceso para www.fiflp.com
        elif dominio == "www.fiflp.com":
            section = soup.find('section', class_='container')
            if not section:
                break
            items = section.find_all('div', class_='item')
            if not items:
                break
            for item in items:
                a = item.find('a')
                if a and a.get('href'):
                    url_noticia = urljoin(url, a.get('href'))
                    urls_noticias.append(url_noticia)
        else:
            print(f"Dominio no soportado: {dominio}")
            break
        pagina += 1
    return pagina - 1, urls_noticias, titulo_listado


def limpiar_nombre_archivo(nombre):
    # Eliminar espacios, acentos y caracteres no alfanuméricos, y acortar a 20 caracteres
    nombre = nombre.lower()
    nombre = re.sub(r'[^a-z0-9]', '', nombre)
    return nombre[:20]


def limpiar_fecha(fecha):
    # Quitar espacios en blanco y caracteres no alfanuméricos
    return re.sub(r'\s+', '', fecha)


def guardar_noticias(url_base):
    total, urls, titulo_listado = contar_paginas_paginadas(url_base)
    print(f"Total de páginas paginadas encontradas: {total}")
    print(f"Total de URLs de noticias encontradas: {len(urls)}")
    dominio = urlparse(url_base).netloc
    if dominio == "www.ftf.es":
        subdirectorio = "ftf"
    elif dominio == "www.fiflp.com":
        subdirectorio = "fiflp"
    else:
        subdirectorio = "otros"
    # Crear carpeta con el nombre del listado dentro del subdirectorio correspondiente
    nombre_carpeta = os.path.join(subdirectorio, limpiar_nombre_archivo(titulo_listado or 'listado_noticias'))
    if not os.path.exists(nombre_carpeta):
        os.makedirs(nombre_carpeta)
    for url in urls:
        datos = extraer_datos(url)
        if datos and datos.titulo:
            fecha_archivo = limpiar_fecha(datos.fecha)
            titulo_archivo = limpiar_nombre_archivo(datos.titulo)
            nombre_archivo = f"{fecha_archivo}_{titulo_archivo}.json"
            ruta_archivo = os.path.join(nombre_carpeta, nombre_archivo)
            with open(ruta_archivo, 'w', encoding='utf-8') as f:
                f.write(json.dumps(datos.model_dump(), ensure_ascii=False, indent=2))
            print(f"Noticia guardada: {ruta_archivo}")
        else:
            print(f"No se pudo extraer la noticia: {url}")

# NUEVA FUNCIÓN: Guardar documentos descargables
def guardar_documentos_descargables(url):
    documentos = extraer_documentos_descargables(url)
    print(f"Total de documentos descargables encontrados: {len(documentos)}")
    # Carpeta destino fija
    carpeta_destino = "ftf_documentos"
    if not os.path.exists(carpeta_destino):
        os.makedirs(carpeta_destino)
    # Obtener la ruta de la URL sin el dominio y formatear el nombre del archivo
    parsed = urlparse(url)
    ruta = parsed.path.lstrip('/')  # quitar barra inicial
    if not ruta:
        ruta = 'root'

    # Quitar la última barra de la ruta
    ruta = ruta.rstrip('/')

    # Reemplazar barras por guiones bajos, mantener guiones originales y quitar otros caracteres problemáticos
    ruta = ruta.replace('/', '_')
    nombre_archivo = re.sub(r'[^a-zA-Z0-9_\-]', '', ruta)
    if not nombre_archivo.endswith('.json'):
        nombre_archivo += '.json'
    ruta_archivo = os.path.join(carpeta_destino, nombre_archivo)
    with open(ruta_archivo, 'w', encoding='utf-8') as f:
        json.dump([doc.model_dump() for doc in documentos], f, ensure_ascii=False, indent=2)
    print(f"Lista de documentos guardada: {ruta_archivo}")

def main():
    print("¿Qué tipo de escaneo deseas realizar?")
    print("1. Escanear noticias (funcionamiento anterior)")
    print("2. Escanear documentos descargables (nuevo para páginas tipo circulares FTF)")
    opcion = input("Introduce 1 o 2: ").strip()
    if opcion == '1':
        url_base = input("Introduce la URL base del listado a analizar: ")
        guardar_noticias(url_base)
    elif opcion == '2':
        url = input("Introduce la URL de la página de documentos descargables: ")
        guardar_documentos_descargables(url)
    else:
        print("Opción no válida.")

if __name__ == "__main__":
    main() 