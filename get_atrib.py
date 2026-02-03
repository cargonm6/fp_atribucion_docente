import csv
import os
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
import pandas as pd

base_url = "https://www.todofp.es"
urls = [
    "/que-estudiar/grados-d/fp-grado-basico.html",
    "/que-estudiar/grados-d/grado-medio.html",
    "/que-estudiar/grados-d/grado-superior.html",
    "/que-estudiar/grados-e/curso-especializacion.html"
]

filename = "atribuciones_fp.csv"


def get_title_info(p_url: str) -> list:
    try:
        response = requests.get(p_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        title = soup.find('div', class_='titulo').find('h1').get_text(strip=True)
        branch = soup.find('div', class_='titulo').find('p').get_text(strip=True)
        level = soup.find('div', class_='info').find('p').get_text(strip=True)

        return [level, branch, title]

    except Exception as e:
        print(f"Error obteniendo info de título: {p_url} -> {e}")
        return ["", "", ""]


def extract_modules_from_atribuciones(url_atribuciones: str) -> list:
    try:
        response = requests.get(url_atribuciones)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        modules = []

        for div in soup.find_all('div', class_='elemento'):
            modulo = div.find('p', class_='titulo')
            cuerpo_div = div.find('div', class_='cte')

            if modulo and cuerpo_div:
                modulo_text = modulo.get_text(strip=True)
                cuerpos = cuerpo_div.find_all('li')
                for li in cuerpos:
                    cuerpo_text = li.get_text(strip=True)
                    if cuerpo_text:
                        modules.append((modulo_text, cuerpo_text))

        return modules

    except Exception as e:
        print(f"Error accediendo a atribuciones: {url_atribuciones} -> {e}")
        return []


def recorrer_y_guardar():

    resultados = []

    for path in urls:
        print(f"\n🔍 Accediendo a: {base_url + path}")
        response = requests.get(base_url + path)
        soup = BeautifulSoup(response.content, 'html.parser')

        # Extraer todas las filas de títulos
        rows = [
            tr for tr in soup.find_all('tr')
            if tr.find('td', {'headers': 'titulacion'}) and tr.find('td', {'headers': 'titulacion'}).find('a')
        ]

        for tr in tqdm(rows, desc=f"Procesando {path}", unit="título"):
            a = tr.find('td', {'headers': 'titulacion'}).find('a')
            if a and a.get('href'):
                detalle_url = base_url + a.get('href')
                atrib_url = detalle_url[:-5] + "/atribucion-docente.html"

                level, branch, title = get_title_info(detalle_url)
                mod_cuerpo_pairs = extract_modules_from_atribuciones(atrib_url)

                for modulo, cuerpo in mod_cuerpo_pairs:
                    resultados.append([level, branch, title, modulo, cuerpo, atrib_url])

    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Nivel', 'Familia', 'Título', 'Módulo', 'Cuerpo', 'URL'])
        writer.writerows(resultados)

    print(f"\n✅ Archivo generado: {os.path.abspath(filename)}")


if __name__ == "__main__":

    if not os.path.isfile(filename):
        recorrer_y_guardar()

    titulos = [
        'Técnico en Sistemas Microinformáticos y Redes',
        'Técnico Superior en Desarrollo de Aplicaciones Web',
        'Técnico Superior en Administración de Sistemas Informáticos en Red',
        'Curso de Especialización en Desarrollo de videojuegos y realidad virtual (Acceso GS)',
        'Curso de especialización de Desarrollo de aplicaciones en lenguaje Python (Acceso GS)',
        'Técnico Superior en Animaciones 3D, Juegos y Entornos Interactivos',
    ]

    df = pd.read_csv(filename, encoding="utf-8")
    df_filtrado = df[(df['Cuerpo'] == 'Informática (CAT/PES)') & (df['Título'].isin(titulos))]
    df_filtrado.to_csv('atribuciones_inf.csv', encoding='latin1', sep=';', index=False)
