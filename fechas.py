import requests
import json
import bs4
import datetime
import re
from pathlib import Path


# ligas = [[15,"copadeliga"],[23,"alemania"],[39,"brasil"]]
# ligas = [1107,["torneo=1107"],[15,"copadeliga"],[39,"brasil"]]
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:95.0) Gecko/20100101 Firefox/95.0'
    }
nombre_liga = "copadeliga"
codigo_liga = 15
fechas_arr = []
fecha_act = 1

equipos_info = [{"nombre": "Argentinos", "zona": 1}, {"nombre": "Arsenal", "zona": 1}, {"nombre": "Atl Tucuman", "zona": 1}, {"nombre": "Banfield", "zona": 1}, {"nombre": "Barracas Central", "zona": 1}, {"nombre": "Colon", "zona": 1}, {"nombre": "Gimnasia (LP)", "zona": 1}, {"nombre": "Huracan", "zona": 1}, {"nombre": "Independiente", "zona": 1}, {"nombre": "Instituto", "zona": 1}, {"nombre": "River Plate", "zona": 1}, {"nombre": "Rosario Central", "zona": 1}, {"nombre": "Talleres (C)", "zona": 1}, {"nombre": "Velez", "zona": 1}, {
    "nombre": "Belgrano", "zona": 2}, {"nombre": "Boca Juniors", "zona": 2}, {"nombre": "Central Cba (SdE)", "zona": 2}, {"nombre": "Def y Justicia", "zona": 2}, {"nombre": "Estudiantes (LP)", "zona": 2}, {"nombre": "Godoy Cruz", "zona": 2}, {"nombre": "Lanus", "zona": 2}, {"nombre": "Newells", "zona": 2}, {"nombre": "Platense", "zona": 2}, {"nombre": "Racing Club", "zona": 2}, {"nombre": "San Lorenzo", "zona": 2}, {"nombre": "Sarmiento (J)", "zona": 2}, {"nombre": "Tigre", "zona": 2}, {"nombre": "Union", "zona": 2}]


def get_zona(equipo):
    for equipo_info in equipos_info:
        if equipo_info["nombre"] == equipo:
            return equipo_info["zona"]


def get_status(class_name):
    if class_name == 'game-fin':
        return 'finalizado'
    elif class_name == 'game-play':
        return 'jugando'
    elif class_name == 'game-time':
        return 'no empezado'
    elif class_name == 'game-sus':
        return 'suspendido'
    else:
        return ""


def crawl_fecha(fecha):
    link_fecha = "https://www.promiedos.com.ar/verfecha.php?fecha=" + \
        str(fecha) + "_" + str(codigo_liga)
    res = requests.get(link_fecha, headers=headers)
    soup = bs4.BeautifulSoup(res.text, 'html.parser')

    partido_arr = soup.select("#fixturein tr")
    dia = ""
    partidos = 0
    autores_arr = []
    fecha = {"fecha": fecha, "partidos": []}
    for i in range(len(partido_arr)):
        if partido_arr[i].has_attr("class"):
            if partido_arr[i]["class"][0] == "goles":
                gl = partido_arr[i].select("td")[0].text
                gv = partido_arr[i].select("td")[1].text
                autores_arr.append([gl, gv])

    for i in range(len(partido_arr)):
        partido = ""
        if partido_arr[i].has_attr("class"):
            if partido_arr[i]["class"][0] == "diapart":
                dia = partido_arr[i].text.replace("Ã¡","á").replace("Ã©","é")

                print(dia)

        elif partido_arr[i].has_attr("id"):

            pid = int(partido_arr[i]["id"][1:])
            row = partido_arr[i].select("td")
            estado = get_status(row[0]["class"][0])
            cronometro = row[0].text.strip()

            local = row[1].text
            visitante = row[4].text
            zona_local = ""
            zona_visitante = ""
            zona_local = get_zona(local)
            zona_visitante = get_zona(visitante)

            escudo_local = row[1].select("img")[0]["src"]
            escudo_visitante = row[4].select("img")[0]["src"]

            rojas_local = len(row[2].select(".roja"))
            rojas_visitante = len(row[3].select(".roja"))

            goles_local = ""
            if row[2].text != "":
                goles_local = int(row[2].text)

            goles_visitante = ""
            if row[3].text != "":
                goles_visitante = int(row[3].text)

            resultado = ""
            if goles_local > goles_visitante:
                resultado = "L"
            elif goles_local < goles_visitante:
                resultado = "V"
            elif goles_local == goles_visitante and goles_local != "" and goles_visitante != "":
                resultado = "E"
            else:
                resultado = ""

            hay_ficha = len(row[5].select("a")) > 0

            ficha = ""
            video_id = ""
            if hay_ficha:
                f = row[5].select("a")[0]["href"]
                # ficha = re.search("=\w+",f)[0]
                # ficha = re.search("ficha=(\w+)&c=14(&v=(\w+))?",f) is not None
                ficha = re.search("ficha=([^#\&\?]*)?", f)[1]

                hay_video = re.search("v=([^#\&\?]*)?", f) is not None

                if hay_video:
                    video_id = re.search("v=([^#\&\?]*)?", f)[1]

            autores_local = autores_arr[partidos][0][:-2].split("; ")
            autores_visitante = autores_arr[partidos][1][:-2].split("; ")

            partidos = partidos+1
            partido = {"id": pid, "dia": dia, "estado": estado, "cronometro": cronometro, "escudo_local": escudo_local, "local": local, "goles_local": goles_local, "rojas_local": rojas_local, "escudo_visitante": escudo_visitante, "visitante": visitante,
                       "goles_visitante": goles_visitante, "rojas_visitante": rojas_visitante, "ficha": ficha, "video_id": video_id, "autores_local": autores_local, "autores_visitante": autores_visitante, "resultado": resultado, "zona_local": zona_local, "zona_visitante": zona_visitante}

        if partido != "":
            fecha["partidos"].append(partido)
    print(fecha["fecha"])
    return fecha


link = "https://www.promiedos.com.ar/" + nombre_liga
res = requests.get(link, headers=headers)
soup = bs4.BeautifulSoup(res.text, 'html.parser')

cant_fechas = len(soup.select(".cfecha"))+1
fecha_act = soup.select(".cfechact")[0].text


for fecha in range(1, cant_fechas+1):
    fechas_arr.append(crawl_fecha(fecha))

now = datetime.datetime.now()
updatetime = str(now.year)+"/"+str(now.month)+"/"+str(now.day) + \
    "_" + str(now.hour)+":"+str(now.minute)+":"+str(now.second)

main_obj = {"fecha_actual": fecha_act,"fechas": fechas_arr, "actualizado": updatetime}
contenido = json.dumps(main_obj)

ruta = Path(__file__).parent.resolve().joinpath('fechas.json')
archivo = open(ruta, 'w', encoding='utf-8')
archivo.write(contenido)
archivo.close()



# import requests
# import bs4
# link = "https://www.promiedos.com.ar/copadeliga"
# headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:95.0) Gecko/20100101 Firefox/95.0'}
# res = requests.get(link, headers=headers)
# soup = bs4.BeautifulSoup(res.text, 'html.parser')