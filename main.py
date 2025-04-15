import requests
from bs4 import BeautifulSoup
import csv
import os

"""
CÓDIGO PARA OBTENER LOS CICLOS CON ATRIBUCIONES DOCENTES PARA [INFORMÁTICA (CAT/PES)]
Máster en Profesor/a de Educación Secundaria - Carlos González Marco
"""

# Variables globales
keyword = "Tecnología"
base_url = "https://www.todofp.es"
urls = ["/que-estudiar/grados-d/fp-grado-basico.html",
        "/que-estudiar/grados-d/grado-medio.html",
        "/que-estudiar/grados-d/grado-superior.html",
        "/que-estudiar/grados-e/curso-especializacion.html"]


def check_title(p_url: str) -> list:
    """
    Función para obtener el nivel, familia y título del curso en la página web.
    :param p_url: URL de la web.
    :return:
    """
    try:
        print("Buscando palabra clave (%s)..." % p_url, end="")
        # Obtener el contenido de la página web
        respuesta = requests.get(p_url)
        respuesta.raise_for_status()  # Lanza una excepción si la petición no tiene éxito

        soup = BeautifulSoup(respuesta.content, 'html.parser')

        tit, bra, lev = "", "", ""

        # Verificar si el texto específico está en el contenido de la página
        for div in soup.find_all('div', {'class': 'titulo'}):
            h1 = div.find('h1')
            tit = h1.get_text() if h1 else ""

        for div in soup.find_all('div', {'class': 'titulo'}):
            p = div.find('p')
            bra = p.get_text() if p else ""

        for div in soup.find_all('div', {'class': 'info'}):
            p = div.find('p')
            lev = p.get_text() if p else ""

        return [lev, bra, tit]

    except requests.exceptions.RequestException as e:
        print(" ERROR:", e)
        return []


def check_text(p_url: str, p_keyword: str) -> list:
    """
    Función para buscar palabras clave en la página web.
    :param p_url: URL de la web.
    :param p_keyword: Palabra clave.
    :return: Booleano.
    """
    try:
        print("Buscando palabra clave (%s)..." % p_url, end="")
        # Obtener el contenido de la página web
        respuesta = requests.get(p_url)
        respuesta.raise_for_status()  # Lanza una excepción si la petición no tiene éxito

        soup = BeautifulSoup(respuesta.content, 'html.parser')

        kw_in = []

        # Verificar si el texto específico está en el contenido de la página
        for div in soup.find_all('div', {'class': 'elemento'}):
            p = div.find('p', {'class': 'titulo'})
            cte = div.find('div', {'class': 'cte'})
            if p and cte:
                if p_keyword.upper() in cte.getText().upper():
                    kw_in.append(p.getText())

        if len(kw_in) > 0:
            print(" SÍ")
            return kw_in
        else:
            print(" NO")
            return []

    except requests.exceptions.RequestException as e:
        print(" ERROR:", e)
        return []


def extract_urls(p_url: str, p_keyword: str) -> list:
    """
    Función para extraer las URL de los enlaces en las tablas, y obtener las que tienen la palabra clave.
    :param p_url: URL base.
    :param p_keyword: Palabra clave.
    :return: Lista de URL con palabra clave.
    """
    response = requests.get(base_url + p_url)
    soup = BeautifulSoup(response.content, 'html.parser')

    p_urls = []

    # Buscar todas las filas de datos (tr)
    for tr in soup.find_all('tr'):
        # Buscar los td con headers "nivel" y "titulacion"
        # td_nivel = tr.find('td', {'headers': 'nivel'})
        td_titulacion = tr.find('td', {'headers': 'titulacion'})

        # Si se encuentran ambos, extraer la URL del enlace
        if td_titulacion:
            link = td_titulacion.find('a')
            if link:
                new_url = (base_url + link.get('href'))
                level, branch, title = check_title(new_url)
                new_url = (base_url + link.get('href'))[:-5] + "/atribucion-docente.html"
                mod = check_text(new_url, p_keyword)

                if len(mod) > 0:
                    val = {
                        "level": level,
                        "branch": branch,
                        "title": title,
                        "module": mod,
                        "staff": p_keyword,
                        "url": new_url
                    }

                    p_urls.append(val)

    return p_urls


if __name__ == "__main__":

    answer = input(f"Introduzca especialidad (o ENTER para valor por defecto, \"{keyword}\") > ")
    answer = keyword if answer == "" else answer

    filename = keyword.replace("/", "-").strip()

    data = []

    # Recorre las URL base y añade a la lista las que presentan la palabra clave
    for url in urls:
        print(f"URL: {url}")
        data.extend(extract_urls(url, keyword))

        with open(f'{filename}.csv', mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(
                ['Nivel', 'Familia', 'Título', 'Módulo', 'Cuerpo', 'URL'])  # Escribe las cabeceras en el CSV

            for entry in data:
                # Para cada módulo, escribe una fila con el title, url y el módulo correspondiente
                for module in entry['module']:
                    writer.writerow(
                        [entry['level'], entry['branch'], entry['title'], module, entry['staff'], entry['url']])

    print(f"Se ha generado un resultado en: \"{os.path.abspath(filename)}\"")
