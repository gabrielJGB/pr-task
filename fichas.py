# import requests
# import bs4

# headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:95.0) Gecko/20100101 Firefox/95.0'}
# link = "https://www.promiedos.com.ar/ficha=xjktktrdqgpn"
# res = requests.get(link, headers=headers)
# soup = bs4.BeautifulSoup(res.text, 'html.parser')

from operator import itemgetter
import requests
import bs4
import json
import re
from pathlib import Path

with open('fichas.json', 'r') as json_file:
    contenido = json.load(json_file)

with open('partidos_verificar.json', 'r') as json_file:
    partidos_verificar = json.load(json_file)

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:95.0) Gecko/20100101 Firefox/95.0'}


incidencias_partido = []


def set_incidencias_partido(arr):
    incidencias_partido.append(arr)


def clear_incidencias_partido():
    incidencias_partido.clear()


def get_incidencias_partido():
    return incidencias_partido


def handle_jugador(tr):
    elem = tr.select("td")

    posicion = elem[0].text
    numero = elem[1].text
    esCapitan = elem[1]["class"][0] == "camiseta2"
    pais = ""
    if len(elem[2].select("img")):
        pais = elem[2].select("img")[0]["src"][3:]
    nombre = elem[2].text.strip()
    edad = elem[3].text
    altura = elem[4].text
    cambio_in = 0
    cambio_out = 0
    lesion = 0
    goles = 0
    amarillas = 0
    rojas = 0

    imgs = elem[2].select("img")
    for img in imgs:
        if "flechaout" in img["src"]:
            cambio_out = 1
        elif "flechain" in img["src"]:
            cambio_in = 1
        elif "lesion" in img["src"]:
            lesion = 1
        elif "pelo" in img["src"]:
            goles = goles + 1
        elif "amarilla" in img["src"]:
            amarillas = amarillas + 1
        elif "roja" in img["src"]:
            rojas = rojas + 1

    return {"posicion": posicion, "numero": numero, "esCapitan": esCapitan, "pais": pais, "nombre": nombre, "edad": edad, "altura": altura, "cambio_in": cambio_in, "cambio_out": cambio_out, "lesion": lesion, "goles": goles, "amarillas": amarillas, "rojas": rojas}


def get_info_equipo(trs, equipo):
    seccion = 0
    info_equipo = {"titulares": [], "suplentes": [], "tecnico": "", "goles": "",
                   "amarillas": [], "rojas": [], "cambios": [], "incidencias": []}

    def handle_incidencia(tr, tipo):

        def handle_minuto(minuto):
            minutos = 0
            if "+" in minuto:
                arr = re.findall("(\d+)\(\+(\d+)\)", minuto)[0]
                for num in arr:
                    minutos = minutos + int(num)
            else:
                minutos = int(minuto)

            return minutos

        arr = tr.text.strip()[:-1].split(";")
        incidencias = []

        for elem in arr:
            incidencia_elem = elem.split("'")
            incidencia = {"minuto": handle_minuto(incidencia_elem[0].strip(
            )), "jugador": incidencia_elem[1].strip().split("⇆"), "tipo": tipo, "equipo": equipo}

            incidencias.append(incidencia)
            set_incidencias_partido(incidencia)

        return incidencias

    for tr in trs:
        if tr.text.strip() == "TITULARES":
            seccion = 1
        elif tr.has_attr("class") and tr["class"][0] == "dttr":
            seccion = 2
        elif tr.text.strip() == "SUPLENTES":
            seccion = 3
        elif tr.text.strip() == "GOLES":
            seccion = 4
        elif tr.text.strip() == "AMARILLAS":
            seccion = 5
        elif tr.text.strip() == "ROJAS":
            seccion = 6
        elif tr.text.strip() == "CAMBIOS":
            seccion = 7
        elif tr.text.strip() == "INCIDENCIAS":
            seccion = 8

        if seccion == 1 and tr.text.strip() != "TITULARES" and tr.text.strip() != "PosN°JugadorEdadAlt(cm)":
            jugador = handle_jugador(tr)
            info_equipo["titulares"].append(jugador)

        elif seccion == 2:
            tecnico = tr.select("td")[1].text.strip()
            info_equipo["tecnico"] = tecnico
            seccion = 0

        elif seccion == 3 and tr.text.strip() != "SUPLENTES":
            jugador = handle_jugador(tr)
            info_equipo["suplentes"].append(jugador)

        elif seccion == 4 and tr.text.strip() != "GOLES":
            incidencias = handle_incidencia(tr, "gol")
            info_equipo["goles"] = incidencias

        elif seccion == 5 and tr.text.strip() != "AMARILLAS":
            incidencias = handle_incidencia(tr, "amarilla")
            info_equipo["amarillas"] = incidencias

        elif seccion == 6 and tr.text.strip() != "ROJAS":
            incidencias = handle_incidencia(tr, "roja")
            info_equipo["rojas"] = incidencias

        elif seccion == 7 and tr.text.strip() != "CAMBIOS":
            incidencias = handle_incidencia(tr, "cambio")
            info_equipo["cambios"] = incidencias

        elif seccion == 8 and tr.text.strip() != "INCIDENCIAS":
            incidencias = handle_incidencia(tr, "incidencia")
            info_equipo["incidencia"] = incidencias

    return info_equipo


