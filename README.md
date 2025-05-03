# ScrapperPython

Aplicación en Python para extraer y guardar información de todas las noticias de un listado paginado de una web. Actualmente soporta los dominios www.ftf.es y www.fiflp.com, cada uno con su propio formato de extracción.

## Descripción
Este proyecto permite obtener y guardar los datos de todas las noticias listadas en una página web con paginación. Utiliza las librerías `requests` para realizar las peticiones HTTP y `BeautifulSoup` para analizar el HTML y extraer la información deseada.

El script recorre todas las páginas del listado, obtiene los enlaces de las noticias y guarda los datos de cada noticia en un archivo `.json` dentro de una carpeta específica.

## Funcionamiento general
- Se solicita la URL base del listado de noticias (por ejemplo, la página principal de un blog o sección de noticias).
- El script recorre todas las páginas del listado añadiendo el parámetro `?p=2`, `?p=3`, etc., hasta que no haya más noticias.
- De cada noticia, se extraen los siguientes datos:
  - **titulo**
  - **contenido**
  - **fecha**
  - **imagenes**
- Los datos de cada noticia se guardan en un archivo `.json` dentro de una carpeta cuyo nombre corresponde al título del listado (limpiado y acortado).
- El nombre de cada archivo es la fecha de la noticia (sin espacios), seguida de un guion bajo y 20 caracteres del título (sin espacios ni caracteres extraños).

## Soporte para dominios y particularidades

### www.ftf.es
- **Listado de noticias:**
  - Cada noticia está en una etiqueta `<article>`, el enlace está en `<h3><a></a></h3>`.
- **Extracción de datos de la noticia:**
  - **Título:** Primer `<h2>` dentro de `<article>`
  - **Contenido:** Todos los `<p>` dentro de `<article>`
  - **Fecha:** Texto de la etiqueta `<i class="ti-calendar">` (ver código para detalles)
  - **Imágenes:** Todas las `<img>` dentro de `<article>`

### www.fiflp.com
- **Listado de noticias:**
  - Buscar `<section class="container">`, dentro de ella cada noticia está en `<div class="item">`, el enlace está en el `<a>` dentro de ese div.
- **Extracción de datos de la noticia:**
  - **Título:** Dentro de `<header class="blog-post">`, el contenido de `<h1>`
  - **Contenido:** Todos los `<p>` dentro de `<article>`
  - **Fecha:** Dentro de `<header class="blog-post">` → `<small class="fsize13">`, el contenido del segundo `<span>`
  - **Imágenes:** Todas las `<img>` dentro de `<section class="container">`

## Requisitos
- Python 3.7 o superior
- Las dependencias listadas en `requirements.txt`

## Crear un entorno virtual (opcional pero recomendado)
Se recomienda crear un entorno virtual para aislar las dependencias del proyecto. Puedes hacerlo con los siguientes comandos:

En Windows:
```bash
python -m venv venv
venv\Scripts\activate
```

En macOS/Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```

## Instalación
1. Clona este repositorio o descarga los archivos en tu máquina local.
2. (Opcional) Crea y activa un entorno virtual como se indica arriba.
3. Instala las dependencias ejecutando:
   ```bash
   pip install -r requirements.txt
   ```

## Uso
1. Ejecuta el script principal:
   ```bash
   python scraper.py
   ```
2. Introduce la URL base del listado de noticias cuando se te solicite.
3. El programa recorrerá todas las páginas del listado, extraerá los datos de cada noticia y los guardará en archivos `.json` dentro de una carpeta.

## Ejemplo de estructura de salida
```
listadodenoticias/  # Carpeta creada a partir del título del listado
  02mayo2025_titulodelanoticiaejem.json
  03mayo2025_otranoticiaejemplo.json
  ...
```

## Personalización
- Puedes modificar la función `extraer_datos` en `scraper.py` para adaptar la lógica de extracción a la estructura de las páginas de tu sitio objetivo.

## Licencia
Este proyecto está bajo la licencia MIT. 