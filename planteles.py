# import requests
# import bs4
# headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:95.0) Gecko/20100101 Firefox/95.0'}
# link = "https://www.transfermarkt.es/club-atletico-river-plate/startseite/verein/209/saison_id/2022"
# res = requests.get(link, headers=headers)
# soup = bs4.BeautifulSoup(res.text, 'html.parser')

import requests
import bs4
import json
import time
import re

with open('planteles.json', 'r') as json_file:
    contenido = json.load(json_file)

headers = {'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36'}

# link_base = "https://webcache.googleusercontent.com/search?q=cache:https://www.transfermarkt.es"
link_base = "https://www.transfermarkt.es"


def main():
    soup = get_soup_element("/copa-de-la-liga-profesional-de-futbol/startseite/wettbewerb/CDLP")
    trs = soup.select(".items")[0].select("tr")[2:]
    

    for tr in trs:
        link = tr.select("a")[0]["href"]
        nombre = tr.select("a")[0]["title"]
        nombre_modificado = modificar_nombre(nombre)
        contenido.append(crawl_team(link,nombre_modificado))
        time.sleep(0.5)

        


def modificar_nombre(nombre):
    if nombre == "CA River Plate":
        return "River Plate"
    elif nombre == "CA Boca Juniors":
        return "Boca Juniors"
    elif nombre == "CA San Lorenzo de Almagro":
        return "San Lorenzo"
    elif nombre == "CA Talleres":
        return "Talleres (C)"
    elif nombre == "CA Vélez Sarsfield":
        return "Velez"
    elif nombre == "Club Estudiantes de La Plata":
        return "Estudiantes (LP)"
    elif nombre == "AA Argentinos Juniors":
        return "Argentinos"
    elif nombre == "CSD Defensa y Justicia":
        return "Def y Justicia"
    elif nombre == "CA Newell's Old Boys":
        return "Newells"
    elif nombre == "Club Atlético Lanús":
        return "Lanus"
    elif nombre == "Club Atlético Tigre":
        return "Tigre"
    elif nombre == "CA Huracán":
        return "Huracan"
    elif nombre == "Club Atlético Colón":
        return "Colon"
    elif nombre == "Club Atlético Tucumán":
        return "Atl Tucuman"
    elif nombre == "CA Banfield":
        return "Banfield"
    elif nombre == "CA Independiente":
        return "Independiente"
    elif nombre == "Club de Gimnasia y Esgrima La Plata":
        return "Gimnasia (LP)"
    elif nombre == "Club Atlético Belgrano":
        return "Belgrano"
    elif nombre == "CA Rosario Central":
        return "Rosario Central"
    elif nombre == "Club Atlético Unión":
        return "Union"
    elif nombre == "CD Godoy Cruz Antonio Tomba":
        return "Godoy Cruz"
    elif nombre == "Instituto AC Córdoba":
        return "Instituto"
    elif nombre == "CA Barracas Central":
        return "Barracas Central"
    elif nombre == "CA Central Córdoba (SdE)":
        return "Central Cba (SdE)"
    elif nombre == "CA Platense":
        return "Platense"
    elif nombre == "CA Sarmiento (Junín)":
        return "Sarmiento (J)"
    elif nombre == "Arsenal Fútbol Club":
        return "Arsenal"
    else:
        return nombre

    
def get_soup_element(link):
    res = requests.get(link_base+link, headers=headers)
    return bs4.BeautifulSoup(res.text, 'html.parser')


def get_player_info(player_elem,equipo):
    jugador = {
        "numero": "-",
        "posicion": "",
        "equipo":equipo,
        "pos_detalle": "",
        "foto_small": "",
        "foto_medium": "",
        "foto_big": "",
        "link":"",
        "nombre": "",
        "fecha_nac": "",
        "edad": 0,
        "nacionalidad": [],
        "valor": ""
    }

    tds = player_elem.select("td")

    jugador["posicion"] = tds[0]["title"]
    jugador["numero"] = tds[0].text
    jugador["pos_detalle"] = tds[1].select("td")[2].text
    jugador["nombre"] = tds[1].select(".inline-table img")[0]["alt"]

    fecha_text = tds[6].text
    fecha_elem = re.findall("(\d+\/\d+\/\d+) \((\d+)\)",fecha_text)
    if len(fecha_elem):
        jugador["fecha_nac"] = fecha_elem[0][0]
        jugador["edad"] = fecha_elem[0][1]

    jugador["pais"] = tds[7].select("img")[0]["alt"]

    # print("\n\n")
    # print(" ----- ",equipo,jugador["nombre"]," ------ ")
    # print(tds[1].select("img")[0])
    # print(" -------------------------------------------------")
    # print("\n\n")

    # if tds[1].select("img")[0]["alt"] == jugador["nombre"]:
    img = tds[1].select(".inline-table img")[0].attrs["data-src"]
    
        
    jugador["foto_small"] = img
    jugador["foto_medium"] = img.replace("small","medium")
    jugador["foto_big"] = img.replace("small","big")

    flags = tds[7].select("td img")

    for flag in flags:
        jugador["nacionalidad"].append({
            "pais":flag["alt"],
            "bandera":flag["src"]
        })

    if len(tds[8].select("a")) == 0:
        jugador["valor"] = "-"
    else:
        jugador["valor"] = tds[8].select("a")[0].text.replace(" mill.","M").replace(" mil ","k ")
        
    jugador["link"] = "https://www.transfermarkt.es" + tds[1].select("tr")[0]["data-link"]

    

    return jugador


def crawl_team(link,equipo):

    equipo = {
        "equipo": equipo,
        "escudo": "",
        "jugadores": []
    }

    soup = get_soup_element(link)
    # equipo["equipo"] = soup.select("h1")[0].text[2:].strip()
    equipo["escudo"] = soup.select("#main > main > header > div.data-header__profile-container img")[0]["src"]

    players_elem = soup.select(".even")

    for player_elem in players_elem:
        x = get_player_info(player_elem,equipo["equipo"])
        equipo["jugadores"].append(x)


    players_elem = soup.select(".odd")
    
    for player_elem in players_elem:
        x = get_player_info(player_elem,equipo["equipo"])
        equipo["jugadores"].append(x)

    print(equipo["equipo"])

    return equipo


main()


with open('planteles.json', 'w') as json_file:
    json.dump(contenido, json_file, separators=(',', ':'))