def crawl_stats(stats_elem):

    def handle_stat_elem(div,stat):
        p1 = div[0]
        num_l = int(re.findall("(\d+)%?", p1.text)[0])
        width_l = int(re.findall("width:(\d+)%", p1["style"])[0])

        p2 = div[1]
        num_v = int(re.findall("(\d+)%?", p2.text)[0])
        width_v = int(re.findall("width:(\d+)%", p2["style"])[0])

        return {
            "stat":stat,
            "local_num": num_l,
            "local_width": width_l,
            "visit_num": num_v,
            "visit_width": width_v
        }

    # stats = {
    #     "posesion": handle_stat_elem(stats_elem[0].select("div")),
    #     "tiros_efectivos": handle_stat_elem(stats_elem[1].select("div")),
    #     "tiros_total": handle_stat_elem(stats_elem[2].select("div")),
    #     "fouls": handle_stat_elem(stats_elem[3].select("div")),
    #     "corners": handle_stat_elem(stats_elem[4].select("div"))
    # }

    stats = []
    arr = ["posesion", "tiros_efectivos", "tiros_total", "fouls", "corners"]

    for i in range(0,5):
        stat_obj = handle_stat_elem(stats_elem[i].select("div"),arr[i])
        stats.append(stat_obj)

    return stats


def crawl_ficha(ficha, pid):
    # Local, Visitante, goles local, goles visitante, escudos
    # Fecha y hora, Estadio, Arbitro

    # Formaciones: Local,Visitante; Titulares, Suplentes; Tecnicos: Nombre, Edad

    # Incidencias: GOLES, AMARILLAS, ROJAS, CAMBIOS
    # Estadisticas: POSESION. TIROS EFECTIVOS, TIROS TOTALES, FALTAS, CORNERS
    # Jugador: Posicion, Numero (Capitan?), Pais, Nombre,(Incidencia?), Edad, Altura

    link = "https://www.promiedos.com.ar/ficha=" + ficha
    res = requests.get(link, headers=headers)
    soup = bs4.BeautifulSoup(res.text, 'html.parser')
    escudo_local = soup.select('#ficha-escudos img')[0]["src"]
    escudo_visitante = soup.select('#ficha-escudos img')[1]["src"]
    estado = soup.select('#ficha-tiempo span')[0].text
    goles_local = soup.select('#ficha-resultado1')[0].text
    goles_visitante = soup.select('#ficha-resultado2')[0].text
    arbitro = soup.select(".refe span")[0].text.strip()
    colores_local = re.findall("\:(\#[a-z0-9]+)",soup.select(".nomequipo")[0]["style"])
    colores_visitante = re.findall("\:(\#[a-z0-9]+)",soup.select(".nomequipo")[1]["style"])


    local = soup.select(".nomequipo")[0].text
    visitante = soup.select(".nomequipo")[1].text

    trs = soup.select("#formacion1 tr")
    info_local = get_info_equipo(trs, "local")
    trs = soup.select("#formacion2 tr")
    info_visitante = get_info_equipo(trs, "visitante")

    stats = crawl_stats(soup.select("#ficha-estadisticas > div > div"))
    

    ficha_partido = {"local": local, "visitante": visitante, "id_ficha": ficha, "id_partido": pid, "info_local": info_local, "info_visitante": info_visitante, "escudo_local": escudo_local, "escudo_visitante": escudo_visitante,
                     "estado": estado, "goles_local": goles_local, "goles_visitante": goles_visitante, "arbitro": arbitro, "incidencias": sorted(get_incidencias_partido(), key=lambda x: x["minuto"]), "estadisticas": stats}

    clear_incidencias_partido()

    return ficha_partido


link = "https://gabrieljgb.github.io/pr-task/fechas.json"
res = requests.get(link, headers=headers)

if res.status_code == 200:
    fechas_resp = res.json()

    # partidos = [[partido["ficha"],partido["id"]] for fecha in fechas_resp["fechas"] for partido in fecha["partidos"]]
    partidos_res = [{"ficha": partido["ficha"], "video_id": partido["video_id"], "id":partido["id"], "estado":partido["estado"]}
                    for fecha in fechas_resp["fechas"] for partido in fecha["partidos"]]

for partido_res in partidos_res:
    if partido_res["video_id"] != "":
        for partido_verificar in partidos_verificar:
            if partido_verificar["id"] == partido_res["id"] and partido_verificar["verificado"] == False:
                ficha_partido = crawl_ficha(
                    partido_res["ficha"], partido_res["id"])
                contenido.append(ficha_partido)
                partido_verificar["verificado"] = True
                print("id: ", partido_res["id"])


with open('fichas.json', 'w') as json_file:
    json.dump(contenido, json_file, separators=(',', ':'))

with open('partidos_verificar.json', 'w') as json_file:
    json.dump(partidos_verificar, json_file, indent=4)
