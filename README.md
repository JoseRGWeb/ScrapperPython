# ScrapperPython

Aplicación en Python para extraer y guardar información de todas las noticias de un listado paginado de una web.

## Descripción
Este proyecto permite obtener y guardar los datos de todas las noticias listadas en una página web con paginación. Utiliza las librerías `requests` para realizar las peticiones HTTP y `BeautifulSoup` para analizar el HTML y extraer la información deseada.

El script recorre todas las páginas del listado, obtiene los enlaces de las noticias y guarda los datos de cada noticia en un archivo `.json` dentro de una carpeta específica.

## Funcionamiento
- Se solicita la URL base del listado de noticias (por ejemplo, la página principal de un blog o sección de noticias).
- El script recorre todas las páginas del listado añadiendo el parámetro `?p=2`, `?p=3`, etc., hasta que no haya más noticias.
- De cada noticia, se extraen los siguientes datos:
  - **titulo**: El texto del primer `<h2>` dentro de `<article>`.
  - **contenido**: Todo el texto de los `<p>` dentro de `<article>`, concatenado y separado por saltos de línea.
  - **fecha**: El texto de la etiqueta `<i>` con clase `ti-calendar` dentro de `<article>`.
  - **imagenes**: Lista de URLs absolutas de todas las imágenes (`<img>`) dentro de `<article>`.
- Los datos de cada noticia se guardan en un archivo `.json` dentro de una carpeta cuyo nombre corresponde al título del listado (limpiado y acortado).
- El nombre de cada archivo es la fecha de la noticia (sin espacios), seguida de un guion bajo y 20 caracteres del título (sin espacios ni caracteres extraños).

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